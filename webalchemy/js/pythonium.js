object = {__bases__:[],__name__:"object"};
object.__mro__ = [object];
type = {__bases__:[object],__mro__:[object],__name__:"type"};
object.__metaclass__ = type;
__ARGUMENTS_PADDING__ = {ARGUMENTS_PADDING:"YES IT IS!"};
var __is__ = function(me, other) {
    return (me === other);
};
__is__.is_method = true;
object.__is__ = __is__;
var __isnot__ = function(me, other) {
    return !(me === other);
};
__isnot__.is_method = true;
object.__isnot__ = __isnot__;
var mro = function(me) {
    var l,raw;
    if((me === object)) {
        raw = me.__mro__;
    }
    else {
        if(me.__class__) {
            raw = me.__class__.__mro__;
        }
        else {
            raw = me.__mro__;
        }
    }
    l = pythonium_call(tuple);
    l.jsobject = raw.slice();
    return l;
};
mro.is_method = true;
object.mro = mro;
var __hash__ = function(me) {
    var uid;
    uid = lookup(me, "uid");
    if(!uid) {
        uid = object._uid;
        object._uid = object._uid + 1;
        me.__uid__ = uid;
    }
    return pythonium_call(str, ("{" + uid));
};
__hash__.is_method = true;
object._uid = 1;
object.__hash__ = __hash__;
var __rcontains__ = function(me, other) {
    var contains;
    contains = lookup(other, "__contains__");
    return contains(me);
};
__rcontains__.is_method = true;
object.__rcontains__ = __rcontains__;
var issubclass = function(klass, other) {
    if((klass === other)) {
        return __TRUE;
    }
    if(!klass.__bases__) {
        return __FALSE;
    }
    var iterator_base = klass.__bases__;
    for (var base_iterator_index=0; base_iterator_index < iterator_base.length; base_iterator_index++) {
        var base = iterator_base[base_iterator_index];
        if((issubclass(base, other) === __TRUE)) {
            return __TRUE;
        }
    }
    return __FALSE;
};
var pythonium_is_true = function(v) {
    var length;
    if((v === false)) {
        return false;
    }
    if((v === true)) {
        return true;
    }
    if((v === undefined)) {
        return false;
    }
    if((v === __NONE)) {
        return false;
    }
    if((v === __FALSE)) {
        return false;
    }
    if((isinstance(v, int)||isinstance(v, float))) {
        if((v.jsobject == 0)) {
            return false;
        }
    }
    length = lookup(v, "__len__");
    if((length&&(length().jsobject == 0))) {
        return false;
    }
    return true;
};
var isinstance = function(obj, klass) {
    if(obj.__class__) {
        return issubclass(obj.__class__, klass);
    }
    return __FALSE;
};
var pythonium_obj_to_js_exception = function(obj) {
    var exception = function() {
        this.exception = obj;
    };
    return exception;
};
var pythonium_is_exception = function(obj, exc) {
    if((obj === exc)) {
        return true;
    }
    return isinstance(obj, exc);
};
var pythonium_call = function(obj) {
    var args,instance,init;
    args = Array.prototype.slice.call(arguments, 1);
    if(obj.__metaclass__) {
        instance = {__class__:obj};
        init = lookup(instance, "__init__");
        if(init) {
            init.apply(instance, args);
        }
        return instance;
    }
    else {
        return obj.apply(undefined, args);
    }
};
var pythonium_create_empty_dict = function() {
    var instance;
    instance = {__class__:dict};
    instance._keys = pythonium_call(list);
    instance.jsobject = Object();
    return instance;
};
var pythonium_mro = function(bases) {
    var seqs,candidate,res,not_head,non_empty,out;
    "Calculate the Method Resolution Order of bases using the C3 algorithm.\n\n    Suppose you intended creating a class K with the given base classes. This\n    function returns the MRO which K would have, *excluding* K itself (since\n    it doesn't yet exist), as if you had actually created the class.\n\n    Another way of looking at this, if you pass a single class K, this will\n    return the linearization of K (the MRO of K, *including* itself).\n    ";
    var __comp18__ = [];
    var __iterator19__ = bases;
    for (var __index20__ = 0; __index20__<__iterator19__.length; __index20__++) {
        var C = __iterator19__[__index20__];
        __comp18__.push(C.__mro__.slice());
    }
    seqs = __comp18__;
    seqs.push(bases.slice());
    var cdr = function(l) {
        l = l.slice();
        l = l.splice(1);
        return l;
    };
    var contains = function(l, c) {
        var iterator_i = l;
        for (var i_iterator_index=0; i_iterator_index < iterator_i.length; i_iterator_index++) {
            var i = iterator_i[i_iterator_index];
            if((i === c)) {
                return true;
            }
        }
        return false;
    };
    res = [];
    while(true) {
        non_empty = [];
        var iterator_seq = seqs;
        for (var seq_iterator_index=0; seq_iterator_index < iterator_seq.length; seq_iterator_index++) {
            var seq = iterator_seq[seq_iterator_index];
            out = [];
            var iterator_item = seq;
            for (var item_iterator_index=0; item_iterator_index < iterator_item.length; item_iterator_index++) {
                var item = iterator_item[item_iterator_index];
                if(item) {
                    out.push(item);
                }
            }
            if((out.length != 0)) {
                non_empty.push(out);
            }
        }
        if((non_empty.length == 0)) {
            return res;
        }
        var iterator_seq = non_empty;
        for (var seq_iterator_index=0; seq_iterator_index < iterator_seq.length; seq_iterator_index++) {
            var seq = iterator_seq[seq_iterator_index];
            candidate = seq[0];
            not_head = [];
            var iterator_s = non_empty;
            for (var s_iterator_index=0; s_iterator_index < iterator_s.length; s_iterator_index++) {
                var s = iterator_s[s_iterator_index];
                if(contains(cdr(s), candidate)) {
                    not_head.push(s);
                }
            }
            if((not_head.length != 0)) {
                candidate = undefined;
            }
            else {
                break;
            }
        }
        if(!candidate) {
            throw TypeError("Inconsistent hierarchy, no C3 MRO is possible");
        }
        res.push(candidate);
        var iterator_seq = non_empty;
        for (var seq_iterator_index=0; seq_iterator_index < iterator_seq.length; seq_iterator_index++) {
            var seq = iterator_seq[seq_iterator_index];
            if((seq[0] === candidate)) {
                seq[0] = undefined;
            }
        }
        seqs = non_empty;
    }
};
var pythonium_create_class = function(name, bases, attrs) {
    var mro;
    attrs.__name__ = name;
    attrs.__metaclass__ = type;
    attrs.__bases__ = bases;
    mro = pythonium_mro(bases);
    mro.splice(0, 0, attrs);
    attrs.__mro__ = mro;
    return attrs;
};
var lookup = function(obj, attr) {
    var class_attr,obj_attr,__mro__;
    obj_attr = obj[attr];
    if((obj_attr != undefined)) {
        if((obj_attr&&({}.toString.call(obj_attr) == "[object Function]")&&obj_attr.is_method&&!obj_attr.bound)) {
            var method_wrapper = function() {
                var args;
                args = Array.prototype.slice.call(arguments);
                args.splice(0, 0, obj);
                return obj_attr.apply(undefined, args);
            };
            method_wrapper.bound = true;
            return method_wrapper;
        }
        return obj_attr;
    }
    else {
        if(obj.__class__) {
            __mro__ = obj.__class__.__mro__;
        }
        else {
            if(obj.__metaclass__) {
                __mro__ = obj.__metaclass__.__mro__;
            }
            else {
                return undefined;
            }
        }
        var iterator_base = __mro__;
        for (var base_iterator_index=0; base_iterator_index < iterator_base.length; base_iterator_index++) {
            var base = iterator_base[base_iterator_index];
            class_attr = base[attr];
            if((class_attr != undefined)) {
                if((({}.toString.call(class_attr) == "[object Function]")&&class_attr.is_method&&!class_attr.bound)) {
                    var method_wrapper = function() {
                        var args;
                        args = Array.prototype.slice.call(arguments);
                        args.splice(0, 0, obj);
                        return class_attr.apply(undefined, args);
                    };
                    method_wrapper.bound = true;
                    return method_wrapper;
                }
                return class_attr;
            }
        }
    }
};
var pythonium_object_get_attribute = function(obj, attr) {
    var getattr,r;
    r = lookup(obj, attr);
    if((r != undefined)) {
        return r;
    }
    else {
        getattr = lookup(obj, "__getattr__");
        if(getattr) {
            return getattr(attr);
        }
        else {
            console.trace("AttributeError", attr, obj);
            throw AttributeError;
        }
    }
};
pythonium_object_get_attribute.is_method = true;
object.__getattribute__ = pythonium_object_get_attribute;
var pythonium_get_attribute = function(obj, attr) {
    var getattribute,r;
    if((obj.__class__||obj.__metaclass__)) {
        getattribute = lookup(obj, "__getattribute__");
        r = getattribute(attr);
        return r;
    }
    attr = obj[attr];
    if(attr) {
        if(({}.toString.call(attr) == "[object Function]")) {
            var method_wrapper = function() {
                return attr.apply(obj, arguments);
            };
            return method_wrapper;
        }
        else {
            return attr;
        }
    }
};
var pythonium_set_attribute = function(obj, attr, value) {
    obj[attr] = value;
};
var ASSERT = function(condition, message) {
    if(!condition) {
        throw (message||pythonium_call(str, "Assertion failed"));
    }
};
/* class definition int */
var __int___init__ = function(self, jsobject) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "jsobject", jsobject);
};
__int___init__.is_method = true;

