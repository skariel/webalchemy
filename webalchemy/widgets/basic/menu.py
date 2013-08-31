
class menu:
    def __init__(self,rdoc,on_add=None):
        self.rdoc= rdoc
        self.element= rdoc.element('nav')
        vn= '#'+self.element.varname
        self.stylesheet= self.rdoc.stylesheet()
        self.rule_menu= self.stylesheet.rule(vn)
        self.rule_item= self.stylesheet.rule(vn+' > li')
        self.rule_item_hover= self.stylesheet.rule(vn+' > li:hover')
        self.rule_item_selected= self.stylesheet.rule(vn+' > li.selected')
        self.rule_item_selected_hover= self.stylesheet.rule(vn+' > li.selected:hover')
        self.on_add= on_add

    def add_item(self,*varargs):
        for text in varargs:
            i= self.rdoc.element('li',text)
            self.element.append(i)
            if self.on_add:
                self.on_add(i)

