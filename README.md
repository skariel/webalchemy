##Webalchemy: realtime web framework for Python
helps keep frontend code simple by automating it through a websocket connection

###Features:

- Data binding and MVVM support, Angular style: [TodoMVC implementation](http://skariel.org/webalchemy/todomvc.html) only [69 SLOC](https://github.com/skariel/webalchemy/tree/master/webalchemy/examples/todomvc)
- Realtime and live-editing, Meteor style. Checkout our [demo (video)](https://vimeo.com/74150054)
- Use pure Python3, thanks to [Pythonium](https://github.com/pythonium/pythonium)
- [MIT licensed](LICENSE.txt)

##Getting started

###Installation

* Python3
* Install latest [tornado](http://www.tornadoweb.org/en/stable/#installation)
* copy the webalchemy directory to your project root directory (yeah, poorman's install, never fails!)

###Hello world

```python
class HellowWorldApp:
    def initialize(self, **kwargs):
        kwargs['remote_document'].body.element(h1='Hello World!!!')
```

That's it. Now to run just do:

```python
from webalchemy import server
server.run(colors_meteor_app) 
```

now set your browser to http://127.0.0.1:8080

###Running the example from the video:

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source is in the examples directory, it can be executed like this:

```python
from webalchemy import server
from webalchemy.examples.colors_meteor_example import colors_meteor_app
server.run(colors_meteor_app) 
```

###Running the todomvc via websocket:

```python
from webalchemy.examples.todomvc.serve_through_websocket import run
run()
```

there is a file in the same directory that serves to freeze the app into a single html file

###Documentation

The project is young, documentation is high priority but still missing. There are [discussion](https://groups.google.com/forum/#!forum/webalchemy/) forums though.

##Philosophy and Roadmap

Run relatively simple Javascript code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

###What to expect:

- integration of [Pythonium](https://github.com/pythonium/pythonium)
- Documentation :)

