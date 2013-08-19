#
# a simple example. Currently used for feature testing
#
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
        self.p.att.onmouseout = lambda: self.p.att.style(color='blue')
        self.p.att.onmousemove= lambda: self.p.att.style(color='red')
        self.rdoc.body.append(self.p)

        total_clients= str(len(wshandler.sharedhandlers))
        self.p_doc= self.rdoc.element('p',text='total documents open: '+total_clients)
        self.rdoc.body.append(self.p_doc)

        self.i= self.rdoc.startinterval(1000, lambda: self.rdoc.msg('interval!'))
        self.i.count= 0
        self.rdoc.begin_block() #
        e= self.rdoc.element('p',text=':)')
        e.att.color='green'
        self.rdoc.body.append(e)
        self.i2= self.rdoc.startinterval(2500) # consume previous code block
        self.wsh.msg_in_proc(total_clients)
    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, txt):
        if txt!='interval!':
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
        self.tp.att.style(
            position='absolute',
            left=str(50*self.i.count)+'px',
            top=str(50*self.i.count)+'px')
        self.rdoc.body.append(self.tp)
        self.p.text= 'there are now '+str(self.i.count+1)+' paragraphs'
    # this method is called when a session messages everybody other session
    @gen.coroutine
    def outmessage(self, txt, sender):
        self.p_doc.text= 'total documents open: '+txt
    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        total_clients= str(len(self.wsh.sharedhandlers))
        self.wsh.msg_in_proc(total_clients)

if __name__=='__main__':
    import webalchemy.server
    server.run(8083,my_app)
