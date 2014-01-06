import os
import imp
import sys
import time
import random
import logging
import os.path

from types import ModuleType
from collections import OrderedDict

import webalchemy.tornado
import webalchemy.tornado.web
import webalchemy.tornado.ioloop
import webalchemy.tornado.websocket

from webalchemy.tornado import gen

from webalchemy.remotedocument import RemoteDocument

# logger for internal purposes
log = logging.getLogger(__name__)


def _generate_session_id():
    return str(random.randint(0, 1e16))


class _MainHandler(webalchemy.tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        log.info('Initiallizing new app!')
        self.main_html = kwargs['main_html']

    @gen.coroutine
    def get(self, *varargs):
        self.add_header('X-UA-Compatible', 'IE=edge')
        if not varargs:
            varargs = ('',)
        self.main_html = self.main_html.replace('__ARGS__', str(varargs[0]))
        self.write(self.main_html)


class WebSocketHandler(webalchemy.tornado.websocket.WebSocketHandler):

    @gen.coroutine
    def initialize(self, **kwargs):
        log.info('Initiallizing a websocket handler!')
        try:
            self.id = _generate_session_id()
            self.remotedocument = RemoteDocument()
            self.closed = True
            self.session_id = None
            self.tab_id = None
            self.vendor_type = None
            self.shared_data = kwargs['shared_data']
            self.session_data_store = kwargs['session_data_store']
            self.tab_data_store = kwargs['tab_data_store']
            self.session_data = None
            self.tab_data = None
            self.local_doc = kwargs['local_doc_class']()
            self.local_doc_initialized = False
            self.sharedhandlers = kwargs['shared_wshandlers']
            self.sharedhandlers[self.id] = self
            self.is_new_tab = None
            self.is_new_session = None
            self.main_html = kwargs['main_html']
        except:
            log.exception('Initialization of websocket handler failed!')

    @gen.coroutine
    def open(self, *varargs):
        self.closed = False
        log.info('WebSocket opened')
        self.getargs = varargs

    @gen.coroutine
    def handle_binary_message(self, message):
        # TODO: implement this!
        raise NotImplementedError

    @gen.coroutine
    def on_message(self, message):
        log.info('Message received:\n' + message)
        try:
            if not isinstance(message, str):
                log.info('binary data')
                yield self.handle_binary_message(message)
            elif not self.local_doc_initialized:
                log.info('Initializing local document...')
                self.session_id = message.split(':')[1]
                self.is_new_session = False
                if self.session_id == 'null':
                    log.info('initializing new session...')
                    self.is_new_session = True
                    self.session_id = self.id
                    self.remotedocument.inline('set_cookie("webalchemy","' + self.session_id + '",3);\n')
                self.tab_id = message.split(':')[3]
                self.is_new_tab = False
                if self.tab_id == '':
                    log.info('initializing new tab...')
                    self.tab_id = self.id
                    self.remotedocument.inline('window.name="' + self.tab_id + '";\n')
                    self.is_new_tab = True
                self.vendor_type = message.split(':')[-1]
                self.remotedocument.set_vendor_prefix(self.vendor_type)
                self.session_data = self.session_data_store.get_store(self.session_id)
                self.tab_data = self.tab_data_store.get_store(self.tab_id)
                r = self.local_doc.initialize(remote_document=self.remotedocument, comm_handler=self,
                                              session_id=self.session_id, tab_id=self.tab_id,
                                              shared_data=self.shared_data, session_data=self.session_data,
                                              tab_data=self.tab_data, is_new_tab=self.is_new_tab,
                                              is_new_session=self.is_new_session,
                                              getargs=self.getargs,
                                              main_html=self.main_html)
                if r is not None:
                    yield r
                self.local_doc_initialized = True
            else:
                if message.startswith('rpc: '):
                    yield self.handle_js_to_py_rpc_message(message)
                elif message != 'done':
                    log.info('Passing message to document inmessage...')
                    r = self.local_doc.inmessage(message)
                    if r is not None:
                        yield r
                elif message != 'done':
                    raise Exception('bad message received: '+str(message))

            yield self.flush_dom()
        except:
            log.exception('Failed handling message:')

    @gen.coroutine
    def send_data(self, text, data):
        # TODO: implement!
        # will have to have a binary format for both text and binary data
        # also change the handling in the client
        raise NotImplementedError

    @gen.coroutine
    def flush_dom(self):
        code = self.remotedocument.pop_all_code()
        if code != '':
            log.info('FLUSHING DOM WITH FOLLOWING MESSAGE:\n' + code)
            # this is good to simulate latency
            #yield async_delay(2)
            self.write_message(code)
        else:
            log.info('FLUSHING DOM: **NOTHING TO FLUSH**')

    @gen.coroutine
    def please_reload(self):
        self.write_message('location.reload();\n')
        self.close()

    @gen.coroutine
    def msg_to_sessions(self, msg, send_to_self=False, to_session_ids=None):
        log.info('Sending message to sessions ' + str(len(self.sharedhandlers)) + ' documents in process:')
        log.info('Message: ' + msg)
        if not to_session_ids:
            lst = self.sharedhandlers.keys()
        else:
            lst = to_session_ids
        for k in lst:
            h = self.sharedhandlers[k]
            if h is not self or send_to_self:
                try:
                    r = h.local_doc.outmessage(self.id, msg)
                    if r is not None:
                        yield r
                    yield h.flush_dom()
                except:
                    log.exception('Failed handling outmessage. Exception:')

    @gen.coroutine
    def on_close(self):
        self.closed = True
        log.info('WebSocket closed')
        log.info('Removing shared doc')
        del self.sharedhandlers[self.id]
        if hasattr(self.local_doc, 'onclose'):
            log.info('Calling local document onclose:')
            try:
                r = self.local_doc.onclose()
                if r is not None:
                    yield r
            except:
                log.exception('Failed handling local document onclose. Exception:')

    @gen.coroutine
    def prepare_session_for_general_reload(self):
        if hasattr(self.local_doc, 'prepare_session_for_general_reload'):
            log.info('preparing session for reload...')
            r = self.local_doc.prepare_session_for_general_reload()
            if r is not None:
                yield r

    @gen.coroutine
    def handle_js_to_py_rpc_message(self, msg):
        log.info('Handling message as js->py RPC call')
        pnum, *etc = msg[5:].split(',')
        pnum = int(pnum)
        args_len = etc[:pnum]
        args_txt = ''.join(etc[pnum:])
        args = []
        curr_pos = 0
        for ln in args_len:
            ln = int(ln)
            args.append(args_txt[curr_pos:curr_pos + ln])
            curr_pos += ln
        rep, *args = args
        wr = self.remotedocument.jsrpcweakrefs[rep]
        fn = wr()
        if fn is None:
            del self.remotedocument.jsrpcweakrefs[rep]
        log.info('Calling local function: ' + str(fn))
        log.info('With args: ' + str(args))
        try:
            r = fn(self.id, *args)
            if r is not None:
                yield r
        except:
            log.exception('JS RPC call failed')

    @gen.coroutine
    def rpc(self, f, *varargs, send_to_self=False, to_session_ids=None, **kwargs):
        log.info('Sending py->py rpc: ' + f.__name__)
        log.info('PARAMS: varargs: ' + str(varargs) + ' kwargs: ' + str(kwargs))
        if not to_session_ids:
            lst = self.sharedhandlers.keys()
        else:
            lst = to_session_ids
        log.info('lst=' + str(lst))
        log.info('self.id=' + self.id)
        for k in lst:
            h = self.sharedhandlers[k]
            if h is not self or send_to_self:
                try:
                    r = getattr(h.local_doc, f.__name__)(self.id, *varargs, **kwargs)
                    if r is not None:
                        yield r
                    yield h.flush_dom()
                except:
                    log.exception('PY RPC call failed for target session: ' + k)


@gen.coroutine
def async_delay(secs):
    yield gen.Task(webalchemy.tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)


def _dreload(module, dreload_blacklist_starting_with, just_visit=False):
    _s = {module.__name__}
    _base_file = os.path.realpath(module.__file__)
    _base_path = os.path.dirname(_base_file)
    _reloaded_files = []

    def __dreload(mdl):
        """Recursively reload modules."""
        nonlocal _s
        nonlocal _base_path
        nonlocal _reloaded_files

        for name in dir(mdl):
            mm = getattr(mdl, name)
            if type(mm) is not ModuleType:
                if (hasattr(mm, '__module__') and
                        mm.__module__ is not None):
                    mm = sys.modules[mm.__module__]

            if (not hasattr(mm, '__file__') or
                    not os.path.realpath(mm.__file__).startswith(_base_path) or
                    mm.__name__[0] == '_' or
                    '._' in mm.__name__ or
                    mm.__name__ in _s or
                    any(mm.__name__.startswith(bln) for bln in dreload_blacklist_starting_with)):
                continue

            _s.add(mm.__name__)
            __dreload(mm)
        _reloaded_files.append(os.path.realpath(mdl.__file__))
        if not just_visit:
            log.info('reloading: ' + str(mdl.__name__))
            imp.reload(mdl)
        else:
            log.info('visiting: ' + str(mdl.__name__))

    __dreload(module)
    return _reloaded_files


class _AppUpdater:
    def __init__(self, app, cls, shared_wshandlers, hn, dreload_blacklist_starting_with, shared_data,
                 additional_monitored_files):
        self.app = app
        self.cls = cls
        self.shared_wshandlers = shared_wshandlers
        self.shared_data = shared_data
        self.hn = hn
        self.dreload_blacklist_starting_with = dreload_blacklist_starting_with
        self.mdl = sys.modules[self.cls.__module__]
        self.mdl_fn = self.mdl.__file__
        self.monitored_files = _dreload(self.mdl, self.dreload_blacklist_starting_with, just_visit=True)
        self.set_additional_monitored_files(additional_monitored_files)
        log.info('monitored files: ' + str(self.monitored_files))
        self.last_time_modified = {
            fn: os.stat(fn).st_mtime for fn in self.monitored_files
        }

    def set_additional_monitored_files(self, fns):
        if fns:
            self.monitored_files.extend(fns)

    def update_app(self):
        try:
            # this is inside a try block so we track for missing files
            if not any(os.stat(fn).st_mtime != self.last_time_modified[fn] for fn in self.monitored_files):
                return
        except:
            pass
        log.info('Reloading document!')
        self.last_time_modified = {fn: os.stat(fn).st_mtime for fn in self.monitored_files}
        data = None
        if hasattr(self.cls, 'prepare_app_for_general_reload'):
            data = self.cls.prepare_app_for_general_reload()
        _dreload(self.mdl, self.dreload_blacklist_starting_with)
        tmp_cls = getattr(self.mdl, self.cls.__name__)
        if hasattr(tmp_cls, 'recover_app_from_general_reload'):
            tmp_cls.recover_app_from_general_reload(data)
        if hasattr(tmp_cls, 'initialize_shared_data'):
            tmp_cls.initialize_shared_data(self.shared_data)

        self.app.handlers[0][1][self.hn].kwargs['local_doc_class'] = tmp_cls
        log.info('wsh=' + str(self.shared_wshandlers))
        for wsh in self.shared_wshandlers.values():
            wsh.prepare_session_for_general_reload()
            wsh.please_reload()


class PrivateDataStore:

    def __init__(self):
        self.d = dict()

    def get_store(self, uid):
        if uid in self.d:
            return self.d[uid]
        pd = OrderedDict()
        self.d[uid] = pd
        return pd

    def remove_store(self, uid):
        del self.d[uid]


def run(app=None, host='127.0.0.1', port=8080, **kwargs):

    static_path_from_local_doc_base = kwargs.get('static_path_from_local_doc_base', 'static')
    main_html_file_path = kwargs.get('main_html_file_path', None)
    dreload_blacklist_starting_with = kwargs.get('', ('webalchemy', 'webalchemy.tornado'))
    shared_data_class = kwargs.get('shared_data_class', OrderedDict)
    tab_data_store_class = kwargs.get('private_data_store_class', PrivateDataStore)
    session_data_store_class = kwargs.get('private_data_store_class', PrivateDataStore)
    additional_monitored_files = kwargs.get('additional_monitored_files', None)
    ssl = kwargs.get('ssl', False)
    ssl_cert_file = kwargs.get('cert_file', 'mydomain.crt')
    ssl_key_file = kwargs.get('ket_file', 'mydomain.key')
    ws_explicit_route = kwargs.get('ws_explicit_route', r'websocket')
    ws_route = r'/'+ws_explicit_route+r'/(.*)'
    main_explicit_route = kwargs.get('main_route', None)
    if not main_explicit_route:
        main_route = r'/(.*)'
    else:
        main_route = r'/'+main_explicit_route+r'/(.*)'

    if static_path_from_local_doc_base:
        mdl = sys.modules[app.__module__]
        mdl_fn = mdl.__file__
        static_path = os.path.realpath(mdl_fn)
        static_path = os.path.dirname(static_path)
        static_path = os.path.join(static_path, static_path_from_local_doc_base)
        log.info('static_path: ' + static_path)
        hn = 3
    else:
        static_path = None
        hn = 0

    shared_wshandlers = {}
    shared_data = shared_data_class()
    if hasattr(app, 'initialize_shared_data'):
        app.initialize_shared_data(shared_data)
    session_data_store = session_data_store_class()
    tab_data_store = tab_data_store_class()

    # prepare main_html ...
    mfn = os.path.realpath(__file__)
    mfn = os.path.dirname(mfn)
    if not main_html_file_path:
        ffn = os.path.join(mfn, 'main.html')
    else:
        ffn = main_html_file_path
    lines = []
    with open(ffn, 'r') as f:
        for l in f:
            if l.lstrip().startswith('-->'):
                fnjs = l.split()[1].strip()
                if fnjs == 'websocket':
                    continue
                if fnjs == 'include':
                    if hasattr(app, 'include'):
                        for i in app.include:
                            lines.append('<script src="'+i+'"></script>\n')
                    continue
                if fnjs == 'meta':
                    if hasattr(app, 'meta'):
                        for m in app.meta:
                            js = '<meta '
                            for a, v in m.items():
                                js += a+'="'+v+'" '
                            js += '>\n'
                            lines.append(js)
                    continue
                fnjs = os.path.join(mfn, fnjs)
                with open(fnjs, 'r') as fjs:
                    l = fjs.read()
            lines.append(l)
    main_html = ''.join(lines)
    main_html = main_html.replace('__WEBSOCKET__', ws_explicit_route)
    main_html = main_html.replace('__PORT__', str(port)).replace('__HOST__', host)
    if ssl:
        main_html = main_html.replace('ws://', 'wss://')

    # setting-up the webalchemy.tornado server
    application = webalchemy.tornado.web.Application([
        (ws_route, WebSocketHandler, dict(local_doc_class=app,
                                          shared_wshandlers=shared_wshandlers,
                                          shared_data=shared_data,
                                          session_data_store=session_data_store,
                                          tab_data_store=tab_data_store,
                                          main_explicit_route=main_explicit_route,
                                          main_html=main_html)),
        (main_route, _MainHandler, dict(main_html=main_html)),
    ], static_path=static_path)
    au = _AppUpdater(application, app, shared_wshandlers, hn, dreload_blacklist_starting_with,
                     shared_data, additional_monitored_files=additional_monitored_files)
    webalchemy.tornado.ioloop.PeriodicCallback(au.update_app, 1000).start()
    if not ssl:
        application.listen(port)
    else:
        mdl = sys.modules[app.__module__]
        mdl_fn = mdl.__file__
        lib_dir = os.path.realpath(mdl_fn)
        lib_dir = os.path.dirname(lib_dir)
        application.listen(port, ssl_options={
            'certfile': os.path.join(lib_dir, ssl_cert_file),
            'keyfile': os.path.join(lib_dir, ssl_key_file),
        })

    log.info('starting Tornado event loop')
    webalchemy.tornado.ioloop.IOLoop.instance().start()


def generate_static(App, writefile, main_html_file_path=None):
    # prepare main_html ...
    mfn = os.path.realpath(__file__)
    mfn = os.path.dirname(mfn)
    if not main_html_file_path:
        ffn = os.path.join(mfn, 'main.html')
    else:
        ffn = main_html_file_path
    lines = []
    with open(ffn, 'r') as f:
        for l in f:
            if l.strip() == '<body onload="init_communication()">':
                l = '<body>'
            if l.lstrip().startswith('-->'):
                fnjs = l.split()[1].strip()
                if fnjs in ['js/classy.js', 'js/weba.js']:
                    mfn = os.path.realpath(__file__)
                    mfn = os.path.dirname(mfn)
                    fnjs = os.path.join(mfn, fnjs)
                    with open(fnjs, 'r') as fjs:
                        l = fjs.read()
                    lines.append(l)
                    continue
                if fnjs == 'include':
                    if hasattr(App, 'include'):
                        for i in App.include:
                            lines.append('<script src="'+i+'"></script>\n')
                    continue
                if fnjs == 'meta':
                    if hasattr(App, 'meta'):
                        for m in App.meta:
                            js = '<meta '
                            for a, v in m.items():
                                js += a+'="'+v+'" '
                            js += '>\n'
                            lines.append(js)
                    continue
                if fnjs != 'websocket':
                    continue
            lines.append(l)
    main_html = ''.join(lines)

    static_html = []
    for l in lines:
        if l.lstrip().startswith('-->'):
            rdoc = RemoteDocument()
            app = App()
            app.initialize(remote_document=rdoc, main_html=main_html)
            l = rdoc.pop_all_code()
        static_html.append(l)
    static_html = ''.join(static_html)

    with open(writefile, 'w') as f:
        f.write(static_html)



