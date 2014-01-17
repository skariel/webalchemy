#!/usr/bin/env python3
"""pythonium

Usage: pythonium [-h][-d][-r][-V] [FILE ...] [-o FILE] | [-g]

Options:
  -h --help        show this
  -v --version     show version
  -V --veloce      use veloce mode, generated code is faster but least compliant
  -o --output FILE specify output file [default: stdout]
  -d --deep        generate file dependencies. If --output is not provided, 
                   it will generate for each source file a coresponding .js file.
  -r --requirejs   generate requirejs compatible module
  -g --generate    generate pythonium runtime (exclusive option)

The default mode, without -V or --veloce option is *experimental*.

If you generate code without -V or --veloce you will need to use the library 
generated with -g or --generate option to run the code.
"""
import os
import sys

from .veloce.veloce import Veloce
from .compliant.compliant import Compliant
from .utils import pythonium_generate_js

__version__ = '0.6.3'


def main(argv=None):
    from docopt import docopt
    args = docopt(__doc__, argv, version='pythonium ' + __version__)
    if args['--generate']:
        # call ourself for each file in pythonium.lib:
        from pythonium import compliant
        from pythonium.compliant import builtins

        # runtime is built separatly
        # it must appear first in the file
        # and it must be built using veloce mode
        path = compliant.__path__[0]
        argv = ['--veloce', os.path.join(path, 'runtime.py')]
        main(argv)

        # compile builtins
        for path in builtins.__path__:
            for name in sorted(os.listdir(path)):
                if name.endswith('.py'):
                    argv = [os.path.join(path, name)]
                    main(argv)
        return

    filepaths = args['FILE']
    if not filepaths:
        main(['--help'])
        return

    translator = Veloce if args['--veloce'] else Compliant
    options = {'translator_class': translator,
               'requirejs': args['--requirejs'],
               'deep': args['--deep'],
               }

    outfile = args['--output']
    if outfile:
        with open(outfile, 'w') as output:
            for filepath in filepaths:
                pythonium_generate_js(filepath, output=output, **options)
    else:
        for filepath in filepaths:
            pythonium_generate_js(filepath, output=sys.stdout, **options)


if __name__ == '__main__':
    main()
