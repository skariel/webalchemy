##Webalchemy todomvc

69 sloc. PURE F****** PYTHON! Idiomatic Python I would say. Routing, LocalStorage, efficient rendering. Everything included. Check out the [result](http://skariel.org/webalchemy/todomvc.html)

Clean separation between [HTML View](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/static/template/index.html),
[Model](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/todomvc.py#L12-L51),
and [ViewModel](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/todomvc.py#L55-L94).

The app can be compiled to a "static" page via [This file](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/freeze_app.py).
The [final HTML](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/todomvc.html) lives [here](http://skariel.org/webalchemy/todomvc.html).

Note the size of generated JS when gziped is only ~5K. This is an advantage when compared to the minumal ~40K of angular.
Plus, the whole thing can be served through a websocket with [this](https://github.com/skariel/webalchemy/blob/master/webalchemy/examples/todomvc/serve_through_websocket.py). If you do so then you enjoy live editing and reactivity features like what [Meteor](https://www.meteor.com/) has to offer.
Checkout our initial reactivity [demo](https://vimeo.com/74150054)

This is powered by [Pythonium](https://github.com/pythonium/pythonium).
