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

        self.increase_count= self.rdoc.jsfunction('''
            element.app.clickedcount++;
            element.textContent= '('+element.app.clickedcount+') '+element.app.text;
        ''','element')
        self.onclick= self.rdoc.jsfunction('''
            element= event.target;
            message('evt: '+element.app.text);\n'''+
            self.increase_count.varname+'(element);','event')
        def on_add(element,text):
            nonlocal self
            element.att.app.text= text
            element.att.app.clickedcount= 0
            element.att.onclick= self.onclick
        self.menu= menu(self.rdoc, on_add)
        # style the menu!
        self.menu.rule_nav.att.style(display='table',margin='10px')
        self.menu.rule_navli.att.style(
            color='#000000',
            fontSize='2em',
            textTransform='uppercase',
            fontFamily='Arial, Verdana, Sans-serif',
            float='bottom',
            padding='10px',
            listStyle='none',
            cursor='pointer',
            webkitTransition='all 0.3s linear',
            webkitUserSelect='none'
        )
        self.menu.rule_navlihover.att.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
            webkitTransform='rotate(5deg)'
        )
        self.rdoc.body.append(self.menu.element)
        self.menu.add_item(
            'foo',
            'bar',
            'wowowowowo!!!',
            'this is cool',
            'WEBALCHEMY ROCKS'
        )

    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, text):
        if text.startswith('evt: '):
            clicked_text= text[5:]
            self.wsh.msg_in_proc(clicked_text)

    # this method is called on incomming messages from other sessions
    @gen.coroutine
    def outmessage(self, text, sender):
        for e in self.menu.element.childs:
            if e.text==text:
                self.rdoc.inline(self.increase_count.varname+'('+e.varname+');\n')

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        pass

if __name__=='__main__':
    import webalchemy.server
    server.run(8083,colors_app) # the first parameter is the port...
