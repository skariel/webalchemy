import re
import random
import inspect
import logging
from webalchemy.saferef import safeRef


# logger for internal purposes
log = logging.getLogger(__name__)


class StyleAtt:
    # TODO: populate this...
    _style_atts_requiring_vendor = {'transition', 'transform', 'userSelect', 'animation'}

    @staticmethod
    def _vendorize(vendor_prefix, item):
        if item == 'float':
            return ['cssFloat']
        if item.startswith('vendor'):
            real_item_cap = item[6:]
            real_item_uncap = real_item_cap[:1].lower() + real_item_cap[1:]
        elif item in StyleAtt._style_atts_requiring_vendor:
            real_item_cap = item[0].upper() + item[1:]
            real_item_uncap = item
        else:
            return [item]
        vendorized = [real_item_uncap]
        if vendor_prefix:
            vendorized.append(vendor_prefix + real_item_cap)
        return vendorized

    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self, item, val):
        if isinstance(val, type({})):
            strval = '"{'
            for k, v in val.items():
                strv = ': ' + self.rdoc.stringify(v, encapsulate_strings=False) + ';\n'
                for ki in StyleAtt._vendorize(self.rdoc.vendor_prefix, k):
                    strval += ki
                    strval += strv
            strval += '}"'
        else:
            strval = self.rdoc.stringify(val)
        for vi in StyleAtt._vendorize(self.rdoc.vendor_prefix, item):
            js = self.varname + '.style["' + vi + '"]=' + strval + ';\n'
            self.rdoc.inline(js)
            self.d[vi] = val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js = self.varname + '.style["' + item + '"];\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self, item):
        for vi in StyleAtt._vendorize(self.rdoc.vendor_prefix, item):
            js = self.varname + '.style.removeProperty("' + vi + '");\n'
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


class ClassAtt:
    def __init__(self, rdoc, varname):
        self.rdoc = rdoc
        self.varname = varname
        self.lst = []

    def append(self, *varargs):
        for name in varargs:
            js = self.varname + '.classList.add("' + name + '");\n'
            self.rdoc.inline(js)
            self.lst.append(name)

    def extend(self, name_list):
        for name in name_list:
            self.append(name)

    def remove(self, *varargs):
        for name in varargs:
            js = self.varname + '.classList.remove("' + name + '");\n'
            self.rdoc.inline(js)
            self.lst.remove(name)

    def replace(self, old_name, new_name):
        self.remove(old_name)
        self.append(new_name)

    def __delitem__(self, name):
        self.remove(name)


class SimpleAtt:
    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self, item, val):
        js = self.varname + '.setAttribute("' + item + '",' + self.rdoc.stringify(val) + ');\n'
        self.rdoc.inline(js)
        self.d[item] = val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js = self.varname + '.getAttribute("' + item + '");\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self, item):
        js = self.varname + '.removeAttribute("' + item + '");\n'
        self.rdoc.inline(js)
        del self.d[item]

    def __delattr__(self, name):
        del self[name]

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v


class EventListener:
    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)

    def add(self, **kwargs):
        for event, listener in kwargs.items():
            if hasattr(listener, 'varname'):
                l = listener.varname
            elif type(listener) is str:
                l = listener
            else:
                self.rdoc.begin_block()
                l = listener()
                if not l:
                    l = self.rdoc.pop_block()
                    l = 'function(){' + l.rstrip('\n').rstrip(';') + '}'
                else:
                    self.rdoc.cancel_block()

            js = self.varname + '.addEventListener("' + event + '",' + l + ',false);\n'
            self.rdoc.inline(js)

    def remove(self, event, listener):
        js = self.varname + '.removeEventListener("' + event + '",' + listener + ');\n'
        self.rdoc.inline(js)


class SimpleProp:
    def __init__(self, rdoc, varname, namespace):
        super().__setattr__('rdoc', rdoc)
        if namespace:
            super().__setattr__('varname', varname + '.' + namespace)
        else:
            super().__setattr__('varname', varname)
        super().__setattr__('d', {})

    def __setitem__(self, item, val):
        v = self.rdoc.stringify(val)
        js = self.varname + '["' + item + '"]=' + v + ';\n'
        self.rdoc.inline(js)
        self.d[item] = val

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getitem__(self, item):
        js = self.varname + '["' + item + '"];\n'
        self.rdoc.inline(js)
        return self.d[item]

    def __getattr__(self, name):
        return self[name]

    def __delitem__(self, item):
        js = 'delete ' + self.varname + '["' + item + '"];\n'
        self.rdoc.inline(js)
        del self.d[item]

    def __delattr__(self, name):
        del self[name]

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v


