class remotedocument:

    def __init__(self):
        self.__uid_count= 0
        self.__code_strings=[]
        self.__block_ixs=[]
        class __body:
            def __init__(self):
                self.childs= []
        self.__body= __body()

    def __get_new_uid(self):
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

    def get_body(self):
        return self.__body

    def pop_all_code(self):
        code= ''.join(self.__code_strings)
        self.__code_strings.clear()
        self.__block_ixs.clear()
        return code

    def create_element(self,typ,attrs=None,txt=None):
        class element:
            def __init__(self,typ,attrs,txt,rdoc,uid):
                self.typ  = typ
                self.attrs= attrs
                self.txt  = txt
                self.uid= uid
                self.parent= None
                self.childs= []
                self.rdoc= rdoc
                if self.attrs is None:
                    self.attrs= {}
                if 'style' not in self.attrs:
                    self.attrs['style']= {}
            def set_attribute(self,name,value):
                self.rdoc.inline(self.uid+".setAttribute('"+name+"','"+value+"');\n")
                self.attrs[name]=value
            def set_text(self,txt):
                self.rdoc.inline(self.uid+'.textContent="'+txt+'";\n')
                self.txt=txt
            def set_style_att(self,name=None,value=None,**kwargs):
                if name is not None:
                    self.rdoc.inline(self.uid+'.style["'+name+'"]="'+value+'";\n')
                    self.attrs['style'][name]= value
                else:
                    s=''
                    for name,value in kwargs.items():
                        s+= self.uid+'.style["'+name+'"]="'+value+'";\n'
                        self.attrs['style'][name]= value
                    self.rdoc.inline(s)
            def set_event(self,**kwargs):
                s=''
                for k,v in reversed(kwargs.items()):
                    code= self.rdoc._remotedocument__code_strings.pop()
                    s+=self.uid+".setAttribute('"+k+"','"+code.rstrip('\n')+"');\n"
                    self.attrs[k]=code
                self.rdoc.inline(s)
            def remove(self):
                self.rdoc.inline(self.uid+'.parentNode.removeChild('+self.uid+');\n')
                self.parent= None

        e= element(typ,attrs,txt,self,self.__get_new_uid())

        s = e.uid+'= document.createElement("'+e.typ+'");\n'
        s+= 'var t= document.createTextNode("'+e.txt+'");\n'
        if e.txt is not None:
            s+=e.uid+'.appendChild(t);\n'
        for k,v in e.attrs.items():
            if type(v) is not dict:
                s+=e.uid+'.setAttribute("'+k+'","'+v+'");\n'
            else:
                for kk, vv in v: 
                    s+=e.uid+'.'+k+'.setAttribute("'+kk+'","'+vv+'");\n'
        self.inline(s)
        return e
    
    def create_interval(self,ms,*exps):
        class interval:
            def __init__(self,rdoc,uid,ms,code):
                self.rdoc=rdoc
                self.uid=uid
                self.ms=ms
                self.is_running= True
                self.code= code
            def stop(self):
                self.is_running=False
                self.rdoc.inline('clearInterval('+self.uid+');\n')
        if len(exps)==0:
            code= self.__pop_block()
        else:
            code=''
            for ex in exps:
                code= self.__code_strings.pop() + code
        i= interval(self,self.__get_new_uid(),ms,code)
        s= i.uid+'=setInterval(function(){'+code+'},'+str(ms)+');\n'
        self.inline(s)
        return i

    def inline(self,txt):
        '''
        insert a code block (contained in 'txt' parameter)
        '''
        self.__code_strings.append(txt)

    def root_append(self,e):
        e.parent= self.__body
        self.__body.childs.append(e)
        self.inline('document.body.appendChild('+e.uid+');\n')

    def msg(self,txt):
        self.inline('message("'+txt+'");')

    def set_title(self,txt):
        self.inline('document.title='+txt+';\n');

