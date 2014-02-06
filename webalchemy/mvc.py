from html.parser import HTMLParser


class controller:
    def __init__(self, rdoc, html, m=None, vm=None, prerender=None, run=True):
        self.rdoc = rdoc
        class c:
            pass
        self.e = c()
        self.model = m or self.rdoc.dict()
        self.viewmodel = vm or self.rdoc.dict()
        self.prerender = prerender

        self.cls = self.rdoc.jsfunction('vm', 'm', 'e', 'newval', 'i', 'cls', body='''
            if (newval)
                e.classList.add(cls);
            else
                e.classList.remove(cls);
            ''')

        self.style = self.rdoc.jsfunction('vm', 'm', 'e', 'newval', 'i', 'style_att', 'style_opt', body='''
            if (newval)
                e.style[style_att]=style_opt;
            else
                e.style[style_att]='';
        ''')

        self.repeat = self.rdoc.jsfunction('vm', 'm', 'e', 'newval', 'i', body='''
            if (typeof e.app.template=='undefined') {
                e.app.template = e.children[0];
                e.removeChild(e.children[0]);
            }

            var ec = e.children;
            var ecl = ec.length;
            var arr = newval;
            var arrl = arr.length;
            var c = arrl-ecl;
            var te = e.app.template;
            var tag = te.tagName;
            var ih = te.innerHTML;
            var app = te.app;
            var eid = String(e.getAttribute('id'));
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
                to.app.m = m;
                to.app.vm = vm;

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
                    var ee = te.cloneNode(true);
                    var eid = id+(i+ecl);
                    ee.setAttribute('id', eid);
                    ee.innerHTML = ih;
                    ee.app = {};
                    copy_app_execute_controller(ee, te, ecl+i);
                    e.appendChild(ee);
                }
            else
                // remove un-needed elements
                for (var i=c; i<0; i++)
                    e.removeChild(ec[ec.length-1]);
        ''')

        self.property = self.rdoc.jsfunction('vw', 'm', 'e', 'newval', 'i', 'prop', body='''
            e[prop] = newval;
        ''')

        self.code = self.rdoc.jsfunction('vm', 'm', 'e', 'newval', 'i', 'code', body='''
            eval(code);
        ''')

        self.ismuttable = self.rdoc.jsfunction('test', body='''return (test && (typeof test == 'object' || typeof test == 'function'))''')

        self.bind_html(html)

        if run:
            self.call_on_request_frame()

    def execute(self):
        self.rdoc.JS('''
            function crawl_element(e) {
                if ((typeof e!='undefined')&&(typeof e.app!='undefined')) {
                    e.app.m = #{self.model};
                    e.app.vm = #{self.viewmodel};
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
            fnc = self.rdoc.jsfunction('vm', 'm', 'e', 'i', body='return '+code)
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
            #{element}.app.m = #{self.model};
            #{element}.app.vm = #{self.viewmodel};
            #{element}.app.execute_controller.push(
                function(vm, m, e, j, i) {
                    var newval = #{fnc}(vm, m, e, i);
                    if ((#{self.ismuttable}(newval)) || (newval != e.app.oldval[j])) {
                        #{whattodo}(vm, m, e, newval, i'''+s+''');
                        e.app.oldval[j] = newval;
                    }
                });
        ''', encapsulate_strings=False)
        # TODO: remove above closure, for performance... maybe just turn the jsfunctions into strings to be embedded?

    def bind_html(self, html):
        class MyHTMLParser(HTMLParser):
            def __init__(self, ctrl):
                super().__init__()
                self.ctrl = ctrl
                self.tagdict = {}

            def handle_starttag(self, tag, attrs):
                if tag in self.tagdict:
                    self.tagdict[tag] += 1
                else:
                    self.tagdict[tag] = 0
                e = self.ctrl.rdoc.element(tag)
                self.ctrl.rdoc.JS('#{e} = document.getElementsByTagName(#{tag})['+str(self.tagdict[tag])+']')
                self.ctrl.rdoc.JS('''
                    if (typeof #{e}.app=='undefined')
                        #{e}.app = {};
                    #{e}.app.m = #{self.ctrl.model};
                    #{e}.app.vm = #{self.ctrl.viewmodel};
                ''')
                for attr in attrs:
                    if attr[0] == 'id':
                        eid = attr[1]
                        setattr(self.ctrl.e, eid.replace('-', '_').strip().replace(' ', '_'), e)
                    elif attr[0].startswith('weba-'):
                        at = attr[0][5:]
                        fv = attr[1]
                        for v in fv.split(':&:'):
                            s = v.split('::')
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
            window.requestAnimationFrame(__recursive__);
        '''
        js_execute = self.rdoc.jsfunction(self.execute)
        fnc = self.rdoc.jsfunction(js, call=True, recursive=True)
