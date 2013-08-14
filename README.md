##webalchemy

webalchemy is a light and Pythonic framework to build interactive webapps. It is open source (MIT licensed) you can use it alsso in commercial software.

webalchemy works with Python >= 3.3, the only external dependency to Python standard library is Tornado >= 3.1 

The library is currently in veery early stages of development, and it is not feature complete (or even close to this)

The webapps developped with webalchemy require a modern browser implementing some feature from HTML5, websockets and CSS3

##Philosophy

webapps made with webalchemy are highly dynamic: the application and server will exchange many messages over websockets. Only a minimal amount of static cintent is initially served, but from there on all page is rendered dynamically

Use Python to automate the front end: simple library calls generate the JS required on the frontend. You program like you would program a desktop app, not caring much about HTML, CSS, or JS

Keep fronend code simple: Frequent information exchange between server and fronend allows you to put all complex (business?) logic on the server side. This is good since you can use regular Python to build this complex logic. Python makes complex things posssible :)




