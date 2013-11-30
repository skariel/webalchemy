import os
import imp
import sys
import time
import logging
import os.path

from types import ModuleType

import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket

from tornado import gen

from webalchemy.remotedocument import RemoteDocument


# logger for internal purposes
log = logging.getLogger(__name__)

curr_session_counter = 0


def generate_session_id():
    global curr_session_counter
    curr_session_counter += 1
    return 's' + str(curr_session_counter) + 'p' + str(os.getpid())


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        log.info('Initiallizing new app!')
        ffn = os.path.realpath(__file__)
        ffn = os.path.dirname(ffn)
        ffn = os.path.join(ffn, 'main.html')
        with open(ffn, 'r') as f:
            self.main_html = f.read()
        self.main_html = self.main_html.replace('PORT', str(kwargs['port'])).replace('HOST', kwargs['host'])

    @gen.coroutine
    def get(self):
        self.add_header('X-UA-Compatible', 'IE=edge')
        self.write(self.main_html)


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    @gen.coroutine
    def initialize(self, **kwargs):
        log.info('Initiallizing new websocket handler!')
        self.id = generate_session_id()
        self.remotedocument = RemoteDocument()
        self.closed = True
        self.sessionid = None
        self.tabid = None
        self.vendor_type = None
        self.local_doc = kwargs['local_doc_class']()
        self.local_doc_initialized = False
        self.sharedhandlers = kwargs['shared_wshandlers']
        self.sharedhandlers[self.id] = self

    @gen.coroutine
    def open(self):
        self.closed = False
        log.info('WebSocket opened')

    @gen.coroutine
    def on_message(self, message):
        log.info('Message received:\n' + message)
        try:
            if not self.local_doc_initialized:
                log.info('Initializing local document...')
                self.sessionid = message.split(':')[1]
                if self.sessionid == 'null':
                    log.info('initializing new session...')
                    self.sessionid = self.id
                    self.remotedocument.inline('set_cookie("webalchemy","' + self.sessionid + '",3);\n')
                self.tabid = message.split(':')[3]
                if self.tabid == '':
                    log.info('initializing new tab...')
                    self.tabid = self.id
                    self.remotedocument.inline('window.name="' + self.tabid + '";\n')
                self.vendor_type = message.split(':')[-1]
                self.remotedocument.set_vendor_prefix(self.vendor_type)
                yield self.local_doc.initialize(self.remotedocument, self, self.sessionid, self.tabid)
                self.local_doc_initialized = True
            else:
                if message.startswith('rpc: '):
                    yield self.handle_js_to_py_rpc_message(message)
                elif message.startswith('msg: '):
                    log.info('Passing message to document inmessage...')
                    yield self.local_doc.inmessage(message)
                else:
                    log.info('Discarding message...')
            yield self.flush_dom()
        except:
            log.exception('Failed handling message:')

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
                    yield h.local_doc.outmessage(self.id, msg)
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
                yield self.local_doc.onclose()
                yield sys.stdout.flush()
            except:
                log.exception('Failed handling local document onclose. Exception:')

    @gen.coroutine
    def prepare_session_for_general_reload(self):
        if hasattr(self.local_doc, 'prepare_session_for_general_reload'):
            log.info('preparing session for reload...')
            yield self.local_doc.prepare_session_for_general_reload()

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
        fname, *args = args
        if fname not in js_to_py_rpcdict:
            raise Exception('Function not found in js->py RPC table: ' + fname)
        log.info('Calling local function: ' + fname)
        log.info('With args: ' + str(args))
        try:
            yield js_to_py_rpcdict[fname](self.local_doc, self.id, *args)
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
                    yield py_to_py_rpcdict[f.__name__](h.local_doc, self.id, *varargs, **kwargs)
                    yield h.flush_dom()
                except:
                    log.exception('PY RPC call failed for target session: ' + k)

# decorator to register functions for js->py rpc
js_to_py_rpcdict = {}


def jsrpc(f):
    log.info('registering function to js->py rpc: ' + f.__name__)
    try:
        if f.__name__ in js_to_py_rpcdict:
            raise Exception('cannot decorate with js->py rpc since name already exists: ' + f.__name__)
        js_to_py_rpcdict[f.__name__] = f
        return f
    except:
        log.exception('Failed registering js->py RPC function')

# decorator to register functions for py->py rpc
py_to_py_rpcdict = {}


def pyrpc(f):
    log.info('registering function to py->py rpc: ' + f.__name__)
    try:
        if f.__name__ in py_to_py_rpcdict:
            raise Exception('cannot decorate with py->py rpc since name already exists: ' + f.__name__)
        py_to_py_rpcdict[f.__name__] = f
        return f
    except:
        log.exception('Failed registering py->py RPC function')


