##webalchemy: realtime, Pythonic web framework
**webalchemy** takes a fresh approach on realtime web development inspired by [SqlAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). It let's you write server code as if it were running on the client Err.., In fact forget about client and server altogether. Develop like you would for the desktop.

**webalchemy** is MIT licensed, it can be freely used for commercial or open source products. 

##Develop a webapp like you would a desktop app
webapps made with **webalchemy** are highly dynamic: the browser and server frequently exchange messages over websockets, in essense it allows you to automate the frontend using Python. Simple library calls generate the JS required on the frontend, and you program like you would for a desktop app - not caring much about HTML, CSS, or JS (these can still be used on demand, and nothing prevents usage of a templating engine).

####Example
Below is the complete implementation of simple realtime application, demostrating some features: dynamically creating a few paragraphs, styles, intervals, etc., message exchanging between frontend and server, and messagin between different sessions. Note how __everything__ fits in a single class:
```python
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
        rdoc.begin() # begin code block
        e=rdoc.create_element('p',txt=':)', )
        rdoc.root_append(e)
        rdoc.end()
        self.i2= rdoc.create_interval(2500) # use the code block above
        wshandler.msg_in_proc(total_docs) # message all other sessions in this process

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

    # this method is called when a session messages every other session
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

In addition, **webalchemy** webapps require a modern webbrowser supporting websockets

##Status
The library is currently in early stages of development, still far from being feature complete

##Philosophy
Lightweight - does one thing and does it well!

Pythonic - Explicit, magicless, easy to understand whats going on

Non oppinionated - plays well with others

High performance - Async, Websockets, CSS3 animations, etc.









