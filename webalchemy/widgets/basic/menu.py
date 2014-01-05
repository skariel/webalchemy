class Menu:

    def __init__(self, rdoc, on_add=None):
        self.rdoc = rdoc
        self.element = rdoc.element('nav')
        vn = '#' + self.element.varname
        self.rule_menu = rdoc.stylesheet.rule(vn)
        self.rule_item = rdoc.stylesheet.rule(vn + ' > li')
        self.rule_item_hover = rdoc.stylesheet.rule(vn + ' > li:hover')
        self.rule_item_selected = rdoc.stylesheet.rule(vn + ' > li.selected')
        self.rule_item_selected_hover = rdoc.stylesheet.rule(vn + ' > li.selected:hover')
        self.on_add = on_add
        self.id_dict = {}

    def add_item(self, *varargs):
        for text in varargs:
            i = self.rdoc.element('li', text)
            self.id_dict[i.att.varname] = i
            self.element.append(i)
            if self.on_add:
                self.on_add(i)
