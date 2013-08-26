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
function message(s) {
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
                log('passing message to document...')
                yield self.local_doc.inmessage(message)
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
        log('Calling local document on_close:')
        try:
            yield self.local_doc.onclose()
        except:
            log('Failed handling local document onclose. Exception:')
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()




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
 