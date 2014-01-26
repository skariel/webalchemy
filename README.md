![Alt Webalchemy](https://i.imgur.com/su7TdAd.png "Webalchemy")

Modern web development with Python3, [MIT licensed](LICENSE.txt). Powered by [Pythonium](https://github.com/pythonium/pythonium) and [Tornado](https://github.com/facebook/tornado). Some examples:

- Angular style TodoMVC [demo](http://skariel.org/webalchemy/todomvc.html) -- [Source](https://github.com/skariel/webalchemy/tree/master/examples/todomvc)
- Meteor style realtime and live editing [video](https://vimeo.com/74150054) -- [Source](https://github.com/skariel/webalchemy/blob/master/examples/colors_meteor_example.py) (this screencast is old, new code contains no JS)
- WebGL Earth [demo](http://skariel.org/webalchemy/webglearth.html) -- [Source](https://github.com/skariel/webalchemy/blob/master/examples/three_d_earth/three_d_earth.py)

Contributions are welcome! open a pull request, open an issue, mail me code, or post in the [mailing list](https://groups.google.com/forum/#!forum/webalchemy)

##Getting Started

###Installation

Make sure you are using Python3. Then`pip install webalchemy`. Note this doesn't installs the examples. For this please download the [zip](https://github.com/skariel/webalchemy/archive/master.zip)

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
from myapp import HellowWorldApp
server.run(HellowWorldApp)
```

Try to change the header text content and save the file, see how the client changes accordingly.
Note that the App has to be imported for the live-editing to work correctly.

Lets put some style:

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

Want to use CSS rules to style all h1`s? no problem!

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

lets define a simple event in which each click deletes the 1st letter in the heading. This is run on the client, it is translated to JS behind the scenes:

```Python
def clicked(self):
    self.textContent = self.textContent[1:]
```

In addition, if we want to notify the server that the button was clicked we could use an RPC call from the client to the server. The function above should be added one line:

```Python
def clicked(self):
    self.textContent = self.textContent[1:]
    rpc(self.handle_click_on_backend, 'some message', 'just so you see how to pass paramaters')
```

In the server we can do something like this:

```Python
def handle_click_on_backend(self, sender_id, m1, m2):
    self.rdoc.body.element(h1=m1+m2)
```

The program looks like this:

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

This how you push and pull data to and from the client. Now you may wonder if it's dangerous for the client to be able to call any function on the server.
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

webalchemy supports the MVC pattern, usage of existing HTML, several configuration options and much more. All this missing documentation is WIP.
Meanwhile take a look in the examples below.
I also suggest you play a bit, try making a few containers - you can spread them across multiple Python files. It's not too complicated :)


The examples below demonstrate a few more features.

####Example 1: Realtime Meteor Colors:

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source is in the examples directory ([here](https://github.com/skariel/webalchemy/blob/master/examples/colors_meteor_example.py)), it can be executed like this:

```python
from webalchemy import server
from examples.colors_meteor_example import ColorsMeteorApp
server.run(ColorsMeteorApp)
```

####Example 2: TodoMVC:

This is a client-only app. It can be served from a websocket like this:

```python
from webalchemy import server
from examples.todomvc.todomvc import AppTodoMvc as app
server.run(app)
```

or it can be "frozen" to be served from a static folder (see [live demo](http://skariel.org/webalchemy/todomvc.html))like this:

```Python
from webalchemy import server
from examples.todomvc.todomvc import AppTodoMvc as app
server.generate_static(app)
```

This will generate `todomvc.html` as defined in the configuration in `app`. Note the references to static files in the HTML, you have to place the file where these are accessible or just change the paths. More on this app [here](https://github.com/skariel/webalchemy/tree/master/examples/todomvc)

####Example 3: WebGL Earth:

```python
from webalchemy import server
from examples.three_d_earth.three_d_earth import ThreeDEarth
server.run(ThreeDEarth)
```

see frozen app [here](http://skariel.org/webalchemy/webglearth.html) and source [here](https://github.com/skariel/webalchemy/blob/master/examples/three_d_earth/three_d_earth.py)

##Philosophy

The main idea is to write all server-side code and automate the client using proxy objects. This works well for all kinds of apps. For e.g. if you want 100% client side, just tell the server to generate or serve the client code. If you want 99% server then don't use any client code except for passing events to the server, which will decide what to do.
This is like the opposite of what Meteor does, but seems to have several advantages. The best advantage is that you get to enjoy all the Python ecosystem on the server. Want to do some number crunching, machine learning, natural language analysis, or cartography? No problem! Other advantages are server-side code and HTML generation, Python on client side, scaling with ZMQ, etc.

##What to expect:

- Documentation :)
- Major cleanup
- [asyncio](http://docs.python.org/3.4/library/asyncio.html) and [AutobahnPython](http://autobahn.ws/python/) to replace Tornado in Python3.4
- [pyzmq](https://github.com/zeromq/pyzmq) for some real scalability, like with IPython
- Data binding for general usage, not just the DOM. Use it with [pixi.js](https://github.com/GoodBoyDigital/pixi.js/) sprites, use it to bind server-side model with client side model, etc.

