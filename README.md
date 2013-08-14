##webalchemy
webalchemy is a light and Pythonic framework to build interactive webapps. It is open source (MIT licensed) you can use it in commercial software. The library requires Python >= 3.3, and Tornado >= 3.1. Note it is currently in early stages of development, still far from being feature complete. webalchemy webapps require a modern browser implementing some feature from HTML5, websockets and CSS3.

webalchemy represents a novel approach to webapp development obviously inspired by [sqlalchemy](http://www.sqlalchemy.org/), and the IPython [notebook](http://ipython.org/). It let's you write server code as if it were running on the client Err.., In fact forget about client and server altogether. Develop like you would for the desktop.

##Develop a webapp like you would a desktop app

webapps made with webalchemy are highly dynamic: the browser and server frequently exchange messages over websockets. Only a minimal amount of static content is initially served, and from there on all page is rendered dynamically. This allows to keep fronend code simple as all complex logic is implemented on the server, using regular Python. In essense, with webalchemy you automate the front end with Python. Simple library calls generate the JS required on the frontend, and you program like you would a desktop app - not caring much about HTML, CSS, or JS.

##Philosophy
Lightweight - does one thing and does it well!

Pure Python - as much a possible for webapps

Non oppinionated - plays well with others

High performance









