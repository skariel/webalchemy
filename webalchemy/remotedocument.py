

import re
import inspect
import logging




# logger for internal purposes
log= logging.getLogger(__name__)





class style_att:
    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})
    def __setitem__(self,item,val):
        js= self.varname+'.style["'+item+'"]="'+str(val)+'";\n'
        self.rdoc.inline(js)
        self.d[item]=val
    def __setattr__(self,attr,val):
        self[attr]=val
    def __getitem__(self,item):
        js= self.varname+'.style["'+item+'"];\n'
        self.rdoc.inline(js)
        return self.d[item]
    def __getattr__(self,name):
        return self[name]
    def __delitem__(self,item):
        js= self.varname+'.removeProperty("'+item+'");\n'
        self.rdoc.inline(js)
        del self.d[item]
    def __delattr__(self,name):
        del self[name]
    def __call__(self,**kwargs):
        for k,v in kwargs.items():
            self[k]= v




class class_att:
    def __init__(self, rdoc, varname):
        self.rdoc= rdoc
        self.varname= varname
        self.lst=[]
    def append(self,name):
        js= self.varname+'.classList.add("'+name+'");\n'
        self.rdoc.inline(js)
        self.lst.append(name)
    def extend(self,name_list):
        for name in name_list:
            self.append(name)
    def remove(self,name):
        js= self.varname+'.classList.remove("'+name+'");\n'
        self.rdoc.inline(js)
        self.lst.remove(name)        
    def replace(old_name, new_name):
        self.remove(old_name)
        self.append(new_name)
    def __delitem__(self,name):
        self.remove(name)




class simple_att:
    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
        super().__setattr__('d', {})
    def __setitem__(self,item,val):
        js= self.varname+'.setAttribute("'+item+'","'+str(val)+'");\n'
        self.rdoc.inline(js)
        self.d[item]=val
    def __setattr__(self,attr,val):
        self[attr]=val
    def __getitem__(self,item):
        js= self.varname+'.getAttribute("'+item+'");\n'
        self.rdoc.inline(js)
        return self.d[item]
    def __getattr__(self,name):
        return self[name]
    def __delitem__(self,item):
        js= self.varname+'.removeAttribute("'+item+'");\n'
        self.rdoc.inline(js)
        del self.d[item]
    def __delattr__(self,name):
        del self[name]
    def __call__(self,**kwargs):
        for k,v in kwargs.items():
            self[k]= v






class event_listener:
    def __init__(self, rdoc, varname):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname)
    def add(self,**kwargs):
        for event,listener in kwargs.items():
            if hasattr(listener,'varname'):
                l= listener.varname
            elif type(listener) is str:
                l= listener
            else:
                self.rdoc.begin_block()
                l= listener()
                if not l:
                    l= self.rdoc.pop_block()
                    l= 'function(){'+l.rstrip('\n').rstrip(';')+'}'
                else:
                    self.rdoc.cancel_block()
            js= self.varname+'.addEventListener("'+event+'",'+l+',false);\n'
            self.rdoc.inline(js)
    def remove(self,event,listener):
        js= self.varname+'.removeEventListener("'+event+'",'+listener+');\n'
        self.rdoc.inline(js)





class simple_prop:
    def __init__(self, rdoc, varname, namespace):
        super().__setattr__('rdoc', rdoc)
        super().__setattr__('varname', varname+'.'+namespace)
        super().__setattr__('d', {})
    def __setitem__(self,item,val):
        if type(val) is str:
            v='"'+val+'"'
        else:
            v= str(val)
        js= self.varname+'["'+item+'"]='+v+';\n'
        self.rdoc.inline(js)
        self.d[item]=val
    def __setattr__(self,attr,val):
        self[attr]=val
    def __getitem__(self,item):
        js= self.varname+'["'+item+'"];\n'
        self.rdoc.inline(js)
        return self.d[item]
    def __getattr__(self,name):
        return self[name]
    def __delitem__(self,item):
        js= 'delete '+self.varname+'["'+item+'"];\n'
        self.rdoc.inline(js)
        del self.d[item]
    def __delattr__(self,name):
        del self[name]
    def __call__(self,**kwargs):
        for k,v in kwargs.items():
            self[k]= v




class element:
    def __init__(self,rdoc,typ,text=None):
        self.varname= rdoc.get_new_uid()
        self.rdoc= rdoc
        self.typ= typ
        self.parent=None
        self.childs=[]
        js=self.varname+'=document.createElement("'+typ+'");\n'
        js+=self.varname+'.app={};\n'
        if text is not None:
            self._text=text
            js+= self.varname+'.textContent="'+text+'";\n'
        rdoc.inline(js)

        self.cls= class_att(rdoc, self.varname)
        self.att= simple_att(rdoc, self.varname)
        self.style= style_att(rdoc, self.varname)
        self.events= event_listener(rdoc, self.varname)
        self.app= simple_prop(rdoc, self.varname, 'app')

        self.att.id= self.varname
        self.cls.append(self.varname)
    def remove(self):
        s=self.varname+'.parentNode.removeChild('+self.varname+');\n'
        self.rdoc.inline(s)
        self.parent.childs.remove(self)
        self.parent= None
    def append(self,e):
        self.childs.append(e)
        e.parent=self
        s=self.varname+'.appendChild('+e.varname+');\n'
        self.rdoc.inline(s)
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, text):
        self.set_text(text)
    def set_text(self,text):
        self._text = text
        js= self.varname+'.textContent="'+text+'";\n'
        self.rdoc.inline(js)
    def __str__(self):
        return self.varname
    




