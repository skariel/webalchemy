import os
import sys

from ast import Str
from ast import Name
from ast import List
from ast import Tuple
from ast import parse
from ast import Assign
from ast import Global
from ast import FunctionDef
from ast import NodeVisitor

from ..utils import YieldSearch, Writer


class Veloce(NodeVisitor):

    @classmethod
    def translate(cls, code):
        translator = cls()
        ast = parse(code)
        translator.visit(ast)
        return translator.writer.value()

    def __init__(self):
        super().__init__()
        self.dependencies = []
        self.in_classdef = None
        self._function_stack = []
        self.__all__ = None
        self.writer = Writer()
        self._uuid = -1

    def uuid(self):
        self._uuid += 1
        return self._uuid

    def visit(self, node):
        if os.environ.get('DEBUG', False):
            sys.stderr.write(">>> {} {}\n".format(node.__class__.__name__, node._fields))
        return super().visit(node)

    ######################################################################
    # mod = Module | Interactive | Expression | Suite
    #
    # stmt = FunctionDef | ClassDef | Return | Delete | Assign | AugAssign
    #      | For | While | If | With | Raise | Try | Assert | Import | ImportFrom
    #      | Global | Nonlocal | Expr | Pass | Break | Continue
    #
    # expr = BoolOp | BinOp | UnaryOp | Lambda | IfExp | Dict | Set 
    #      | ListComp | SetComp | DictComp | GeneratorExp | Yield | YieldFrom
    #      | Compare | Call | Num | Str | Bytes | Ellipsis | Attribute
    #      | Subscript | Starred | Name | List | Tuple
    #
    # expr_context = Load | Store | Del | AugLoad | AugStore | Param
    #
    # slice = Slice | ExtSlice | Index
    #
    # boolop = And | Or
    #
    # operator = Add | Sub | Mult | Div | Mod | Pow | LShift | RShift
    #          | BitOr | BitXor | BitAnd | FloorDiv
    #
    # unaryop = Invert | Not | UAdd | USub
    #
    # cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
    #
    # comprehension = (expr target, expr iter, expr* ifs)
    #
    # excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)
    #
    # arguments = (arg* args, identifier? vararg, expr? varargannotation,
    #              arg* kwonlyargs, identifier? kwarg, expr? kwargannotation, 
    #              expr* defaults, expr* kw_defaults)
    #
    # arg = (identifier arg, expr? annotation)
    #
    # keyword = (identifier arg, expr value)
    #
    # alias = (identifier name, identifier? asname)
    #
    # withitem = (expr context_expr, expr? optional_vars)
    ######################################################################

    # Interactive(stmt* body)
    def visit_Interactive(self, node): raise NotImplemented

    # Expression(expr body)
    def visit_Expression(self, node): raise NotImplemented

    # Suite(stmt* body)
    def visit_Suite(self, node): raise NotImplemented

    # expr_context = Load | Store | Del | AugLoad | AugStore | Param
    def visit_Load(self, node): raise NotImplemented
    def visit_Store(self, node): raise NotImplemented
    def visit_Del(self, node): raise NotImplemented
    def visit_AugLoad(self, node): raise NotImplemented
    def visit_AugStore(self, node): raise NotImplemented
    def visit_Param(self, node): raise NotImplemented

    # Pass
    def visit_Pass(self, node):
        self.writer.write('/* pass */')

    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    def visit_Try(self, node):
        self.writer.write('try {')
        self.writer.push()
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')
        self.writer.write('catch(__exception__) {')
        self.writer.push()
        list(map(self.visit, node.handlers))
        self.writer.pull()
        self.writer.write('}')

    # Raise(expr? exc, expr? cause)
    def visit_Raise(self, node):
        self.writer.write('throw {};'.format(self.visit(node.exc)))

    # ExceptHandler(expr? type, identifier? name, stmt* body)
    def visit_ExceptHandler(self, node):
        list(map(self.visit, node.body))

    # Yield(expr? value)
    def visit_Yield(self, node):
        return 'yield {}'.format(self.visit(node.value))

    # YieldFrom(expr value)
    def visit_YieldFrom(self, node): raise NotImplemented

    # In
    def visit_In(self, node):
        return ' in '

    # NotIn
    def visit_NotIn(self, node): raise NotImplemented

    # Module(stmt* body)
    def visit_Module(self, node):
        list(map(self.visit, node.body))

    # Tuple(expr* elts, expr_context ctx)
    def visit_Tuple(self, node):
        return '[{}]'.format(', '.join(map(self.visit, node.elts)))

    # List(expr* elts, expr_context ctx) 
    def visit_List(self, node):
        return '[{}]'.format(', '.join(map(self.visit, node.elts)))

    # Set(expr* elts)
    def visit_Set(self, node): raise NotImplemented

    # alias = (identifier name, identifier? asname)
    def visit_alias(self, node): raise NotImplemented

    # Import(alias* names)
    def visit_Import(self, node): raise NotImplemented

    # ImportFrom(identifier? module, alias* names, int? level)
    def visit_ImportFrom(self, node):
        if len(node.names) > 1:
            raise NotImplemented
        if len(node.names) == 0:
            raise NotImplemented
        out = ''
        name = node.names[0].name
        asname = node.names[0].asname
        if not asname:
            asname = name
        modules = '/'.join(node.module.split('.'))
        path = modules + '/' + name
        if node.level == 0:
            self.writer.write('var {} = require("{}");'.format(asname, path))
            self.dependencies.append('/' + path)  # relative to project root
        elif node.level == 1:
            self.writer.write('var {} = require.toUrl("./{}");'.format(asname, path))
            self.dependencies.append('./' + path)  # relative to current file
        else:
            path = '../' * node.level + path
            self.writer.write('var {} = require.toUrl("{}");'.format(asname, path))
            self.dependencies.append(path)  # relative to current file
        return out

    # Global(identifier* names)
    def visit_Global(self, node):
        # handled in visit_FunctionDef
        return ''

    # Nonlocal(identifier* names)
    def visit_Nonlocal(self, node): raise NotImplemented

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns)
    def visit_FunctionDef(self, node):
        # 'name', 'args', 'body', 'decorator_list', 'returns'
        self._function_stack.append(node.name)
        args, kwargs, varargs, varkwargs = self.visit(node.args)

        all_parameters = list(args)
        all_parameters.extend(kwargs.keys())
        if varargs:
            all_parameters.append(varargs)
        if varkwargs:
            all_parameters.append(varkwargs)
        all_parameters = set(all_parameters)

        name = node.name
        # handle yield
        has_yield = False
        for child in node.body:
            searcher = YieldSearch()
            searcher.visit(child)
            if getattr(searcher, 'has_yield', False):
                has_yield = True
                break
        if self.in_classdef and len(self._function_stack) == 1:
            __args = ', '.join(args[1:])
            if has_yield:
                self.writer.write('{}: function*({}) {{'.format(name, __args))
            else:
                self.writer.write('{}: function({}) {{'.format(name, __args))
        else:
            __args = ', '.join(args)
            if has_yield:
                self.writer.write('var {} = function*({}) {{'.format(name, __args))
            else:
                self.writer.write('var {} = function({}) {{'.format(name, __args))
        self.writer.push()
        if not varkwargs:
            varkwargs = '__kwargs'

        # unpack arguments
        if varargs or varkwargs != '__kwargs' or kwargs:
            self.writer.write('var __args = Array.prototype.slice.call(arguments);')
        if varkwargs != '__kwargs' or kwargs:
            self.writer.write('var {} = __args[__args.length - 1] || {{}};'.format(varkwargs))
        for keyword in kwargs.keys():
            self.writer.write('{} = {} || {}.{} || {};'.format(keyword, keyword, varkwargs, keyword, kwargs[keyword]))
            self.writer.write('delete {}.{};'.format(varkwargs, keyword))
        if varargs:
            self.writer.write('var {} = __args.splice({});'.format(varargs, len(args)))
            self.writer.write('{}.pop();'.format(varargs))
        # check for variable creation use var if not global
        def retrieve_vars(body, vars=None):
            local_vars = set()
            global_vars = vars if vars else set()
            for n in body:
                if isinstance(n, Assign) and isinstance(n.targets[0], Name):
                    local_vars.add(n.targets[0].id)
                elif isinstance(n, Assign) and isinstance(n.targets[0], Tuple):
                    for target in n.targets:
                        for target in target.elts:
                            local_vars.add(target.id)
                elif isinstance(n, Global):
                    global_vars.update(n.names)
                elif hasattr(n, 'body') and not isinstance(n, FunctionDef):
                    # do a recursive search inside new block except function def
                    l, g = retrieve_vars(n.body)
                    local_vars.update(l)
                    global_vars.update(g)
                    if hasattr(n, 'orelse'):
                        l, g = retrieve_vars(n.orelse)
                        local_vars.update(l)
                        global_vars.update(g)
            return local_vars, global_vars

        local_vars, global_vars = retrieve_vars(node.body, all_parameters)

        if local_vars - global_vars:
            a = ','.join(local_vars-global_vars)
            self.writer.write('var {};'.format(a))

        # output function body
        list(map(self.visit, node.body))
        self.writer.pull()
        if self.in_classdef and len(self._function_stack) == 1:
            self.writer.write('},')
        else:
            self.writer.write('};')

        for decorator in node.decorator_list:
            decorator = self.visit(decorator)
            self.writer.write('{} = {}({});'.format(node.name, decorator, node.name))
        self._function_stack.pop()

    # Slice(expr? lower, expr? upper, expr? step) 
    def visit_Slice(self, node):
        start = self.visit(node.lower) if node.lower else 'undefined'
        end = self.visit(node.upper) if node.upper else 'undefined'
        step = self.visit(node.step) if node.step else 'undefined'
        return 'slice({}, {}, {})'.format(start, step, end)

    # Index(expr value)
    def visit_Index(self, node):
        return self.visit(node.value)

    # ExtSlice(slice* dims) 
    def visit_ExtSlice(self, node): raise NotImplemented

    # Subscript(expr value, slice slice, expr_context ctx)
    def visit_Subscript(self, node):
        return '{}[{}]'.format(self.visit(node.value), self.visit(node.slice))

    # arguments = (arg* args, identifier? vararg, expr? varargannotation,
    #              arg* kwonlyargs, identifier? kwarg, expr? kwargannotation, 
    #              expr* defaults, expr* kw_defaults)
    def visit_arguments(self, node):
        # 'args', 'vararg', 'varargannotation', 'kwonlyargs', 'kwarg', 'kwargannotation', 'defaults', 'kw_defaults'
        args = list(map(lambda x: x.arg, node.args))
        vararg = node.vararg
        kwonlyargs = node.kwonlyargs
        varkwargs = node.kwarg
        defaults = list(map(self.visit, node.defaults))
        kwargs = dict(zip(args[-len(defaults):], defaults))
        return args, kwargs, vararg, varkwargs

    # arg = (identifier arg, expr? annotation)
    def visit_arg(self, node): raise NotImplemented

    # Name(identifier id, expr_context ctx)
    def visit_Name(self, node):
        if node.id == 'None':
            return 'undefined'
        elif node.id == 'self':
            return 'this'
        elif node.id == 'True':
            return 'true'
        elif node.id == 'False':
            return 'false'
        elif node.id == 'null':
            return 'null'
        return node.id.replace('__DOLLAR__', '$')

    # Attribute(expr value, identifier attr, expr_context ctx)
    def visit_Attribute(self, node):
        name = self.visit(node.value)
        attr = node.attr.replace('__DOLLAR__', '$')
        return '{}.{}'.format(name, attr)

    # keyword = (identifier arg, expr value)
    def visit_keyword(self, node):
        if isinstance(node.arg, str):
            return node.arg, self.visit(node.value)
        return self.visit(node.arg), self.visit(node.value)

    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    def visit_Call(self, node):
        name = self.visit(node.func)
        if name == 'instanceof':
            # this gets used by "with javascript:" blocks
            # to test if an instance is a JavaScript type
            args = list(map(self.visit, node.args))
            if len(args) == 2:
                return '{} instanceof {}'.format(*tuple(args))
            else:
                raise SyntaxError(args)
        elif name == 'JSObject':
            if node.keywords:
                kwargs = map(self.visit, node.keywords)
                f = lambda x: '"{}": {}'.format(x[0], x[1])
                out = ', '.join(map(f, kwargs))
                return '{{}}'.format(out)
            else:
                return 'Object()'
        elif name == 'var':
            args = map(self.visit, node.args)
            out = ', '.join(args)
            return 'var {}'.format(out)
        elif name == 'new':
            args = list(map(self.visit, node.args))
            object = args[0]
            args = ', '.join(args[1:])
            return 'new {}({})'.format(object, args)
        elif name == 'super':
            args = ', '.join(map(self.visit, node.args))
            return 'this.$super({})'.format(args)
        elif name == 'JSArray':
            if node.args:
                args = map(self.visit, node.args)
                out = ', '.join(args)
            else:
                out = ''
            return '[{}]'.format(out)
        elif name == 'jscode':
            return node.args[0].s
        elif name == 'jstype':
            return self.visit(node.args[0])
        elif name == 'print':
            args = [self.visit(e) for e in node.args]
            s = 'console.log({})'.format(', '.join(args))
            return s
        else:
            # positional args
            if node.args:
                args = [self.visit(e) for e in node.args]
                args = [e for e in args if e]
            else:
                args = []
            # variable arguments aka. starargs
            call_arguments = 'call_arguments{}'.format(self.uuid())
            if node.starargs:
                varargs = self.visit(node.starargs)
                code = "for i in {}: jscode('{}.push(i)')".format(varargs, call_arguments)
                self.writer.write(self.translate(code))
            # keywords and variable keywords arguments aka. starkwargs
            if node.kwargs:
                kwargs = self.visit(node.kwargs)
                if node.keywords:
                    for key, value in map(self.visit, node.keywords):
                        self.writer.write('{}["{}"] = {};'.format(kwargs, key, value))
            elif node.keywords:
                kwargs = '__pythonium_kwargs'
                self.writer.write('var __pythonium_kwargs = {};')
                for key, value in map(self.visit, node.keywords):
                    self.writer.write('{}["{}"] = {};'.format(kwargs, key, value))
            if node.kwargs or node.keywords:
                # XXX: define for every call since we can't define it globaly
                self.writer.write('__ARGUMENTS_PADDING__ = {};')
                args.append('__ARGUMENTS_PADDING__')
                args.append(kwargs)
            return '{}({})'.format(name, ', '.join(args))

    # ListComp(expr elt, comprehension* generators)
    def visit_ListComp(self, node):
        # 'elt', 'generators'
        comprehension = '__comp{}__'.format(self.uuid())
        self.writer.write('var {} = [];'.format(comprehension))
        list(map(self.visit, node.generators))
        value = self.visit(node.elt)
        self.writer.write('{}.push({});'.format(comprehension, value))
        for _ in node.generators:
            self.writer.pull()
            self.writer.write('}')
        return comprehension

    # SetComp(expr elt, comprehension* generators)
    visit_SetComp = NotImplemented

    # DictComp(expr key, expr value, comprehension* generators)
    visit_DictComp = NotImplemented

    # GeneratorExp(expr elt, comprehension* generators)
    visit_GeneratorExp = NotImplemented

    # comprehension = (expr target, expr iter, expr* ifs)
    def visit_comprehension(self, node):
        # 'target', 'iter', 'ifs'
        iterator = '__iterator{}__'.format(self.uuid())
        index = '__index{}__'.format(self.uuid())
        self.writer.write('var {} = {};'.format(iterator, self.visit(node.iter)))
        self.writer.write('for (var {} = 0; {}<{}.length; {}++) {{'.format(index, index, iterator, index))
        self.writer.push()
        self.writer.write('var {} = {}[{}];'.format(self.visit(node.target), iterator, index))
        if node.ifs:
            self.writer.write('if(!{}) {{ continue; }}'.format(' && '.join(map(self.visit, node.ifs))))

    # While(expr test, stmt* body, stmt* orelse)
    def visit_While(self, node):
        self.writer.write('while({}) {{'.format(self.visit(node.test)))
        self.writer.push()
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')

    # AugAssign(expr target, operator op, expr value)
    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        self.writer.write('{} = {} {} {};'.format(target, target, self.visit(node.op), self.visit(node.value)))

    # Str(string s)
    def visit_Str(self, node):
        s = node.s.replace('\n', '\\n')
        if '"' in s:
            return "'{}'".format(s)
        return '"{}"'.format(s)

    # Bytes(bytes s)
    visit_Bytes = NotImplemented

    # BinOp(expr left, operator op, expr right)
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        return '({} {} {})'.format(left, op, right)

    def visit_Mult(self, node):
        return '*'

    def visit_Add(self, node):
        return '+'

    visit_UAdd = NotImplemented

    def visit_Sub(self, node):
        return '-'

    def visit_USub(self, node):
        return '-'

    def visit_Div(self, node):
        return '/'

    visit_FloorDiv = NotImplemented
    visit_Pow      = NotImplemented
    visit_Invert   = NotImplemented

    def visit_Mod(self, node):
        return '%'

    def visit_Lt(self, node):
        return '<'

    def visit_Gt(self, node):
        return '>'

    def visit_GtE(self, node):
        return '>='

    def visit_LtE(self, node):
        return '<='

    def visit_LShift(self, node):
        return '<<'

    def visit_RShift(self, node):
        return '>>'

    def visit_BitXor(self, node):
        return '^'

    def visit_BitOr(self, node):
        return '|'

    def visit_BitAnd(self, node):
        return '&'

    def visit_Eq(self, node):
        return '=='

    def visit_NotEq(self, node):
        return '!='

    # Num(object n)
    def visit_Num(self, node):
        return str(node.n)

    def visit_Is(self, node):
        return '==='

    def visit_Not(self, node):
        return '!'

    def visit_IsNot(self, node):
        return '!=='

    # UnaryOp(unaryop op, expr operand)
    def visit_UnaryOp(self, node):
        return self.visit(node.op) + self.visit(node.operand)

    def visit_And(self, node):
        return '&&'

    def visit_Or(self, node):
        return '||'

    # Delete(expr* targets)
    def visit_Delete(self, node):
        for target in node.targets:
            target = self.visit(target)
            self.writer.write('delete {};'.format(target))

    # Assign(expr* targets, expr value)
    def visit_Assign(self, node):
        value = self.visit(node.value)
        if len(node.targets) == 1 and not isinstance(node.targets[0], Tuple):
            target = self.visit(node.targets[0])
            self.writer.write('{} = {};'.format(target, value))
            return
        self.writer.write('var __assignement = {};'.format(value))
        for target in node.targets:
            if isinstance(target, Tuple):
                targets = map(self.visit, target.elts)
                for index, target in enumerate(targets):
                    self.writer.write('{} = __assignement[{}];'.format(target, index))
            else:
                target = self.visit(target)
                if self.in_classdef and len(self._function_stack) == 0:
                    self.writer.write('{}: {},'.format(target, value))
                else:
                    if target == '__all__':
                        if isinstance(node.value, Name):
                            self.__all__ = value
                        elif isinstance(node.value, Str):
                            self.__all__ = node.value.s
                        elif isinstance(node.value, List):
                            if isinstance(node.value.elts[0], Name):
                                self.__all__ = list(map(self.visit, node.value.elts))
                            else:
                                self.__all__ = list(map(lambda x: x.s, node.value.elts))
                        else:
                            raise NotImplementedError
                    else:
                        self.writer.write('{} = __assignement;'.format(target))

    # Expr(expr value)
    def visit_Expr(self, node):
        self.writer.write(self.visit(node.value) + ';')

    # Return(expr? value)
    def visit_Return(self, node):
        if node.value:
            self.writer.write('return {};'.format(self.visit(node.value)))
        else:
            self.writer.write('return undefined;')

    # Compare(expr left, cmpop* ops, expr* comparators)
    def visit_Compare(self, node):
        def merge(a, b, c):
            if a and b:
                c.append(self.visit(a[0]))
                c.append(self.visit(b[0]))
                return merge(a[1:], b[1:], c)
            else:
                return c
        ops = merge(node.ops, node.comparators, [self.visit(node.left)])

        iter = reversed(ops)
        c = next(iter)
        for op in iter:
            c = '({} {} {})'.format(next(iter), op, c)
        return c

    # BoolOp(boolop op, expr* values)
    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        return '({})'.format(op.join([self.visit(v) for v in node.values]))

    # Assert(expr test, expr? msg)
    visit_Assert = NotImplemented

    # If(expr test, stmt* body, stmt* orelse)
    def visit_If(self, node):
        test = self.visit(node.test)
        self.writer.write('if({}) {{'.format(test))
        self.writer.push()
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')
        if node.orelse:
            self.writer.write('else {')
            self.writer.push()
            list(map(self.visit, node.orelse))
            self.writer.pull()
            self.writer.write('}')

    # IfExp(expr test, expr body, expr orelse)
    def visit_IfExp(self, node):
        name = '__pythonium_ifexp_{}'.format(self.uuid())
        self.writer.write('if ({}) {{'.format(self.visit(node.test)))
        self.writer.push()
        body = self.visit(node.body)
        self.writer.write('var {} = {};'.format(name, body))
        self.writer.pull()
        self.writer.write('} else {')
        self.writer.push()
        orelse = self.visit(node.orelse)
        self.writer.write('var {} = {};'.format(name, orelse))
        self.writer.pull()
        self.writer.write('}')
        return name

    # Ellipsis
    visit_Ellipsis = NotImplemented

    # Starred(expr value, expr_context ctx)
    visit_Starred = NotImplemented

    # Dict(expr* keys, expr* values)
    def visit_Dict(self, node):
        a = []
        for i in range(len(node.keys)):
            k = self.visit(node.keys[i])
            v = self.visit(node.values[i])
            a.append('{}:{}'.format(k, v))
        b = ','.join(a)
        return '{{{}}}'.format(b)

    # With(withitem* items, stmt* body)
    visit_With = NotImplemented

    # withitem = (expr context_expr, expr? optional_vars)
    visit_withitem = NotImplemented

    # For(expr target, expr iter, stmt* body, stmt* orelse)
    def visit_For(self, node):
        # support only arrays
        target = node.target.id 
        iterator_index = target + '_iterator_index'
        iterator = self.visit(node.iter) # iter is the python iterator
        iterator_name = 'iterator_{}'.format(target)
        self.writer.write('var {} = {};'.format(iterator_name, iterator))
        # replace the replace target with the javascript iterator
        self.writer.write('for (var {}=0; {} < {}.length; {}++) {{'.format(iterator_index, iterator_index, iterator_name, iterator_index))
        self.writer.push()
        self.writer.write('var {} = {}[{}];'.format(target, iterator_name, iterator_index))
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')

    # Continue
    def visit_Continue(self, node):
        self.writer.write('continue;')

    # Break
    def visit_Break(self, node):
        self.writer.write('break;')

    def _unpack_arguments(self, args, kwargs, varargs, varkwargs):
        self.writer.write('/* BEGIN arguments unpacking */')
        if not varkwargs and kwargs:
            varkwargs = '__kwargs'

        if varargs or (varkwargs and varkwargs != '__kwargs') or kwargs:
            self.writer.write('var __args = Array.prototype.slice.call(arguments);')
        if (varkwargs and varkwargs != '__kwargs') or kwargs:
            self.writer.write('if (__args[__args.length - 2] === __ARGUMENTS_PADDING__) {')
            self.writer.push()
            self.writer.write('var {} = __args[__args.length - 1];'.format(varkwargs))
            self.writer.write('var varkwargs_start = __args.length - 2;')
            self.writer.pull()
            self.writer.write('} else {')  # no variable keywords was provided so it's empty
            self.writer.push()
            self.writer.write('var {} = {{}};'.format(varkwargs))
            self.writer.write('var varkwargs_start = undefined;')
            self.writer.pull()
            self.writer.write('}')
        num_args = len(args)
        for index, keyword in enumerate(kwargs.keys()):
            position = num_args + index - 1
            self.writer.write('if (varkwargs_start !== undefined && {} > varkwargs_start) {{'.format(position))
            self.writer.push()
 
            self.writer.write('{} = {}[{}] || {};'.format(keyword, varkwargs, keyword, kwargs[keyword])) 
            self.writer.pull()
            self.writer.write('} else {')
            self.writer.push()
            self.writer.write('{} = {} || {}[{}] || {};'.format(keyword, keyword, varkwargs, keyword, kwargs[keyword]))
            self.writer.pull()
            self.writer.write('}')
            if varkwargs != '__kwargs':
                self.writer.write('delete {}.{};'.format(varkwargs, keyword))
        if varargs:
            self.writer.write('__args = __args.splice({});'.format(len(args)))
            if varkwargs and (varkwargs != '__kwargs' or kwargs):
                self.writer.write('if (varkwargs_start) {{ __args.splice(varkwargs_start - {}) }}'.format(len(args)))
            self.writer.write('{} = __args;'.format(varargs))
        self.writer.write('/* END arguments unpacking */')

    # Lambda(arguments args, expr body)
    def visit_Lambda(self, node):
        args, kwargs, vararg, varkwargs = self.visit(node.args)
        name = '__lambda{}'.format(self.uuid())
        self.writer.write('var {} = function({}) {{'.format(name, ', '.join(args)))
        self.writer.push()
        self._unpack_arguments(args, kwargs, vararg, varkwargs)
        body = self.visit(node.body)
        self.writer.write(body)
        self.writer.pull()
        self.writer.write('}')
        return name

    # ClassDef(identifier name, expr* bases, keyword* keywords, 
    #          expr? starargs, expr? kwargs, stmt* body, expr* decorator_list)
    def visit_ClassDef(self, node):
        # 'name', 'bases', 'keywords', 'starargs', 'kwargs', 'body', 'decorator_lis't
        if len(node.bases) > 1:
            raise NotImplemented
        name = node.name
        if len(node.bases) == 0:
            self.writer.write('var {} = Class.$extend({{'.format(name))
        else:
            base = self.visit(node.bases[0])
            self.writer.write('var {} = {}.$extend({{'.format(name, base))
        self.writer.push()
        self.in_classdef = name
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('});')
        self.in_classdef = None

