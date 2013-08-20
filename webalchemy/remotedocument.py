

from webalchemy.utils import log



class element:
    def __init__(self,rdoc,typ,text=None):
        self.varname= rdoc.get_new_uid()
        self.att= rdoc.jsdict(self.__attr_changed)
        self.rdoc= rdoc
        self.typ= typ
        self.parent=None
        self.childs=[]
        js=self.varname+'=document.createElement("'+typ+'");\n'
        if text is not None:
            self._text=text
            js+= self.varname+'.textContent="'+text+'";\n'
        rdoc.inline(js)
        self.att.id= self.varname
        self.att.className= self.varname
    def __attr_changed(self,text):
        js= self.varname+text
        self.rdoc.inline(js)
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
        return self._title
    @text.setter
    def text(self, text):
        self._text = text
        js= self.varname+'.textContent="'+text+'";\n'
        self.rdoc.inline(js)
    



class interval:
    def __init__(self,rdoc,ms,exp=None):
        self.rdoc= rdoc
        self.varname= rdoc.get_new_uid()
        self.ms= ms
        self.is_running= True
        if exp is None:
            code= rdoc._remotedocument__pop_block()
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
    def __init__(self,rdoc,exp=None):
        self.rdoc= rdoc
        self.varname= rdoc.get_new_uid()
        if exp is None:
            code= rdoc._remotedocument__pop_block()
        else:
            exp()
            code= rdoc._remotedocument__code_strings.pop()
        js='function '+self.varname+'(){\n'+code+'\n}\n'
        rdoc.inline(self.js)
    def __call__(self):
        js=str(self)
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
        self.att= self.rdoc.jsdict(self.__attr_changed)
    def __attr_changed(self,text):
        js= self.varname+text
        self.rdoc.inline(js)





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
        self.__code_buff_list=[]
        self.__block_buff_list=[]
    def push_buff(self):
        self.__code_buff_list.append(self.__code_strings)
        self.__block_buff_list.append(self.__block_ixs)
        self.__code_strings=[]
        self.__block_ixs=[]
    def pop_buff(self):
        self.__code_strings= self.__code_buff_list.pop()
        self.__block_strings= self.__block_buff_list.pop()
    def element(self,typ,text=None):
        return element(self,typ,text)
    def startinterval(self,ms,exp=None):
        return interval(self,ms,exp)
    def function(self,exp=None):
        return function(self,exp)
    def get_new_uid(self):
        uid= '__v'+str(self.__uid_count)
        self.__uid_count+=1        
        return uid
    def begin_block(self):
        self.__block_ixs.append(len(self.__code_strings))
    def __pop_block(self):
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
    def jsdict(self,att_changed_callback,stringify=None):
        rdoc=self
        class writer:
            def __init__(self,att_changed_callback):
                self.buff=''
                self.att_changed_callback=att_changed_callback
            def write(self,text):
                self.buff+=text
            def done_writing(self):
                if self.buff[-1]!='\n':
                    self.buff+=';\n'
                self.att_changed_callback(self.buff)
                self.buff=''
            def start_writing(self):
                self.buff=''
            def stringify(self,value):
                if callable(value):
                    # value() can change the buffer, so lets take care of that:
                    nonlocal rdoc
                    tmpbuff= self.buff
                    value()
                    self.buff= tmpbuff
                    code= rdoc._remotedocument__code_strings.pop()
                    js='function(){\n'+code+'}\n'
                    return js
                else:
                    return str(value)
        class jsdict(dict):
            def __init__(self,ctx,isroot=None):
                super().__setattr__('ctx',ctx)
                if isroot:
                    ctx.start_writing()
            def __getattr__(self,name):
                if name in self:
                    return self[name]
                super().__getattribute__('ctx').write('["'+name+'"]')
                n=jsdict(super().__getattribute__('ctx'),False)
                super().__setitem__(name, n)
                return n
            def __getitem__(self,name):
                super().__getattribute__('ctx').write('["'+name+'"]')
                if name not in self:
                    super().__setitem__(name,jsdict(super().__getattribute__('ctx'),False))
                return super().__getitem__(name)
            def __setattr__(self,name,value):
                self[name]=value
            def __setitem__(self,name,value):
                if type(value) is str:
                    q= '"'+value+'"'
                else:
                    nonlocal stringify
                    if not stringify:
                        q=super().__getattribute__('ctx').stringify(value)        
                    else:
                        q=stringity(value)
                super().__getattribute__('ctx').write('["'+name+'"]='+q)
                super().__setitem__(name,value)
                super().__getattribute__('ctx').done_writing()
            def __call__(self,**kwargs):
                for k,v in kwargs.items():
                    buff= super().__getattribute__('ctx').buff
                    self[k]=v
                    super().__getattribute__('ctx').write(buff)
        return jsdict(writer(att_changed_callback), True)
    def stylesheet(self):
        return stylesheet(self)