class interval:
    def __init__(self,rdoc,ms,exp=None):
        self.rdoc= rdoc
        self.varname= rdoc.get_new_uid()
        self.ms= ms
        self.is_running= True
        if exp is None:
            code= rdoc.pop_block()
        else:
            exp()
            code= rdoc._remotedocument__code_strings.pop()
        js= self.varname+'=setInterval(function(){'+code+'},'+str(ms)+');\n'
        rdoc.inline(js)
    def stop(self):
        self.is_running=False
        js='clearInterval('+self.varname+');\n'
        self.rdoc.inline(js)





class function:
    def __init__(self,rdoc,exp=None,*varargs):
        self.rdoc= rdoc
        self.varname= rdoc.get_new_uid()
        if exp is None:
            code= rdoc.pop_block()
        else:
            exp()
            code= rdoc._remotedocument__code_strings.pop()
        args=','.join(varargs)
        self.js=self.varname+'=function('+args+'){\n'+code+'\n}\n'
        rdoc.inline(self.js)
    def __call__(self,*varargs):
        js=self.varname+'('+','.join([str(v) for v in varargs])+');\n'
        self.rdoc.inline(js)
    def __str__(self):
        return self.varname+'();\n'





class stylesheet:
    def __init__(self,rdoc):
        self.rdoc=rdoc
        self.varname= rdoc.get_new_uid()
        self.element= rdoc.element('style')
        self.element.att.type='text/css'
        self.rdoc.body.append(self.element)
        js= self.varname+'=document.styleSheets[0];\n'
        self.rdoc.inline(js)
    def rule(self,selector,text=None,**kwargs):
        return rule(self,selector,text,**kwargs)





class rule:
    def __init__(self,stylesheet,selector,text=None,**kwargs):
        self.stylesheet= stylesheet
        self.rdoc= self.stylesheet.rdoc
        self.varname= self.rdoc.get_new_uid()
        self.selector= selector
        self.props= kwargs
        props=' '.join([k+':'+v+';' for k,v in kwargs.items()])
        if text:
            props+=text
            if props[-1]!=';':
                props+=';'
        ssn= self.stylesheet.varname
        js = ssn+'.addRule("'+selector+'","'+props+'");\n'
        js+= self.varname+'='+ssn+'.rules['+ssn+'.rules.length-1];\n'
        self.rdoc.inline(js)
        self.style= style_att(self.rdoc, self.varname)





class remotedocument:
    def __init__(self):
        self.varname='document'
        self.__uid_count= 0
        self.__code_strings=[]
        self.__block_ixs=[]
        self.body= self.element('body','')
        self.body.varname='document.body'
        self.pop_all_code() # body is special, it's created by static content
        self.title=''
    def element(self,typ,text=None):
        return element(self,typ,text)
    def startinterval(self,ms,exp=None):
        return interval(self,ms,exp)
    def function(self,exp=None,*varargs):
        return function(self,exp,*varargs)
    def jsfunction(self,*varargs):
        self.begin_block()
        code=varargs[-1]

        # inline interpolation...
        prev_frame= inspect.getouterframes(inspect.currentframe())[1][0]
        locals= prev_frame.f_locals
        globals= prev_frame.f_globals
        for item in re.findall(r'#\{([^}]*)\}', code):
            code = code.replace('#{%s}' % item,
                        eval(item+'.varname', globals, locals))

        self.inline(code)
        return self.function(None,*varargs[:-1])
    def get_new_uid(self):
        uid= '__v'+str(self.__uid_count)
        self.__uid_count+=1        
        return uid
    def begin_block(self):
        self.__block_ixs.append(len(self.__code_strings))
    def cancel_block(self):
        self.__block_ixs.pop()
    def pop_block(self):
        ix= self.__block_ixs.pop()
        code=''
        for i in range(len(self.__code_strings)-ix):
            code= self.__code_strings.pop()+code
        return code
    def pop_all_code(self):
        code= ''.join(self.__code_strings)
        self.__code_strings.clear()
        self.__block_ixs.clear()
        return code
    def inline(self,text):
        '''
        insert a code block (contained in 'text' parameter)
        '''
        self.__code_strings.append(text)
    def msg(self,text):
        self.inline('message("'+text+'");')
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, text):
        self._title = text
        js= self.varname+'.title="'+text+'";\n'
        self.inline(js)
    def stylesheet(self):
        return stylesheet(self)