var __int___not__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    if (pythonium_is_true(jsobject == 0)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___not__.is_method = true;

var __int___abs__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(self, "__lt__")(pythonium_call(int, 0))))) {
        return pythonium_call(pythonium_get_attribute(self, "__neg__"));
    }
    return self;
};
__int___abs__.is_method = true;

var __int___neg__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments0 = [int, -self.jsobject];
    return pythonium_call.apply(undefined, call_arguments0);
};
__int___neg__.is_method = true;

var __int___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments1 = [str, pythonium_get_attribute(self, "jsobject")];
    return pythonium_call.apply(undefined, call_arguments1);
};
__int___hash__.is_method = true;

var __int___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_get_attribute(self, "jsobject");
};
__int___jstype__.is_method = true;

var __int___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments2 = [str, jsobject.toString()];
    return pythonium_call.apply(undefined, call_arguments2);
};
__int___repr__.is_method = true;

var __int___add__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments3 = [int, a + b];
    return pythonium_call.apply(undefined, call_arguments3);
};
__int___add__.is_method = true;

var __int___sub__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments4 = [int, a - b];
    return pythonium_call.apply(undefined, call_arguments4);
};
__int___sub__.is_method = true;

var __int___lt__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a < b)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___lt__.is_method = true;

var __int___gt__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a > b)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___gt__.is_method = true;

var __int___gte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a >= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___gte__.is_method = true;

var __int___lte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a <= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___lte__.is_method = true;

var __int___mul__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var c,b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    c = a * b;
    var call_arguments5 = [int, c];
    return pythonium_call.apply(undefined, call_arguments5);
};
__int___mul__.is_method = true;

var __int___or__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var c,b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    c = a || b;
    var call_arguments6 = [int, c];
    return pythonium_call.apply(undefined, call_arguments6);
};
__int___or__.is_method = true;

var __int___eq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a == b)) {
        return __TRUE;
    }
    return __FALSE;
};
__int___eq__.is_method = true;

var __int___neq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments7 = [pythonium_get_attribute(self, "__eq__"), other];
    return pythonium_call(pythonium_get_attribute(pythonium_call.apply(undefined, call_arguments7), "__not__"));
};
__int___neq__.is_method = true;

var __int___div__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments8 = [int, a / b];
    return pythonium_call.apply(undefined, call_arguments8);
};
__int___div__.is_method = true;

var __int___mod__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments9 = [int, a % b];
    return pythonium_call.apply(undefined, call_arguments9);
};
__int___mod__.is_method = true;

var int = pythonium_create_class("int", [object], {
    __init__: __int___init__,
    __not__: __int___not__,
    __abs__: __int___abs__,
    __neg__: __int___neg__,
    __hash__: __int___hash__,
    __jstype__: __int___jstype__,
    __repr__: __int___repr__,
    __add__: __int___add__,
    __sub__: __int___sub__,
    __lt__: __int___lt__,
    __gt__: __int___gt__,
    __gte__: __int___gte__,
    __lte__: __int___lte__,
    __mul__: __int___mul__,
    __or__: __int___or__,
    __eq__: __int___eq__,
    __neq__: __int___neq__,
    __div__: __int___div__,
    __mod__: __int___mod__,
});
/* class definition bool */
var __bool___init__ = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(obj !== undefined)) {
        var call_arguments0 = [pythonium_is_true, obj];
        pythonium_set_attribute(self, "jsobject", pythonium_call.apply(undefined, call_arguments0));
    }
    else {
        pythonium_set_attribute(self, "jsobject", false);
    }
};
__bool___init__.is_method = true;

