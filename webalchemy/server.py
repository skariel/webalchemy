"""WebAlchemy Server implementation.

When the "run" method is invoked with an application as argument 
the server sets some configurations and executes the Tornado Webserver
with two handlers.

The _MainHandler is responsible for handling the requests to the base 
html file. The base html file, in the client, then connects through a 
websocket to the WebAlchemy server.

The WebSocketHandler is responsible for starting the application and 
handling the client requests through the websocket.

This file includes also resources for monitoring changes in local files.
"""


import os
import imp
import sys
import time
import random
import logging
import os.path
import linecache

from types import ModuleType
from collections import OrderedDict

from uuid import uuid1

import tornado
import tornado.web
import tornado.ioloop

from sockjs.tornado import SockJSRouter, SockJSConnection

from tornado import gen

from .remotedocument import RemoteDocument
from .mainhtml import generate_main_html_for_server, generate_static_main_html
from .config import read_config_from_app

# logger for internal purposes
log = logging.getLogger(__name__)


def _generate_session_id():
    """Generate a session id.
    a Version 1 uuid as specified by RFC4122, see here: http://tools.ietf.org/html/rfc4122.html"""
    return str(uuid1())

@gen.coroutine
def async_delay(secs):
    """Forces an asynchronous delay on the Tornado server loop.
    This allows us to implement our own loops without messing with the main Tornado loop."""
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)

def _dreload(module, dreload_blacklist_starting_with, just_visit=False):
    """Reloads a module.
    This is usually called when a local file is changed."""
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
            linecache.clearcache()
            imp.reload(mdl)
        else:
            log.info('visiting: ' + str(mdl.__name__))

    __dreload(module)
    return _reloaded_files


# ================================ #
#      Tornado server handlers     #
# ================================ #

class _MainHandler(tornado.web.RequestHandler):
    """Handles the initial requests to the main html page."""

    def initialize(self, **kwargs):
        log.info('Initiallizing new app!')
        self.main_html = kwargs['main_html']

    @gen.coroutine
    def get(self, *varargs):
        """ Implement the HTTP GET method. """
        self.add_header('X-UA-Compatible', 'IE=edge')
        if not varargs:
            varargs = ('',)
        self.main_html = self.main_html.replace('__ARGS__', str(varargs[0]))
        self.write(self.main_html)


@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)


