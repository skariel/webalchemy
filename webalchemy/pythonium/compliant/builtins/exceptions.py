class Exception:
    
    def __init__(self, message):
        self.message = message


class TypeError(Exception):
    pass


class AttributeError(Exception):
    pass


class KeyError(Exception):
    pass


class StopIteration(Exception):
    pass


class NotImplementedError(Exception):
    pass


class NotImplemented(Exception):
    pass


class ValueError(Exception):
    pass
