class ListIterator:

    def __init__(self, obj):
        self.list = obj
        self.index = 0
        self.length = len(obj)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == self.length:
            raise StopIteration
        index = self.index
        self.index = self.index + 1
        return self.list[index]


class list:
    
    def __init__(self, iterable):
        self.jsobject = JSArray()
        if jscode('iterable !== undefined'):
            for item in iterable:
                self.append(item)

    def __or__(self, other):
        if self:
            return self
        if other:
            return other
        return False

    def __hash__(self):
        raise TypeError("unhashable type: 'list'")

    def __repr__(self):
        iterable = map(nest_str_with_quotes, self)
        return "[" + ", ".join(iterable) + "]"

    def __jstype__(self):
        out = JSArray()
        for item in self:
            item = jstype(item)
            jscode('out.push(item)')
        return out

    def append(self, item):
        jsobject = self.jsobject
        jscode('jsobject.push(item)')

    def insert(self, index, item):
        self.jsobject.splice(index, 0, item)

    def __setitem__(self, index, value):
        jsobject = self.jsobject
        index = index.jsobject
        jscode('jsobject[index] = value')

    def __getitem__(self, s):
        jsobject = self.jsobject
        index = jstype(s)
        return jscode('jsobject[index]')

    def __len__(self):
        jsobject = self.jsobject
        length = jscode('jsobject.length')
        return int(length)

    def __iter__(self):
        return ListIterator(self)

    def __contains__(self, obj):
        for item in self:
            if obj == item:
                return True
        return False
            
    def pop(self):
        return self.jsobject.pop()

    def index(self, obj):
        index = 0
        for item in self:
            if item == obj:
                return index
            index += 1
        raise ValueError

    def remove(self, obj):
        index = self.index(obj)
        jsobject = self.jsobject
        jscode('jsobject.splice(jstype(index), 1)')

    def __delitem__(self, index):
        self.jsobject.splice(jstype(index), 1)
