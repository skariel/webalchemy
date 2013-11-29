#
# a massive multiplayer tictactoe server
#
import logging
from tornado import gen

from webalchemy.examples.tictactoe.board import board
from webalchemy.widgets.basic.menu import menu

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)

class tictactoe_app:    

    @gen.coroutine
    def initialize(self, remotedocument, wshandler, sessionid, tabid):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler
        log.info('New session opened, id='+self.wsh.id)

        self.board= board(self.rdoc, 13, 500.0)
        self.rdoc.body.append(self.board.svg)



