#
# trying to reconstruct Meteor color application
#
import logging

from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import Menu

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ColorsMeteorApp:
# shared state between sessions in process
    colors_count = {
        'foo': 0,
        'baar': 0,
        'wowowowowo!!!': 0,
        'this is cool': 0,
        'WEBALCHEMY ROCKS': 0,
    }

    colors_selected = {}

    @staticmethod
    def prepare_app_for_general_reload():
        return {
            'colors_count': ColorsMeteorApp.colors_count,
            'colors_selected': ColorsMeteorApp.colors_selected}

    @staticmethod
    def recover_app_from_general_reload(data):
        colors_count = data['colors_count']
        ColorsMeteorApp.colors_selected = data['colors_selected']
        for color in ColorsMeteorApp.colors_count.keys():
            if color in colors_count:
                ColorsMeteorApp.colors_count[color] = colors_count[color]

    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, sessionid, tabid):

        # remember these for later use
        self.tabid = tabid
        self.sessionid = sessionid
        self.rdoc = remotedocument
        self.wsh = wshandler

        # insert a title
        self.title = self.rdoc.body.element('h1', 'COLORS I REALLY LIKE :)')
        self.title.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='3.5em',
        )
        self.rdoc.props.title = 'colors app!'

        # insert a menu
        self.menu = self.build_menu()
        self.menu.element.style(marginLeft='50px', marginBottom='30px', width='400px', borderWidth='2px')
        self.rdoc.body.append(self.menu.element)

        # insert a button
        self.button = self.rdoc.body.element('button', 'Like!')
        self.button.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
        )
        self.button.events.add(click=self.rdoc.jsfunction(body='''
            if (!#{self.menu.element}.app.selected) return;
            #{self.menu.increase_count_by}(#{self.menu.element}.app.selected,1);
            rpc('color_liked', #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, 1);
        '''))

        # insert another button !!
        self.button2 = self.rdoc.body.element('button', 'UNLike!')
        self.button2.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
        )
        self.button2.events.add(click=self.rdoc.jsfunction(body='''
            if (!#{self.menu.element}.app.selected) return;
            #{self.menu.increase_count_by}(#{self.menu.element}.app.selected,-1);
            rpc('color_liked', #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, -1);
        '''))

        if tabid in ColorsMeteorApp.colors_selected:
            for i in self.menu.id_dict.values():
                if i.text == ColorsMeteorApp.colors_selected[tabid]:
                    break
            self.menu.select_color(i)

    # register the method so we can call it from frontend js,
    # and then also from other sessions (from Python)
    @server.jsrpc
    @server.pyrpc
    @gen.coroutine
    def color_liked(self, sender_id, item_id, color, amount):
        if sender_id == self.wsh.id:
            # button clicked on this session
            ColorsMeteorApp.colors_count[color] += int(amount)
            self.wsh.rpc(self.color_liked, item_id, color, amount)
        else:
            # button clicked by other session
            item = self.menu.id_dict[item_id]
            self.menu.increase_count_by(item, int(amount))

    @server.jsrpc
    @gen.coroutine
    def color_selected(self, sender_id, item_id, color):
        ColorsMeteorApp.colors_selected[self.tabid] = color

    def build_menu(self):
        # the following function will be used to initialize all menu items
        def on_add(item):
            nonlocal m
            col = item.text
            item.app.color = col
            item.app.clickedcount = ColorsMeteorApp.colors_count[col]
            m.increase_count_by(item, 0)

            # create a menu element with the above item initializer

        m = Menu(self.rdoc, on_add)
        # function to increase the count in front-end
        m.sort = self.rdoc.jsfunction(body='''
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
        m.increase_count_by = self.rdoc.jsfunction('element', 'amount', body='''
            att= element.app;
            att.clickedcount+= amount;
            #{m.sort}();
            if (att.clickedcount>0.5) {
                element.textContent= '('+att.clickedcount+') '+att.color;
            }''')
        m.select_color = self.rdoc.jsfunction('element', body='''
            element.classList.add('selected');
            if ((#{m.element}.app.selected)&&(#{m.element}.app.selected!=element))
                #{m.element}.app.selected.classList.remove('selected');
            #{m.element}.app.selected= element;
            rpc('color_selected', element.id, element.app.color);
        ''')
        m.element.events.add(click=self.rdoc.jsfunction('event', body='''
            #{m.select_color}(event.target);
        '''))
        # style the menu
        m.rule_menu.style(display='table', margin='10px')
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
        for color in sorted(ColorsMeteorApp.colors_count.keys()):
            m.add_item(color)
        m.sort()
        return m
