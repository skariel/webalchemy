##Webalchemy
Modern web development with Python, powered by [Pythonium](https://github.com/pythonium/pythonium) and [Tornado](https://github.com/facebook/webalchemy.tornado) (and in the future AsyncIO, AutobahnPython, PyZMQ). it's [MIT licensed](LICENSE.txt)

- Angular style [TodoMVC implementation](http://skariel.org/webalchemy/todomvc.html) -- [Source](https://github.com/skariel/webalchemy/tree/master/webalchemy/examples/todomvc)
- Meteor style live editing [demo](https://vimeo.com/74150054) -- [Source](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/colors_meteor_example.py)
- WebGL Earth [demo](http://skariel.org/webalchemy/webglearth.html) -- [Source](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/three_d_earth/three_d_earth.py)

##Getting Started

###Installation

* Use Python3
* Copy the webalchemy directory to your project root directory (yeah, poorman's install, never fails!)

###Tutorial and Documentation

There is not much yet except a few examples. See below how to run them:

```python
class HellowWorldApp:
    def initialize(self, **kwargs):
        kwargs['remote_document'].body.element(h1='Hello World!!!')
```

to run just do:

```python
from webalchemy import server
server.run(HellowWorldApp)
```

set your browser to http://127.0.0.1:8080

####Example 1: Realtime Meteor Colors:

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source is in the examples directory, it can be executed like this:

```python
from webalchemy import server
from webalchemy.examples.colors_meteor_example import ColorsMeteorApp
server.run(ColorsMeteorApp)
```

####Example 2: "Static" TodoMVC:

```python
from webalchemy import server
from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
server.run(app, main_html_file_path='static/template/index.html')
```

####Example 3: WebGL Earth:

```python
from webalchemy import server
from webalchemy.examples.three_d_earth.three_d_earth import ThreeDEarth
server.run(ThreeDEarth)
```

there is a file in the same directory that serves to freeze the app into a single html file

##Philosophy

The main idea is to write all server-side code and automate the client using proxy objects. This works well for all kinds of apps. For e.g. if you want 100% client side, just tell the server to generate or serve the client code. If you want 99% server then don't use any client code except for passing events to the server, which will decide what to do.
This is like the opposite of what Meteor does, but seems to have several advantages. The best advantage is that you get to enjoy all the Python ecosystem on the server. Want to do some number crunching, machine learning, natural language analysis, or cartography? No problem! Other advantages are server-side code and HTML generation, Python on client side, scaling with ZMQ, etc.

##What to expect:

- Documentation :)
- Major cleanup
- [asyncio](http://docs.python.org/3.4/library/asyncio.html) to replace Tornado in Python3.4
- [ZMQ](http://docs.python.org/3.4/library/asyncio.html) (for some real scalability, like with IPython)
- Data binding for general usage, not just the DOM. Use it with [pixi.js](https://github.com/GoodBoyDigital/pixi.js/) sprites, use it to bind server-side model with client side model, etc.

