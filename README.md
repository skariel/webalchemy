![Alt Webalchemy](https://raw2.github.com/skariel/webalchemy/master/logo.png "Webalchemy")
                   
powered by [Pythonium](https://github.com/pythonium/pythonium) and [Tornado](https://github.com/facebook/webalchemy.tornado). it's [MIT licensed](LICENSE.txt)

- Angular style TodoMVC [live demo](http://skariel.org/webalchemy/todomvc.html) -- [Source](https://github.com/skariel/webalchemy/tree/master/webalchemy/examples/todomvc)
- Meteor style realtime and live editing [video](https://vimeo.com/74150054) -- [Source](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/colors_meteor_example.py) (this screencast is old, still containing some JS. a new one is WIP)
- WebGL Earth [live demo](http://skariel.org/webalchemy/webglearth.html) -- [Source](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/three_d_earth/three_d_earth.py)

##Getting Started

###Installation

* Make sure you use Python3
* Copy the webalchemy directory to your project root directory (yeah, poorman's install, never fails!)
* no external dependencies, all Pure Python, all included. Arriving to PIP soon :)

###Tutorial and Documentation

A Webalchemy application is a regular Python class (no need to inherit anything) that provides relevant methods used by the Webalchemy server.
The only required method is `initialize`, which is called when the client side is ready for automation. Here we create a header and
append it to the document body:

```python
class HellowWorldApp:
    def initialize(self, **kwargs):
        kwargs['remote_document'].body.element(h1='Hello World!!!')
```

to serve through a websocket just feed it to the run function and set your browser to http://127.0.0.1:8080

```python
from webalchemy import server
server.run(HellowWorldApp)
```

Try to change the header text content and save the file, see how the client changes accordingly. Lets put some style:

```Python
class HellowWorldApp:
    def initialize(self, **kwargs):
        h1 = kwargs['remote_document'].body.element(h1='Hello World!!!')
        h1.style(
            color='#FF0000',
            marginLeft='75px',
            marginTop='75px',
            background='#00FF00'
        )
```

Want to use css rules to style all h1`s? no problem!

```Python
class HellowWorldApp:
    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.rdoc.body.element(h1='Hello World!!!')
        self.rdoc.body.element(h1='--------------')
        self.rdoc.stylesheet.rule('h1').style(
            color='#FF0000',
            marginLeft='75px',
            marginTop='75px',
            background='#00FF00'
        )
```

Lets add a click listener now by using the elements `events` property like this:

 ```Python
self.rdoc.body.element(h1='Hello World!!!').events.add(click=self.clicked, translate=True)
 ```

lets define a simple event in which each click deletes the 1st letter in the heading:

```Python
def clicked(self):
    self.textContent = self.textContent[1:]
```

lets also notify the server that the button was clicked:

```Python
def clicked(self):
    self.textContent = self.textContent[1:]
    rpc(self.handle_click_on_backend, 'some message', 'just so you see how to pass paramaters')
```

The above function is run in the client. In the server we'll do the following:

```Python
def handle_click_on_backend(self, sender_id, m1, m2):
    self.rdoc.body.element(h1=m1+m2)
```

The whole program look like this:

```Python
class HellowWorldApp:
    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.rdoc.body.element(h1='Hello World!!!').events.add(click=self.clicked, translate=True)
        self.rdoc.body.element(h2='--------------')
        self.rdoc.stylesheet.rule('h1').style(
            color='#FF0000',
            marginLeft='75px',
            marginTop='75px',
            background='#00FF00'
        )

    def clicked(self):
        self.textContent = self.textContent[1:]
        rpc(self.handle_click_on_backend, 'some message', 'just so you see how to pass paramaters')

    def handle_click_on_backend(self, sender_id, m1, m2):
        self.rdoc.body.element(h1=m1+m2)
```

This demonstrated how to push and pull data from the client. Now you may wonder if it's dangerous for the client to be able to call any function on the server.
Well actually the client can only call registered functions. In our case `handle_click_on_backend` got registered when we assigned it to the `rpc()` call on the client.

####Including external scripts

no need to require :)

```Python
class ThreeDEarth:

    include = ['https://rawgithub.com/mrdoob/three.js/master/build/three.min.js']

    def initialize(self, **kwargs):
        # do something cool here!
```

####Further help

Join the [mailing list](https://groups.google.com/forum/#!forum/webalchemy).

webalchemy supports the MVC pattern, usage of existing HTML, and much more. All this missing documentation is WIP.
Meanwhile take a look in the examples below.
I also suggest you play a bit, try making a few containers - you can spread them across multiple Python files. It's not too complicated :)


See examples below, they demonstrate a lot more than the above. Further docs and tutorials are WIP

####Example 1: Realtime Meteor Colors:

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source is in the examples directory ([here](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/colors_meteor_example.py)), it can be executed like this:

```python
from webalchemy import server
from webalchemy.examples.colors_meteor_example import ColorsMeteorApp
server.run(ColorsMeteorApp)
```

Note this example still contains a bit of JS, it will be translated to pure Python soon.

####Example 2: TodoMVC:

This is a client-only app. It can be served from a websocket like this:

```python
from webalchemy import server
from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
server.run(app)
```

or it can be "frozen" to be served from a static folder (see [live demo](http://skariel.org/webalchemy/todomvc.html))like this:

```Python
from webalchemy import server
from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
server.generate_static(app, writefile='todomvc.html')
```

more on this app [here](https://github.com/skariel/webalchemy/tree/master/webalchemy/examples/todomvc)

####Example 3: WebGL Earth:

```python
from webalchemy import server
from webalchemy.examples.three_d_earth.three_d_earth import ThreeDEarth
server.run(ThreeDEarth)
```

see frozen app [here](http://skariel.org/webalchemy/webglearth.html) and source [here](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/three_d_earth/three_d_earth.py)

##Philosophy

The main idea is to write all server-side code and automate the client using proxy objects. This works well for all kinds of apps. For e.g. if you want 100% client side, just tell the server to generate or serve the client code. If you want 99% server then don't use any client code except for passing events to the server, which will decide what to do.
This is like the opposite of what Meteor does, but seems to have several advantages. The best advantage is that you get to enjoy all the Python ecosystem on the server. Want to do some number crunching, machine learning, natural language analysis, or cartography? No problem! Other advantages are server-side code and HTML generation, Python on client side, scaling with ZMQ, etc.

##What to expect:

- Documentation :)
- Major cleanup
- [asyncio](http://docs.python.org/3.4/library/asyncio.html) and [AutobahnPython](http://autobahn.ws/python/) to replace Tornado in Python3.4
- [pyzmq](https://github.com/zeromq/pyzmq) for some real scalability, like with IPython
- Data binding for general usage, not just the DOM. Use it with [pixi.js](https://github.com/GoodBoyDigital/pixi.js/) sprites, use it to bind server-side model with client side model, etc.

