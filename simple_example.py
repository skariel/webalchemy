#
# a simple example. Currently used for feature testing
#
from tornado import gen
class my_app:    
    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler):
        self.rdoc= remotedocument # remember these for later use
        self.wsh= wshandler
        rdoc= self.rdoc # just an alias
        self.p= rdoc.create_element('p',txt='This is an empty document')
        rdoc.root_append(self.p)
        total_docs= str(len(wshandler.sharedhandlers))
        self.p_doc= rdoc.create_element('p',txt='total documents open:'+total_docs)
        rdoc.root_append(self.p_doc)
        self.i= rdoc.create_interval(1000,rdoc.msg('interval!'))
        self.i.count=0
        rdoc.begin()
        e=rdoc.create_element('p',txt=':)', )
        rdoc.root_append(e)
        rdoc.end()
        self.i2= rdoc.create_interval(2500)
        wshandler.msg_in_proc(total_docs)

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
        except:
            pass
        self.tp= self.rdoc.create_element('p',txt='New paragraph #'+str(self.i.count))
        self.tp.set_style_att(position='absolute', left=str(50*self.i.count)+'px', top=str(50*self.i.count)+'px')
        self.rdoc.root_append(self.tp)
        self.p.set_text('there are now '+str(self.i.count+1)+' paragraphs')

    # this method is called when a session messages everybody other session
    @gen.coroutine
    def outmessage(self, txt, sender):
        self.p_doc.set_text('total documents open:'+txt)

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        total_docs= str(len(self.wsh.sharedhandlers))
        self.wsh.msg_in_proc(total_docs)


if __name__=='__main__':
    import webalchemy.server
    server.run(8083,my_app)
