class str:

    def __init__(self, jsobject):
        self.jsobject = jsobject

    def __repr__(self):
        return self

    def __jstype__(self):
        return self.jsobject

    def __hash__(self):
        return '"' + self

    def __contains__(self, s):
        jsobject = self.jsobject
        s = jstype(s)
        i = jscode('jsobject.indexOf(s)')
        if int(i) != -1:
            return True
        return False

    def __iter__(self):
        return ListIterator(self)

    def join(self, iterable):
        iterable = iter(iterable)
        try:
            out = next(iterable)
        except StopIteration:
            return ""
        for item in iterable:
            out = out + self + item
        return out

    def __add__(self, other):
        a = self.jsobject
        b = other.jsobject
        return str(jscode('a + b'))

    def __len__(self):
        jsobject = jscode('self.jsobject')
        return int(jscode('jsobject.length'))

    def __lte__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a <= b'):
            return True
        return False

    def __gte__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a >= b'):
            return True
        return False

    def __gt__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a > b'):
            return True
        return False

    def __eq__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a == b'):
            return True
        return False
        
    def __getitem__(self, index):
        jsobject = self.jsobject
        index = index.jsobject
        c = jscode('jsobject[index]')
        return str(c)

    def __neq__(self, other):
        return not self.__eq__(other)