class WebSocketHandler(SockJSConnection):
    """Handless the websocket calls from the client."""

    @gen.coroutine
    def on_open(self, info):
        log.info('Initiallizing a websocket handler!')
        try:
            self.id = _generate_session_id()
            self.remotedocument = RemoteDocument()
            self.closed = True
            self.session_id = None
            self.tab_id = None
            self.vendor_type = None
            self.additional_args = self.session.server.settings['handler_args']
            self.shared_data = self.additional_args['shared_data']
            self.session_data_store = self.additional_args['session_data_store']
            self.tab_data_store = self.additional_args['tab_data_store']
            self.session_data = None
            self.tab_data = None
            self.local_doc = self.additional_args['local_doc_class']()
            self.local_doc_initialized = False
            self.sharedhandlers = self.additional_args['shared_wshandlers']
            self.sharedhandlers[self.id] = self
            self.is_new_tab = None
            self.is_new_session = None
            self.main_html = self.additional_args['main_html']
        except:
            log.exception('Initialization of websocket handler failed!')

        self.closed = False
        log.info('WebSocket opened')

    @gen.coroutine
    def handle_binary_message(self, message):
        # TODO: implement this!
        raise NotImplementedError
    
    @gen.coroutine
    def on_close(self):
        """Removes all shared function handlers and prepares
        the application for termination or reloading."""
        self.closed = True
        log.info('WebSocket closed')
        log.info('Removing shared doc')
        del self.sharedhandlers[self.id]
        if hasattr(self.local_doc, 'onclose'):
            log.info('Calling local document onclose:')
            try:
                # Inform application of the termination and yield results
                res = self.local_doc.onclose()
                if (res):
                    yield res
            except:
                log.exception('Failed handling local document onclose. Exception:')

    @gen.coroutine
    def on_message(self, message):
        """Receives a message from the client and handles it according to the content."""
        log.info('Message received:\n' + message)
        try:
            if not isinstance(message, str):
                log.info('binary data')
                yield self.handle_binary_message(message)
            elif message == 'heartbeat':
                # Heartbeat is only to keep connections alive
                pass
            elif not self.local_doc_initialized:
                log.info('Initializing local document...')
                self.init_localdocument(message)
                yield self.send_heartbeat()
            else:
                if message.startswith('rpc: '):
                    yield self.handle_js_to_py_rpc_message(message)
                elif message != 'done':
                    log.info('Passing message to document inmessage...')
                    res = self.local_doc.inmessage(message)
                    if (res):
                        yield res
                elif message != 'done':
                    raise Exception('bad message received: ' + str(message))
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
        """Clears the DOM manipulation content on the remote document."""
        code = self.remotedocument.pop_all_code()
        if code != '':
            log.info('FLUSHING DOM WITH FOLLOWING MESSAGE:\n' + code)
            #yield async_delay(2)  # this is good to simulate latency
            self.send(code)
        else:
            log.info('FLUSHING DOM: **NOTHING TO FLUSH**')

    @gen.coroutine
    def please_reload(self):
        """Sends a reload request through the websocket and closes."""
        self.send('location.reload();\n')
        self.close()

    @gen.coroutine
    def msg_to_sessions(self, msg, send_to_self=False, to_session_ids=None):
        """Broadcasts a message to all sessions in the 'to_session_ids' list.
        If no sessions are mentioned, it broadcasts to all sessions. """
        log.info('Sending message to sessions ' + str(len(self.sharedhandlers)) + ' documents in process:')
        log.info('Message: ' + msg)
        session_ids = to_session_ids if (to_session_ids) else self.sharedhandlers.keys()
        for _id in session_ids:
            handler = self.sharedhandlers[_id]
            if (handler is not self) or send_to_self:
                try:
                    res = handler.local_doc.outmessage(self.id, msg)
                    if (res):
                        yield res
                    yield handler.flush_dom()
                except:
                    log.exception('Failed handling outmessage. Exception:')

    @gen.coroutine
    def prepare_session_for_general_reload(self):
        if hasattr(self.local_doc, 'prepare_session_for_general_reload'):
            log.info('preparing session for reload...')
            res = self.local_doc.prepare_session_for_general_reload()
            if (res):
                yield res
                
    @gen.coroutine
    def handle_binary_message(self, message):
        # TODO: implement this!
        raise NotImplementedError

    @gen.coroutine
    def send_heartbeat(self):
        """Keeps sending a message to keep the client alive."""
        while True:
            if self.closed:
                return
            # we have to send something executable by JS, or else treat it on the other side...
            self.send(';')
            log.info('sending heartbeat...')
            yield async_delay(random.random()*10 + 30)
            
    @gen.coroutine
    def init_localdocument(self, message):
        """ Procedure to initiate the local application. """
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
        
        # Initializes the application and yields any returning results
        res = self.local_doc.initialize(remote_document=self.remotedocument, comm_handler=self,
                                        session_id=self.session_id, tab_id=self.tab_id,
                                        shared_data=self.shared_data, session_data=self.session_data,
                                        tab_data=self.tab_data, is_new_tab=self.is_new_tab,
                                        is_new_session=self.is_new_session,
                                        main_html=self.main_html)
        if (res):
            yield res
        self.local_doc_initialized = True

    @gen.coroutine
    def handle_js_to_py_rpc_message(self, msg):
        """Handles a RPC request initiated on the client."""
        log.info('Handling message as js->py RPC call')
        # Retrieve the arguments from the message
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
        # Get the reference to the local function
        wr = self.remotedocument.jsrpcweakrefs[rep]
        fn = wr()
        if fn is None:
            del self.remotedocument.jsrpcweakrefs[rep]
        log.info('Calling local function: ' + str(fn))
        log.info('With args: ' + str(args))
        try:
            # Execute the function and yield any results
            # TODO: Has the client permission to execute the function?
            res = fn(self.id, *args)
            if (res):
                yield res
        except:
            log.exception('JS RPC call failed')

    @gen.coroutine
    def rpc(self, f, *varargs, send_to_self=False, to_session_ids=None, **kwargs):
        """Executes a local initiated RPC call."""
        log.info('Sending py->py rpc: ' + f.__name__)
        log.info('PARAMS: varargs: ' + str(varargs) + ' kwargs: ' + str(kwargs)) 
        session_ids = to_session_ids if (to_session_ids) else self.sharedhandlers.keys()
        # Get the session handlers and execute the function
        for _id in session_ids:
            handler = self.sharedhandlers[_id]
            if (handler is not self) or send_to_self:
                try:
                    res = getattr(handler.local_doc, f.__name__)(self.id, *varargs, **kwargs)
                    if (res):
                        yield res
                    yield handler.flush_dom()
                except:
                    log.exception('PY RPC call failed for target session: ' + _id)


# ================================ #
#          Reload handler          #
# ================================ #

