class range:

    def __init__(self, a, b=None):
        if b:
            self.index = a
            self.end = b
        else:
            self.index = 0
            self.end = a

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.end:
            index = self.index
            self.index += 1
            return index
        raise StopIteration


def range(a, b=None):
    out = list()
    while index < end:
        out.append(index)
        index += 1
    return out


def repr(obj):
    if obj is object:
        return "<class 'object'>"
    return obj.__repr__()


def print(*args):
    out = JSArray()
    for arg in args:
        if jscode('arg.__class__ !== undefined'):
            r = jstype(repr(arg))
            jscode('out.push(r)')
        elif jscode('arg.__metaclass__ !== undefined'):
            name = jscode('arg.__name__')
            jscode("""out.push("<class '"+ name +"'>")""")
        else:
            jscode('out.push(arg)')
    jscode('console.log.apply(console, out)')


class map:

    def __init__(self, func, iterable):
        self.func = func
        self.iterable = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        n = next(self.iterable)
        r = self.func(n)
        return r

    def __repr__(self):
        return '<builtins.map xxx>'


def jstype(obj):
    return obj.__jstype__()


def hash(obj):
    return obj.__hash__()


def iter(obj):
    return obj.__iter__()


def next(obj):
    if jscode('obj.next !== undefined'):
        r = jscode('obj.next()')
        if jscode('r.done'):
            raise StopIteration
        else:
            return jscode('r.value')
    return obj.__next__()


def len(obj):
    return obj.__len__()


def abs(obj):
    return obj.__abs__()


def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True


def any(iterable):
    for element in iterable:
        if element:
            return True
    return False


def callable(obj):
    if jscode("{}.toString.call(obj) == '[object Function]'"):
        return True
    if jscode('obj.__metaclass__ !== undefined'):
        return True
    if jscode("lookup(obj, '__call__')"):
        return True
    return False


def classmethod(func):
    func.classmethod = True
    return func


def staticmethod(func):
    func.staticmethod = True
    return func


class enumerate:

    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self.index = 0

    def __repr__(self):
        return '<enumerate object at 0x1234567890>'

    def __iter__(self):
        return self

    def __next__(self):
        index = self.index
        self.index = self.index + 1
        return (index, next(self.iterator))


def getattr(obj, attr, d):
    r = lookup(obj, attr)
    if jscode('r === undefined'):
        if jscode('d === undefined'):
            raise AttributeError
        else:
            return d
    else:
        return r
