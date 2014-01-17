import copy

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

    old_visit_call = copy.copy(Veloce.visit_Call)
    def weba_visit_Call(self, node):
        name = self.visit(node.func)
        if name == 'rpc':
            args = list(map(self.visit, node.args))
            args = ', '.join(args)
            return '#rpc{{{}}}'.format(args)
        elif name == 'srv':
            args = list(map(self.visit, node.args))
            args = ', '.join(args)
            return '#{{{}}}'.format(args)
        else:
            old_visit_call(self, node)


    from pythonium.veloce.veloce import Veloce
    Veloce.visit_Lambda = fixed_visit_Lambda
    Veloce.visit_Subscript = fixed_visit_Subscript
    Veloce.visit_Call = weba_visit_Call


def monkeypatch():
    monkeypatch_pythonium()