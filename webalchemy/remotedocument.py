
import re
import inspect
import logging


# logger for internal purposes
log = logging.getLogger(__name__)


# TODO: populate this...
style_atts_requiring_vendor = ['transition', 'transform', 'userSelect', 'animation']


def vendorize(vendor_prefix, item):
    if item == 'float':
        return ['cssFloat']
    if item.startswith('vendor'):
        real_item_cap = item[6:]
        real_item_uncap = real_item_cap[:1].lower() + real_item_cap[1:]
    elif item in style_atts_requiring_vendor:
        real_item_cap = item[0].upper()+item[1:]
        real_item_uncap = item
    else:
        return [item]
    vendorized = [real_item_uncap]
    if vendor_prefix:
        vendorized.append(vendor_prefix+real_item_cap)
    return vendorized


class style_att:

    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self, item, val):
        if isinstance(val, type({})):
            strval='{'
            for k, v in val.items():
                strv = ': '+self.rdoc.stringify(v) + ';\n'
                for ki in vendorize(self.rdoc.vendor_prefix, k):
                    strval += ki
                    strval += strv
            strval += '}'
        else:
            strval = self.rdoc.stringify(val)
        for vi in vendorize(self.rdoc.vendor_prefix, item):
            js = self.varname+'.style["'+vi+'"]='+strval+';\n'
            self.rdoc.inline(js)
            self.d[vi] = val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js = self.varname+'.style["'+item+'"];\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self, item):
        for vi in vendorize(self.rdoc.vendor_prefix, item):
            js = self.varname+'.removeProperty("'+vi+'");\n'
            self.rdoc.inline(js)
            del self.d[vi]

    def __delattr__(self, name):
        del self[name]

    def __call__(self, d=None, **kwargs):
        if d:
            for k, v in d.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v


class class_att:

    def __init__(self, rdoc, varname):
        self.rdoc = rdoc
        self.varname = varname
        self.lst = []

    def append(self, *varargs):
        for name in varargs:
            js= self.varname+'.classList.add("'+name+'");\n'
            self.rdoc.inline(js)
            self.lst.append(name)

    def extend(self, name_list):
        for name in name_list:
            self.append(name)

    def remove(self, *varargs):
        for name in varargs:
            js = self.varname+'.classList.remove("'+name+'");\n'
            self.rdoc.inline(js)
            self.lst.remove(name)

    def replace(self, old_name, new_name):
        self.remove(old_name)
        self.append(new_name)

    def __delitem__(self, name):
        self.remove(name)


class simple_att:

    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self,item,val):
        js= self.varname+'.setAttribute("'+item+'",'+self.rdoc.stringify(val)+');\n'
        self.rdoc.inline(js)
        self.d[item]=val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js= self.varname+'.getAttribute("'+item+'");\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self,item):
        js= self.varname+'.removeAttribute("'+item+'");\n'
        self.rdoc.inline(js)
        del self.d[item]

    def __delattr__(self, name):
        del self[name]

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v


class event_listener:

    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)

    def add(self, **kwargs):
        for event, listener in kwargs.items():
            if hasattr(listener,'varname'):
                l = listener.varname
            elif type(listener) is str:
                l = listener
            else:
                self.rdoc.begin_block()
                l = listener()
                if not l:
                    l = self.rdoc.pop_block()
                    l = 'function(){'+l.rstrip('\n').rstrip(';')+'}'
                else:
                    self.rdoc.cancel_block()

            js = self.varname+'.addEventListener("'+event+'",'+l+',false);\n'
            self.rdoc.inline(js)

    def remove(self,event,listener):
        js = self.varname+'.removeEventListener("'+event+'",'+listener+');\n'
        self.rdoc.inline(js)


class simple_prop:

    def __init__(self, rdoc, varname, namespace):
        super().__setattr__('rdoc', rdoc)
        if namespace:
            super().__setattr__('varname', varname+'.'+namespace)
        else:
            super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self, item, val):
        v= self.rdoc.stringify(val)
        js= self.varname+'["'+item+'"]='+v+';\n'
        self.rdoc.inline(js)
        self.d[item]=val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js= self.varname+'["'+item+'"];\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self, item):
        js = 'delete '+self.varname+'["'+item+'"];\n'
        self.rdoc.inline(js)
        del self.d[item]

    def __delattr__(self, name):
        del self[name]

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v




