#
# a massive multiplayer tictactoe server
#
import logging
from itertools import product

from tornado import gen
from webalchemy import server

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)
server.log.setLevel(logging.INFO)

class board:
    def __init__(self, rdoc, n):

        self.rdoc= rdoc
        self.px= 600

        self.svg= rdoc.element('svg')
        self.svg.att.viewBox='0 0 '+str(self.px)+' '+str(self.px)

        self.stylesheet= self.rdoc.stylesheet()
        vn= '#'+self.svg.varname
        self.rule_svg= self.stylesheet.rule(vn)#,position='absolute')
        self.rule_lines= self.stylesheet.rule(vn+' > line',)
        self.rule_rect= self.stylesheet.rule(vn+' > rect')
        self.rule_rect_hover= self.stylesheet.rule(vn+' > rect:hover')

        self.rule_lines.style(
            stroke='black',
            strokeWidth=1
            )
        self.rule_rect.style(
            fill='rgb(255,0,0)',
            strokeWidth=0,
            webkitTransition='all 0.3s linear',
            )
        self.rule_rect_hover.style(
            fill='rgb(0,255,0)',
            )

        dx= self.px/n
        rng= range(n)
        # draw rectangles
        for xi,yi in product(rng,rng):
            r= self.rdoc.element('rect')
            r.att.x= str(int(dx*xi))
            r.att.y= str(int(dx*yi))
            r.att.width= dx
            r.att.height= dx
            self.svg.append(r)
        # draw vertical lines
        for xi in rng[1:]:
            l= self.rdoc.element('line')
            l.att.x1= l.att.x2= str(int(dx*xi))
            l.att.y1= str(0)
            l.att.y2= str(self.px)
            self.svg.append(l)
        # draw horizontal lines
        for yi in rng[1:]:
            l= self.rdoc.element('line')
            l.att.y1= l.att.y2= str(int(dx*yi))
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

        self.div= self.rdoc.element('div')
        self.div.style.width='200px'
        self.div.style.height='200px'
        self.board= board(self.rdoc, 7)
        self.div.append(self.board.svg)
        self.rdoc.body.append(self.div)



if __name__=='__main__':
    server.run('localhost',8083,tictactoe)
