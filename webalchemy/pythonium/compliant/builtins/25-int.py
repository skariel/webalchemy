class int:

    def __init__(self, jsobject):
        self.jsobject = jsobject

    def __not__(self):
        jsobject = self.jsobject
        if jscode('jsobject == 0'):
            return True
        return False

    def __abs__(self):
        if self < 0:
            return -self
        return self

    def __neg__(self):
        jsobject = self.jsobject
        return int(jscode('-self.jsobject'))

    def __hash__(self):
        return str(self.jsobject)

    def __jstype__(self):
        return self.jsobject

    def __repr__(self):
        jsobject = self.jsobject
        return str(jscode('jsobject.toString()'))

    def __add__(self, other):
        a = self.jsobject
        b = other.jsobject
        return int(jscode('a + b'))

    def __sub__(self, other):
        a = self.jsobject
        b = other.jsobject
        return int(jscode('a - b'))

    def __lt__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a < b'):
            return True
        return False

    def __gt__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a > b'):
            return True
        return False        

    def __gte__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a >= b'):
            return True
        return False        

    def __lte__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a <= b'):
            return True
        return False

    def __mul__(self, other):
        a = self.jsobject
        b = other.jsobject
        c = jscode('a * b')
        return int(c)

    def __or__(self, other):
        a = self.jsobject
        b = other.jsobject
        c = jscode('a || b')
        return int(c)

    def __eq__(self, other):
        a = self.jsobject
        b = other.jsobject
        if jscode('a == b'):
            return True
        return False

    def __neq__(self, other):
        return not self.__eq__(other)

    def __div__(self, other):
        a = self.jsobject
        b = other.jsobject
        return int(jscode('a / b'))

    def __mod__(self, other):
        a = self.jsobject
        b = other.jsobject
        return int(jscode('a % b'))