# List of namespaces
unique_ns= {
    'ww3/svg':'http://www.w3.org/2000/svg',
}

# Namespace in which to create items of type 'typ'
ns_typ_dict= {
    'svg':'ww3/svg',
    'line':'ww3/svg',
    'rect':'ww3/svg',
    'circle':'ww3/svg',
    'ellipse':'ww3/svg',
    'polyline':'ww3/svg',
    'polygon':'ww3/svg',
    'path':'ww3/svg',
    'g':'ww3/svg',
}

# additional attributes that elements of type 'typ' should have
add_attr_typ_dict = {
    'svg': {'xmlns': 'http://www.w3.org/2000/svg'},
}


class element:

    def __init__(self, rdoc, typ, text=None):
        self.varname = rdoc.get_new_uid()
        self.rdoc = rdoc
        self.typ = typ
        self.parent = None
        self.childs = []
        global ns_typ_dict
        if typ in ns_typ_dict:
            ns = unique_ns[ns_typ_dict[typ]]
            js = self.varname+'=document.createElementNS("'+ns+'","'+typ+'");\n'
        else:
            js = self.varname+'=document.createElement("'+typ+'");\n'
        js += self.varname+'.app={};\n'
        if text is not None:
            self._text = text
            js += self.varname+'.textContent="'+text+'";\n'
        else:
            self._text = ''
        rdoc.inline(js)

        self.cls = class_att(rdoc, self.varname)
        self.att = simple_att(rdoc, self.varname)
        self.style = style_att(rdoc, self.varname)
        self.events = event_listener(rdoc, self.varname)
        self.app = simple_prop(rdoc, self.varname, 'app')
        self.att.id = self.varname
        self.cls.append(self.varname)

        if typ in add_attr_typ_dict:
            self.att(**add_attr_typ_dict[typ])

    def remove(self):
        s = self.varname+'.parentNode.removeChild('+self.varname+');\n'
        self.rdoc.inline(s)
        self.parent.childs.remove(self)
        self.parent = None

    def append(self, e):
        self.childs.append(e)
        e.parent = self
        s = self.varname+'.appendChild('+e.varname+');\n'
        self.rdoc.inline(s)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self.set_text(text)

    def set_text(self, text, transmit=True):
        self._text = text
        if transmit:
            js = self.varname+'.textContent="'+text+'";\n'
            self.rdoc.inline(js)

    def __str__(self):
        return self.varname

    def element(self, typ, txt=None):
        e = self.rdoc.element(typ, txt)
        self.append(e)
        return e
    

def inline(code, level=1):
    # inline interpolation...
    prev_frame = inspect.getouterframes(inspect.currentframe())[level][0]
    locals = prev_frame.f_locals
    globals = prev_frame.f_globals
    for item in re.findall(r'#\{([^}]*)\}', code):
        rep = eval(item, globals, locals)
        if hasattr(rep,'varname'):
            rep = rep.varname
        else:
            rep = str(rep)
        code = code.replace('#{%s}' % item, rep)
    return code


class interval:

    def __init__(self, rdoc, ms, exp=None, level=2):
        self.rdoc = rdoc
        self.varname = rdoc.get_new_uid()
        self.ms = ms
        self.is_running = True
        code = self.rdoc.stringify(exp, pop_line=False)
        code = inline(code, level=level)
        if not callable(exp):
            code = 'function(){'+code+'}'
        js = self.varname+'=setInterval('+code+','+str(ms)+');\n'
        rdoc.inline(js)

    def stop(self):
        self.is_running = False
        js = 'clearInterval('+self.varname+');\n'
        self.rdoc.inline(js)


class jsfunction:

    def __init__(self, rdoc, *varargs, body=None, level=2):
        self.rdoc = rdoc
        self.varname = rdoc.get_new_uid()
        code = self.rdoc.stringify(body, encapsulate_strings=False, pop_line=False)
        code = inline(code, level=level)
        code = code.rstrip(';\n')
        args = ','.join(varargs)
        self.js = self.varname+'=function('+args+'){\n'+code+'\n}\n'
        rdoc.inline(self.js)

    def __call__(self, *varargs):
        js = self.varname+'('+','.join([str(v) for v in varargs])+');\n'
        self.rdoc.inline(js)

    def __str__(self):
        return self.varname+'();\n'


