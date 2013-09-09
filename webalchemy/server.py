import imp
import sys
import time
import logging

import os
import os.path

import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket

from tornado import gen

from webalchemy.remotedocument import remotedocument



# logger for internal purposes
log= logging.getLogger(__name__)



curr_session_counter=0
def generate_session_id():
    global curr_session_counter
    curr_session_counter+=1
    return 's'+str(curr_session_counter)+'p'+str(os.getpid())




class MainHandler(tornado.web.RequestHandler):
    def initialize(self, port, host):
        log.info('Initiallizing new app!')
        ffn=os.path.realpath(__file__)
        ffn=os.path.dirname(ffn)
        ffn=os.path.join(ffn,'main.html') 
        with open(ffn,'r') as f:
            self.main_html= f.read().replace('PORT',str(port)).replace('HOST',host)
    @gen.coroutine
    def get(self):
        self.write(self.main_html)
  



class WebSocketHandler(tornado.websocket.WebSocketHandler):

    @gen.coroutine
    def initialize(self, local_doc_class, shared_wshandlers):
        log.info('Initiallizing new documet!')
        log.info('Reloading code if necessary...')
        self.remotedocument= remotedocument()
        self.sharedhandlers= shared_wshandlers
        self.local_doc= local_doc_class()
        self.local_doc_initialized= False
        self.id= generate_session_id()
        self.sharedhandlers[self.id]= self


    @gen.coroutine
    def open(self):
        self.closed=False
        log.info('WebSocket opened')

    @gen.coroutine
    def on_message(self, message):
        log.info('Message received:\n'+message)
        try:
            if not self.local_doc_initialized:
                log.info('Initializing local document...')
                self.sessionid= message.split(':')[1]
                if self.sessionid=='null':
                    log.info('initializing new session...')
                    self.sessionid= self.id
                    self.remotedocument.inline('set_cookie("webalchemy","'+self.sessionid+'",3);\n')
                self.tabid= message.split(':')[3]
                if self.tabid=='':
                    log.info('initializing new tab...')
                    self.tabid= self.id
                    self.remotedocument.inline('window.name="'+self.tabid+'";\n')
                yield self.local_doc.initialize(self.remotedocument,self,self.sessionid,self.tabid)
                self.local_doc_initialized= True
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
        code= self.remotedocument.pop_all_code()
        if code!='':
            log.info('FLUSHING DOM WITH FOLLOWING MESSAGE:\n'+code)
            # this is good to simulate latency
            #yield async_delay(2)
            self.write_message(code)
        else:
            log.info('FLUSHING DOM: **NOTHING TO FLUSH**')

    @gen.coroutine
    def please_reload(self):
        self.write_message('location.reload();\n')

    @gen.coroutine
    def msg_to_sessions(self,msg,send_to_self=False,to_session_ids=None):
        log.info('Sending message to sessions '+str(len(self.sharedhandlers))+' documents in process:')
        log.info('Message: '+msg)
        if not to_session_ids:
            lst= self.sharedhandlers.keys()
        else:
            lst= to_session_ids
        for k in lst:
            h= self.sharedhandlers[k]
            if h is not self or send_to_self:
                try:
                    yield h.local_doc.outmessage(self.id,msg)
                    yield h.flush_dom()
                except:
                    log.exception('Failed handling outmessage. Exception:')
    @gen.coroutine
    def on_close(self):
        self.closed=True
        log.info('WebSocket closed')
        log.info('Removing shared doc')
        del self.sharedhandlers[self.id]
        if hasattr(self.local_doc,'onclose'):
            log.info('Calling local document onclose:')
            try:
                yield self.local_doc.onclose()
                yield sys.stdout.flush()
            except:
                log.exception('Failed handling local document onclose. Exception:')

    @gen.coroutine
    def prepare_session_for_general_reload(self):
        if hasattr(self.local_doc,'prepare_session_for_general_reload'):
            log.info('preparing session for reload...')
            yield self.local_doc.prepare_session_for_general_reload()

    @gen.coroutine
    def handle_js_to_py_rpc_message(self,msg):
        log.info('Handling message as js->py RPC call')
        pnum, *etc= msg[5:].split(',')
        pnum= int(pnum)
        args_len= etc[:pnum]
        args_txt= ''.join(etc[pnum:])
        args=[]
        curr_pos=0
        for ln in args_len:
            ln= int(ln)
            args.append(args_txt[curr_pos:curr_pos+ln])
            curr_pos+= ln
        fname, *args= args
        if fname not in js_to_py_rpcdict:
            raise Exception('Function not found in js->py RPC table: '+fname)
        log.info('Calling local function: '+fname)
        log.info('With args: '+str(args))
        try:
            yield js_to_py_rpcdict[fname](self.local_doc,self.id,*args)
        except:
            log.exception('JS RPC call failed')

    @gen.coroutine
    def rpc(self,f,*varargs,send_to_self=False,to_session_ids=None,**kwargs):
        log.info('Sending py->py rpc: '+f.__name__)
        log.info('PARAMS: varargs: '+str(varargs)+' kwargs: '+str(kwargs))
        if not to_session_ids:
            lst= self.sharedhandlers.keys()
        else:
            lst= to_session_ids
        log.info('lst='+str(lst))
        log.info('self.id='+self.id)
        for k in lst:
            h= self.sharedhandlers[k]
            if h is not self or send_to_self:
                try:
                    yield js_to_py_rpcdict[f.__name__](h.local_doc,self.id,*varargs,**kwargs)
                    yield h.flush_dom()
                except:
                    log.exception('PY RPC call failed for target session: '+k)