var __bool___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_get_attribute(self, "jsobject");
};
__bool___jstype__.is_method = true;

var __bool___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(pythonium_get_attribute(self, "jsobject"))) {
        return pythonium_call(str, "True");
    }
    return pythonium_call(str, "False");
};
__bool___repr__.is_method = true;

var __bool___and__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self)) {
        if (pythonium_is_true(other)) {
            return __TRUE;
        }
    }
    return __FALSE;
};
__bool___and__.is_method = true;

var __bool___or__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self)) {
        return __TRUE;
    }
    if (pythonium_is_true(other)) {
        return __TRUE;
    }
    return __FALSE;
};
__bool___or__.is_method = true;

var __bool___is__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self === other)) {
        return __TRUE;
    }
    return __FALSE;
};
__bool___is__.is_method = true;

var __bool___neg__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self)) {
        return __FALSE;
    }
    return __TRUE;
};
__bool___neg__.is_method = true;

var __bool___not__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self)) {
        return __FALSE;
    }
    return __TRUE;
};
__bool___not__.is_method = true;

var bool = pythonium_create_class("bool", [int], {
    __init__: __bool___init__,
    __jstype__: __bool___jstype__,
    __repr__: __bool___repr__,
    __and__: __bool___and__,
    __or__: __bool___or__,
    __is__: __bool___is__,
    __neg__: __bool___neg__,
    __not__: __bool___not__,
});
var call_arguments1 = [bool, true];
__TRUE = pythonium_call.apply(undefined, call_arguments1);
var call_arguments2 = [bool];
__FALSE = pythonium_call.apply(undefined, call_arguments2);
var nest_str_with_quotes = function(s) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var r;
    /* BEGIN function */
    var call_arguments0 = [repr, s];
    r = pythonium_call.apply(undefined, call_arguments0);
    var call_arguments1 = [isinstance, s, str];
    if (pythonium_is_true(pythonium_call.apply(undefined, call_arguments1))) {
        if (pythonium_is_true((pythonium_get_attribute(pythonium_call(str, "'"), "__rcontains__")(r)))) {
            r = (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(pythonium_call(str, '"'), "__add__"), r)), "__add__"), pythonium_call(str, '"')));
        }
        else {
            r = (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(pythonium_call(str, "'"), "__add__"), r)), "__add__"), pythonium_call(str, "'")));
        }
    }
    return r;
};

/* class definition dict */
var __dict___init__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments2 = [list];
    pythonium_set_attribute(self, "_keys", pythonium_call.apply(undefined, call_arguments2));
    pythonium_set_attribute(self, "jsobject", Object());
};
__dict___init__.is_method = true;

var __dict___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments3 = [TypeError, pythonium_call(str, "unhashable type: 'dict'")];
    throw pythonium_call.apply(undefined, call_arguments3);
};
__dict___hash__.is_method = true;

var __dict___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    throw NotImplementedError;
};
__dict___jstype__.is_method = true;

var __dict___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var out,key_repr,value_repr;
    /* BEGIN function */
    out = pythonium_call(list);
    try {
        var __next4__ = pythonium_get_attribute(iter(pythonium_get_attribute(self, "_keys")), "__next__");
        while(true) {
            var key = __next4__();
            var call_arguments5 = [nest_str_with_quotes, key];
            key_repr = pythonium_call.apply(undefined, call_arguments5);
            var call_arguments6 = [nest_str_with_quotes, pythonium_call(pythonium_get_attribute(self, '__getitem__'), key)];
            value_repr = pythonium_call.apply(undefined, call_arguments6);
            var call_arguments7 = [pythonium_get_attribute(out, "append"), (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(key_repr, "__add__"), pythonium_call(str, ": "))), "__add__"), value_repr))];
            pythonium_call.apply(undefined, call_arguments7);
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    var call_arguments8 = [pythonium_get_attribute(pythonium_call(str, ", "), "join"), out];
    return (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(pythonium_call(str, "{"), "__add__"), pythonium_call.apply(undefined, call_arguments8))), "__add__"), pythonium_call(str, "}")));
};
__dict___repr__.is_method = true;

var __dict_get = function(self, key, d) {
    /* BEGIN arguments unpacking */
    var __args = Array.prototype.slice.call(arguments);
    if (__args[__args.length - 2] === __ARGUMENTS_PADDING__) {
        var __kwargs = __args[__args.length - 1];
        var varkwargs_start = __args.length - 2;
    } else {
        var __kwargs = pythonium_create_empty_dict();
        var varkwargs_start = undefined;
    }
    if (varkwargs_start !== undefined && 2 > varkwargs_start) {
        d = __kwargs.__class__.get(__kwargs, d) || __NONE;
    } else {
        d = d || __kwargs.__class__.get(__kwargs, d) || __NONE;
    }
    /* END arguments unpacking */
    var jsobject,h;
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(key, "__rcontains__")(pythonium_get_attribute(self, "_keys"))))) {
        var call_arguments9 = [hash, key];
        var call_arguments10 = [jstype, pythonium_call.apply(undefined, call_arguments9)];
        h = pythonium_call.apply(undefined, call_arguments10);
        jsobject = pythonium_get_attribute(self, "jsobject");
        return jsobject[h];
    }
    return d;
};
__dict_get.is_method = true;

var __dict___len__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments11 = [len, pythonium_get_attribute(self, "_keys")];
    return pythonium_call.apply(undefined, call_arguments11);
};
__dict___len__.is_method = true;

var __dict___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments12 = [ListIterator, pythonium_get_attribute(self, "_keys")];
    return pythonium_call.apply(undefined, call_arguments12);
};
__dict___iter__.is_method = true;

var __dict___getitem__ = function(self, key) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,h;
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(key, "__rcontains__")(pythonium_get_attribute(self, "_keys"))))) {
        var call_arguments13 = [hash, key];
        var call_arguments14 = [jstype, pythonium_call.apply(undefined, call_arguments13)];
        h = pythonium_call.apply(undefined, call_arguments14);
        jsobject = pythonium_get_attribute(self, "jsobject");
        return jsobject[h];
    }
    var call_arguments15 = [KeyError, key];
    throw pythonium_call.apply(undefined, call_arguments15);
};
__dict___getitem__.is_method = true;

