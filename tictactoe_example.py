#
# a massive multiplayer tictactoe server
#
import logging

from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import menu

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)
server.log.setLevel(logging.INFO)

class board:
    def __init__(self, rdoc, n):

        self.rdoc= rdoc
        self.px= 300


        self.svg= rdoc.element('svg')
        self.svg.att.viewBox='0 0 '+str(self.px)+' '+str(self.px)

        self.stylesheet= self.rdoc.stylesheet()
        vn= '#'+self.svg.varname
        self.rule_svg= self.stylesheet.rule(vn,position='absolute')
        self.rule_lines= self.stylesheet.rule(vn+' > line',)
        self.rule_hover= self.stylesheet.rule(vn+' > li:hover')

        dx= int(self.px/n)
        for xi in range(1,n):
            l= self.rdoc.element('line')
            l.att.x1= l.att.x2= str(dx*xi)
            l.att.y1= str(0)
            l.att.y2= str(self.px)
            self.svg.append(l)
        dy= int(self.px/n)
        for yi in range(1,n):
            l= self.rdoc.element('line')
            l.att.y1= l.att.y2= str(dy*yi)
            l.att.x1= str(0)
            l.att.x2= str(self.px)
            self.svg.append(l)


class tictactoe:    

    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler
        log.info('New session openned, id='+self.wsh.id)
        # insert a menu into the page
        self.board= board(self.rdoc, 7)
        self.rdoc.body.append(self.board.svg)



if __name__=='__main__':
    server.run('localhost',8083,tictactoe)
