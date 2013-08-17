##webalchemy: realtime, Pythonic web framework
webalchemy is a fast, simple and lightweight realtime micro web-framework for Python, inspired by [SqlAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). With webalchemy you develop webapps like you would develop a desktop (or mobile) app. See example below to understand what I mean

####Example
Below is a simple realtime application demostrating dynamically creation of paragraphs, styles, intervals, etc., message exchanging between frontend and server, messaging between parallel sessions, and events. Note how everything fits in a single file and class:
```python
from tornado import gen
class my_app:    
    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        self.rdoc= remotedocument # remember these for later use
        self.wsh= wshandler
        rdoc= self.rdoc # just an alias
        self.p= rdoc.create_element('p',txt='This is an empty document')
        self.p.set_event(onmouseout=self.p.set_style_att(color='blue'),onmousemove=self.p.set_style_att(color='red'))
        rdoc.root_append(self.p)
        total_docs= str(len(wshandler.sharedhandlers))
        self.p_doc= rdoc.create_element('p',txt='total documents open:'+total_docs)
        rdoc.root_append(self.p_doc)
        self.i= rdoc.create_interval(1000,rdoc.msg('interval!'))
        self.i.count=0
        rdoc.begin_block() #
        e=rdoc.create_element('p',txt=':)', )
        e.set_style_att(color='green')
        rdoc.root_append(e)
        self.i2= rdoc.create_interval(2500) # consume previous code block
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
```
##Requirements
Python >= 3.3

Tornado >= 3.1

In addition, webalchemy webapps require a modern webbrowser supporting websockets

##Status
The library is currently in early stages of development, still far from being feature complete

##Philosophy
Lightweight - does one thing and does it well!

Pythonic - Explicit, magicless, easy to understand whats going on

Non oppinionated - plays well with others

High performance - Async, Websockets, CSS3 animations, etc.

##License
Code and documentation (yet to be written...) are available under the MIT license as detailed in the file [LICENSE.txt](LICENSE.txt)

>The MIT License (MIT)
>
>Copyright (c) 2013 Ariel Keselman
>
>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