var __dict___setitem__ = function(self, key, value) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,h;
    /* BEGIN function */
    var call_arguments16 = [hash, key];
    var call_arguments17 = [jstype, pythonium_call.apply(undefined, call_arguments16)];
    h = pythonium_call.apply(undefined, call_arguments17);
    jsobject = pythonium_get_attribute(self, "jsobject");
    jsobject[h] = value;
    var call_arguments18 = [pythonium_get_attribute(pythonium_get_attribute(self, "_keys"), "append"), key];
    pythonium_call.apply(undefined, call_arguments18);
};
__dict___setitem__.is_method = true;

var __dict_keys = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_get_attribute(self, "_keys");
};
__dict_keys.is_method = true;

var __dict_items = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var out;
    /* BEGIN function */
    var call_arguments19 = [list];
    out = pythonium_call.apply(undefined, call_arguments19);
    try {
        var __next20__ = pythonium_get_attribute(iter(pythonium_get_attribute(self, "_keys")), "__next__");
        while(true) {
            var key = __next20__();
            var __a_list21 = pythonium_call(list);
            __a_list21.jsobject = [key, pythonium_call(pythonium_get_attribute(self, '__getitem__'), key)];
            var call_arguments22 = [pythonium_get_attribute(out, "append"), __a_list21];
            pythonium_call.apply(undefined, call_arguments22);
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return out;
};
__dict_items.is_method = true;

var __dict___delitem__ = function(self, key) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,h;
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(key, "__rcontains__")(pythonium_get_attribute(self, "_keys"))))) {
        var call_arguments23 = [pythonium_get_attribute(pythonium_get_attribute(self, "_keys"), "remove"), key];
        pythonium_call.apply(undefined, call_arguments23);
        var call_arguments24 = [hash, key];
        var call_arguments25 = [jstype, pythonium_call.apply(undefined, call_arguments24)];
        h = pythonium_call.apply(undefined, call_arguments25);
        jsobject = pythonium_get_attribute(self, "jsobject");
        delete jsobject[h];
    }
    else {
        throw KeyError;
    }
};
__dict___delitem__.is_method = true;

var dict = pythonium_create_class("dict", [object], {
    __init__: __dict___init__,
    __hash__: __dict___hash__,
    __jstype__: __dict___jstype__,
    __repr__: __dict___repr__,
    get: __dict_get,
    __len__: __dict___len__,
    __iter__: __dict___iter__,
    __getitem__: __dict___getitem__,
    __setitem__: __dict___setitem__,
    keys: __dict_keys,
    items: __dict_items,
    __delitem__: __dict___delitem__,
});
/* class definition Exception */
var __Exception___init__ = function(self, message) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "message", message);
};
__Exception___init__.is_method = true;

var Exception = pythonium_create_class("Exception", [object], {
    __init__: __Exception___init__,
});
/* class definition TypeError */
/* pass */
var TypeError = pythonium_create_class("TypeError", [Exception], {
});
/* class definition AttributeError */
/* pass */
var AttributeError = pythonium_create_class("AttributeError", [Exception], {
});
/* class definition KeyError */
/* pass */
var KeyError = pythonium_create_class("KeyError", [Exception], {
});
/* class definition StopIteration */
/* pass */
var StopIteration = pythonium_create_class("StopIteration", [Exception], {
});
/* class definition NotImplementedError */
/* pass */
var NotImplementedError = pythonium_create_class("NotImplementedError", [Exception], {
});
/* class definition NotImplemented */
/* pass */
var NotImplemented = pythonium_create_class("NotImplemented", [Exception], {
});
/* class definition ValueError */
/* pass */
var ValueError = pythonium_create_class("ValueError", [Exception], {
});
/* class definition float */
var __float___init__ = function(self, jsobject) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "jsobject", jsobject);
};
__float___init__.is_method = true;

var __float___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments0 = [str, pythonium_get_attribute(self, "jsobject")];
    return pythonium_call.apply(undefined, call_arguments0);
};
__float___hash__.is_method = true;

var __float___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments1 = [str, jsobject.toString()];
    return pythonium_call.apply(undefined, call_arguments1);
};
__float___repr__.is_method = true;

var __float___neg__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments2 = [int, -self.jsobject];
    return pythonium_call.apply(undefined, call_arguments2);
};
__float___neg__.is_method = true;

var __float___abs__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(self, "__lt__")(pythonium_call(int, 0))))) {
        return pythonium_call(pythonium_get_attribute(self, "__neg__"));
    }
    return self;
};
__float___abs__.is_method = true;

var __float___sub__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments3 = [float, a - b];
    return pythonium_call.apply(undefined, call_arguments3);
};
__float___sub__.is_method = true;

var __float___eq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a == b)) {
        return __TRUE;
    }
    return __FALSE;
};
__float___eq__.is_method = true;

var __float___add__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments4 = [int, a + b];
    return pythonium_call.apply(undefined, call_arguments4);
};
__float___add__.is_method = true;

var __float___lt__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a < b)) {
        return __TRUE;
    }
    return __FALSE;
};
__float___lt__.is_method = true;

var __float___gt__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a > b)) {
        return __TRUE;
    }
    return __FALSE;
};
__float___gt__.is_method = true;

var __float___gte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a >= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__float___gte__.is_method = true;

var __float___lte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a <= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__float___lte__.is_method = true;

var __float___mul__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var c,b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    c = a * b;
    var call_arguments5 = [int, c];
    return pythonium_call.apply(undefined, call_arguments5);
};
__float___mul__.is_method = true;

var __float___or__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var c,b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    c = a || b;
    var call_arguments6 = [int, c];
    return pythonium_call.apply(undefined, call_arguments6);
};
__float___or__.is_method = true;

var __float___neq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments7 = [pythonium_get_attribute(self, "__eq__"), other];
    return pythonium_call(pythonium_get_attribute(pythonium_call.apply(undefined, call_arguments7), "__not__"));
};
__float___neq__.is_method = true;

var __float___div__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments8 = [int, a / b];
    return pythonium_call.apply(undefined, call_arguments8);
};
__float___div__.is_method = true;

