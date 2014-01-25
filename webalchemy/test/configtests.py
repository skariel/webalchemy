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
        self.verify_config(cfg, AppDummyWithoutConfig)

    def test_overridden_settings(self):
        cfg = config.read_config_from_app(AppDummyWithConfig)
        self.verify_config(cfg, AppDummyWithConfig)

    def verify_config(self, cfg, app):
        for key, value in config.DEFAULT_SETTINGS.items():
            if hasattr(app, 'config') and key in app.config:
                self.assertEqual(cfg[key], app.config[key])
            else:
                self.assertEqual(cfg[key], config.DEFAULT_SETTINGS[key])


if __name__ == '__main__':
    unittest.main()
