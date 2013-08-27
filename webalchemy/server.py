# TODO: inter session RPC
# TODO: escape the RPC call in JS


import sys
import time
import traceback

import tornado
import tornado.web
import tornado.ioloop
import tornado.websocket
from tornado import gen

from webalchemy.remotedocument import remotedocument
from webalchemy.utils import log




main_html='''
<!DOCTYPE html>
<html>
<body>
<script>
var ws = new WebSocket('ws://localhost:PORT/websocket');
message= function (s) {
    console.log('sending message:')
    console.log(s)
    ws.send(s)
}
ws.onopen = function() {
   message('hi');
};
ws.onmessage = function (evt) {
   console.log('message received:')
   console.log(evt.data)
   eval(evt.data)
   message('done')
};
rpc= function () {
    var s=''
    s+= arguments.length
    for (var i = 0; i < arguments.length; i++) {
        var si= arguments[i].toString()
        s+= ','+si.length
    }
    for (var i = 0; i < arguments.length; i++) {
        var si= arguments[i].toString()
        s+= ','+si
    }
    message('rpc: '+s)
}    
</script>
</body>
</html> 
'''



class MainHandler(tornado.web.RequestHandler):
    def initialize(self, port):
        log('Initiallizing new app!')
        self.main_html= main_html.replace('PORT',str(port))        
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
                    yield self.handle_rpc_message(message)
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
            log('sending message:\n'+code)
            # this is good to simulate latency
            #yield async_delay(2)
            self.write_message(code)
        else:
            log('**NOTHING**')
    @gen.coroutine
    def msg_in_proc(self,msg,send_to_self=False):
        log('sending message to all '+str(len(self.sharedhandlers))+' documents in process:')
        log(msg)
        for h in self.sharedhandlers:
            if h.local_doc is not self.local_doc or send_to_self:
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
    def handle_rpc_message(self,msg):
        log('handling message as RPC call')
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
        if fname not in rpcdict:
            raise Exception('function not found in RPC table: '+fname)
        log('function: '+fname)
        log('args: '+str(args))
        if rpcdict[fname]['is_method']:
            yield rpcdict[fname]['f'](self.local_doc,*args)
        else:
            yield rpcdict[fname]['f'](*args)



# this is the rpc decorator to register functions
rpcdict={}
def rpc_gen(is_method):
    def dec(f):
        if is_method:
            log('registering method to js->py rpc: '+str(f))
        else:
            log('registering non-method to js->py rpc: '+str(f))
        try:
            if f.__name__ in rpcdict:
                raise Exception('cannot decorate with rpc since name already exists: '+f.__name__)        
            rpcdict[f.__name__]={}
            rpcdict[f.__name__]['is_method']=is_method
            rpcdict[f.__name__]['f']=f
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




def run(port,local_doc):
    shared_wshandlers= []
    application = tornado.web.Application([
        (r'/', MainHandler, dict(port=port)),
        (r'/websocket', WebSocketHandler, dict(local_doc=local_doc, shared_wshandlers=shared_wshandlers)),
    ])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
 