from html.parser import HTMLParser


class controller:
    def __init__(self, rdoc):
        self.rdoc = rdoc
        class c:
            pass
        self.e = c()
        self.model = self.rdoc.dict()

        self.toggled_class = self.rdoc.jsfunction('model', 'element', 'fnc', 'cls', body='''
            if (fnc(model, element))
                element.classList.add(cls);
            else
                element.classList.remove(cls);
            ''')

        self.toggled_style = self.rdoc.jsfunction('model', 'element', 'fnc', 'style_att', 'style_opt', body='''
            if (fnc(model, element))
                element.style[style_att]=style_opt;
            else
                element.style[style_att]='';
        ''')

        self.repeat_child_for_i_in_range = self.rdoc.jsfunction('model', 'element', 'fnc', body='''
            if (typeof element.app.template=='undefined')
                element.app.template = element.children[0];
            c = (fnc(model, element)-element.children.length);
            te = element.app.template;
            tag = te.tagName;
            ih = te.innerHTML;
            for (var i=0; i<c; i++) {
                e = document.createElement(tag);
                e.innerHTML = ih;
                element.appendChild(e);
            }
        ''')

        self.property = self.rdoc.jsfunction('model', 'element', 'fnc', 'prop', body='''
            element[prop]=fnc(model, element);
        ''')

    def execute(self):
        self.rdoc.JS('''
            for (var i=0, a=document.all, c=a.length; i<c; i++)
                if ((typeof a[i]!='undefined')&&(typeof a[i].app!='undefined')&&
                (typeof a[i].app.execute_controller!='undefined'))
                    a[i].app.execute_controller();
        ''')

    def bind(self, at, element, code, *varargs):
        if isinstance(code, str):
            fnc = self.rdoc.jsfunction('model', 'element', body='return '+code)
        else:
            fnc = code
        whattodo = getattr(self, at)
        params = ','.join(varargs)
        s = '#{params}'
        if params:
            s = ',' + s
        self.rdoc.JS('''
            if (typeof #{element}.app == 'undefined')
                #{element}.app = {};
            #{element}.app.execute_controller = function(model, element) {
                #{whattodo}(self.model, element, #{fnc}'''+s+''');
            }
        ''', encapsulate_strings=False)

    def bind_html(self, html):
        class MyHTMLParser(HTMLParser):
            def __init__(self, ctrl):
                super().__init__()
                self.ctrl = ctrl

            def handle_starttag(self, tag, attrs):
                for attr in attrs:
                    if attr[0] == 'id':
                        eid = attr[1]
                        e = self.ctrl.rdoc.getElementById(eid)
                        setattr(self.ctrl.e, eid.replace('-', '_').strip().replace(' ', '_'), e)
                        for att in attrs:
                            if att[0].startswith('weba-'):
                                at = att[0][5:]
                                v = att[1]
                                s = v.split(',')
                                c = s[-1]
                                v = [l.strip() for l in s[:-1]]
                                self.ctrl.bind(at, e, c, *v)
                        break
        parser = MyHTMLParser(self)
        parser.feed(html)

    def call_on_request_frame(self):
        js = ''
        if hasattr(self, 'prerender'):
            js = '#{self.prerender}();\n'
        js += '''
            #{js_execute}();
            window.requestAnimationFrame(#{self.rdoc.jsfunctions_being_built[-1]});
        '''
        js_execute = self.rdoc.jsfunction(self.execute)
        fnc = self.rdoc.jsfunction(js, call=True)
