##webalchemy: realtime, Pythonic web framework
webalchemy is a fast, simple and lightweight realtime micro web-framework for Python, inspired by [SqlAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). With webalchemy you develop webapps like you would develop a desktop (or mobile) app

####Example
a simple application demostrating dynamically creation of paragraphs, inline styles, stylesheets, intervals, etc., and message exchanging between frontend and server, messaging between parallel sessions, and events. Note how everything fits in a single file and class:
```python
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

        # communication with other sessions (see below for more)
        total_clients= str(len(wshandler.sharedhandlers))
        self.p_doc= self.rdoc.element('p',text='total documents open: '+total_clients)
        self.rdoc.body.append(self.p_doc)
        self.wsh.msg_in_proc(total_clients)

        # intervals, instantiated in two ways
        self.i= self.rdoc.startinterval(1000, lambda: self.rdoc.msg('interval!'))
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

    # this method is called on incomming messages from other sessions
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
    server.run(8083,my_app) # the first parameter is the port...

```
##Philosophy and Roadmap
Run relatively simple code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

##Requirements
Python >= 3.3

Tornado >= 3.1

In addition, webalchemy webapps require a modern webbrowser supporting websockets

##License
The MIT License (MIT)

Copyright (c) 2013 Ariel Keselman

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

