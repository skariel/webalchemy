import os
import sys
from collections import namedtuple

from ast import Str
from ast import Name
from ast import List
from ast import Tuple
from ast import parse
from ast import Assign
from ast import Global
from ast import Attribute
from ast import Subscript
from ast import FunctionDef
from ast import NodeVisitor

from ..utils import YieldSearch, Writer
from ..veloce.veloce import Veloce

ClassDefNode = namedtuple('ClassDef', 'name')
FunctionDefNode = namedtuple('FunctionDef', 'name')


class Compliant(NodeVisitor):

    @classmethod
    def translate(cls, code):
        translator = cls()
        ast = parse(code)
        translator.visit(ast)
        return translator.writer.value()

    def __init__(self):
        super().__init__()
        self.dependencies = []
        self._def_stack = []
        self.__all__ = []
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
    visit_Interactive = NotImplemented

    # Expression(expr body)
    visit_Expression = NotImplemented

    # Suite(stmt* body)
    visit_Suite = NotImplemented

    # expr_context = Load | Store | Del | AugLoad | AugStore | Param
    visit_Load = NotImplemented
    visit_Store = NotImplemented
    visit_Del = NotImplemented
    visit_AugLoad = NotImplemented
    visit_AugStore = NotImplemented
    visit_Param = NotImplemented

    # Pass
    def visit_Pass(self, node):
        self.writer.write('/* pass */')

    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    def visit_Try(self, node):
        self.writer.write('try {')
        self.writer.push()
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('} catch (__exception__) {')
        self.writer.push()
        list(map(self.visit, node.handlers))
        self.writer.pull()
        self.writer.write('}')

    # Raise(expr? exc, expr? cause)
    def visit_Raise(self, node):
        self.writer.write('throw {};'.format(self.visit(node.exc)))

    # ExceptHandler(expr? type, identifier? name, stmt* body)
    def visit_ExceptHandler(self, node):
        if node.type:
            if node.name:
                self.writer.write('var {} = __exception__;'.format(node.name))
                name = node.name
            else:
                name = '__exception__'
            self.writer.write('if (pythonium_is_exception({}, {})) {{'.format(name, self.visit(node.type)))
            self.writer.push()
        list(map(self.visit, node.body))
        if node.type:
            self.writer.pull()
            self.writer.write('}')

    # Yield(expr? value)
    def visit_Yield(self, node):
        return 'yield {}'.format(self.visit(node.value))

    # YieldFrom(expr value)
    def visit_YieldFrom(self, node):
        pass

    # In
    def visit_In(self, node):
        return '__rcontains__'

    # NotIn
    visit_NotIn = NotImplemented

    # Module(stmt* body)
    def visit_Module(self, node):
        list(map(self.visit, node.body))

    # Tuple(expr* elts, expr_context ctx)
    def visit_Tuple(self, node):
        args = ', '.join(map(self.visit, node.elts))
        if args:
            name = '__a_tuple{}'.format(self.uuid())
            self.writer.write('var {} = pythonium_call(tuple);'.format(name))
            self.writer.write('{}.jsobject = [{}];'.format(name, args))
            return name
        else:
            return 'pythonium_call(tuple)'

    # List(expr* elts, expr_context ctx)
    def visit_List(self, node):
        args = ', '.join(map(self.visit, node.elts))
        if args:
            name = '__a_list{}'.format(self.uuid())
            self.writer.write('var {} = pythonium_call(list);'.format(name))
            self.writer.write('{}.jsobject = [{}];'.format(name, args))
            return name
        else:
            return 'pythonium_call(list)'

    # Set(expr* elts)
    visit_Set = NotImplemented

    # alias = (identifier name, identifier? asname)
    def visit_alias(self, node):
        out = ''
        name = node.name
        asname = node.asname
        if not asname:
            asname = name
        path = []
        for module in name.split('.')[:-1]:
            path.append(module)
            path_to_module = '.'.join(path)
            self.writer.write("var {} = typeof({}) == 'undefined' ? {{}} : {}".format(path_to_module, path_to_module, path_to_module))
        path.append(asname.split('.')[-1])
        path = '/'.join(path)
        self.writer.write('var {} = require("{}");'.format(asname, path))
        path = '/'.join(name.split('.'))
        self.dependencies.append('/' + path)  # relative to project root

    # Import(alias* names)
    visit_Import = NotImplemented

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
        path = modules
        if node.level == 0:
            self.writer.write('var {} = require("{}").{};'.format(asname, path, name))
            self.dependencies.append('/' + path)  # relative to project root
        elif node.level == 1:
            self.writer.write('var {} = require.toUrl("./{}").{};'.format(asname, path, name))
            self.dependencies.append('./' + path)  # relative to current file
        else:
            path = '../' * node.level + path
            self.writer.write('var {} = require.toUrl("{}").{};'.format(asname, path, name))
            self.dependencies.append(path)  # relative to current file
        return out

    # Global(identifier* names)
    def visit_Global(self, node):
        # handled in visit_FunctionDef
        return ''

    # Nonlocal(identifier* names)
    visit_Nonlocal = NotImplemented

    def _is_inside_method_definition(self):
        if len(self._def_stack) >= 2:
            if isinstance(self._def_stack[-2], ClassDefNode):
                if isinstance(self._def_stack[-1], FunctionDefNode):
                    return True
        return False

    def _is_inside_class_definition(self):
        return isinstance(self._def_stack[-1], ClassDefNode)

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns)
    def visit_FunctionDef(self, node):
        # 'name', 'args', 'body', 'decorator_list', 'returns'
        if len(self._def_stack) == 0:  # module level definition must be exported
            self.__all__.append(node.name)
        self._def_stack.append(FunctionDefNode(node.name))
        args, kwargs, varargs, varkwargs = self.visit(node.args)

        all_parameters = list(args)
        all_parameters.extend(kwargs.keys())
        if varargs:
            all_parameters.append(varargs)
        if varkwargs:
            all_parameters.append(varkwargs)
        all_parameters = set(all_parameters)

        if self._is_inside_method_definition():
            name = '__{}_{}'.format(self._def_stack[-2].name, node.name)
        else:
            name = node.name
        # handle yield
        has_yield = False
        for child in node.body:
            searcher = YieldSearch()
            searcher.visit(child)
            if getattr(searcher, 'has_yield', False):
                has_yield = True
                break

        __args = ', '.join(args)
        if has_yield:
            self.writer.write('var {} = function*({}) {{'.format(name, __args))
        else:
            self.writer.write('var {} = function({}) {{'.format(name, __args))
        self.writer.push()

        self._unpack_arguments(args, kwargs, varargs, varkwargs)

        # check for variable creation use var if not global
        def retrieve_vars(body, vars=None):
            local_vars = set()
            global_vars = vars if vars else set()
            for n in body:
                if isinstance(n, Assign) and isinstance(n.targets[0], Name):
                    local_vars.add(n.targets[0].id)
                elif isinstance(n, Assign) and isinstance(n.targets[0], Tuple):
                    for target in n.targets[0].elts:
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
        self.writer.write('/* BEGIN function */')
        # output function body
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('};')

        if self._is_inside_method_definition():
            self.writer.write('{}.is_method = true;'.format(name))

        for decorator in node.decorator_list:
            decorator = self.visit(decorator)
            self.writer.write('{} = {}({});'.format(name, decorator, name))
        self._def_stack.pop()

        self.writer.write('')
        return node.name, name

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
    visit_ExtSlice = NotImplemented

    # Subscript(expr value, slice slice, expr_context ctx)
    def visit_Subscript(self, node):
        return "pythonium_call(pythonium_get_attribute({}, '__getitem__'), {})".format(self.visit(node.value), self.visit(node.slice))

    # arguments = (arg* args, identifier? vararg, expr? varargannotation,
    #              arg* kwonlyargs, identifier? kwarg, expr? kwargannotation,
    #              expr* defaults, expr* kw_defaults)
    def visit_arguments(self, node):
        args = list(map(lambda x: x.arg, node.args))
        vararg = node.vararg
        kwonlyargs = node.kwonlyargs
        varkwargs = node.kwarg
        defaults = list(map(self.visit, node.defaults))
        kwargs = dict(zip(args[-len(defaults):], defaults))
        return args, kwargs, vararg, varkwargs

    # arg = (identifier arg, expr? annotation)
    visit_arg = NotImplemented

    # Name(identifier id, expr_context ctx)
    def visit_Name(self, node):
        if node.id == 'None':
            return '__NONE'
        elif node.id == 'True':
            return '__TRUE'
        elif node.id == 'False':
            return '__FALSE'
        elif node.id == 'null':
            return 'null'
        return node.id.replace('__DOLLAR__', '$')

    # Attribute(expr value, identifier attr, expr_context ctx)
    def visit_Attribute(self, node):
        name = self.visit(node.value)
        attr = node.attr.replace('__DOLLAR__', '$')
        return 'pythonium_get_attribute({}, "{}")'.format(name, attr)

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
            return 'new {}'.format(object, args)
        elif name == 'JSArray':
            if node.args:
                args = map(self.visit, node.args)
                out = ', '.join(args)
            else:
                out = ''
            return '[{}]'.format(out)
        elif name == 'jscode':
            return node.args[0].s
        else:
            # is it a call to new?
            try:
                if node.func.func.id == 'new':
                    # Do not convert arguments to Python
                    if node.args:
                        veloce = Veloce()
                        args = [veloce.visit(e) for e in node.args]
                        args = [e for e in args if e]
                    else:
                        args = []
                    # use native call since constructors don't have apply method
                    return '{}({})'.format(name, ', '.join(args))
            except AttributeError:
                # it is not
                pass

            # positional args
            if node.args:
                args = [self.visit(e) for e in node.args]
                args = [e for e in args if e]
            else:
                args = []
            args.insert(0, name)
            # variable arguments aka. starargs
            if node.starargs:
                varargs = self.visit(node.starargs)
                code = "for i in {}: jscode('{}.push(i)')".format(varargs, call_arguments)
                self.writer.write(self.translate(code))
            # keywords and variable keywords arguments aka. starkwargs
            if node.kwargs:
                kwargs = self.visit(node.kwargs)
                if node.keywords:
                    for key, value in map(self.visit, node.keywords):
                        self.writer.write('{}.__class__.__setitem__({}, pythonium_call(str, "{}"), {})'.format(kwargs, kwargs, key, value))  # XXX
            elif node.keywords:
                kwargs = '__pythonium_kwargs'
                self.writer.write('var __pythonium_kwargs = pythonium_create_empty_dict();')
                for key, value in map(self.visit, node.keywords):
                    self.writer.write('{}.__class__.__setitem__({}, pythonium_call(str, "{}"), {})'.format(kwargs, kwargs, key, value))
            if node.kwargs or node.keywords:
                args.append('__ARGUMENTS_PADDING__')
                args.append(kwargs)
            call_arguments = 'call_arguments{}'.format(self.uuid())
            self.writer.write('var {} = [{}];'.format(call_arguments, ', '.join(args)))
            return 'pythonium_call.apply(undefined, {})'.format(call_arguments)

    # ListComp(expr elt, comprehension* generators)
    def visit_ListComp(self, node):
        # 'elt', 'generators'
        comprehension = '__comp{}__'.format(self.uuid())
        self.writer.write('var {} = pythonium_call(list);'.format(comprehension))
        list(map(self.visit, node.generators))
        value = self.visit(node.elt)
        self.writer.write('pythonium_get_attribute({}, "append")({});'.format(comprehension, value))
        for _ in node.generators:
            self.writer.pull()
            self.writer.write('}} catch (__exception__) {if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}')
            self.writer.pull()
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
        self.writer.write('var {} = iter({});'.format(iterator, self.visit(node.iter)))
        self.writer.write('try {')
        self.writer.push()
        self.writer.write('while (true) {')
        self.writer.push()
        self.writer.write('var {} = next({});'.format(self.visit(node.target), iterator))
        if node.ifs:
            self.writer.write('if(!pythonium_is_true({})) {{ continue; }}'.format(' && '.join(map(self.visit, node.ifs))))

    # While(expr test, stmt* body, stmt* orelse)
    def visit_While(self, node):
        self.writer.write('while(pythonium_is_true({})) {{'.format(self.visit(node.test)))
        self.writer.push()
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')

    # AugAssign(expr target, operator op, expr value)
    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        self.writer.write('{} = pythonium_call(pythonium_get_attribute({}, "{}"), {});'.format(target, target, self.visit(node.op), self.visit(node.value)))

    # Str(string s)
    def visit_Str(self, node):
        s = node.s.replace('\n', '\\n')
        if '"' in s:
            return "pythonium_call(str, '{}')".format(s)
        return 'pythonium_call(str, "{}")'.format(s)

    # Bytes(bytes s)
    visit_Bytes = NotImplemented

    # BinOp(expr left, operator op, expr right)
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        return '(pythonium_call(pythonium_get_attribute({}, "{}"), {}))'.format(left, op, right)

    def visit_Mult(self, node):
        return '__mul__'

    def visit_Add(self, node):
        return '__add__'

    visit_UAdd = NotImplemented

    def visit_Sub(self, node):
        return '__sub__'

    def visit_USub(self, node):
        return '__neg__'

    def visit_Div(self, node):
        return '__div__'

    visit_FloorDiv = NotImplemented
    visit_Pow      = NotImplemented
    visit_Invert   = NotImplemented

    def visit_Mod(self, node):
        return '__mod__'

    def visit_Lt(self, node):
        return '__lt__'

    def visit_Gt(self, node):
        return '__gt__'

    def visit_GtE(self, node):
        return '__gte__'

    def visit_LtE(self, node):
        return '__lte__'

    def visit_LShift(self, node):
        return '__lshift__'

    def visit_RShift(self, node):
        return '__rshift__'

    def visit_BitXor(self, node):
        return '__xor__'

    def visit_BitOr(self, node):
        return '__or__'

    def visit_BitAnd(self, node):
        return '__and__'

    def visit_Eq(self, node):
        return '__eq__'

    def visit_NotEq(self, node):
        return '__neq__'

    def visit_Num(self, node):
        if isinstance(node.n, float):
            return 'pythonium_call(float, {})'.format(str(node.n))
        else:
            return 'pythonium_call(int, {})'.format(str(node.n))

    # Num(object n)
    def visit_Is(self, node):
        return '__is__'

    def visit_Not(self, node):
        return '__not__'

    def visit_IsNot(self, node):
        return '__isnot__'

    # UnaryOp(unaryop op, expr operand)
    def visit_UnaryOp(self, node):
        return 'pythonium_call(pythonium_get_attribute({}, "{}"))'.format(self.visit(node.operand), self.visit(node.op))

    def visit_And(self, node):
        return '__and__'

    def visit_Or(self, node):
        return '__or__'

    # Delete(expr* targets)
    def visit_Delete(self, node):
        for target in node.targets:
            if isinstance(target, Subscript):
                slice = self.visit(target.slice)
                target = self.visit(target.value)
                self.writer.write("pythonium_get_attribute({}, '__delitem__')({});".format(target, slice))
            else:
                target = self.visit(target)
                self.writer.write('delete {};'.format(target))

    # Assign(expr* targets, expr value)
    def visit_Assign(self, node):
        value = self.visit(node.value)
        if len(self._def_stack) == 0:  # module level definition must be exported
            export = True
        else:
            export = False
        if len(node.targets) == 1 and not isinstance(node.targets[0], Tuple):
            target = node.targets[0]
            if isinstance(target, Attribute):
                self.writer.write('pythonium_set_attribute({}, "{}", {});'.format(
                    self.visit(target.value),
                    target.attr.replace('__DOLLAR__', '$'),
                    value
                ))
                return
            elif isinstance(target, Subscript):
                self.writer.write('pythonium_call(pythonium_get_attribute({}, "__setitem__"), {}, {});'.format(
                    self.visit(target.value),
                    self.visit(target.slice),
                    value,
                ))
                return
            else:
                target = self.visit(target)
                if export:
                    self.__all__.append(target)
                self.writer.write('{} = {};'.format(target, value))
                return

        self.writer.write('var __assignement = {};'.format(value))
        for target in node.targets:
            if isinstance(target, Tuple):
                targets = map(self.visit, target.elts)
                if export:
                    self.__all__.extend(targets)
                self.writer.write('var getitem = pythonium_get_attribute(__assignement, "__getitem__");')
                for index, target in enumerate(targets):
                    self.writer.write('{} = getitem(pythonium_call(int, {}));'.format(target, index))
            else:
                if isinstance(target, Attribute):
                    name = self.visit(target.value)
                    attr = target.attr.replace('__DOLLAR__', '$')
                    self.writer.write('pythonium_set_attribute({}, "{}", {});'.format(
                        name,
                        attr,
                        value,
                    ))
                else:
                    target = self.visit(target)
                    if self._def_stack and isinstance(self._def_stack[-1], ClassDefNode):
                        name = '__{}_{}'.format(self._def_stack[-1].name, target)
                    else:
                        name = target
                        if export:
                            self.__all__.extend(name)
                    self.writer.write('{} = __assignement;'.format(name))
                if self._def_stack and isinstance(self._def_stack[-1], ClassDefNode):
                    return target, name

    # Expr(expr value)
    def visit_Expr(self, node):
        self.writer.write(self.visit(node.value) + ';')

    # Return(expr? value)
    def visit_Return(self, node):
        if node.value:
            self.writer.write('return {};'.format(self.visit(node.value)))
            return
        self.writer.write('return __NONE;')

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
            c = '(pythonium_get_attribute({}, "{}")({}))'.format(next(iter), op, c)
        return c

    # BoolOp(boolop op, expr* values)
    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        out = self.visit(node.values[0])
        for value in node.values[1:]:
            v = self.visit(value)
            out = 'pythonium_call(pythonium_get_attribute({}, "{}"), {})'.format(v, op, out)
        return out

    # Assert(expr test, expr? msg)
    def visit_Assert(self, node):
        test = self.visit(node.test)
        msg = self.visit(node.msg) if node.msg else 'undefined'
        self.writer.write('ASSERT({}, {});'.format(test, msg))

    # If(expr test, stmt* body, stmt* orelse)
    def visit_If(self, node):
        test = self.visit(node.test)
        self.writer.write('if (pythonium_is_true({})) {{'.format(test))
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
        self.writer.write('if (pythonium_is_true({})) {{'.format(self.visit(node.test)))
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
        keys = []
        values = []
        for i in range(len(node.keys)):
            k = self.visit(node.keys[i])
            keys.append(k)
            v = self.visit(node.values[i])
            values.append(v)
        if node.keys:
            name = '__a_dict{}'.format(self.uuid())
            self.writer.write('var {} = pythonium_call(dict);'.format(name))
            for key, value in zip(keys, values):
                self.writer.write('{}.__class__.__setitem__({}, {}, {});'.format(name, name, key, value))
            return name
        else:
            return 'pythonium_call(dict)'

    # With(withitem* items, stmt* body)
    visit_With = NotImplemented

    # withitem = (expr context_expr, expr? optional_vars)
    visit_withitem = NotImplemented

    # For(expr target, expr iter, stmt* body, stmt* orelse)
    def visit_For(self, node):
        # support only arrays
        target = node.target.id
        iterator = self.visit(node.iter) # iter is the python iterator
        self.writer.write('try {')
        self.writer.push()
        nextname = '__next{}__'.format(self.uuid())
        self.writer.write('var {} = pythonium_get_attribute(iter({}), "__next__");'.format(nextname, iterator))
        self.writer.write('while(true) {')
        self.writer.push()
        self.writer.write('var {} = {}();'.format(target, nextname))
        list(map(self.visit, node.body))
        self.writer.pull()
        self.writer.write('}')
        self.writer.pull()
        self.writer.write('} catch (__exception__) { if (!pythonium_is_exception(__exception__, StopIteration)) { throw x; }}')

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
            self.writer.write('var {} = pythonium_create_empty_dict();'.format(varkwargs))
            self.writer.write('var varkwargs_start = undefined;')
            self.writer.pull()
            self.writer.write('}')
        num_args = len(args)
        for index, keyword in enumerate(kwargs.keys()):
            position = num_args + index - 1
            self.writer.write('if (varkwargs_start !== undefined && {} > varkwargs_start) {{'.format(position))
            self.writer.push()

            self.writer.write('{} = {}.__class__.get({}, {}) || {};'.format(keyword, varkwargs, varkwargs, keyword, kwargs[keyword]))
            self.writer.pull()
            self.writer.write('} else {')
            self.writer.push()
            self.writer.write('{} = {} || {}.__class__.get({}, {}) || {};'.format(keyword, keyword, varkwargs, varkwargs, keyword, kwargs[keyword]))
            self.writer.pull()
            self.writer.write('}')
            if varkwargs != '__kwargs':
                self.writer.write('delete {}.{};'.format(varkwargs, keyword))
        if varargs:
            self.writer.write('__args = __args.splice({});'.format(len(args)))
            if varkwargs and (varkwargs != '__kwargs' or kwargs):
                self.writer.write('if (varkwargs_start) {{ __args.splice(varkwargs_start - {}) }}'.format(len(args)))
            self.writer.write('var {} = pythonium_call(tuple);'.format(varargs))
            self.writer.write('{}.jsobject = __args;'.format(varargs))
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
        if len(self._def_stack) == 0:  # module level definition must be exported
            self.__all__.append(node.name)
        if len(node.bases) == 0:
            bases = ['object']
        else:
            bases = map(self.visit, node.bases)
        bases = '[{}]'.format(', '.join(bases))

        self._def_stack.append(ClassDefNode(node.name))
        self.writer.write('/* class definition {} */'.format(node.name))
        definitions = []
        for child in node.body:
            definitions.append(self.visit(child))

        self.writer.write('var {} = pythonium_create_class("{}", {}, {{'.format(node.name, node.name, bases))
        self.writer.push()
        for o in definitions:
            if not o:
                continue
            name, definition = o
            self.writer.write('{}: {},'.format(name, definition))
        self.writer.pull()
        self.writer.write('});')
        self._def_stack.pop()
