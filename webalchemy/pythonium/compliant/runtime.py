object = {__bases__: [], __name__: 'object'}
object.__mro__ = [object]

type = {__bases__: [object], __mro__: [object], __name__: 'type'}

object.__metaclass__ = type


__ARGUMENTS_PADDING__ = {ARGUMENTS_PADDING: "YES IT IS!"}


def __is__(me, other):
    return (me is other)
__is__.is_method = True
object.__is__ = __is__

def __isnot__(me, other):
    return not (me is other)
__isnot__.is_method = True
object.__isnot__ = __isnot__

def mro(me):
    if me is object:
        raw = me.__mro__
    elif me.__class__:
        raw = me.__class__.__mro__
    else:
        raw = me.__mro__
    l = pythonium_call(tuple)
    l.jsobject = raw.slice()
    return l
mro.is_method = True
object.mro = mro

def __hash__(me):
    uid = lookup(me, 'uid')
    if not uid:
        uid = object._uid
        object._uid += 1
        me.__uid__ = uid
    return pythonium_call(str, '{' + uid)
__hash__.is_method = True
object._uid = 1
object.__hash__ = __hash__


def __rcontains__(me, other):
    contains = lookup(other, '__contains__')
    return contains(me)
__rcontains__.is_method = True
object.__rcontains__ = __rcontains__


def issubclass(klass, other):
    if klass is other:
        return __TRUE
    if not klass.__bases__:
        return __FALSE
    for base in klass.__bases__:
        if issubclass(base, other) is __TRUE:
            return __TRUE
    return __FALSE


def pythonium_is_true(v):
    if v is False:
        return False
    if v is True:
        return True
    if v is None:
        return False
    if v is __NONE:
        return False
    if v is __FALSE:
        return False
    if isinstance(v, int) or isinstance(v, float):
        if v.jsobject == 0:
            return False
    length = lookup(v, '__len__')
    if length and length().jsobject == 0:
        return False
    return True


def isinstance(obj, klass):
    if obj.__class__:
        return issubclass(obj.__class__, klass)
    return __FALSE

def pythonium_obj_to_js_exception(obj):
    def exception():
        this.exception = obj
    return exception


def pythonium_is_exception(obj, exc):
    if obj is exc:
        return True
    return isinstance(obj, exc)


def pythonium_call(obj):
    args = Array.prototype.slice.call(arguments, 1)
    if obj.__metaclass__:
        instance = {__class__: obj}
        init = lookup(instance, '__init__')
        if init:
            init.apply(instance, args)
        return instance
    else:
        return obj.apply(None, args)

def pythonium_create_empty_dict():
    instance = {__class__: dict}
    instance._keys = pythonium_call(list)
    instance.jsobject = JSObject()
    return instance


def pythonium_mro(bases):
    """Calculate the Method Resolution Order of bases using the C3 algorithm.

    Suppose you intended creating a class K with the given base classes. This
    function returns the MRO which K would have, *excluding* K itself (since
    it doesn't yet exist), as if you had actually created the class.

    Another way of looking at this, if you pass a single class K, this will
    return the linearization of K (the MRO of K, *including* itself).
    """
    # based on http://code.activestate.com/recipes/577748-calculate-the-mro-of-a-class/
    seqs = [C.__mro__.slice() for C in bases]
    seqs.push(bases.slice())
    
    def cdr(l):
        l = l.slice()
        l = l.splice(1)
        return l
    def contains(l, c):
        for i in l:
            if i is c:
                return True
        return False
    res = []
    while True:
        non_empty = []
        for seq in seqs:
            out = []
            for item in seq:
                if item:
                    out.push(item)
            if out.length != 0:
                non_empty.push(out)
        if non_empty.length == 0:
            # Nothing left to process, we're done.
            return res
        for seq in non_empty:  # Find merge candidates among seq heads.
            candidate = seq[0]
            not_head = []
            for s in non_empty:
                if contains(cdr(s), candidate):
                    not_head.push(s)
            if not_head.length != 0:
                candidate = None
            else:
                break
        if not candidate:
            raise TypeError("Inconsistent hierarchy, no C3 MRO is possible")
        res.push(candidate)
        for seq in non_empty:
            # Remove candidate.
            if seq[0] is candidate:
                seq[0] = None
        seqs = non_empty


def pythonium_create_class(name, bases, attrs):
    attrs.__name__ = name
    attrs.__metaclass__ = type
    attrs.__bases__ = bases
    mro = pythonium_mro(bases)
    mro.splice(0, 0, attrs)
    attrs.__mro__ = mro
    return attrs


def lookup(obj, attr):
    obj_attr = obj[attr]
    if obj_attr != None:
        if obj_attr and {}.toString.call(obj_attr) == '[object Function]' and obj_attr.is_method and not obj_attr.bound:
            def method_wrapper():
                args = Array.prototype.slice.call(arguments)
                args.splice(0, 0, obj)
                return obj_attr.apply(None, args)
            method_wrapper.bound = True
            return method_wrapper
        return obj_attr
    else:
        if obj.__class__:
            __mro__ = obj.__class__.__mro__
        elif obj.__metaclass__:
            __mro__ = obj.__metaclass__.__mro__
        else:
            # it's a function
            return None
        for base in __mro__:
            class_attr = base[attr]
            if class_attr != None:
                if {}.toString.call(class_attr) == '[object Function]' and class_attr.is_method and not class_attr.bound:
                    def method_wrapper():
                        args = Array.prototype.slice.call(arguments)
                        args.splice(0, 0, obj)
                        return class_attr.apply(None, args)
                    method_wrapper.bound = True
                    return method_wrapper
                return class_attr


def pythonium_object_get_attribute(obj, attr):
    r = lookup(obj, attr)
    if r != None:
        return r
    else:
        getattr = lookup(obj, '__getattr__')
        if getattr:
            return getattr(attr)
        else:
            console.trace('AttributeError', attr, obj)
            raise AttributeError
pythonium_object_get_attribute.is_method = True
object.__getattribute__ = pythonium_object_get_attribute


def pythonium_get_attribute(obj, attr):
    if obj.__class__ or obj.__metaclass__:
        getattribute = lookup(obj, '__getattribute__')
        r = getattribute(attr)
        return r
    attr = obj[attr]
    if attr:
        if {}.toString.call(attr) == '[object Function]':
            def method_wrapper():
                return attr.apply(obj, arguments)
            return method_wrapper
        else:
            return attr


def pythonium_set_attribute(obj, attr, value):
    obj[attr] = value


def ASSERT(condition, message):
    if not condition:
        raise message or pythonium_call(str, 'Assertion failed')
