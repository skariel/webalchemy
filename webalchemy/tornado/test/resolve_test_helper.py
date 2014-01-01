from __future__ import absolute_import, division, print_function, with_statement
from webalchemy.tornado.ioloop import IOLoop
from webalchemy.tornado.netutil import ThreadedResolver
from webalchemy.tornado.util import u

# When this module is imported, it runs getaddrinfo on a thread. Since
# the hostname is unicode, getaddrinfo attempts to import encodings.idna
# but blocks on the import lock. Verify that ThreadedResolver avoids
# this deadlock.

resolver = ThreadedResolver()
IOLoop.current().run_sync(lambda: resolver.resolve(u('localhost'), 80))
