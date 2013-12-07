#
# trying to reconstruct Meteor color application
#

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
        self.selected_color_text = self.tdata.get('selected color text', None)

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
            #rpc{self.color_liked, #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, 1};
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
            #rpc{self.color_liked, #{self.menu.element}.app.selected.id, #{self.menu.element}.app.selected.app.color, -1};
        '''))

    @server.pyrpc
    def color_liked(self, sender_id, item_id, color, amount):
        if sender_id == self.com.id:
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
            if item.text == self.selected_color_text:
                m.select_color(item)

        # create a menu element with the above item initializer
        m = Menu(self.rdoc, on_add)
        # function to increase the count in front-end
        m.sort = self.rdoc.jsfunction(body='''
            e=#{m.element}
            var arr = Array.prototype.slice.call( e.children ).sort(function (a,b) {
                if (a.app.clickedcount < b.app.clickedcount) return -1;
                if (a.app.clickedcount > b.app.clickedcount) return 1;
                return 0;                
            });
            for(i=0;i<arr.length;i++)
                e.appendChild(arr[i])
            ''')
        m.increase_count_by = self.rdoc.jsfunction('element', 'amount', body='''
            element.app.clickedcount+= amount;
            #{m.sort}();
            element.textContent= '('+element.app.clickedcount+') '+element.app.color;
            ''')
        m.select_color = self.rdoc.jsfunction('element', body='''
            element.classList.add('selected');
            if ((#{m.element}.app.selected)&&(#{m.element}.app.selected!=element))
                #{m.element}.app.selected.classList.remove('selected');
            #{m.element}.app.selected= element;
            #rpc{self.color_selected, element.app.color};
            // SYNC HERE INSTEAD OF LINE ABOVE!!!
        ''')
        # TODO: the dsync above
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
        m.add_item(*self.sdata.keys())
        m.sort()
        return m
