#
# trying to reconstruct Meteor color application
#
import logging

from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import menu

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)
server.log.setLevel(logging.INFO)

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
        log.info('New session openned, id='+self.wsh.id)
        # insert a menu into the page
        self.menu= self.build_menu()
        self.rdoc.body.append(self.menu.element)

    # register the method so we can call it from frontend js,
    # and then also from other sessions (from Python)
    @server.jsrpc
    @server.pyrpc
    @gen.coroutine
    def button_clicked(self, sender_id, item_id, color):
        if sender_id==self.wsh.id:
            # button clicked on this session
            colors_app.colors_count[color]+= 1
            self.wsh.rpc(self.button_clicked, item_id, color)
        else:
            # button clicked by other session
            log.info('got an update...')
            item= self.menu.id_dict[item_id]
            self.menu.increase_count_by(item, 1)

    def build_menu(self):
        # the following function will be used to initialize all menu items
        def on_add(item):
            nonlocal m
            color= item.text
            item.att.app.color= color
            item.att.app.clickedcount= colors_app.colors_count[color]
            # note below inline interpolation and rpc call
            item.att.onclick= self.rdoc.jsfunction('event','''
                rpc('button_clicked', event.target.id, event.target.app.color);
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
                element.textContent= '('+element.app.clickedcount+') '+element.app.color;
            }''')
        # populate the menu with shared colors dict
        for color in colors_app.colors_count:
            m.add_item(color)
        return m



if __name__=='__main__':
    server.run('localhost',8083,colors_app)
