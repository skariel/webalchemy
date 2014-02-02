

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
    def __init__(self, element, prev_stacker=None):
        # proxy everything to element - copy __dict__ and __class__
        self.__class__ = type(element.__class__.__name__,
                              (self.__class__, element.__class__),
                              {})
        self.__dict__ = element.__dict__

        if prev_stacker:
            self._stack = prev_stacker._stack
        else:
            self._stack = [element]
        self._element = element

        
    def element(self, *args, **kwargs):
        '''Create an element - parent is head of stack'''
        parent = self._stack[-1]
        e = parent.element(*args, **kwargs)
        se = Stacker(e, self)
        return se
         
    def __enter__(self, **kwargs):
        self._stack.append(self._element)
        return self
    
    def __exit__(self, type, value, traceback):
        self._stack.pop()
        
    
