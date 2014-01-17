from __future__ import absolute_import, division, print_function, with_statement
from webalchemy.tornado.test.util import unittest


class ImportTest(unittest.TestCase):
    def test_import_everything(self):
        # Some of our modules are not otherwise tested.  Import them
        # all (unless they have external dependencies) here to at
        # least ensure that there are no syntax errors.
        import webalchemy.tornado.auth
        import webalchemy.tornado.autoreload
        import webalchemy.tornado.concurrent
        # import webalchemy.tornado.curl_httpclient  # depends on pycurl
        import webalchemy.tornado.escape
        import webalchemy.tornado.gen
        import webalchemy.tornado.httpclient
        import webalchemy.tornado.httpserver
        import webalchemy.tornado.httputil
        import webalchemy.tornado.ioloop
        import webalchemy.tornado.iostream
        import webalchemy.tornado.locale
        import webalchemy.tornado.log
        import webalchemy.tornado.netutil
        import webalchemy.tornado.options
        import webalchemy.tornado.process
        import webalchemy.tornado.simple_httpclient
        import webalchemy.tornado.stack_context
        import webalchemy.tornado.tcpserver
        import webalchemy.tornado.template
        import webalchemy.tornado.testing
        import webalchemy.tornado.util
        import webalchemy.tornado.web
        import webalchemy.tornado.websocket
        import webalchemy.tornado.wsgi

    # for modules with dependencies, if those dependencies can be loaded,
    # load them too.

    def test_import_pycurl(self):
        try:
            import pycurl
        except ImportError:
            pass
        else:
            import webalchemy.tornado.curl_httpclient
