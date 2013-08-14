import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
from webalchemy.remotedocument import remotedocument
import sys
import time
import traceback

main_html='''
<!DOCTYPE html>
<html>
<body id="body">
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

def log(msg):
    print(msg)
    sys.stdout.flush()
    
class MainHandler(tornado.web.RequestHandler):
    def initialize(self, port):
        log('Initiallizing new app!')
        self.main_html= main_html.replace('PORT',str(port))
        
    @gen.coroutine
    def get(self):
        self.write(self.main_html)

        
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    @gen.coroutine
    def initialize(self, local_doc):
        log('Initiallizing new documet!')
        self.rdoc= remotedocument()        
        try:
            self.local_doc = local_doc(self.rdoc)
        except:
            log('Failed initializing. Exception:')
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
        
    @gen.coroutine
    def open(self):
        log('WebSocket opened')
        yield self.flush_dom()

    @gen.coroutine
    def on_message(self, message):
        log('message received:\n'+message)
        log('passing message to document...')
        try:
            yield self.local_doc.message(self.rdoc,message)
            yield self.flush_dom()
        except:
            log('Failed handling message. Exception:')
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
      
    @gen.coroutine
    def flush_dom(self):
        if self.rdoc.get_buff()!='':
            log('sending message:\n'+self.rdoc.get_buff())
            self.write_message(self.rdoc.get_buff())
            self.rdoc.clear_buff()
        
    def on_close(self):
        log('WebSocket closed')

@gen.coroutine
def async_delay(secs):
    yield gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + secs)

def run(port,local_doc):
    application = tornado.web.Application([
        (r'/', MainHandler, dict(port=port)),
        (r'/websocket', WebSocketHandler, dict(local_doc=local_doc)),
    ])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
 