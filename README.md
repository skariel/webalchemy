##webalchemy: realtime, Pythonic web framework
webalchemy is a minimalist, realtime web-framework for Python. It is currently built on top of [Tornado](http://www.tornadoweb.org/en/stable/) (and in the future Tulip), and it is inspired by [SQLAlchemy](http://www.sqlalchemy.org/), the [IPython notebook](http://ipython.org/), and of course [Meteor](http://www.meteor.com/). We do not aim to replace Javascript, but just to keep it simple by automating it with Python. The project is young, documentation is high priority but still missing

- **Homepage:** <http://skariel.org/webalchemy/>
- **Discussion:** <https://groups.google.com/forum/#!forum/webalchemy/>
- **License (MIT):** [LICENSE.txt](LICENSE.txt)

We "translated" Meteor colors app to webalchemy. The app below can be seen in action [here](https://vimeo.com/74150054) and the Meteor original [here](http://www.meteor.com/screencast)
```python
import logging

from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import menu

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)

class colors_meteor_app:    

    # shared state between sessions in process
    colors_count={
        'foo'             :0,
        'baar'            :0,
        'wowowowowo!!!'   :0,
        'this is cool'    :0,
        'WEBALCHEMY ROCKS':0,
    }

    colors_selected={}

    @staticmethod
    def prepare_app_for_general_reload():
        return {
            'colors_count':colors_meteor_app.colors_count,
            'colors_selected':colors_meteor_app.colors_selected}

    @staticmethod
    def recover_app_from_general_reload(data):
        colors_count=data['colors_count']
        colors_meteor_app.colors_selected= data['colors_selected']
        for color in colors_meteor_app.colors_count.keys():
            if color in colors_count:
                colors_meteor_app.colors_count[color]= colors_count[color]

    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, sessionid, tabid):

        # remember these for later use
        self.tabid= tabid
        self.sessionid= sessionid
        self.rdoc= remotedocument
        self.wsh= wshandler

        # insert a title
        self.title= self.rdoc.element('h1','COLORS I REALLY LIKE :)')
        self.title.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='3.5em',
            )

        self.rdoc.body.append(self.title)

        # insert a menu
        self.menu= self.build_menu()
        self.menu.element.style(marginLeft='50px',marginBottom='30px',width='400px',borderWidth='2px')
        self.rdoc.body.append(self.menu.element)

        # insert a button
        self.button= self.rdoc.element('button','Like!')
        self.button.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
            )
        self.button.events.add(click= self.rdoc.jsfunction(body='''
            if (!#{self.menu.element}.app.selected) return;
            #{self.menu.increase_count_by}(#{self.menu.element}.app.selected,1);
            rpc('color_liked', #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, 1);
        '''))        
        self.rdoc.body.append(self.button)

        # insert another button !!
        self.button2= self.rdoc.element('button','UNLike!')
        self.button2.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
            )
        self.button2.events.add(click= self.rdoc.jsfunction(body='''
            if (!#{self.menu.element}.app.selected) return;
            #{self.menu.increase_count_by}(#{self.menu.element}.app.selected,-1);
            rpc('color_liked', #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, -1);
        '''))        
        self.rdoc.body.append(self.button2)

        if tabid in colors_meteor_app.colors_selected:
            for i in self.menu.id_dict.values():
                if i.text==colors_meteor_app.colors_selected[tabid]:
                    break
            self.menu.select_color(i)

    # register the method so we can call it from frontend js,
    # and then also from other sessions (from Python)
    @server.jsrpc
    @server.pyrpc
    @gen.coroutine
    def color_liked(self, sender_id, item_id, color, amount):
        if sender_id==self.wsh.id:
            # button clicked on this session
            colors_meteor_app.colors_count[color]+= int(amount)
            self.wsh.rpc(self.color_liked, item_id, color, amount)
        else:
            # button clicked by other session
            item= self.menu.id_dict[item_id]
            self.menu.increase_count_by(item, int(amount))

    @server.jsrpc
    @gen.coroutine
    def color_selected(self, sender_id, item_id, color):
        colors_meteor_app.colors_selected[self.tabid]= color

    def build_menu(self):
        # the following function will be used to initialize all menu items
        def on_add(item):
            nonlocal m
            color= item.text
            item.app.color= color
            item.app.clickedcount= colors_meteor_app.colors_count[color]
            m.increase_count_by(item,0)
        # create a menu element with the above item initializer
        m= menu(self.rdoc, on_add)
        # function to increase the count in front-end
        m.sort= self.rdoc.jsfunction(body='''
            e=#{m.element}
            var arr = Array.prototype.slice.call( e.children ).sort(function (a,b) {
                if (a.app.clickedcount < b.app.clickedcount)
                    return -1;
                if (a.app.clickedcount > b.app.clickedcount)
                    return 1;
                return 0;                
            });
            for(i=0;i<arr.length;i++)
                e.appendChild(arr[i])
            return arr;
            ''')
        m.increase_count_by= self.rdoc.jsfunction('element','amount',body='''
            att= element.app;
            att.clickedcount+= amount;
            #{m.sort}();
            if (att.clickedcount>0.5) {
                element.textContent= '('+att.clickedcount+') '+att.color;
            }''')
        m.select_color= self.rdoc.jsfunction('element',body='''
            element.classList.add('selected');
            if ((#{m.element}.app.selected)&&(#{m.element}.app.selected!=element))
                #{m.element}.app.selected.classList.remove('selected');
            #{m.element}.app.selected= element;
            rpc('color_selected', element.id, element.app.color);
        ''')
        m.element.events.add(click= self.rdoc.jsfunction('event',body='''
            #{m.select_color}(event.target);
        '''))
        # style the menu
        m.rule_menu.style(display='table',margin='10px')
        m.rule_item.style(
            color='#000000',
            fontSize='1.5em',
            textTransform='uppercase',
            fontFamily='Arial, Verdana, Sans-serif',
            float='bottom',
            padding='10px',
            listStyle='none',
            cursor='pointer',
            webkitTransition='all 0.3s linear',
            webkitUserSelect='none'
        )
        m.rule_item_hover.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
        )
        m.rule_item_selected.style(
            padding='10px',
            background='#FF0000',
            color='#000000',
            webkitTransform='rotate(3deg)'
        )
        # populate the menu with shared colors dict
        for color in sorted(colors_meteor_app.colors_count.keys()):
            m.add_item(color)
        m.sort()
        return m


if __name__=='__main__':
    server.run('localhost',8084,colors_meteor_app)
```
##Getting started
###Installation
* Install latest [tornado](http://www.tornadoweb.org/en/stable/#installation)
* copy the webalchemy directory to your project root directory (yeah, poorman's install, never fails!)

###Run the example
from your project root:

```python
from webalchemy import server
import logging
server.log.setLevel(logging.INFO)
from webalchemy.examples.colors_meteor_example import colors_meteor_app
server.run('127.0.0.1',8083,colors_meteor_app) 
```

now set your browser to http://127.0.0.1:8083

###Requirements
* Python >= 3.3
* Tornado >= 3.1
* webalchemy webapps require a modern webbrowser supporting websockets (too much web in this sentence)

##Philosophy and Roadmap
Run relatively simple Javascript code in the frontend, and structure this code so it is easy to automate from the backend. I would like to have a rich widgets library and a strategy for easy development of new ones. The roadmap to achieve this is to use webalchemy to reimplement demos and examples from Meteor and other frameworks, while filling in missing functionality.

