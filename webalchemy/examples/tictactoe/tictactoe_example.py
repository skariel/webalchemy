#
# a massive multiplayer tictactoe server
#
import logging
from tornado import gen

from webalchemy.examples.tictactoe.board import board

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)

class tictactoe_app:    

    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler
        log.info('New session opened, id='+self.wsh.id)

        self.div= self.rdoc.element('div')
        self.div.style.width='600px'
        self.div.style.height='600px'
        self.board= board(self.rdoc, 17)
        self.div.append(self.board.svg)
        self.rdoc.body.append(self.div)



