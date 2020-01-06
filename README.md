[![PyPi version](https://img.shields.io/pypi/v/Webalchemy.svg)](https://crate.io/packages/Webalchemy/)
[![PyPi downloads](https://img.shields.io/pypi/dm/Webalchemy.svg)](https://crate.io/packages/Webalchemy/)

![Alt Webalchemy](https://i.imgur.com/su7TdAd.png "Webalchemy")

Modern web development with Python3, [MIT licensed](LICENSE.txt). Powered by [Pythonium](https://github.com/pythonium/pythonium), [Tornado](https://github.com/facebook/tornado), and [SockJS](https://github.com/sockjs/sockjs-client). Some examples:

- Angular style TodoMVC [demo](http://skariel.org/webalchemy/todomvc.html) -- [Source](https://github.com/skariel/webalchemy/tree/master/examples/todomvc)
- Meteor style realtime and live editing [video](https://vimeo.com/74150054) --  [Demo](http://weba-colors.herokuapp.com/) -- [Source](https://github.com/skariel/webalchemy/blob/master/examples/colors_meteor/colors_meteor_example.py)
- WebGL Earth [demo](http://skariel.org/webalchemy/webglearth.html) -- [Source](https://github.com/skariel/webalchemy/blob/master/examples/three_d_earth/three_d_earth.py)

Contributions are welcome! Open a pull request, open an issue, mail me code, or post in the [mailing list](https://groups.google.com/forum/#!forum/webalchemy).

## Getting Started

### Installation

Make sure you are using Python3. Then`pip install webalchemy`. Note that this does not install the examples. You can download the examples from the [zip](https://github.com/skariel/webalchemy/archive/master.zip).

### Tutorial and Documentation

A Webalchemy application is a regular Python class (no need to inherit anything) that provides relevant methods used by the Webalchemy server. The only required method is `initialize`, which is called when the client side is ready for automation. Here we create a header and append it to the document body:

```python
class HellowWorldApp:
    def initialize(self, **kwargs):
        kwargs['remote_document'].body.element(h1='Hello World!!!')
```

To serve through a websocket just feed it to the run function and set your browser to http://127.0.0.1:8080.

```python
from webalchemy import server
from myapp import HellowWorldApp
server.run(HellowWorldApp)
```

Try to change the header text content and save the file to see how the client changes accordingly. Note that the App has to be imported for the live-editing to work correctly.

It is also possible to add some styles:

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

Want to use CSS rules to style all h1's? No problem!

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

Adding event listerners is also possible. Let's add a click listener using the elements `events` property like this:

 ```Python
self.rdoc.body.element(h1='Hello World!!!').events.add(click=self.clicked, translate=True)
 ```

Let's define a simple event in which each click deletes the 1st letter of the heading. This is run on the client and it is translated to JS behind the scenes:

```Python
def clicked(self):
    self.textContent = self.textContent[1:]
```

In addition, if we want to notify the server that the button was clicked we could use an RPC call from the client to the server. We just need to add one line:

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

This how you push and pull data to and from the client. See this program live on [heroku](http://weba-hello.herokuapp.com/).

Now you may wonder if it's dangerous for the client to be able to call any function on the server. Actually the client can only call registered functions. In our case `handle_click_on_backend` got registered when we assigned it to the `rpc()` call on the client.

#### Including external scripts

Use `include` to import external scripts into your project.

```Python
class ThreeDEarth:

    include = ['https://rawgithub.com/mrdoob/three.js/master/build/three.min.js']

    def initialize(self, **kwargs):
        # do something cool here!
```

#### Including external stylesheets

Use `stylesheets` to import external stylesheets.

```Python
class JQueryMobileExample:

    # Include the jQuery mobile stylesheet and the jQuery/jQuery mobile scripts
    stylesheets = ['http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.css']
    
    include = ['http://code.jquery.com/jquery-1.10.2.min.js',
               'http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.js']

    def initialize(self, **kwargs):
        # do something cool here!
```

This will produce the following html in your client:

```html
<!DOCTYPE html>
<html>
   <head>
       <base href="http://127.0.0.1:8080/"></base>
       <link href="http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.css" rel="stylesheet"></link>
       <script src="http://code.jquery.com/jquery-1.10.2.min.js" type="text/javascript"></script>
       <script src="http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.js" type="text/javascript"></script>
```

#### Hosting

Webalchemy uses SockJS so no need for a host supporting websockets. Howvever real websockets can still provide a
benefit in terms of performance. If you are interested to support websockets try hosting with
[Heroku](https://www.heroku.com/) or [OpenShift](https://www.openshift.com/) - these are two good options.

#### Further help

Join the [mailing list](https://groups.google.com/forum/#!forum/webalchemy).

Webalchemy supports the MVC pattern, usage of existing HTML, several configuration options and much more. All this missing documentation is WIP. We also suggest you play a bit, try making a few containers - you can spread them across multiple Python files. It's not too complicated :)

The examples below demonstrate a few more features.

#### Example 1: Realtime Meteor Colors:

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source is in the examples directory ([here](https://github.com/skariel/webalchemy/blob/master/examples/colors_meteor/colors_meteor_example.py)), it can be executed like this:
```python
from webalchemy import server
from examples.colors_meteor.colors_meteor_example import ColorsMeteorApp
server.run(ColorsMeteorApp)
```
A live version is [here](http://weba-colors.herokuapp.com/)

#### Example 2: TodoMVC:

This is a client-only app. It can be served from a websocket like this:

```python
from webalchemy import server
from examples.todomvc.todomvc import AppTodoMvc as app
server.run(app)
```

or it can be "frozen" to be served from a static folder (see [live demo](http://skariel.org/webalchemy/todomvc.html)) like this:

```Python
from webalchemy import server
from examples.todomvc.todomvc import AppTodoMvc as app
server.generate_static(app)
```

This will generate `todomvc.html` as defined in the configuration in `app`. Note the references to static files in the HTML, you have to place the file where these are accessible or just change the paths. More on this app [here](https://github.com/skariel/webalchemy/tree/master/examples/todomvc).

#### Example 3: WebGL Earth:

```python
from webalchemy import server
from examples.three_d_earth.three_d_earth import ThreeDEarth
server.run(ThreeDEarth)
```

See the frozen app [here](http://skariel.org/webalchemy/webglearth.html) and the source [here](https://github.com/skariel/webalchemy/blob/master/examples/three_d_earth/three_d_earth.py).

## Philosophy

The main idea is to write all server-side code and automate the client using proxy objects. This works well for all kinds of apps. For e.g. if you want 100% client side, just tell the server to generate or serve the client code. If you want 99% server then don't use any client code except for passing events to the server, which will decide what to do. This is like the opposite of what Meteor does, but seems to have several advantages. 

The best advantage is that you get to enjoy all the Python ecosystem on the server. Want to do some number crunching, machine learning, natural language analysis, or cartography? No problem! Other advantages are server-side code and HTML generation, Python on client side, scaling with ZMQ, etc.

## What to expect:

- Documentation, tutorials :)
- Major cleanup.
- [pyzmq](https://github.com/zeromq/pyzmq) for some real scalability, like with IPython.
- Data binding for general usage, not just the DOM. Use it with [pixi.js](https://github.com/GoodBoyDigital/pixi.js/) sprites, use it to bind server-side model with client side model, etc.
- A few API changes (the project is still very young).
- A Community!

