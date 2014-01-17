import os
from ast import NodeVisitor, parse
from io import StringIO


class YieldSearch(NodeVisitor):

    def visit_Yield(self, node):
        self.has_yield = True

    def visit_FunctionDef(self, node):
        pass  # do not visit nest function definition to determine
              # if a function has a yield or not...



class Writer:

    def __init__(self):
        self.level = 0
        self.output = StringIO()

    def push(self):
        self.level += 1

    def pull(self):
        self.level -= 1

    def write(self, code):
        self.output.write(' ' * 4 * self.level + code + '\n')

    def value(self):
        return self.output.getvalue()


def pythonium_generate_js(filepath, translator_class, requirejs=False, root_path=None, output=None, deep=None):
    dirname = os.path.abspath(os.path.dirname(filepath))
    if not root_path:
        root_path = dirname
    basename = os.path.basename(filepath)
    output_name = os.path.join(dirname, basename + '.js')
    if not output:
        print('Generating {}'.format(output_name))
    # generate js
    with open(os.path.join(dirname, basename)) as f:
        input = parse(f.read())
    tree = parse(input)
    translator = translator_class()
    translator.visit(tree)
    script = translator.writer.value()
    if requirejs:
        out = 'define(function(require) {\n'
        out += script
        if isinstance(translator.__all__, str):
            out += '\nreturn {};\n'.format(translator.__all__)
        elif isinstance(translator.__all__, list):
            all = ["{!r}: {}".format(x, x) for x in translator.__all__]
            public = '{{{}}}'.format(', '.join(all))
            out += '\nreturn {};\n'.format(public)
        else:
            raise Exception('__all__ is not defined!')
        out += '\n})\n'
        script = out
    if deep:
        for dependency in translator.dependencies:
            if dependency.startswith('.'):
                pythonium_generate_js(os.path.join(dirname, dependency + '.py'), requirejs, root_path, output, deep)
            else:
                pythonium_generate_js(os.path.join(root_path, dependency[1:] + '.py'), requirejs, root_path, output, deep)
    output.write(script)
