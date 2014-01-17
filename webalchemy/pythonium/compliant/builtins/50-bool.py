class bool(int):

    def __init__(self, obj):
        if jscode('obj !== undefined'):
            self.jsobject = pythonium_is_true(obj)
        else:
            self.jsobject = jscode('false')

    def __jstype__(self):
        return self.jsobject

    def __repr__(self):
        if self.jsobject:
            return 'True'
        return 'False'

    def __and__(self, other):
        if self:
            if other:
                return True
        return False

    def __or__(self, other):
        if self:
            return True
        if other:
            return True
        return False

    def __is__(self, other):
        if jscode('self === other'):
            return True
        return False

    def __neg__(self):
        if self:
            return False
        return True

    def __not__(self):
        if self:
            return False
        return True


__TRUE = bool(jscode('true'))
__FALSE = bool()
