##webalchemy: realtime, Pythonic web framework
webalchemy is a fast, simple and lightweight realtime micro web-framework for Python, inspired by [SqlAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). With webalchemy you develop webapps like you would develop a desktop (or mobile) app

####Example
We "translated" Meteor colors app to webalchemy. The app below can be seen in action [here](https://vimeo.com/73073766) and the Meteor original [here](http://www.meteor.com/screencast)
```python
from tornado import gen
from webalchemy.widgets.basic.menu import menu

class colors_app:    

    # shared state between sessions
    colors_count={
        'foo'             :0,
        'bar'             :0,
        'wowowowowo!!!'   :0,
        'this is cool'    :0,
        'WEBALCHEMY ROCKS':0,
    }

    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler

        self.increase_count_by= self.rdoc.jsfunction('element','amount','''
            element.app.clickedcount+= amount;
            if (element.app.clickedcount>0.5) {
                element.textContent= '('+element.app.clickedcount+') '+element.app.text;
            }''')

        # this function will be applied to each item in the menu
        self.onclick= self.rdoc.jsfunction('event','''
            message('evt: '+event.target.app.text);
            #{self.increase_count_by}(event.target,1);
        ''')

        # do this for each element added to the menu
        def on_add(element,color):
            nonlocal self
            element.att.app.text= color
            element.att.app.clickedcount= colors_app.colors_count[color]
            element.att.onclick= self.onclick
            # calling this just to update the count in the item text
            self.increase_count_by(element,0)

        # the menu, with some styling
        self.menu= menu(self.rdoc, on_add)
        self.menu.rule_nav.att.style(display='table',margin='10px')
        self.menu.rule_navli.att.style(
            color='#000000',
            fontSize='2em',
            textTransform='uppercase',
            fontFamily='Arial, Verdana, Sans-serif',
            float='bottom',
            padding='10px',
            listStyle='none',
            cursor='pointer',
            webkitTransition='all 0.3s linear',
            webkitUserSelect='none'
        )
        self.menu.rule_navlihover.att.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
            webkitTransform='rotate(5deg)'
        )
        # populate...
        self.rdoc.body.append(self.menu.element)
        for color in colors_app.colors_count:
            self.menu.add_item(color)

    # this method is called when the frontend sends the server a message
    @gen.coroutine
    def inmessage(self, text):
        if text.startswith('evt: '):
            color= text[5:]
            colors_app.colors_count[color]+= 1
            self.wsh.msg_in_proc(color)

    # this method is called on incomming messages from other sessions
    @gen.coroutine
    def outmessage(self, text, sender):
        for e in self.menu.element.childs:
            if e.text==text:
                self.increase_count_by(e,1)

    # this method is called when session is closed
    @gen.coroutine
    def onclose(self):
        pass

if __name__=='__main__':
    import webalchemy.server
    server.run(8083,colors_app) # the first parameter is the port...
```
##Philosophy and Roadmap
Run relatively simple code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

##Requirements
Python >= 3.3

Tornado >= 3.1

In addition, webalchemy webapps require a modern webbrowser supporting websockets

##License (MIT)
Copyright (c) 2013 Ariel Keselman

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

