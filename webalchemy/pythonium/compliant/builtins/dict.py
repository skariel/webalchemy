def nest_str_with_quotes(s):
    r = repr(s)
    if isinstance(s, str):
        if "'" in r:
            r = '"' + r + '"'
        else:
            r = "'" + r + "'"
    return r

class dict:

    def __init__(self):
        self._keys = list()
        self.jsobject = JSObject()

    def __hash__(self):
        raise TypeError("unhashable type: 'dict'")

    def __jstype__(self):
        raise NotImplementedError

    def __repr__(self):
        out = []
        for key in self._keys:
            key_repr = nest_str_with_quotes(key)
            value_repr = nest_str_with_quotes(self[key])
            out.append(key_repr + ': ' + value_repr)
        return "{" + ", ".join(out) + "}"

    def get(self, key, d=None):
        if key in self._keys:
            h = jstype(hash(key))
            jsobject = self.jsobject
            return jscode('jsobject[h]')
        return d

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return ListIterator(self._keys)

    def __getitem__(self, key):
        if key in self._keys:
            h = jstype(hash(key))
            jsobject = self.jsobject
            return jscode('jsobject[h]')
        raise KeyError(key)

    def __setitem__(self, key, value):
        h = jstype(hash(key))
        jsobject = self.jsobject
        jscode('jsobject[h] = value')
        self._keys.append(key)

    def keys(self):
        return self._keys

    def items(self):
        out = list()
        for key in self._keys:
            out.append([key, self[key]])
        return out

    def __delitem__(self, key):
        if key in self._keys:
            self._keys.remove(key)
            h = jstype(hash(key))
            jsobject = self.jsobject
            jscode('delete jsobject[h]')
        else:
            raise KeyError
