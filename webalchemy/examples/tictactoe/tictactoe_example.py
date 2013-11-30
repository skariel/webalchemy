#
# a massive multiplayer tictactoe server
#
# This is WIP, no quite working yet...
#

import logging
from tornado import gen

from webalchemy.examples.tictactoe.board import board

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class TickTackToeApp:
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, sessionid, tabid):
        # remember these for later use
        self.rdoc = remotedocument
        self.wsh = wshandler
        log.info('New session opened, id=' + self.wsh.id)

        self.board = board(self.rdoc, 13, 500.0)
        self.rdoc.body.append(self.board.svg)



