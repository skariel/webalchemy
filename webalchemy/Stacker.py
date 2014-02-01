

from .remotedocument import Element


class Stacker:
    '''Allow stacking element creation with "with" statements
    
    eg.
    s = Stacker(self.rdoc.body)
    with s.element('div', cls='panel') as panel:
        s.element('div', text='Hello', cls='panel-heading')
        with s.element('div', cls='panel-body'):
            s.element(p="this is text inside body")
        s.element('div', text="panel footer here", cls="panel-footer")
    '''
    def __init__(self, root):
        self.stack = [root]
        
    def element(self, *args, **kwargs):
        '''Create an element - parent is head of stack'''
        parent = self.stack[-1]
        e = parent.element(*args, **kwargs)
        se = StackerElement(self, e)
        return se
         
    
    
class StackerElement(Element):
    '''Wrapper for Element - knows to push to stack and pop from stack'''
    def __init__(self, stacker, element):
        self.__class__ = type(element.__class__.__name__,
                              (self.__class__, element.__class__),
                              {})
        self.__dict__ = element.__dict__
        self.stacker = stacker
        self._element = element
        
    def element(self, *args, **kwargs):
        '''Create an element - parent is head of stack'''
        parent = self.stack[-1]
        e = parent.element(*args, **kwargs)
        se = StackerElement(self, e)
        return se
    
    def __enter__(self, **kwargs):
        self.stacker.stack.append(self._element)
        return self
    
    def __exit__(self, type, value, traceback):
        self.stacker.stack.pop()
        
