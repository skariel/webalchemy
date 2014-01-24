import os.path
import sys
import unittest

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from webalchemy import config


class AppDummyWithoutConfig:
    
    def initialize(self, **kwargs):
        pass


class AppDummyWithConfig:

    config = {
            'SERVER_PORT': 3000,
            'SERVER_STATIC_PATH': 'public',
            'SERVER_SSL_CERT': 'mydomain.crt',
            'SERVER_SSL_KEY': 'mydomain.key',
            'FREEZE_OUTPUT': 'output.html',
    }
    
    def initialize(self, **kwargs):
        pass


class TestConfig(unittest.TestCase):

    def test_default_settings(self):
        cfg = config.read_config_from_app(AppDummyWithoutConfig)
        self.assertEqual('static', cfg['SERVER_STATIC_PATH'])
        self.assertEqual('websocket', cfg['SERVER_WS_ROUTE'])
        self.assertEqual('127.0.0.1', cfg['SERVER_HOST'])
        self.assertEqual(8080, cfg['SERVER_PORT'])
        self.assertIsNone(cfg['SERVER_MONITORED_FILES'])
        self.assertIsNone(cfg['SERVER_SSL_CERT'])
        self.assertIsNone(cfg['SERVER_SSL_KEY'])
        self.assertIsNone(cfg['SERVER_MAIN_ROUTE'])
        self.assertIsNone(cfg['FREEZE_OUTPUT'])

    def test_overridden_settings(self):
        cfg = config.read_config_from_app(AppDummyWithConfig)
        self.assertEqual('public', cfg['SERVER_STATIC_PATH'])
        self.assertEqual('websocket', cfg['SERVER_WS_ROUTE'])
        self.assertEqual('127.0.0.1', cfg['SERVER_HOST'])
        self.assertEqual(3000, cfg['SERVER_PORT'])
        self.assertIsNone(cfg['SERVER_MONITORED_FILES'])
        self.assertEqual('mydomain.crt', cfg['SERVER_SSL_CERT'])
        self.assertEqual('mydomain.key', cfg['SERVER_SSL_KEY'])
        self.assertIsNone(cfg['SERVER_MAIN_ROUTE'])
        self.assertEqual('output.html', cfg['FREEZE_OUTPUT'])


if __name__ == '__main__':
    unittest.main()
