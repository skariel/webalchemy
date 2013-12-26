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

        self.repeat_i_in = self.rdoc.jsfunction('model', 'element', 'fnc', body='''
            if (typeof element.app.template=='undefined') {
                element.app.template = element.children[0];
                element.removeChild(element.children[0]);
            }

            var ec = element.children;
            var ecl = ec.length;
            var arr = fnc(model, element);
            var arrl = arr.length;
            var c = arrl-ecl;
            var te = element.app.template;
            var tag = te.tagName;
            var ih = te.innerHTML;
            var app = te.app;
            var eid = String(element.getAttribute('id'));
            var tid = String(te.getAttribute('id'));
            var id = eid+'_'+tid+'_';
            function copy_app_execute_controller(to, from, i) {
                if (typeof to.app=='undefined')
                    to.app = {};
                if ((typeof from.app!='undefined')&&
                    (typeof from.app.execute_controller!='undefined'))
                    to.app.execute_controller = from.app.execute_controller;
                to.app.model = model;
                to.app.i = i;

                var fc = from.children;
                if (typeof fc=='undefined')
                    return;
                var tc = to.children;
                var l = tc.length;
                for (var ci=0; ci<l; ci++)
                    copy_app_execute_controller(tc[ci], fc[ci], i)
            }
            if (c>0)
                // add new elements
                for (var i=0; i<c; i++) {
                    var e = te.cloneNode(true);
                    var eid = id+i;
                    e.setAttribute('id', eid);
                    e.innerHTML = ih;
                    e.app = {};
                    copy_app_execute_controller(e, te, ecl+i);
                    element.appendChild(e);
                }
            else
                // remove un-needed elements
                for (var i=c; i<0; i++) {
                    console.log('removing...')
                    element.removeChild(element.children[element.children.length-1]);
                    console.log('removed!')
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
                    for (var j=0; k=a[i].app.execute_controller.length, j<k; j++)
                        a[i].app.execute_controller[j](#{self.model}, a[i]);
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
            if (typeof #{element}.app.execute_controller == 'undefined')
                #{element}.app.execute_controller = [];
            if (typeof #{element}.app.model == 'undefined')
                #{element}.app.model = #{self.model};
            #{element}.app.execute_controller.push(
                function(model, element) {
                    #{whattodo}(model, element, #{fnc}'''+s+''');
                });
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
                        self.ctrl.rdoc.JS('''
                            if (typeof #{e}.app=='undefined')
                                #{e}.app = {};
                            if (typeof #{e}.app.model=='undefined')
                                #{e}.app.model = #{self.ctrl.model};
                        ''')
                        setattr(self.ctrl.e, eid.replace('-', '_').strip().replace(' ', '_'), e)
                    elif attr[0].startswith('weba-'):
                        at = attr[0][5:]
                        v = attr[1]
                        s = v.split(',')
                        c = s[-1]
                        v = [l.strip() for l in s[:-1]]
                        self.ctrl.bind(at, e, c, *v)

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
