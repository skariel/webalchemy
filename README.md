##webalchemy
webalchemy is a light and Pythonic framework to build interactive webapps. It is open source (MIT licensed) you can use it in commercial software. The library requires Python >= 3.3, and Tornado >= 3.1. Note it is currently in early stages of development, still far from being feature complete. webalchemy webapps require a modern browser supporting websockets.

webalchemy represents a novel approach to webapp development obviously inspired by [SqlAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). It let's you write server code as if it were running on the client Err.., In fact forget about client and server altogether. Develop like you would for the desktop.

##Develop a webapp like you would a desktop app
webapps made with webalchemy are highly dynamic: the browser and server frequently exchange messages over websockets. Only a minimal amount of static content is initially served, and from there on all page is rendered dynamically. This allows to keep frontend code simple as all complex logic is implemented on the server, using regular Python. In essense, with webalchemy you use Python to automate the frontend. Simple library calls generate the JS required on the frontend, and you program like you would a desktop app - not caring much about HTML, CSS, or JS (they can still be used on demand, and nothing prevents usage of a templating engine).

####Example
Below is the complete implementation of simple but dynamic application. The app creates 2 time intervals, one adding paragraphs to the DOM and the other communicating with the server. The server then responds and creates a new paragraph, and deletes the previous one. Despite all the dynamism all the code is encapsulated in a single class, written in pure Python:
```python
from tornado import gen
class my_app:    
    def __init__(self, rdoc):
        self.p= rdoc.create_element('p',txt='This is an empty document', )
        rdoc.root_append(self.p)
        self.i= rdoc.create_interval(1000,rdoc.msg('interval!'))
        self.i.count=0
        rdoc.begin()
        e=rdoc.create_element('p',txt=':)', )
        rdoc.root_append(e)
        rdoc.end()
        self.i2= rdoc.create_interval(2500)
    
    @gen.coroutine
    def message(self, rdoc, txt):
        if txt!='interval!':
            return
        if self.i.count>5:
            self.i.stop()
            self.i2.stop()
        self.i.count+=1
        try:
            self.tp.remove()
        except:
            pass # nothing to remove
        self.tp= rdoc.create_element('p',txt='New paragraph #'+str(self.i.count))
        self.tp.set_style_att(position='absolute', left=str(50*self.i.count)+'px', top=str(50*self.i.count)+'px')
        self.p.set_text('there are now '+str(self.i.count+1)+' paragraphs')
        rdoc.root_append(self.tp)
            
if __name__=='__main__':
    import webalchemy.server
    server.run(8083,my_app)
```
##Philosophy
Lightweight - does one thing and does it well!

Pure Python - as much as possible for webapps

Non oppinionated - plays well with others

High performance - Async, Websockets, CSS3 animations, etc.









