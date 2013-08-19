
 
class jsdict(dict):
    def __init__(self,ctx,isroot=True):
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
            q=super().__getattribute__('ctx').stringify(value)        
        super().__getattribute__('ctx').write('["'+name+'"]='+q)
        super().__setitem__(name,value)
        super().__getattribute__('ctx').done_writing()
    def __call__(self,**kwargs):
        for k,v in kwargs.items():
            buff= super().__getattribute__('ctx').buff
            self[k]=v
            super().__getattribute__('ctx').write(buff)



class element:
    def __init__(self,rdoc,typ,text=None):
        class writer:
            def __init__(self,parent):
                self.buff=''
                self.parent=parent
            def write(self,text):
                self.buff+=text
            def done_writing(self):
                self.parent._element__attr_changed(self.buff)
                self.buff=''
            def start_writing(self):
                self.buff=''
            def stringify(self,value):
                if callable(value):
                    # value() can change the buffer, so lets take care of that:
                    tmpbuff= self.buff
                    value()
                    self.buff= tmpbuff
                    code= self.parent.rdoc._remotedocument__code_strings.pop()
                    js='function(){\n'+code+'}\n'
                    return js
                else:
                    return str(value)
        self.__writer= writer(self)
        self.id= rdoc.get_new_uid()
        self.att= jsdict(self.__writer)
        self.rdoc= rdoc
        self.typ= typ
        self.parent=None
        self.childs=[]
        js=self.id+'=document.createElement("'+typ+'");\n'
        if text is not None:
            self._text=text
            js+= self.id+'.textContent="'+text+'";\n'

        rdoc.inline(js)
    def __attr_changed(self,text):
        s= self.id+text
        if s[-1]!='\n':
            s+=';\n'
        self.rdoc.inline(s)
    def remove(self):
        s=self.id+'.parentNode.removeChild('+self.id+');\n'
        self.rdoc.inline(s)
        self.parent.childs.remove(self)
        self.parent= None
    def append(self,e):
        self.childs.append(e)
        e.parent=self
        s=self.id+'.appendChild('+e.id+');\n'
        self.rdoc.inline(s)
    @property
    def text(self):
        return self._title
    @text.setter
    def text(self, text):
        self._text = text
        js= self.id+'.textContent="'+text+'";\n'
        self.rdoc.inline(js)
    

class interval:
    def __init__(self,rdoc,ms,exp=None):
        self.rdoc= rdoc
        self.id= rdoc.get_new_uid()
        self.ms= ms
        self.is_running= True
        if exp is None:
            code= rdoc._remotedocument__pop_block()
        else:
            exp()
            code= rdoc._remotedocument__code_strings.pop()
        js= self.id+'=setInterval(function(){'+code+'},'+str(ms)+');\n'
        rdoc.inline(js)
    def stop(self):
        self.is_running=False
        js='clearInterval('+self.id+');\n'
        self.rdoc.inline(js)




class function:
    def __init__(self,rdoc,exp=None):
        self.rdoc= rdoc
        self.id= rdoc.get_new_uid()
        if exp is None:
            code= rdoc._remotedocument__pop_block()
        else:
            exp()
            code= rdoc._remotedocument__code_strings.pop()
        js='function '+self.id+'(){\n'+code+'\n}\n'
        rdoc.inline(self.js)
    def __call__(self):
        js=str(self)
        self.rdoc.inline(js)
    def __str__(self):
        return self.id+'();\n'




class remotedocument:
    def __init__(self):
        self.id='document'
        self.__uid_count= 0
        self.__code_strings=[]
        self.__block_ixs=[]
        self.body= self.element('body','')
        self.body.id='document.body'
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
    def element(self,typ,text):
        return element(self,typ,text)
    def startinterval(self,ms,exp=None):
        return interval(self,ms,exp)
    def function(self,exp=None):
        return function(self,exp)
    def get_new_uid(self):
        uid= 'e'+str(self.__uid_count)
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
        js= self.id+'.title="'+text+'";\n'
        self.inline(js)
    


