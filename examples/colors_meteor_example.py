'''trying to reconstruct Meteor color application'''

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from webalchemy import server
from webalchemy.widgets.basic.menu import Menu


class ColorsMeteorApp:

    @staticmethod
    def initialize_shared_data(sdata):
        # shared state between sessions in process
        def add_update(d1, d2):
            for k, v in d2.items():
                d1[k] = d1.get(k, 0) + v
        add_update(sdata, {
            'fooooo': 0,
            'baar': 0,
            'wowowowowo!!!': 0,
            'this is cool': 0,
            'WEBALCHEMY ROCKS': 0,
        })

    # this method is called when a new session starts
    def initialize(self, **kwargs):
        # remember these for later use
        self.rdoc = kwargs['remote_document']
        self.com = kwargs['comm_handler']
        self.sdata = kwargs['shared_data']
        self.tdata = kwargs['tab_data']

        # insert a title
        title = self.rdoc.body.element(h1='COLORS I REALLY LIKE :)')
        title.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='3.5em',
        )
        self.rdoc.props.title = 'colors app!'

        # insert a menu
        self.menu = self.build_menu()
        self.menu.element.style(
            marginLeft='50px',
            marginBottom='30px',
            width='400px',
            borderWidth='2px')
        self.rdoc.body.append(self.menu.element)

        # insert a button
        button = self.rdoc.body.element(button='Like!')
        button.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
        )

        def button_click_p():
            if srv(self.menu.element).app.selected is None: return
            srv(self.menu.increase_count_by)(srv(self.menu.element).app.selected, 1)
            rpc(self.color_liked, srv(self.menu.element).app.selected.id,
                srv(self.menu.element).app.selected.app.color, 1)

        button.events.add(click=button_click_p, translate=True)

        # insert another button !!
        button2 = self.rdoc.body.element(button='UNLike!')
        button2.style(
            fontFamily='Arial, Verdana, Sans-serif',
            fontSize='1.5em',
        )
        def button_click_n():
            if srv(self.menu.element).app.selected is None: return
            srv(self.menu.increase_count_by)(srv(self.menu.element).app.selected, -1)
            rpc(self.color_liked, srv(self.menu.element).app.selected.id,
                srv(self.menu.element).app.selected.app.color, -1)

        button2.events.add(click=button_click_n, translate=True)

    def color_liked(self, sender_com_id, item_id, color, amount):
        if sender_com_id == self.com.id:
            # button clicked on this session
            self.sdata[color] += int(amount)
            self.com.rpc(self.color_liked, item_id, color, amount)
        else:
            # button clicked by other session
            item = self.menu.id_dict[item_id]
            self.menu.increase_count_by(item, int(amount))

    def color_selected(self, sender_id, color):
        self.tdata['selected color text'] = color

    def build_menu(self):
        # the following function will be used to initialize all menu items
        def on_add(item):
            nonlocal m
            col = item.text
            item.app.color = col
            item.app.clickedcount = self.sdata.get(col, 0)
            m.increase_count_by(item, 0)
            if item.text == self.tdata.get('selected color text', None):
                m.select_color(item)

        # create a menu element with the above item initializer
        m = Menu(self.rdoc, on_add)

        # function to increase the count in front-end

        def menu_sort():
            def srt_func(a, b):
                if a.app.clickedcount < b.app.clickedcount: return -1
                if a.app.clickedcount > b.app.clickedcount: return 1
                return 0
            e = srv(m.element)
            arr = Array.prototype.slice.call(e.children).sort(srt_func)
            for item in arr:
                e.appendChild(item)

        m.sort = self.rdoc.translate(menu_sort)

        def increase_count_by(element, amount):
            element.app.clickedcount += amount
            srv(m.sort)()
            element.textContent = '(' + element.app.clickedcount + ') ' + element.app.color

        m.increase_count_by = self.rdoc.translate(increase_count_by)

        def select_color(element):
            if element.target is not None:
                element = element.target
            element.classList.add('selected')
            if srv(m.element).app.selected and srv(m.element).app.selected!=element:
                srv(m.element).app.selected.classList.remove('selected')
            srv(m.element).app.selected = element
            rpc(self.color_selected, element.app.color)

        m.select_color = self.rdoc.translate(select_color)

        m.element.events.add(click=m.select_color)

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
        m.add_item(*self.sdata.keys())
        m.sort()
        return m

if __name__ == '__main__':
    server.run(ColorsMeteorApp)
