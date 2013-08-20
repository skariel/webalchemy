from webalchemy import remotedocument

class menu:
    def __init__(self,rdoc,):
        self.rdoc= rdoc
        self.element= rdoc.element('nav')

        # styling!
        vn= 'nav.'+self.element.varname
        self.stylesheet= self.rdoc.stylesheet()
        self.rule_nav= self.stylesheet.rule(vn,display='table',margin='10px')
        self.rule_navli= self.stylesheet.rule(vn+' li')
        self.rule_navli.att.style(
            color='#000000',
            fontSize='2em',
            textTransform='uppercase',
            fontFamily='Arial, Verdana, Sans-serif',
            float='bottom',
            padding='10px',
            listStyle='none',
            cursor='pointer',
            webkitTransition='all 0.3s linear'
        )
        self.rule_navlihover= self.stylesheet.rule(vn+' li:hover')
        self.rule_navlihover.att.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
            webkitTransform='rotate(5deg)'
        )

    def add_item(self,*varargs):
        for text in varargs:
            i= self.rdoc.element('li',text)
            self.element.append(i)