class stylesheet:

    def __init__(self, rdoc):
        self.rdoc = rdoc
        self.element = rdoc.element('style')
        self.varname = self.element.varname
        self.element.att.type = 'text/css'
        self.rdoc.body.append(self.element)
        js = self.varname+'=document.styleSheets[0];\n'
        self.rdoc.inline(js)

    def rule(self, selector, **kwargs):
        return rule(self, selector, **kwargs)


class rule:

    def __init__(self, stylesheet, selector, **kwargs):
        if selector.split()[0] == '@keyframes' and stylesheet.rdoc.vendor_prefix == 'webkit':
            selector= '@-webkit-'+selector[1:]
        self.stylesheet = stylesheet
        self.rdoc = self.stylesheet.rdoc
        self.varname = self.rdoc.get_new_uid()
        self.selector = selector
        # TODO: what if we want to change the selector?!
        ssn = self.stylesheet.varname
        js = ssn+'.insertRule("'+selector+'{}",'+ssn+'.cssRules.length);\n'
        js += self.varname+'='+ssn+'.cssRules['+ssn+'.cssRules.length-1];\n'
        self.rdoc.inline(js)
        self.style = style_att(self.rdoc, self.varname)
        self.style(**kwargs)


class remotedocument:
    def __init__(self):
        self.varname='document'
        self.__uid_count = 0
        self.__code_strings = []
        self.__block_ixs = []
        self.__varname_element_dict = {}
        self.body = self.element('body', '')
        self.body.varname = 'document.body'
        self.pop_all_code() # body is special, it's created by static content
        self.inline('document.app={};\n')
        self.app = simple_prop(self, 'document', 'app')
        self.props = simple_prop(self, 'document', None)
        self.stylesheet = stylesheet(self)
        self.vendor_prefix = None

    def set_vendor_prefix(self, vendor_prefix):
        self.vendor_prefix = vendor_prefix

    def get_element_from_varname(self, varname) -> element:
        return self.__varname_element_dict[varname]

    def element(self, typ, text=None):
        e = element(self, typ, text)
        self.__varname_element_dict[e.varname] = e
        return e

    def startinterval(self, ms, exp=None):
        return interval(self, ms, exp, level=3)

    def jsfunction(self, *varargs, body=None):
        return jsfunction(self, *varargs, body=body, level=3)

    def get_new_uid(self):
        uid = '__v'+str(self.__uid_count)
        self.__uid_count += 1
        return uid

    def begin_block(self):
        self.__block_ixs.append(len(self.__code_strings))

    def cancel_block(self):
        self.__block_ixs.pop()

    def pop_block(self):
        ix = self.__block_ixs.pop()
        code = ''
        for i in range(len(self.__code_strings)-ix):
            code = self.__code_strings.pop()+code
        return code

    def pop_all_code(self):
        code= ''.join(self.__code_strings)
        self.__code_strings.clear()
        self.__block_ixs.clear()
        return code

    def pop_line(self):
        return self.__code_strings.pop()

    def inline(self, text, *varargs):
        '''
        insert a code block (contained in 'text' parameter)
        '''
        if varargs:
            text = text.format(*(v.varname for v in varargs))
        self.__code_strings.append(text)

    def rawjs(self, js):
        return rawjs(js)

    def msg(self, text):
        self.inline('message("'+text+'");')

    def stylesheet(self):
        return stylesheet(self)

    def stringify(self, val=None, custom_stringify=None, encapsulate_strings=True, pop_line=True):
        if type(val) is bool:
            if val:
                return 'true'
            else:
                return 'false'
        if hasattr(val, 'varname'):
            return val.varname
        if type(val) is str:
            if encapsulate_strings:
                return '"'+str(val)+'"'
            return val
        if callable(val):
            self.begin_block()
            tmp = val()
            if tmp:
                self.cancel_block()
            else:
                tmp = self.pop_block()
            return 'function(){'+tmp+'}'                
        if val is None:
            if pop_line:
                return self.pop_line()
            return self.pop_block()
        if custom_stringify:
            return custom_stringify(val)
        return str(val)