class Element:
    # Namespace in which to create items of type 'typ'
    # this is good to handle SVGs, etc.
    _ns_typ_dict = {
        'svg': 'ww3/svg',
        'line': 'ww3/svg',
        'rect': 'ww3/svg',
        'circle': 'ww3/svg',
        'ellipse': 'ww3/svg',
        'polyline': 'ww3/svg',
        'polygon': 'ww3/svg',
        'path': 'ww3/svg',
        'g': 'ww3/svg',
    }

    # List of namespaces
    _unique_ns = {
        'ww3/svg': 'http://www.w3.org/2000/svg',
    }

    # additional attributes that elements of type 'typ' should have
    _add_attr_typ_dict = {
        'svg': {'xmlns': 'http://www.w3.org/2000/svg'},
    }

    def __init__(self, rdoc, typ=None, text=None, customvarname=None, fromid=None):
        if not customvarname:
            self.varname = rdoc.get_new_uid()
        else:
            self.varname = customvarname
        self.rdoc = rdoc
        self.typ = typ
        self.parent = None
        self.childs = []
        if not fromid:
            if typ in Element._ns_typ_dict:
                ns = Element._unique_ns[Element._ns_typ_dict[typ]]
                js = self.varname + '=document.createElementNS("' + ns + '","' + typ + '");\n'
            else:
                js = self.varname + '=document.createElement("' + typ + '");\n'
        else:
            js = self.varname + '=document.getElementById("' + fromid + '");\n'
        js += self.varname + '.app={};\n'
        if text is not None:
            self._text = text
            js += self.varname + '.textContent="' + text + '";\n'
        else:
            self._text = ''
        rdoc.inline(js)

        self.cls = ClassAtt(rdoc, self.varname)
        self.att = SimpleAtt(rdoc, self.varname)
        self.style = StyleAtt(rdoc, self.varname)
        self.events = EventListener(rdoc, self.varname)
        self.app = SimpleProp(rdoc, self.varname, 'app')
        self.att.id = self.varname
        self.cls.append(self.varname)
        self.prop = SimpleProp(self.rdoc, self.varname, None)

        if typ in Element._add_attr_typ_dict:
            self.att(**Element._add_attr_typ_dict[typ])

    def remove(self):
        s = self.varname + '.parentNode.removeChild(' + self.varname + ');\n'
        self.rdoc.inline(s)
        self.parent.childs.remove(self)
        self.parent = None

    def append(self, es):
        if hasattr(es, '__len__'):
            for e in es:
                self.childs.append(e)
                e.parent = self
                s = self.varname + '.appendChild(' + e.varname + ');\n'
                self.rdoc.inline(s)
        else:
            self.childs.append(es)
            es.parent = self
            s = self.varname + '.appendChild(' + es.varname + ');\n'
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
            js = self.varname + '.textContent="' + text + '";\n'
            self.rdoc.inline(js)

    def __str__(self):
        return self.varname

    def element(self, typ=None, txt=None, **kwargs):
        es = self.rdoc.element(typ, txt, **kwargs)
        self.append(es)
        return es


class Window:
    def __init__(self, rdoc):
        self.rdoc = rdoc
        self.varname = 'window'
        self.events = EventListener(rdoc, self.varname)


_rec1_inline = re.compile(r'#\{([^}]*)\}')
_rec2_rpc = re.compile(r'#rpc\{([^}]*)\}')


def _inline(code, level=1, stringify=None, rpcweakrefs=None):
    # inline interpolation...
    prev_frame = inspect.getouterframes(inspect.currentframe())[level][0]
    loc = prev_frame.f_locals
    glo = prev_frame.f_globals
    for item in _rec1_inline.findall(code):
        rep = eval(item, glo, loc)
        if not stringify:
            if hasattr(rep, 'varname'):
                rep = rep.varname
            else:
                rep = str(rep)
        else:
            rep = stringify(rep)
        code = code.replace('#{%s}' % item, rep)

    if rpcweakrefs is not None:
        for item in _rec2_rpc.findall(code):
            sitem = item.split(',')
            litem = sitem[0].strip()
            ritem = ','.join(sitem[1:])
            fnc = eval(litem, glo, loc)
            rep = str(random.randint(0, 1e16))

            def ondelete(r):
                del rpcweakrefs[r.__rep]

            wr = safeRef(fnc, ondelete)
            wr.__rep = rep
            rpcweakrefs[rep] = wr
            code = code.replace('#rpc{%s}' % item, 'rpc(%s)' % ("'"+rep+"',"+ritem))

    return code


class Interval:
    def __init__(self, rdoc, ms, exp=None, level=2):
        self.rdoc = rdoc
        self.varname = rdoc.get_new_uid()
        self.ms = ms
        self.is_running = True
        code = self.rdoc.stringify(exp, pop_line=False)
        code = _inline(code, level=level, rpcweakrefs=self.rdoc.rpcweakrefs)
        if not callable(exp):
            code = 'function(){' + code + '}'
        js = self.varname + '=setInterval(' + code + ',' + str(ms) + ');\n'
        rdoc.inline(js)

    def stop(self):
        self.is_running = False
        js = 'clearInterval(' + self.varname + ');\n'
        self.rdoc.inline(js)


