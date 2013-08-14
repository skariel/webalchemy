from collections import deque
class remotedocument:

    def __init__(self):
        self.__uid_count= 0
        self.__buff= ''
        self.__last_buff_len=0
        self.__block_buff_len=deque()
        class __body:
            def __init__(self):
                self.childs= []
        self.__body= __body()

    def __set_prev_buff_len(self):
        self.__last_buff_len= len(self.__buff)

    def __get_new_uid(self):
        uid= 'e'+str(self.__uid_count)
        self.__uid_count+=1        
        return uid

    def get_body(self):
        return self.__body

    def clear_buff(self):
        self.__buff=''
        self.__set_prev_buff_len()

    def get_buff(self):
        return self.__buff

    def create_element(self,typ,attrs=None,txt=None):
        self.__set_prev_buff_len()
        class element:
            def __init__(self,typ,attrs,txt,rdoc,uid):
                self.typ  = typ
                self.attrs= attrs
                self.txt  = txt
                self.uid= uid
                self.parent= None
                self.childs= []
                self.rdoc= rdoc
            def set_attribute(self,att_name,value):
                self.rdoc.inline(self.uid+'.setAttribute("'+name+'","'+value+'");\n')
            def set_text(self,txt):
                self.rdoc.inline(self.uid+'.textContent="'+txt+'";\n')
            def set_style_att(self,name,value):
                self.rdoc.inline(self.uid+'.style["'+name+'"]="'+value+'";\n')

        e= element(typ,attrs,txt,self,self.__get_new_uid())
    
        self.__buff+=e.uid+'= document.createElement("'+e.typ+'");\n'
        self.__buff+='var t= document.createTextNode("'+e.txt+'");\n'
        if e.txt is not None:
            self.__buff+=e.uid+'.appendChild(t);\n'
        if e.attrs is not None:
            for k,v in e.attrs.items():
                self.__buff+=e.uid+'.setAttribute("'+k+'","'+v+'");\n'
        return e
    
    def create_interval(self,ms,ex=None):
        code= self.__buff[self.__last_buff_len:]
        self.__buff= self.__buff[:self.__last_buff_len]
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
        i= interval(self,self.__get_new_uid(),ms,code)
        s= i.uid+'=setInterval(function(){'+code+'},'+str(ms)+');\n'
        self.__buff+=s
        return i

    def inline(self,txt):
        self.__set_prev_buff_len()
        self.__buff+=txt

    def root_append(self,e):
        self.__set_prev_buff_len()
        e.parent= self.__body
        self.__body.childs.append(e)
        self.__buff+='document.body.appendChild('+e.uid+');\n'

    def msg(self,txt):
        self.__set_prev_buff_len()
        self.__buff+='message("'+txt+'");'

    def begin(self):
        self.__set_prev_buff_len()
        self.__block_buff_len.appendleft(self.__last_buff_len);

    def end(self):
        self.__last_buff_len= self.__block_buff_len.popleft()