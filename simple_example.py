#
# a simple example. Currently used for testing features
#
from tornado import gen
import sys
class my_app:    
    def __init__(self, rdoc):
        self.p= rdoc.create_element('p',txt='This is an empty document', )
        rdoc.root_append(self.p)
        self.i= rdoc.create_interval(1000,rdoc.msg('interval!'))
        self.i.count=0
        rdoc.begin()
        e=rdoc.create_element('p',txt=':)', )
        rdoc.root_append(e)
        rdoc.end()
        self.i2= rdoc.create_interval(2500)
    
    @gen.coroutine
    def message(self, rdoc, txt):
        if txt!='interval!':
            return
        if self.i.count>5:
            self.i.stop()
            self.i2.stop()
        self.i.count+=1
        p= rdoc.create_element('p',txt='New paragraph #'+str(self.i.count))
        p.set_style_att('position','absolute')
        p.set_style_att('left',str(50*self.i.count)+'px')
        p.set_style_att('top',str(50*self.i.count)+'px')
        self.p.set_text('there are now '+str(self.i.count+1)+' paragraphs')
        rdoc.root_append(p)
            
if __name__=='__main__':
    import webalchemy.server
    server.run(8083,my_app)