var float = pythonium_create_class("float", [object], {
    __init__: __float___init__,
    __hash__: __float___hash__,
    __repr__: __float___repr__,
    __neg__: __float___neg__,
    __abs__: __float___abs__,
    __sub__: __float___sub__,
    __eq__: __float___eq__,
    __add__: __float___add__,
    __lt__: __float___lt__,
    __gt__: __float___gt__,
    __gte__: __float___gte__,
    __lte__: __float___lte__,
    __mul__: __float___mul__,
    __or__: __float___or__,
    __neq__: __float___neq__,
    __div__: __float___div__,
});
/* class definition range */
var __range___init__ = function(self, a, b) {
    /* BEGIN arguments unpacking */
    var __args = Array.prototype.slice.call(arguments);
    if (__args[__args.length - 2] === __ARGUMENTS_PADDING__) {
        var __kwargs = __args[__args.length - 1];
        var varkwargs_start = __args.length - 2;
    } else {
        var __kwargs = pythonium_create_empty_dict();
        var varkwargs_start = undefined;
    }
    if (varkwargs_start !== undefined && 2 > varkwargs_start) {
        b = __kwargs.__class__.get(__kwargs, b) || __NONE;
    } else {
        b = b || __kwargs.__class__.get(__kwargs, b) || __NONE;
    }
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(b)) {
        pythonium_set_attribute(self, "index", a);
        pythonium_set_attribute(self, "end", b);
    }
    else {
        pythonium_set_attribute(self, "index", pythonium_call(int, 0));
        pythonium_set_attribute(self, "end", a);
    }
};
__range___init__.is_method = true;

var __range___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return self;
};
__range___iter__.is_method = true;

var __range___next__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var index;
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(pythonium_get_attribute(self, "index"), "__lt__")(pythonium_get_attribute(self, "end"))))) {
        index = pythonium_get_attribute(self, "index");
        pythonium_get_attribute(self, "index") = pythonium_call(pythonium_get_attribute(pythonium_get_attribute(self, "index"), "__add__"), pythonium_call(int, 1));
        return index;
    }
    throw StopIteration;
};
__range___next__.is_method = true;

var range = pythonium_create_class("range", [object], {
    __init__: __range___init__,
    __iter__: __range___iter__,
    __next__: __range___next__,
});
var range = function(a, b) {
    /* BEGIN arguments unpacking */
    var __args = Array.prototype.slice.call(arguments);
    if (__args[__args.length - 2] === __ARGUMENTS_PADDING__) {
        var __kwargs = __args[__args.length - 1];
        var varkwargs_start = __args.length - 2;
    } else {
        var __kwargs = pythonium_create_empty_dict();
        var varkwargs_start = undefined;
    }
    if (varkwargs_start !== undefined && 1 > varkwargs_start) {
        b = __kwargs.__class__.get(__kwargs, b) || __NONE;
    } else {
        b = b || __kwargs.__class__.get(__kwargs, b) || __NONE;
    }
    /* END arguments unpacking */
    var out;
    /* BEGIN function */
    var call_arguments0 = [list];
    out = pythonium_call.apply(undefined, call_arguments0);
    while(pythonium_is_true((pythonium_get_attribute(index, "__lt__")(end)))) {
        var call_arguments1 = [pythonium_get_attribute(out, "append"), index];
        pythonium_call.apply(undefined, call_arguments1);
        index = pythonium_call(pythonium_get_attribute(index, "__add__"), pythonium_call(int, 1));
    }
    return out;
};

var repr = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(obj, "__is__")(object)))) {
        return pythonium_call(str, "<class 'object'>");
    }
    var call_arguments2 = [pythonium_get_attribute(obj, "__repr__")];
    return pythonium_call.apply(undefined, call_arguments2);
};

var print = function() {
    /* BEGIN arguments unpacking */
    var __args = Array.prototype.slice.call(arguments);
    __args = __args.splice(0);
    var args = pythonium_call(tuple);
    args.jsobject = __args;
    /* END arguments unpacking */
    var out,r,name;
    /* BEGIN function */
    out = [];
    try {
        var __next3__ = pythonium_get_attribute(iter(args), "__next__");
        while(true) {
            var arg = __next3__();
            if (pythonium_is_true(arg.__class__ !== undefined)) {
                var call_arguments4 = [repr, arg];
                var call_arguments5 = [jstype, pythonium_call.apply(undefined, call_arguments4)];
                r = pythonium_call.apply(undefined, call_arguments5);
                out.push(r);
            }
            else {
                if (pythonium_is_true(arg.__metaclass__ !== undefined)) {
                    name = arg.__name__;
                    out.push("<class '"+ name +"'>");
                }
                else {
                    out.push(arg);
                }
            }
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    console.log.apply(console, out);
};

/* class definition map */
var __map___init__ = function(self, func, iterable) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "func", func);
    var call_arguments6 = [iter, iterable];
    pythonium_set_attribute(self, "iterable", pythonium_call.apply(undefined, call_arguments6));
};
__map___init__.is_method = true;

var __map___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return self;
};
__map___iter__.is_method = true;

var __map___next__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var n,r;
    /* BEGIN function */
    var call_arguments7 = [next, pythonium_get_attribute(self, "iterable")];
    n = pythonium_call.apply(undefined, call_arguments7);
    var call_arguments8 = [pythonium_get_attribute(self, "func"), n];
    r = pythonium_call.apply(undefined, call_arguments8);
    return r;
};
__map___next__.is_method = true;

var __map___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_call(str, "<builtins.map xxx>");
};
__map___repr__.is_method = true;

var map = pythonium_create_class("map", [object], {
    __init__: __map___init__,
    __iter__: __map___iter__,
    __next__: __map___next__,
    __repr__: __map___repr__,
});
var jstype = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments9 = [pythonium_get_attribute(obj, "__jstype__")];
    return pythonium_call.apply(undefined, call_arguments9);
};

var hash = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments10 = [pythonium_get_attribute(obj, "__hash__")];
    return pythonium_call.apply(undefined, call_arguments10);
};

var iter = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments11 = [pythonium_get_attribute(obj, "__iter__")];
    return pythonium_call.apply(undefined, call_arguments11);
};

var next = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var r;
    /* BEGIN function */
    if (pythonium_is_true(obj.next !== undefined)) {
        r = obj.next();
        if (pythonium_is_true(r.done)) {
            throw StopIteration;
        }
        else {
            return r.value;
        }
    }
    var call_arguments12 = [pythonium_get_attribute(obj, "__next__")];
    return pythonium_call.apply(undefined, call_arguments12);
};

