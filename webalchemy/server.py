import sys
import time
import os.path
import traceback

import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import gen

from webalchemy.utils import log
from webalchemy.remotedocument import remotedocument




class MainHandler(tornado.web.RequestHandler):
    def initialize(self, port, host):
        log('Initiallizing new app!')
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
    def initialize(self, local_doc, shared_wshandlers):
        log('Initiallizing new documet!')
        self.remotedocument= remotedocument()
        self.sharedhandlers= shared_wshandlers
        self.local_doc= local_doc()
        self.local_doc_initialized= False
        self.sharedhandlers.append(self)

    @gen.coroutine
    def open(self):
        log('WebSocket opened')

    @gen.coroutine
    def on_message(self, message):
        log('message received:\n'+message)
        try:
            if not self.local_doc_initialized:
                log('Initializing local document with message...')
                yield self.local_doc.initialize(self.remotedocument,self, message)
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
                    log('passing message to document...')
                    yield self.local_doc.inmessage(message)
                else:
                    log('doing nothing with this message...')
            yield self.flush_dom()
        except:
            log('Failed handling message. Exception:')
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()      
    @gen.coroutine
    def flush_dom(self):
        code= self.remotedocument.pop_all_code()
        if code!='':
            log('FLUSHING DOM WITH FOLLOWING MESSAGE:\n'+code)
            # this is good to simulate latency
            #yield async_delay(2)
            self.write_message(code)
        else:
            log('FLUSHING DOM: **NOTHING TO FLUSH**')
    @gen.coroutine
    def msg_in_proc(self,msg,send_to_self=False):
        log('sending message to all '+str(len(self.sharedhandlers))+' documents in process:')
        log(msg)
        for h in self.sharedhandlers:
            if h is not self or send_to_self:
                try:
                    yield h.local_doc.outmessage(msg,self.local_doc)
                    yield h.flush_dom()
                except:
                    log('Failed handling outmessage. Exception:')
                    traceback.print_exc(file=sys.stdout)
                    sys.stdout.flush()
    @gen.coroutine
    def on_close(self):
        log('WebSocket closed')
        log('Removing shared doc')
        self.sharedhandlers.remove(self)
        if hasattr(self.local_doc,'on_close'):
            log('Calling local document on_close:')
            try:
                yield self.local_doc.onclose()
            except:
                log('Failed handling local document onclose. Exception:')
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()

    @gen.coroutine
    def handle_js_to_py_rpc_message(self,msg,srpc=False,sender_doc=None):
        if not srpc:
            log('handling message as js->py RPC call')
            pnum, *etc= msg[5:].split(',')
        else:
            log('handling message as js->py SRPC call')
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
            raise Exception('function not found in js->py RPC table: '+fname)
        log('function: '+fname)
        log('args: '+str(args))
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



# this is the rpc decorator to register functions
js_to_py_rpcdict={}
def rpc_gen(is_method):
    def dec(f):
        if is_method:
            log('registering method to js->py rpc: '+str(f))
        else:
            log('registering non-method to js->py rpc: '+str(f))
        try:
            if f.__name__ in js_to_py_rpcdict:
                raise Exception('cannot decorate with rpc since name already exists: '+f.__name__)        
            js_to_py_rpcdict[f.__name__]={}
            js_to_py_rpcdict[f.__name__]['is_method']=is_method
            js_to_py_rpcdict[f.__name__]['f']=f
            return f
        except:
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
    return dec

def rpc(*varargs,**kwargs):
    if len(varargs)==1 and len(kwargs)==0:
        return rpc_gen(True)(varargs[0])
    else:
        return rpc_gen(kwargs['is_method'])




@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)




def run(host,port,local_doc):
    shared_wshandlers= []
    application = tornado.web.Application([
        (r'/', MainHandler, dict(host=host, port=port)),
        (r'/websocket', WebSocketHandler, dict(local_doc=local_doc, shared_wshandlers=shared_wshandlers)),
    ])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
 