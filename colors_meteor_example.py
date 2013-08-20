#
# trying to reconstruct Meteor color application
#
from tornado import gen
from webalchemy.widgets.basic.menu import menu

class colors_app:    
    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler

        # setup a nice paragraph, with events
        self.menu= menu(self.rdoc)
        self.rdoc.body.append(self.menu.element)
        self.menu.add_item('foo','bar','wowowowowo!!!','this is cool','WEBALCHEMY ROCKS')

    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, txt):
        pass

    # this method is called on incomming messages from other sessions
    @gen.coroutine
    def outmessage(self, txt, sender):
        pass

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        pass

if __name__=='__main__':
    import webalchemy.server
    server.run(8083,colors_app) # the first parameter is the port...
