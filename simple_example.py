#
# a simple example. Currently used for feature testing
#
from webalchemy import server
import logging

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)
server.log.setLevel(logging.INFO)

from tornado import gen
class my_app:    
    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler
        # setup a nice paragraph, with events
        self.p= self.rdoc.element('p',text='This is an empty document')
        self.p.events.add(mouseout = lambda: self.p.style(color='blue'))
        self.p.events.add(mousemove= lambda: self.p.style(color='red'))
        self.rdoc.body.append(self.p)

        # communication with other sessions (see below for more)
        total_clients= str(len(wshandler.sharedhandlers))
        self.p_doc= self.rdoc.element('p',text='total documents open: '+total_clients)
        self.rdoc.body.append(self.p_doc)

        self.wsh.msg_to_sessions(total_clients)

        # intervals, instantiated in two ways
        self.i= self.rdoc.startinterval(1000, lambda: self.rdoc.msg('msg: interval!'))
        self.i.count= 0
        self.rdoc.begin_block() #
        e= self.rdoc.element('p',text=':)')
        e.att.color='green'
        self.rdoc.body.append(e)
        self.i2= self.rdoc.startinterval(2500) # consume previous code block

        # some styling...
        ss= self.rdoc.stylesheet()
        ss.rule('p','font-size:2em;text-transform:uppercase;font-family:Arial, Verdana, Sans-serif;')
        # (can also use r=ss.rule(...) and then r.att.style.color='green' etc.)

    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, txt):
        if txt!='msg: interval!':
            return
        if self.i.count>5:
            self.i.stop()
            self.i2.stop()
        self.i.count+=1
        try:
            self.tp.remove()
        except Exception as e:
            pass
        self.tp= self.rdoc.element('p',text='New paragraph #'+str(self.i.count))
        self.tp.style(
            position='absolute',
            left=str(50*self.i.count)+'px',
            top=str(50*self.i.count)+'px')
        self.rdoc.body.append(self.tp)
        self.p.text= 'there are now '+str(self.i.count+1)+' paragraphs'

    # this method is called on incomming messages from other sessions
    @gen.coroutine
    def outmessage(self, sender_id, txt):
        self.p_doc.text= 'total documents open: '+txt

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        total_clients= str(len(self.wsh.sharedhandlers))
        self.wsh.msg_to_sessions(total_clients)

if __name__=='__main__':
    server.run('localhost',8083,my_app) # the first parameter is the port...
