from html.parser import HTMLParser


class controller:
    def __init__(self, rdoc):
        self.rdoc = rdoc
        class c:
            pass
        self.e = c()
        self.model = self.rdoc.dict()
        self.viewmodel = self.rdoc.dict()

        self.toggled_class = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'newval', 'i', 'cls', body='''
            if (newval)
                element.classList.add(cls);
            else
                element.classList.remove(cls);
            ''')

        self.toggled_style = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'newval', 'i', 'style_att', 'style_opt', body='''
            if (newval)
                element.style[style_att]=style_opt;
            else
                element.style[style_att]='';
        ''')

        self.repeat_i_in = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'newval', 'i', body='''
            if (typeof element.app.template=='undefined') {
                element.app.template = element.children[0];
                element.removeChild(element.children[0]);
            }

            var ec = element.children;
            var ecl = ec.length;
            var arr = newval;
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
                    (typeof from.app.execute_controller!='undefined')) {
                    to.app.execute_controller = from.app.execute_controller;
                    to.app.oldval = new Array(from.app.oldval.length);
                }
                to.app.i = i;
                to.app.model = model;
                to.app.viewmodel = viewmodel;

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
                    var eid = id+(i+ecl);
                    e.setAttribute('id', eid);
                    e.innerHTML = ih;
                    e.app = {};
                    copy_app_execute_controller(e, te, ecl+i);
                    element.appendChild(e);
                }
            else
                // remove un-needed elements
                for (var i=c; i<0; i++)
                    element.removeChild(ec[ec.length-1]);
        ''')

        self.property = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'newval', 'i', 'prop', body='''
            element[prop] = newval;
        ''')

        self.code = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'newval', 'i', 'code', body='''
            eval(code);
        ''')

        self.ismuttable = self.rdoc.jsfunction('test', body='''return (test && (typeof test == 'object' || typeof test == 'function'))''')

    def execute(self):
        self.rdoc.JS('''
            function crawl_element(e) {
                if ((typeof e!='undefined')&&(typeof e.app!='undefined')) {
                    e.app.model = #{self.model};
                    e.app.viewmodel = #{self.viewmodel};
                    if (typeof e.app.execute_controller!='undefined')
                        for (var j=0, k=e.app.execute_controller, kl=k.length; j<kl; j++)
                            k[j](#{self.viewmodel}, #{self.model}, e, j, e.app.i);
                }
                for (var i=0, ec=e.children, ecl=ec.length; i<ecl; i++)
                    crawl_element(ec[i]);
            }
            crawl_element(document.body);
        ''')

    def bind(self, at, element, code, *varargs):
        if isinstance(code, str):
            fnc = self.rdoc.jsfunction('viewmodel', 'model', 'element', 'i', body='return '+code)
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
            if (typeof #{element}.app.oldval == 'undefined')
                #{element}.app.oldval = [];
            #{element}.app.oldval.push(undefined);
            #{element}.app.model = #{self.model};
            #{element}.app.viewmodel = #{self.viewmodel};
            #{element}.app.execute_controller.push(
                function(viewmodel, model, element, j, i) {
                    var newval = #{fnc}(viewmodel, model, element, i);
                    if ((#{self.ismuttable}(newval)) || (newval != element.app.oldval[j])) {
                        #{whattodo}(viewmodel, model, element, newval, i'''+s+''');
                        element.app.oldval[j] = newval;
                    }
                });
        ''', encapsulate_strings=False)
        # TODO: remove above closure, for performance... maybe just turn the jsfunctions into strings to be embedded?

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
                            #{e}.app.model = #{self.ctrl.model};
                            #{e}.app.viewmodel = #{self.ctrl.viewmodel};
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