var len = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments13 = [pythonium_get_attribute(obj, "__len__")];
    return pythonium_call.apply(undefined, call_arguments13);
};

var abs = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments14 = [pythonium_get_attribute(obj, "__abs__")];
    return pythonium_call.apply(undefined, call_arguments14);
};

var all = function(iterable) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    try {
        var __next15__ = pythonium_get_attribute(iter(iterable), "__next__");
        while(true) {
            var element = __next15__();
            if (pythonium_is_true(pythonium_call(pythonium_get_attribute(element, "__not__")))) {
                return __FALSE;
            }
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return __TRUE;
};

var any = function(iterable) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    try {
        var __next16__ = pythonium_get_attribute(iter(iterable), "__next__");
        while(true) {
            var element = __next16__();
            if (pythonium_is_true(element)) {
                return __TRUE;
            }
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return __FALSE;
};

var callable = function(obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true({}.toString.call(obj) == '[object Function]')) {
        return __TRUE;
    }
    if (pythonium_is_true(obj.__metaclass__ !== undefined)) {
        return __TRUE;
    }
    if (pythonium_is_true(lookup(obj, '__call__'))) {
        return __TRUE;
    }
    return __FALSE;
};

var classmethod = function(func) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(func, "classmethod", __TRUE);
    return func;
};

var staticmethod = function(func) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(func, "staticmethod", __TRUE);
    return func;
};

/* class definition enumerate */
var __enumerate___init__ = function(self, iterator) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments17 = [iter, iterator];
    pythonium_set_attribute(self, "iterator", pythonium_call.apply(undefined, call_arguments17));
    pythonium_set_attribute(self, "index", pythonium_call(int, 0));
};
__enumerate___init__.is_method = true;

var __enumerate___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_call(str, "<enumerate object at 0x1234567890>");
};
__enumerate___repr__.is_method = true;

var __enumerate___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return self;
};
__enumerate___iter__.is_method = true;

var __enumerate___next__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var index;
    /* BEGIN function */
    index = pythonium_get_attribute(self, "index");
    pythonium_set_attribute(self, "index", (pythonium_call(pythonium_get_attribute(pythonium_get_attribute(self, "index"), "__add__"), pythonium_call(int, 1))));
    var call_arguments18 = [next, pythonium_get_attribute(self, "iterator")];
    var __a_tuple19 = pythonium_call(tuple);
    __a_tuple19.jsobject = [index, pythonium_call.apply(undefined, call_arguments18)];
    return __a_tuple19;
};
__enumerate___next__.is_method = true;

var enumerate = pythonium_create_class("enumerate", [object], {
    __init__: __enumerate___init__,
    __repr__: __enumerate___repr__,
    __iter__: __enumerate___iter__,
    __next__: __enumerate___next__,
});
var getattr = function(obj, attr, d) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var r;
    /* BEGIN function */
    var call_arguments20 = [lookup, obj, attr];
    r = pythonium_call.apply(undefined, call_arguments20);
    if (pythonium_is_true(r === undefined)) {
        if (pythonium_is_true(d === undefined)) {
            throw AttributeError;
        }
        else {
            return d;
        }
    }
    else {
        return r;
    }
};

/* class definition ListIterator */
var __ListIterator___init__ = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "list", obj);
    pythonium_set_attribute(self, "index", pythonium_call(int, 0));
    var call_arguments0 = [len, obj];
    pythonium_set_attribute(self, "length", pythonium_call.apply(undefined, call_arguments0));
};
__ListIterator___init__.is_method = true;

var __ListIterator___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return self;
};
__ListIterator___iter__.is_method = true;

var __ListIterator___next__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var index;
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(pythonium_get_attribute(self, "index"), "__eq__")(pythonium_get_attribute(self, "length"))))) {
        throw StopIteration;
    }
    index = pythonium_get_attribute(self, "index");
    pythonium_set_attribute(self, "index", (pythonium_call(pythonium_get_attribute(pythonium_get_attribute(self, "index"), "__add__"), pythonium_call(int, 1))));
    return pythonium_call(pythonium_get_attribute(pythonium_get_attribute(self, "list"), '__getitem__'), index);
};
__ListIterator___next__.is_method = true;

var ListIterator = pythonium_create_class("ListIterator", [object], {
    __init__: __ListIterator___init__,
    __iter__: __ListIterator___iter__,
    __next__: __ListIterator___next__,
});
/* class definition list */
var __list___init__ = function(self, iterable) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "jsobject", []);
    if (pythonium_is_true(iterable !== undefined)) {
        try {
            var __next1__ = pythonium_get_attribute(iter(iterable), "__next__");
            while(true) {
                var item = __next1__();
                var call_arguments2 = [pythonium_get_attribute(self, "append"), item];
                pythonium_call.apply(undefined, call_arguments2);
            }
        } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    }
};
__list___init__.is_method = true;

var __list___or__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(self)) {
        return self;
    }
    if (pythonium_is_true(other)) {
        return other;
    }
    return __FALSE;
};
__list___or__.is_method = true;

var __list___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments3 = [TypeError, pythonium_call(str, "unhashable type: 'list'")];
    throw pythonium_call.apply(undefined, call_arguments3);
};
__list___hash__.is_method = true;

var __list___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var iterable;
    /* BEGIN function */
    var call_arguments4 = [map, nest_str_with_quotes, self];
    iterable = pythonium_call.apply(undefined, call_arguments4);
    var call_arguments5 = [pythonium_get_attribute(pythonium_call(str, ", "), "join"), iterable];
    return (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(pythonium_call(str, "["), "__add__"), pythonium_call.apply(undefined, call_arguments5))), "__add__"), pythonium_call(str, "]")));
};
__list___repr__.is_method = true;

var __list___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var out,item;
    /* BEGIN function */
    out = [];
    try {
        var __next6__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next6__();
            var call_arguments7 = [jstype, item];
            item = pythonium_call.apply(undefined, call_arguments7);
            out.push(item);
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return out;
};
__list___jstype__.is_method = true;

var __list_append = function(self, item) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    jsobject.push(item);
};
__list_append.is_method = true;

var __list_insert = function(self, index, item) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments8 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "splice"), index, pythonium_call(int, 0), item];
    pythonium_call.apply(undefined, call_arguments8);
};
__list_insert.is_method = true;

