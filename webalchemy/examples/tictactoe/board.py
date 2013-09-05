import logging
from itertools import product

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)

class board:
    def __init__(self, rdoc, n):
        self.rdoc= rdoc
        self.n= n
        rdoc.props.title='TicTacToe!'
        self.svg= rdoc.element('svg')
        self.px= 600
        self.svg.att.viewBox='0 0 '+str(self.px)+' '+str(self.px)
        self.dx= self.px/self.n

        self.__create_styles()
        self.__style()
        self.__draw_board()
        self.__set_events()

    def __draw_board(self):
        dx= self.dx
        rng= range(self.n)
        # draw rectangles
        for xi,yi in product(rng,rng):
            r= self.rdoc.element('rect')
            r.att.x= int(dx*xi)
            r.att.y= int(dx*yi)
            r.att.width= dx
            r.att.height= dx
            r.app.xi=xi
            r.app.yi=yi
            r.app.marked=False
            self.svg.append(r)
        # draw vertical lines
        for xi in rng[1:]:
            l= self.rdoc.element('line')
            l.att.x1= l.att.x2= int(dx*xi)
            l.att.y1= str(0)
            l.att.y2= str(self.px)
            self.svg.append(l)
        # draw horizontal lines
        for yi in rng[1:]:
            l= self.rdoc.element('line')
            l.att.y1= l.att.y2= int(dx*yi)
            l.att.x1= 0
            l.att.x2= self.px
            self.svg.append(l)

    def __set_events(self):
        dx= self.dx
        self.rdoc.app.circle_turn=True        
        il= self.rdoc.inline
        self.rdoc.begin_block()
        il('if ((event.target.app.marked)||(!document.app.circle_turn)) return;')
        il('event.target.app.marked=true;')
        il('document.app.circle_turn=false;')
        c= self.rdoc.element('circle')
        c.att.cx=il(str(dx)+'*event.target.app.xi+'+str(dx/2))
        c.att.cy=il(str(dx)+'*event.target.app.yi+'+str(dx/2))
        c.att.r=il(str(dx/2)+'-5')
        self.svg.append(c)
        self.draw_circle= self.rdoc.jsfunction('event')

        self.rdoc.begin_block()
        il('if ((event.target.app.marked)||(document.app.circle_turn)) return;')
        il('event.target.app.marked=true;')
        il('document.app.circle_turn=true;')
        g= self.rdoc.element('g')
        l1= self.rdoc.element('line')
        l1.cls.append('x')
        l1.att.x1=il(str(dx)+'*event.target.app.xi+5')
        l1.att.y1=il(str(dx)+'*event.target.app.yi+5')
        l1.att.x2=il(str(dx)+'*(event.target.app.xi+1.0)-5')
        l1.att.y2=il(str(dx)+'*(event.target.app.yi+1.0)-5')
        g.append(l1)
        l2= self.rdoc.element('line')
        l2.cls.append('x')
        l2.att.x1=il(str(dx)+'*(event.target.app.xi+1.0)-5')
        l2.att.y1=il(str(dx)+'*event.target.app.yi+5')
        l2.att.x2=il(str(dx)+'*event.target.app.xi+5')
        l2.att.y2=il(str(dx)+'*(event.target.app.yi+1.0)-5')
        g.append(l2)
        self.svg.append(g)
        self.draw_x= self.rdoc.jsfunction('event')

        self.svg.events.add(click=self.draw_circle)
        self.svg.events.add(click=self.draw_x)


    def __create_styles(self):
        self.stylesheet= self.rdoc.stylesheet()
        vn= '#'+self.svg.varname
        self.rule_svg= self.stylesheet.rule(vn)
        self.rule_lines= self.stylesheet.rule(vn+' > line',)
        self.rule_rect= self.stylesheet.rule(vn+' > rect')
        self.rule_rect_hover= self.stylesheet.rule(vn+' > rect:hover')
        self.rule_circle= self.stylesheet.rule(vn+' > circle')
        self.rule_circle_hover= self.stylesheet.rule(vn+' > circle:hover')
        self.rule_x= self.stylesheet.rule(vn+' > g > line')
        self.rule_x_hover= self.stylesheet.rule(vn+' > g:hover > line')

    def __style(self):
        self.rule_lines.style(
            stroke='black',
            strokeWidth=3
            )
        self.rule_rect.style(
            fill='white',
            strokeWidth=0,
            webkitTransition='all 0.3s linear',
            )
        self.rule_rect_hover.style(
            fill='rgb(200,200,200)',
            )
        self.rule_circle.style(
            stroke='red',
            fill='white',
            strokeWidth=5,
            webkitTransition='all 0.3s linear',
            )
        self.rule_circle_hover.style(
            strokeWidth=15
            )
        self.rule_x.style(
            stroke='green',
            strokeWidth=5,
            webkitTransition='all 0.3s linear',
            )
        self.rule_x_hover.style(
            stroke='green',
            strokeWidth=15
            )