# decorator to register functions for js->py rpc
js_to_py_rpcdict={}
def jsrpc(f):
    log.info('registering function to js->py rpc: '+f.__name__)
    try:
        if f.__name__ in js_to_py_rpcdict:
            raise Exception('cannot decorate with js->py rpc since name already exists: '+f.__name__)
        js_to_py_rpcdict[f.__name__]=f
        return f
    except:
        log.exception('Failed registering js->py RPC function')

# decorator to register functions for py->py rpc
py_to_py_rpcdict={}
def pyrpc(f):
    log.info('registering function to py->py rpc: '+f.__name__)
    try:
        if f.__name__ in py_to_py_rpcdict:
            raise Exception('cannot decorate with py->py rpc since name already exists: '+f.__name__)
        py_to_py_rpcdict[f.__name__]=f
        return f
    except:
        log.exception('Failed registering py->py RPC function')



def clean_rpc():
    global js_to_py_rpcdict
    global py_to_py_rpcdict
    js_to_py_rpcdict={}
    py_to_py_rpcdict={}




@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)





def update_class(app,cls,shared_wshandlers):
    mdl= sys.modules[cls.__module__]
    mdl_fn= mdl.__file__
    last_time_modified= os.stat(mdl_fn).st_mtime
    def func():
        nonlocal app
        nonlocal mdl
        nonlocal mdl_fn
        nonlocal shared_wshandlers
        nonlocal last_time_modified
        current_time_modified= os.stat(mdl_fn).st_mtime
        if current_time_modified == last_time_modified:
            return
        log.info('Reloading document!')
        last_time_modified= current_time_modified
        clean_rpc()
        if hasattr(cls,'prepare_app_for_general_reload'):
            has_data= True
            data= cls.prepare_app_for_general_reload()
        else:
            has_data= False
        mdl= imp.reload(mdl)
        tmp_cls= getattr(mdl, cls.__name__)
        if hasattr(tmp_cls,'recover_app_from_general_reload') and has_data:
            tmp_cls.recover_app_from_general_reload(data)
        app.handlers[0][1][1].kwargs['local_doc_class']= tmp_cls
        log.info('wsh='+str(shared_wshandlers))
        for wsh in shared_wshandlers.values():
            wsh.prepare_session_for_general_reload()
            wsh.please_reload()
    return func




def run(host,port,local_doc_class):
    shared_wshandlers= {}
    application = tornado.web.Application([
        (r'/', MainHandler, dict(host=host, port=port)),
        (r'/websocket/*', WebSocketHandler, dict(local_doc_class=local_doc_class, shared_wshandlers=shared_wshandlers)),
    ])
    application.listen(port)
    tornado.ioloop.PeriodicCallback(update_class(application, local_doc_class, shared_wshandlers), 1500).start()
    log.info('starting Tornado event loop')
    tornado.ioloop.IOLoop.instance().start()
 