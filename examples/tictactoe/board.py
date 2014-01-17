import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class board:
    def __init__(self, rdoc, n, px):
        self.rdoc = rdoc
        self.n = n
        rdoc.props.title = 'TicTacToe!'
        self.svg = rdoc.element('svg')
        self.px = px
        self.dx = self.px / self.n
        self.svg.app.actual_cursorx = 0
        self.svg.app.actual_cursory = 0
        self.svg.app.cursorx_index = 0
        self.svg.app.cursory_index = 0
        self.svg.app.n = self.n
        self.svg.app.checked = {}
        self.svg.att.width = px
        self.svg.att.height = px

        self.__create_styles()
        self.__style()
        self.__draw_board()
        self.__set_events()

    def __draw_board(self):
        dx = self.dx
        rng = range(self.n)
        # draw vertical lines
        for xi in rng[1:]:
            l = self.rdoc.element('line')
            l.att.x1 = l.att.x2 = dx * xi
            l.att.y1 = 0
            l.att.y2 = self.px
            self.svg.append(l)
            # draw horizontal lines
        for yi in rng[1:]:
            l = self.rdoc.element('line')
            l.att.y1 = l.att.y2 = dx * yi
            l.att.x1 = 0
            l.att.x2 = self.px
            self.svg.append(l)
            # draw cursor
        self.cursor = self.rdoc.element('rect')
        self.cursor.att.x = 0
        self.cursor.att.y = 0
        self.cursor.att.width = dx
        self.cursor.att.height = dx
        self.svg.append(self.cursor)

    def __set_events(self):
        self.mouse_move_event_handler = self.rdoc.jsfunction('e', body='''
            var mx= e.pageX-#{self.svg}.offsetLeft;
            var my= e.pageY-#{self.svg}.offsetTop;
            #{self.svg}.app.cursorx_index= ~~ (mx / #{self.dx});
            #{self.svg}.app.cursory_index= ~~ (my / #{self.dx});
            ''')
        self.svg.events.add(mousemove=self.mouse_move_event_handler)
        self.update_cursor_position = self.rdoc.jsfunction(body='''
            var truncated_cursorx= #{self.svg}.app.cursorx_index*#{self.dx};
            var truncated_cursory= #{self.svg}.app.cursory_index*#{self.dx};
            var dx= (truncated_cursorx - #{self.svg}.app.actual_cursorx) / 3.0;
            if ((dx>0.01)||(dx<-0.01)) {
                #{self.svg}.app.actual_cursorx+= dx;
                #{self.cursor}.setAttribute('x',#{self.svg}.app.actual_cursorx)
            }
            var dy= (truncated_cursory - #{self.svg}.app.actual_cursory) / 3.0;
            if ((dy>0.01)||(dy<-0.01)) {
                #{self.svg}.app.actual_cursory+= dy;
                #{self.cursor}.setAttribute('y',#{self.svg}.app.actual_cursory)
            }
            ''')
        self.rdoc.startinterval(20, self.update_cursor_position)

        dx = self.dx
        il = self.rdoc.inline
        self.rdoc.begin_block()
        il('var inx= #{self.svg}.app.cursory_index*#{self.svg}.app.n+#{self.svg}.app.cursorx_index;')
        il('if (inx in #{self.svg}.app.checked) return;')
        il('#{self.svg}.app.checked[inx]="o";')
        c = self.rdoc.element('circle')
        c.att.cx = il('#{self.svg}.app.cursorx_index*#{self.dx}+' + str(dx / 2))
        c.att.cy = il('#{self.svg}.app.cursory_index*#{self.dx}+' + str(dx / 2))
        c.att.r = il(str(dx / 2) + '-9')
        self.svg.append(c)
        self.draw_circle = self.rdoc.jsfunction('event')
        self.svg.events.add(click=self.draw_circle)

        self.rdoc.begin_block()
        il('var inx= #{self.svg}.app.cursory_index*#{self.svg}.app.n+#{self.svg}.app.cursorx_index;')
        il('if (inx in #{self.svg}.app.checked) return;')
        il('#{self.svg}.app.checked[inx]="x";')
        g = self.rdoc.element('g')
        l1 = self.rdoc.element('line')
        l1.cls.append('x')
        il('var xl= #{self.svg}.app.cursorx_index*#{self.dx}+7;')
        il('var xr= xl+#{self.dx}-14;')
        il('var yt= #{self.svg}.app.cursory_index*#{self.dx}+7;')
        il('var yb= yt+#{self.dx}-14;')
        l1.att.x1 = il('xl')
        l1.att.y1 = il('yt')
        l1.att.x2 = il('xr')
        l1.att.y2 = il('yb')
        g.append(l1)
        l2 = self.rdoc.element('line')
        l2.cls.append('x')
        l2.att.x1 = il('xr')
        l2.att.y1 = il('yt')
        l2.att.x2 = il('xl')
        l2.att.y2 = il('yb')
        g.append(l2)
        self.svg.append(g)
        self.draw_x = self.rdoc.jsfunction('event')
        self.svg.events.add(click=self.draw_x)

    def __create_styles(self):
        self.stylesheet = self.rdoc.stylesheet
        vn = '#' + self.svg.varname
        self.rule_svg = self.stylesheet.rule(vn)
        self.rule_lines = self.stylesheet.rule(vn + ' > line')
        self.rule_rect = self.stylesheet.rule(vn + ' > rect')
        self.rule_circle = self.stylesheet.rule(vn + ' > circle')
        self.rule_circle_hover = self.stylesheet.rule(vn + ' > circle:hover')
        self.rule_x = self.stylesheet.rule(vn + ' > g > line')
        self.rule_x_hover = self.stylesheet.rule(vn + ' > g:hover > line')

    def __style(self):
        self.rule_lines.style(
            stroke='black',
            strokeWidth=3
        )
        self.rule_rect.style(
            fill='grey',
            fillOpacity=0.8,
            strokeWidth=0,
        )
        self.rule_circle.style(
            stroke='red',
            fillOpacity=0.0,
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
