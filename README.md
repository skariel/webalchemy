##webalchemy: realtime, Pythonic web framework
webalchemy is a fast, simple and lightweight realtime micro web-framework for Python inspired by [SQLAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). The project is young, documentation is on high priority but still missing

- **MIT License:** <LICENSE.txt>
- **Homepage:** <http://skariel.org/webalchemy/>
- **Discussion:** <https://groups.google.com/forum/#!forum/webalchemy/>

####Example
We "translated" Meteor colors app to webalchemy. The app below can be seen in action [here](https://vimeo.com/73073766) and the Meteor original [here](http://www.meteor.com/screencast)
```python
from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import menu

class colors_app:    

    # shared state between sessions in process
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
        # make page elements..
        self.menu= self.build_menu()
        # populate page
        self.rdoc.body.append(self.menu.element)

    def build_menu(self):
        # This will be passed to the menu initializer
        # so it is applied to each item when added to the menu
        def on_add(item):
            nonlocal m
            color= item.text
            item.att.app.text= color
            item.att.app.clickedcount= colors_app.colors_count[color]
            # note below inline interpolation and rpc call to all sessions
            item.att.onclick= self.rdoc.jsfunction('event','''
                srpc('serverside_on_button_clicked', event.target.app.text);
                #{m.increase_count_by}(event.target,1);
            ''')
            # update the count in the item text
            m.increase_count_by(item,0)

        # create a menu element with the above item initializer
        m= menu(self.rdoc, on_add)
        # style the menu
        m.rule_menu.att.style(display='table',margin='10px')
        m.rule_item.att.style(
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
        m.rule_item_hover.att.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
            webkitTransform='rotate(5deg)'
        )
        # function to increase the count in front-end
        m.increase_count_by= self.rdoc.jsfunction('element','amount','''
            element.app.clickedcount+= amount;
            if (element.app.clickedcount>0.5) {
                element.textContent= '('+element.app.clickedcount+') '+element.app.text;
            }''')
        # populate...
        for color in colors_app.colors_count:
            m.add_item(color)
        return m

    # register the method so we can call it from frontend js directly
    @server.rpc
    @gen.coroutine
    def serverside_on_button_clicked(self, sender_doc, color):
        if sender_doc is self:        
            colors_app.colors_count[color]+= 1
        else:
            for e in self.menu.element.childs:
                if e.text==color:
                    self.menu.increase_count_by(e,1)

if __name__=='__main__':
    server.run('localhost',8083,colors_app)
```
##Philosophy and Roadmap
Run relatively simple code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

##Requirements
* Python >= 3.3
* Tornado >= 3.1
* webalchemy webapps require a modern webbrowser supporting websockets (too much web in this sentence)