var __list___setitem__ = function(self, index, value) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    index = pythonium_get_attribute(index, "jsobject");
    jsobject[index] = value;
};
__list___setitem__.is_method = true;

var __list___getitem__ = function(self, s) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,index;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments9 = [jstype, s];
    index = pythonium_call.apply(undefined, call_arguments9);
    return jsobject[index];
};
__list___getitem__.is_method = true;

var __list___len__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,length;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    length = jsobject.length;
    var call_arguments10 = [int, length];
    return pythonium_call.apply(undefined, call_arguments10);
};
__list___len__.is_method = true;

var __list___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments11 = [ListIterator, self];
    return pythonium_call.apply(undefined, call_arguments11);
};
__list___iter__.is_method = true;

var __list___contains__ = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    try {
        var __next12__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next12__();
            if (pythonium_is_true((pythonium_get_attribute(obj, "__eq__")(item)))) {
                return __TRUE;
            }
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return __FALSE;
};
__list___contains__.is_method = true;

var __list_pop = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments13 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "pop")];
    return pythonium_call.apply(undefined, call_arguments13);
};
__list_pop.is_method = true;

var __list_index = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var index;
    /* BEGIN function */
    index = pythonium_call(int, 0);
    try {
        var __next14__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next14__();
            if (pythonium_is_true((pythonium_get_attribute(item, "__eq__")(obj)))) {
                return index;
            }
            index = pythonium_call(pythonium_get_attribute(index, "__add__"), pythonium_call(int, 1));
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    throw ValueError;
};
__list_index.is_method = true;

var __list_remove = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,index;
    /* BEGIN function */
    var call_arguments15 = [pythonium_get_attribute(self, "index"), obj];
    index = pythonium_call.apply(undefined, call_arguments15);
    jsobject = pythonium_get_attribute(self, "jsobject");
    jsobject.splice(jstype(index), 1);
};
__list_remove.is_method = true;

var __list___delitem__ = function(self, index) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments16 = [jstype, index];
    var call_arguments17 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "splice"), pythonium_call.apply(undefined, call_arguments16), pythonium_call(int, 1)];
    pythonium_call.apply(undefined, call_arguments17);
};
__list___delitem__.is_method = true;

var list = pythonium_create_class("list", [object], {
    __init__: __list___init__,
    __or__: __list___or__,
    __hash__: __list___hash__,
    __repr__: __list___repr__,
    __jstype__: __list___jstype__,
    append: __list_append,
    insert: __list_insert,
    __setitem__: __list___setitem__,
    __getitem__: __list___getitem__,
    __len__: __list___len__,
    __iter__: __list___iter__,
    __contains__: __list___contains__,
    pop: __list_pop,
    index: __list_index,
    remove: __list_remove,
    __delitem__: __list___delitem__,
});
/* class definition _None */
var ___None___and__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(other, "__is__")(__TRUE)))) {
        return __TRUE;
    }
    return __FALSE;
};
___None___and__.is_method = true;

var ___None___or__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true((pythonium_get_attribute(other, "__is__")(__TRUE)))) {
        return __TRUE;
    }
    return __FALSE;
};
___None___or__.is_method = true;

var ___None___is__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    if (pythonium_is_true(other === self)) {
        return __TRUE;
    }
    return __FALSE;
};
___None___is__.is_method = true;

var ___None___neg__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return __TRUE;
};
___None___neg__.is_method = true;

var ___None___not__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return __TRUE;
};
___None___not__.is_method = true;

var _None = pythonium_create_class("_None", [object], {
    __and__: ___None___and__,
    __or__: ___None___or__,
    __is__: ___None___is__,
    __neg__: ___None___neg__,
    __not__: ___None___not__,
});
var call_arguments0 = [_None];
__NONE = pythonium_call.apply(undefined, call_arguments0);
/* class definition slice */
var __slice___init__ = function(self, start, step, end) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "start", start);
    pythonium_set_attribute(self, "step", step);
    pythonium_set_attribute(self, "end", end);
};
__slice___init__.is_method = true;

var slice = pythonium_create_class("slice", [object], {
    __init__: __slice___init__,
});
/* class definition str */
var __str___init__ = function(self, jsobject) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "jsobject", jsobject);
};
__str___init__.is_method = true;

var __str___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return self;
};
__str___repr__.is_method = true;

var __str___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return pythonium_get_attribute(self, "jsobject");
};
__str___jstype__.is_method = true;

var __str___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    return (pythonium_call(pythonium_get_attribute(pythonium_call(str, '"'), "__add__"), self));
};
__str___hash__.is_method = true;

var __str___contains__ = function(self, s) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,i;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments0 = [jstype, s];
    s = pythonium_call.apply(undefined, call_arguments0);
    i = jsobject.indexOf(s);
    var call_arguments1 = [int, i];
    if (pythonium_is_true((pythonium_get_attribute(pythonium_call.apply(undefined, call_arguments1), "__neq__")(pythonium_call(pythonium_get_attribute(pythonium_call(int, 1), "__neg__")))))) {
        return __TRUE;
    }
    return __FALSE;
};
__str___contains__.is_method = true;

var __str___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments2 = [ListIterator, self];
    return pythonium_call.apply(undefined, call_arguments2);
};
__str___iter__.is_method = true;

var __str_join = function(self, iterable) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var out;
    /* BEGIN function */
    var call_arguments3 = [iter, iterable];
    iterable = pythonium_call.apply(undefined, call_arguments3);
    try {
        var call_arguments4 = [next, iterable];
        out = pythonium_call.apply(undefined, call_arguments4);
    } catch (__exception__) {
        if (pythonium_is_exception(__exception__, StopIteration)) {
            return pythonium_call(str, "");
        }
    }
    try {
        var __next5__ = pythonium_get_attribute(iter(iterable), "__next__");
        while(true) {
            var item = __next5__();
            out = (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(out, "__add__"), self)), "__add__"), item));
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return out;
};
__str_join.is_method = true;

var __str___add__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    var call_arguments6 = [str, a + b];
    return pythonium_call.apply(undefined, call_arguments6);
};
__str___add__.is_method = true;

var __str___len__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = self.jsobject;
    var call_arguments7 = [int, jsobject.length];
    return pythonium_call.apply(undefined, call_arguments7);
};
__str___len__.is_method = true;

var __str___lte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a <= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__str___lte__.is_method = true;

var __str___gte__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a >= b)) {
        return __TRUE;
    }
    return __FALSE;
};
__str___gte__.is_method = true;

