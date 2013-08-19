#
# a simple example. Currently used for feature testing
#
from tornado import gen
class my_app:    

    def create_item(self, name, likes):
        p= self.rdoc.create_element('p',txt=str(likes)+' '+name)
        p.set_style_att(width='100px')
        p.set_event(onmouseout = p.set_style_att('background-color','white'),
                    onmousemove= p.set_style_att('background-color','orange'))
        self.rdoc.root_append(p)

    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        self.rdoc= remotedocument # remember these for later use
        self.wsh= wshandler
        rdoc= self.rdoc # just an alias

        self.items= [('red',0),('green',1),('blue',2)]

        for item in self.items:
            self.create_item(*item)

    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, txt):
        pass

    # this method is called when a session messages everybody other session
    @gen.coroutine
    def outmessage(self, txt, sender):
        pass

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        pass


if __name__=='__main__':
    import webalchemy.server
    server.run(8083,my_app)