class _AppUpdater:
    """Tracks changes in local files and triggers reloads."""

    def __init__(self, app, router, cls, shared_wshandlers, dreload_blacklist_starting_with, shared_data,
                 additional_monitored_files):
        self.app = app
        self.router = router
        self.cls = cls
        self.shared_wshandlers = shared_wshandlers
        self.shared_data = shared_data
        self.dreload_blacklist_starting_with = dreload_blacklist_starting_with
        self.mdl = sys.modules[self.cls.__module__]
        self.mdl_fn = self.mdl.__file__
        self.monitored_files = _dreload(self.mdl, self.dreload_blacklist_starting_with, just_visit=True)
        self.set_additional_monitored_files(additional_monitored_files)
        log.info('monitored files: ' + str(self.monitored_files))
        self.last_time_modified = {fn: os.stat(fn).st_mtime for fn in self.monitored_files}

    def set_additional_monitored_files(self, fns):
        if fns:
            self.monitored_files.extend(fns)

    def update_app(self):
        """This method will be looping on the server so it can track changes in local files.
        Every time a change is found, it reloads the application."""
        try:
            # Compare file system modification times with the caches and returns if no modification is found.
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

        self.router.settings['handler_args']['local_doc_class'] = tmp_cls
        for wsh in list(self.shared_wshandlers.values()):
            wsh.prepare_session_for_general_reload()
            wsh.please_reload()


class PrivateDataStore:
    """Implements a simple data storage."""

    def __init__(self):
        self._dict = dict()

    def get_store(self, uid):
        if (uid not in self._dict):
            self._dict[uid] = OrderedDict()
        return self._dict[uid]

    def remove_store(self, uid):
        del self._dict[uid]


# ================================ #
#         Server execution         #
# ================================ #

def run(app=None, **kwargs):
    """WebAlchemy server 'run'.
    
    Receives a WebAlchemy application as argument and other optional arguments.
    
    Loads configuration parameters from the application, sets the URL paths on
    the server, configures the function handlers and sets up the Tornado server.
    
    """
    settings = read_config_from_app(app)
    
    # Application settings
    port = settings['SERVER_PORT']
    static_path_from_local_doc_base = settings['SERVER_STATIC_PATH']
    shared_data_class = kwargs.get('shared_data_class', OrderedDict)
    tab_data_store_class = kwargs.get('private_data_store_class', PrivateDataStore)
    session_data_store_class = kwargs.get('private_data_store_class', PrivateDataStore)
    ssl = not (settings['SERVER_SSL_CERT'] is None)
    ssl_cert_file = settings['SERVER_SSL_CERT']
    ssl_key_file = settings['SERVER_SSL_KEY']
    main_explicit_route = settings['SERVER_MAIN_ROUTE']
    if not main_explicit_route:
        main_route = r'/'
    else:
        main_route = r'/' + main_explicit_route

    # Configure local static path, if given
    if static_path_from_local_doc_base:
        mdl = sys.modules[app.__module__]
        mdl_fn = mdl.__file__
        static_path = os.path.realpath(mdl_fn)
        static_path = os.path.dirname(static_path)
        static_path = os.path.join(static_path, static_path_from_local_doc_base)
        log.info('static_path: ' + static_path)
    else:
        static_path = None

    # Configure shared handlers
    shared_wshandlers = {}
    shared_data = shared_data_class()
    if hasattr(app, 'initialize_shared_data'):
        app.initialize_shared_data(shared_data)
    session_data_store = session_data_store_class()
    tab_data_store = tab_data_store_class()

    # Generate the main html for the client
    main_html = generate_main_html_for_server(app, ssl)

    # setting-up the tornado server
    ws_route = main_route + '/app' if not main_route.endswith('/') else main_route + 'app'
    router = SockJSRouter(WebSocketHandler, ws_route,
                          dict(handler_args=dict(local_doc_class=app,
                                                 shared_wshandlers=shared_wshandlers,
                                                 shared_data=shared_data,
                                                 session_data_store=session_data_store,
                                                 tab_data_store=tab_data_store,
                                                 main_explicit_route=main_explicit_route,
                                                 main_html=main_html)))

    # Set up the tornado wserver
    # We use the _MainHandler to serve the main html file and the
    # WebSocketHandler to handle subsequent websocket requests from the clients
    application = tornado.web.Application(router.urls + [(main_route, _MainHandler, dict(main_html=main_html))],
                                          static_path=static_path)
    dreload_blacklist_starting_with = ('webalchemy', 'tornado')
    additional_monitored_files = settings['SERVER_MONITORED_FILES']
    
    # Set up the service to monitore changes in local files
    au = _AppUpdater(application, router, app, shared_wshandlers, dreload_blacklist_starting_with,
                     shared_data, additional_monitored_files=additional_monitored_files)
    tornado.ioloop.PeriodicCallback(au.update_app, 1000).start()
    
    # Handle certifications
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
    tornado.ioloop.IOLoop.instance().start()


def generate_static(app):
    """Generates an application which can be served in a static folder."""
    settings = read_config_from_app(app)
    writefile = settings['FREEZE_OUTPUT']
    static_html = generate_static_main_html(app)
    with open(writefile, 'w') as f:
        f.write(static_html)

