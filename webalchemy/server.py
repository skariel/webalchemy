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
        self.remotedocument= remotedocument()
        self.sharedhandlers= shared_wshandlers
        self.local_doc= local_doc_class()
        self.local_doc_initialized= False
        self.sharedhandlers.append(self)


    @gen.coroutine
    def open(self):
        log.info('WebSocket opened')

    @gen.coroutine
    def on_message(self, message):
        log.info('Message received:\n'+message)
        try:
            if not self.local_doc_initialized:
                log.info('Initializing local document with message...')
                yield self.local_doc.initialize(self.remotedocument,self, generate_session_id(), message)
                self.local_doc_initialized= True
            else:
                if message.startswith('rpc: '):
                    yield self.handle_js_to_py_rpc_message(message)
                elif message.startswith('srpc: '):
                    for h in self.sharedhandlers:
                        yield h.handle_js_to_py_rpc_message(message,srpc=True,sender_doc=self.local_doc)
                        if h is not self:
                            yield h.flush_dom()
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
    def msg_in_proc(self,msg,send_to_self=False):
        log.info('sending message to all '+str(len(self.sharedhandlers))+' documents in process:')
        log.info(msg)
        for h in self.sharedhandlers:
            if h is not self or send_to_self:
                try:
                    yield h.local_doc.outmessage(msg,self.local_doc)
                    yield h.flush_dom()
                except:
                    log.exception('Failed handling outmessage. Exception:')
    @gen.coroutine
    def on_close(self):
        log.info('WebSocket closed')
        log.info('Removing shared doc')
        self.sharedhandlers.remove(self)
        if hasattr(self.local_doc,'onclose'):
            log.info('Calling local document onclose:')
            try:
                yield self.local_doc.onclose()
                yield sys.stdout.flush()
            except:
                log.exception('Failed handling local document onclose. Exception:')

    @gen.coroutine
    def handle_js_to_py_rpc_message(self,msg,srpc=False,sender_doc=None):
        if not srpc:
            log.info('Handling message as js->py RPC call')
            pnum, *etc= msg[5:].split(',')
        else:
            log.info('Handling message as js->py SRPC call')
            pnum, *etc= msg[6:].split(',')
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
        log.info('with args: '+str(args))
        try:
            if not srpc:
                if js_to_py_rpcdict[fname]['is_method']:
                    yield js_to_py_rpcdict[fname]['f'](self.local_doc,*args)
                else:
                    yield js_to_py_rpcdict[fname]['f'](*args)
            else:
                if js_to_py_rpcdict[fname]['is_method']:
                    yield js_to_py_rpcdict[fname]['f'](self.local_doc,sender_doc,*args)
                else:
                    yield js_to_py_rpcdict[fname]['f'](sender_doc,*args)
        except:
            log.exception('RPF call failed:')



# this is the rpc decorator to register functions
js_to_py_rpcdict={}
def rpc_gen(is_method):
    def dec(f):
        if is_method:
            log.info('registering method to js->py rpc: '+str(f))
        else:
            log.info('registering non-method to js->py rpc: '+str(f))
        try:
            if f.__name__ in js_to_py_rpcdict:
                raise Exception('cannot decorate with rpc since name already exists: '+f.__name__)        
            js_to_py_rpcdict[f.__name__]={}
            js_to_py_rpcdict[f.__name__]['is_method']=is_method
            js_to_py_rpcdict[f.__name__]['f']=f
            return f
        except:
            log.exception('Failed registering RPC function')
    return dec

def rpc(*varargs,**kwargs):
    if len(varargs)==1 and len(kwargs)==0:
        return rpc_gen(True)(varargs[0])
    else:
        return rpc_gen(kwargs['is_method'])




@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)




def run(host,port,local_doc_class):
    shared_wshandlers= []
    application = tornado.web.Application([
        (r'/', MainHandler, dict(host=host, port=port)),
        (r'/websocket', WebSocketHandler, dict(local_doc_class=local_doc_class, shared_wshandlers=shared_wshandlers)),
    ])
    application.listen(port)
    log.info('in run!')
    tornado.ioloop.IOLoop.instance().start()
 