var __str___gt__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a > b)) {
        return __TRUE;
    }
    return __FALSE;
};
__str___gt__.is_method = true;

var __str___eq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var b,a;
    /* BEGIN function */
    a = pythonium_get_attribute(self, "jsobject");
    b = pythonium_get_attribute(other, "jsobject");
    if (pythonium_is_true(a == b)) {
        return __TRUE;
    }
    return __FALSE;
};
__str___eq__.is_method = true;

var __str___getitem__ = function(self, index) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,c;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    index = pythonium_get_attribute(index, "jsobject");
    c = jsobject[index];
    var call_arguments8 = [str, c];
    return pythonium_call.apply(undefined, call_arguments8);
};
__str___getitem__.is_method = true;

var __str___neq__ = function(self, other) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments9 = [pythonium_get_attribute(self, "__eq__"), other];
    return pythonium_call(pythonium_get_attribute(pythonium_call.apply(undefined, call_arguments9), "__not__"));
};
__str___neq__.is_method = true;

var str = pythonium_create_class("str", [object], {
    __init__: __str___init__,
    __repr__: __str___repr__,
    __jstype__: __str___jstype__,
    __hash__: __str___hash__,
    __contains__: __str___contains__,
    __iter__: __str___iter__,
    join: __str_join,
    __add__: __str___add__,
    __len__: __str___len__,
    __lte__: __str___lte__,
    __gte__: __str___gte__,
    __gt__: __str___gt__,
    __eq__: __str___eq__,
    __getitem__: __str___getitem__,
    __neq__: __str___neq__,
});
/* class definition tuple */
var __tuple___init__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    pythonium_set_attribute(self, "jsobject", []);
};
__tuple___init__.is_method = true;

var __tuple___hash__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments0 = [TypeError, pythonium_call(str, "unhashable type: 'list'")];
    throw pythonium_call.apply(undefined, call_arguments0);
};
__tuple___hash__.is_method = true;

var __tuple___repr__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var iterable;
    /* BEGIN function */
    var call_arguments1 = [map, nest_str_with_quotes, self];
    iterable = pythonium_call.apply(undefined, call_arguments1);
    var call_arguments2 = [pythonium_get_attribute(pythonium_call(str, ", "), "join"), iterable];
    return (pythonium_call(pythonium_get_attribute((pythonium_call(pythonium_get_attribute(pythonium_call(str, "("), "__add__"), pythonium_call.apply(undefined, call_arguments2))), "__add__"), pythonium_call(str, ")")));
};
__tuple___repr__.is_method = true;

var __tuple___jstype__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var out,item;
    /* BEGIN function */
    out = [];
    try {
        var __next3__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next3__();
            var call_arguments4 = [jstype, item];
            item = pythonium_call.apply(undefined, call_arguments4);
            out.push(item);
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return out;
};
__tuple___jstype__.is_method = true;

var __tuple_insert = function(self, index, item) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments5 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "splice"), index, pythonium_call(int, 0), item];
    pythonium_call.apply(undefined, call_arguments5);
};
__tuple_insert.is_method = true;

var __tuple___setitem__ = function(self, index, value) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    index = pythonium_get_attribute(index, "jsobject");
    jsobject[index] = value;
};
__tuple___setitem__.is_method = true;

var __tuple___getitem__ = function(self, s) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,index;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    var call_arguments6 = [jstype, s];
    index = pythonium_call.apply(undefined, call_arguments6);
    return jsobject[index];
};
__tuple___getitem__.is_method = true;

var __tuple___len__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,length;
    /* BEGIN function */
    jsobject = pythonium_get_attribute(self, "jsobject");
    length = jsobject.length;
    var call_arguments7 = [int, length];
    return pythonium_call.apply(undefined, call_arguments7);
};
__tuple___len__.is_method = true;

var __tuple___iter__ = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments8 = [ListIterator, self];
    return pythonium_call.apply(undefined, call_arguments8);
};
__tuple___iter__.is_method = true;

var __tuple___contains__ = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    try {
        var __next9__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next9__();
            if (pythonium_is_true((pythonium_get_attribute(obj, "__eq__")(item)))) {
                return __TRUE;
            }
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    return __FALSE;
};
__tuple___contains__.is_method = true;

var __tuple_pop = function(self) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments10 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "pop")];
    return pythonium_call.apply(undefined, call_arguments10);
};
__tuple_pop.is_method = true;

var __tuple_index = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var index;
    /* BEGIN function */
    index = pythonium_call(int, 0);
    try {
        var __next11__ = pythonium_get_attribute(iter(self), "__next__");
        while(true) {
            var item = __next11__();
            if (pythonium_is_true((pythonium_get_attribute(item, "__eq__")(obj)))) {
                return index;
            }
            index = pythonium_call(pythonium_get_attribute(index, "__add__"), pythonium_call(int, 1));
        }
    } catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}
    throw ValueError;
};
__tuple_index.is_method = true;

var __tuple_remove = function(self, obj) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    var jsobject,index;
    /* BEGIN function */
    var call_arguments12 = [pythonium_get_attribute(self, "index"), obj];
    index = pythonium_call.apply(undefined, call_arguments12);
    jsobject = pythonium_get_attribute(self, "jsobject");
    jsobject.splice(jstype(index), 1);
};
__tuple_remove.is_method = true;

var __tuple___delitem__ = function(self, index) {
    /* BEGIN arguments unpacking */
    /* END arguments unpacking */
    /* BEGIN function */
    var call_arguments13 = [jstype, index];
    var call_arguments14 = [pythonium_get_attribute(pythonium_get_attribute(self, "jsobject"), "splice"), pythonium_call.apply(undefined, call_arguments13), pythonium_call(int, 1)];
    pythonium_call.apply(undefined, call_arguments14);
};
__tuple___delitem__.is_method = true;

var tuple = pythonium_create_class("tuple", [object], {
    __init__: __tuple___init__,
    __hash__: __tuple___hash__,
    __repr__: __tuple___repr__,
    __jstype__: __tuple___jstype__,
    insert: __tuple_insert,
    __setitem__: __tuple___setitem__,
    __getitem__: __tuple___getitem__,
    __len__: __tuple___len__,
    __iter__: __tuple___iter__,
    __contains__: __tuple___contains__,
    pop: __tuple_pop,
    index: __tuple_index,
    remove: __tuple_remove,
    __delitem__: __tuple___delitem__,
});