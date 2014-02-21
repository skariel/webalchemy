from ...Stacker import StackerWrapper

class BootstrapShortcuts(StackerWrapper):
    '''Stacker wrapper for Bootstrap entities shortcuts

    eg.
    s = Stacker(self.rdoc.body)
    b = BootstrapShortcuts(s)
    h = HtmlShortcuts(s)
    with b.row(), b.col(md=7, md_offset=2), s.panel('info'):
        b.panel_heading('Hello')
        with b.panel_body():
            h.p(text="this is text inside body")                      # note "p" is regular html <p>  using the "HtmlShortcuts"
            b.button(typ='primary', size="lg", block=True, text='Click here')
        b.panel_footer("panel footer here")

    Note: you need to add Bootstrap CSS and (optional) JS
        stylesheets = ['//netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css']
        include = ['//netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js']
    '''

    ###############################################################################
    # "Shortcut" methods for element types

    def container(self, fluid=True, *args, **kwargs):
        '''Center page - see http://getbootstrap.com/css/#overview-container
        Fluid - use percent width
        '''
        return self.stack(typ='div', cls='container-fluid' if fluid else 'container', *args, **kwargs)

    # Grid:  Row and Columns - see http://getbootstrap.com/css/#grid
    def row(self, *args, **kwargs):
        '''Row is composed of 12 grid cells - below Row there should be at least one Column '''
        return self.stack(typ='div', *args, **kwargs)

    def col(self, *args, **kwargs):
        '''Column

        kwargs integers (0..12) for keys of the template:
        [xs|sm|md|lg]_[|offset|pull|push]
        '''
        cls = kwargs.get('cls', '').split()
        for screensize in ('xs', 'sm', 'md', 'lg'):
            for modifier in ('', 'offset', 'pull', 'push'):
                param = "{}_{}".format(screensize, modifier) if modifier else screensize
                if param in kwargs:
                    cls.append('col-{}-{}'.format(param, kwargs[screensize]))
        kwargs['cls'] = cls
        return self.stack(typ='div',  *args, **kwargs)


    def table(self, striped=False, bordered=False, hover=False, condensed=False, *args, **kwargs):
        '''Table - see http://getbootstrap.com/css/#tables'''
        cls = kwargs.get('cls', '').split()
        cls.append('table')
        if striped:
            cls.append('table-striped')
        if bordered:
            cls.append('table-bordered')
        if hover:
            cls.append('table-hover')
        if condensed:
            cls.append('table-condensed')
        kwargs['cls'] = cls
        return self.stack(typ='div',  *args, **kwargs)


    def button(self, typ="button", size="", block=False, active=False, disabled=False, flavor='default', *args, **kwargs):
        '''Bootstrap Button  see http://getbootstrap.com/css/#buttons

          tag can be: a, button, input (input is not recommended)
          flavor can be:  default, primary, success, info, warning, danger, link
          size can be: "lg" (large), "" (default), "sm" (small), "xs" (xtra-small)
          block:  for block level
        '''
        att = {}
        cls = kwargs.get('cls', '').split()
        cls.append("btn")
        cls.append("btn-"+typ)
        if size:
            cls.append("btn-"+size)
        if block:
            cls.append("btn-block")
        if active:
            cls.append("active")
        if disabled:
            cls.append("disabled")
            att["disabled"]="disabled"
        if "att" in kwargs:
            att.update(kwargs["att"])
            del kwargs['att']
        kwargs['cls'] = cls
        return self.stack(typ=typ, att=att, *args, **kwargs)


    def glyphicon(self, icon, *args, **kwargs):
        '''Bootstrap Icon - see http://getbootstrap.com/components/#glyphicons'''
        cls = kwargs.get('cls', '').split()
        cls.append('glyphicon')
        cls.append('glyphicon-{}'.format(icon))
        kwargs['cls'] = cls
        return self.stack(typ='span', *args, **kwargs)

    def alert(self, flavor='danger', dismissable=False, *args, **kwargs):
        '''Alerts - see http://getbootstrap.com/components/#alerts'''
        cls = kwargs.get('cls', '').split()
        cls.append('alert')
        cls.append('alert-{}'.format(flavor))
        if dismissable:
            cls.append('alert-dismissible')
        kwargs['cls'] = cls
        res = self.stack(typ='div', *args, **kwargs)
        if dismissable:
            with res:
                self.stack(typ='button', cls='close', att={'data-dismiss':'alert', 'aria-hidden':'true'}, innerHtml='&times;')
        return res

    def list_group(self, items=[], *args, **kwargs):
        '''Bootstrap List Group - http://getbootstrap.com/components/#list-group

        items (optional) - list of text items
        '''
        cls = kwargs.get('cls', '').split()
        cls.append('list-group')
        kwargs['cls'] = cls
        res = self.stack(typ='ul', *args, **kwargs)
        if items:
            with res:
                for item in items:
                    self.list_group_item(text=item)
        return res

    def list_group_item(self, *args, **kwargs):
        cls = kwargs.get('cls', '').split()
        cls.append('list-group-item')
        kwargs['cls'] = cls
        return self.stack(typ='li', *args, **kwargs)


    def panel(self, flavor="default", *args, **kwargs):
        '''Panel - see http://getbootstrap.com/components/#panels'''
        cls = kwargs.get('cls', '').split()
        cls.append('panel')
        cls.append('panel-{}'.format(flavor))
        kwargs['cls'] = cls
        return self.stack(typ='div', *args, **kwargs)

    def panel_heading(self, *args, **kwargs):
        cls = kwargs.get('cls', '').split()
        cls.append('panel-heading')
        kwargs['cls'] = cls
        return self.stack(typ='div', *args, **kwargs)

    def panel_body(self, *args, **kwargs):
        cls = kwargs.get('cls', '').split()
        cls.append('panel-body')
        kwargs['cls'] = cls
        return self.stack(typ='div', *args, **kwargs)

    def panel_footer(self, *args, **kwargs):
        cls = kwargs.get('cls', '').split()
        cls.append('panel-footer')
        kwargs['cls'] = cls
        return self.stack(typ='div', *args, **kwargs)