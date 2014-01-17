from pythonium.veloce.veloce import Veloce

def monkeypatch_pythonium():
    '''

    a few fixes:
        - slices
        - lambda

    and a few things related to webalchemy:
        - call magic functions

    '''
    def fixed_visit_Subscript(self, node):
        slice = self.visit(node.slice)
        if not slice.startswith('slice('):
            return '{}[{}]'.format(self.visit(node.value), slice)
        else:
            return '{}.{}'.format(self.visit(node.value), slice)


    def fixed_visit_Lambda(self, node):
        args, kwargs, vararg, varkwargs = self.visit(node.args)
        name = '__lambda{}'.format(self.uuid())
        self.writer.write('var {} = function({}) {{'.format(name, ', '.join(args)))
        self.writer.push()
        self._unpack_arguments(args, kwargs, vararg, varkwargs)
        body = 'return '
        body += self.visit(node.body)
        self.writer.write(body)
        self.writer.pull()
        self.writer.write('}')
        return name

    def weba_visit_Call(self, node):
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
        # WEBA HERE!
        elif name == 'rpc':
            args = list(map(self.visit, node.args))
            args = ', '.join(args)
            return '#rpc{{{}}}'.format(args)
        elif name == 'srv':
            args = list(map(self.visit, node.args))
            args = ', '.join(args)
            return '#{{{}}}'.format(args)
        # END OF WEBA MANIPULATIONS!
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

    Veloce.visit_Lambda = fixed_visit_Lambda
    Veloce.visit_Subscript = fixed_visit_Subscript
    Veloce.visit_Call = weba_visit_Call


def monkeypatch():
    monkeypatch_pythonium()