def clean_rpc():
    global js_to_py_rpcdict
    global py_to_py_rpcdict
    js_to_py_rpcdict = {}
    py_to_py_rpcdict = {}


@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)


def dreload(module, dreload_blacklist_starting_with, just_visit=False):
    _s = {module.__name__}
    _base_file = os.path.realpath(module.__file__)
    _base_path = os.path.dirname(_base_file)
    _reloaded_files = []

    def _dreload(mdl):
        """Recursively reload modules."""
        nonlocal _s
        nonlocal _base_path
        nonlocal _reloaded_files

        for name in dir(mdl):
            mm = getattr(mdl, name)
            if type(mm) is not ModuleType:
                if hasattr(mm, '__module__') and \
                        mm.__module__ is not None:
                    mm = sys.modules[mm.__module__]

            if not hasattr(mm, '__file__') or \
                    not os.path.realpath(mm.__file__).startswith(_base_path) or \
                    mm.__name__[0] == '_' or \
                    '._' in mm.__name__ or \
                    mm.__name__ in _s or \
                    any(mm.__name__.startswith(bln) for bln in dreload_blacklist_starting_with):
                continue

            _s.add(mm.__name__)
            _dreload(mm)
        _reloaded_files.append(os.path.realpath(mdl.__file__))
        if not just_visit:
            log.info('reloading: ' + str(mdl.__name__))
            imp.reload(mdl)
        else:
            log.info('visiting: ' + str(mdl.__name__))

    _dreload(module)
    return _reloaded_files


class AppUpdater:
    def __init__(self, app, cls, shared_wshandlers, hn, dreload_blacklist_starting_with):
        self.app = app
        self.cls = cls
        self.shared_wshandlers = shared_wshandlers
        self.hn = hn
        self.dreload_blacklist_starting_with = dreload_blacklist_starting_with
        self.mdl = sys.modules[self.cls.__module__]
        self.mdl_fn = self.mdl.__file__
        self.monitored_files = dreload(self.mdl, self.dreload_blacklist_starting_with, just_visit=True)
        log.info('monitored files: ' + str(self.monitored_files))
        self.last_time_modified = {
            fn: os.stat(fn).st_mtime for fn in self.monitored_files
        }

    def update_app(self):
        if not any([os.stat(fn).st_mtime != self.last_time_modified[fn] for fn in self.monitored_files]):
            return
        log.info('Reloading document!')
        self.last_time_modified = {
            fn: os.stat(fn).st_mtime for fn in self.monitored_files
        }
        clean_rpc()
        has_data = False
        data = None
        if hasattr(self.cls, 'prepare_app_for_general_reload'):
            has_data = True
            data = self.cls.prepare_app_for_general_reload()
        dreload(self.mdl, self.dreload_blacklist_starting_with)
        tmp_cls = getattr(self.mdl, self.cls.__name__)
        if hasattr(tmp_cls, 'recover_app_from_general_reload') and has_data:
            tmp_cls.recover_app_from_general_reload(data)
        self.app.handlers[0][1][self.hn].kwargs['local_doc_class'] = tmp_cls
        log.info('wsh=' + str(self.shared_wshandlers))
        for wsh in self.shared_wshandlers.values():
            wsh.prepare_session_for_general_reload()
            wsh.please_reload()


def run(host, port, local_doc_class, static_path_from_local_doc_base='static',
        dreload_blacklist_starting_with=('webalchemy',)):
    static_path = None
    hn = 1
    if static_path_from_local_doc_base:
        mdl = sys.modules[local_doc_class.__module__]
        mdl_fn = mdl.__file__
        static_path = os.path.realpath(mdl_fn)
        static_path = os.path.dirname(static_path)
        static_path = os.path.join(static_path, static_path_from_local_doc_base)
        log.info('static_path: ' + static_path)
        hn = 4

    shared_wshandlers = {}
    application = tornado.web.Application([
        (r'/', MainHandler, dict(host=host, port=port)),
        (r'/websocket/*', WebSocketHandler, dict(local_doc_class=local_doc_class,
                                                 shared_wshandlers=shared_wshandlers)),
    ], static_path=static_path)
    au = AppUpdater(application, local_doc_class, shared_wshandlers, hn, dreload_blacklist_starting_with)
    tornado.ioloop.PeriodicCallback(au.update_app, 1000).start()
    application.listen(port)
    log.info('starting Tornado event loop')
    tornado.ioloop.IOLoop.instance().start()
