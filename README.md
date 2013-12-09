##webalchemy: realtime web framework for Python
Built on top of [Tornado](http://www.tornadoweb.org/en/stable/) (and in the future Tulip), inspired by [SQLAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). Helps keep frontend simple by automating it with Python through a websocket connection.

The project is young, documentation is high priority but still missing. Currently tested on recent version of Chrome, Firefox, Opera, and Explorer.

- **Discussion:** <https://groups.google.com/forum/#!forum/webalchemy/>
- **License (MIT):** [LICENSE.txt](LICENSE.txt)

We "translated" Meteor colors app to webalchemy. The app can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast). The source in in the examples directory, read below how to run it.

##Getting started
###Installation
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
server.run(colors_meteor_app) 
```

now set your browser to http://127.0.0.1:8080

###Run the example
from your project root:

```python
from webalchemy import server
from webalchemy.examples.colors_meteor_example import colors_meteor_app
server.run(colors_meteor_app) 
```

now set your browser to http://127.0.0.1:8080

###Requirements
* Python >= 3.3
* Tornado >= 3.1
* webalchemy webapps require a modern webbrowser supporting websockets (too much web in this sentence)

##Philosophy and Roadmap
Run relatively simple Javascript code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

A few key points I'll try to adhere to:
* use pure Python, move to Tulip (in Python 3.4)
* stay minimalistic