class _JSFunction:
    def __init__(self, rdoc, *varargs, body=None, level=2):
        self.rdoc = rdoc
        self.varname = rdoc.get_new_uid()
        code = self.rdoc.stringify(body, encapsulate_strings=False, pop_line=False)
        code = _inline(code, level=level, stringify=rdoc.stringify, rpcweakrefs=self.rdoc.jsrpcweakrefs)
        code = code.rstrip(';\n')
        args = ','.join(varargs)
        self.js = self.varname + '=function(' + args + '){\n' + code + '\n}\n'
        rdoc.inline(self.js)

    def __call__(self, *varargs):
        js = self.varname + '(' + ','.join([str(v) for v in varargs]) + ');\n'
        self.rdoc.inline(js)

    def __str__(self):
        return self.varname + '();\n'


class _StyleSheet:
    def __init__(self, rdoc):
        self.rdoc = rdoc
        self.element = rdoc.element('style')
        self.varname = self.element.varname
        self.element.att.type = 'text/css'
        self.rdoc.body.append(self.element)
        js = self.varname + '=document.styleSheets[0];\n'
        self.rdoc.inline(js)

    def rule(self, selector, **kwargs):
        return _Rule(self, selector, **kwargs)


class _Rule:
    def __init__(self, stylesheet, selector, **kwargs):
        if selector.split()[0] == '@keyframes' and stylesheet.rdoc.vendor_prefix == 'webkit':
            selector = '@-webkit-' + selector[1:]
        self.stylesheet = stylesheet
        self.rdoc = self.stylesheet.rdoc
        self.varname = self.rdoc.get_new_uid()
        self.selector = selector
        # TODO: what if we want to change the selector?!
        ssn = self.stylesheet.varname
        js = ssn + '.insertRule("' + selector + ' {}",' + ssn + '.cssRules.length);\n'
        js += self.varname + '=' + ssn + '.cssRules[' + ssn + '.cssRules.length-1];\n'
        self.rdoc.inline(js)
        self.style = StyleAtt(self.rdoc, self.varname)
        self.style(**kwargs)


class RemoteDocument:
    def __init__(self):
        self.varname = 'document'
        self.__uid_count = 0
        self.__code_strings = []
        self.__block_ixs = []
        self.__varname_element_dict = {}
        self.body = Element(self, 'body', '', customvarname='document.body')
        self.pop_all_code()  # body is special, it's created by static content
        self.inline('document.app={};\n')
        self.app = SimpleProp(self, 'document', 'app')
        self.props = SimpleProp(self, 'document', None)
        self.stylesheet = _StyleSheet(self)
        self.vendor_prefix = None
        self.jsrpcweakrefs = {}
        self.window = Window(self)

    def set_vendor_prefix(self, vendor_prefix):
        self.vendor_prefix = vendor_prefix

    def get_element_from_varname(self, varname) -> Element:
        return self.__varname_element_dict[varname]

    def getElementById(self, fromid):
        return Element(self, fromid=fromid)

    def element(self, typ=None, text=None, **kwargs):
        elems = []
        if typ:
            e = Element(self, typ, text)
            self.__varname_element_dict[e.varname] = e
            elems.append(e)
        if kwargs:
            for i, t in kwargs.items():
                kwe = Element(self, i, t)
                self.__varname_element_dict[kwe.varname] = kwe
                elems.append(kwe)
        if len(elems) > 1:
            return elems
        else:
            return elems[0]

    def startinterval(self, ms, exp=None):
        return Interval(self, ms, exp, level=3)

    def jsfunction(self, *varargs, body=None):
        return _JSFunction(self, *varargs, body=body, level=3)

    def get_new_uid(self):
        uid = '__v' + str(self.__uid_count)
        self.__uid_count += 1
        return uid

    def begin_block(self):
        self.__block_ixs.append(len(self.__code_strings))

    def cancel_block(self):
        self.__block_ixs.pop()

    def pop_block(self):
        ix = self.__block_ixs.pop()
        code = ''
        for i in range(len(self.__code_strings) - ix):
            code = self.__code_strings.pop() + code
        return code

    def pop_all_code(self):
        code = ''.join(self.__code_strings)
        self.__code_strings.clear()
        self.__block_ixs.clear()
        return code

    def pop_line(self):
        return self.__code_strings.pop()

    def inline(self, text, *varargs):
        """
        insert a code block (contained in 'text' parameter)
        """
        if varargs:
            text = text.format(*(v.varname for v in varargs))
        self.__code_strings.append(text)

    def JS(self, text):
        self.__code_strings.append(_inline(text, level=2))

    def msg(self, text):
        self.inline('message("' + text + '");')

    def stylesheet(self):
        return _StyleSheet(self)

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
                return '"' + str(val) + '"'
            return val
        if callable(val):
            self.begin_block()
            tmp = val()
            if tmp:
                self.cancel_block()
            else:
                tmp = self.pop_block()
            return 'function(){' + tmp + '}'
        if val is None:
            if pop_line:
                return self.pop_line()
            return self.pop_block()
        if custom_stringify:
            return custom_stringify(val)
        return str(val)
