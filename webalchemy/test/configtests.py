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


class TestReadConfigFromApp(unittest.TestCase):

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


class TestFromObject(unittest.TestCase):

    def test_from_module(self):
        cfg = config.from_object('settingsmodule')
        self.assertEqual(3, len(cfg))
        self.assertEqual('one', cfg['TEST_SETTING_1'])
        self.assertEqual('two', cfg['TEST_SETTING_2'])
        self.assertEqual(3, cfg['TEST_SETTING_3'])

    def test_from_class(self):
        cfg = config.from_object('settingsmodule.TestSettings')
        self.assertEqual(3, len(cfg))
        self.assertEqual(1, cfg['TEST_SETTING_1'])
        self.assertEqual(2, cfg['TEST_SETTING_2'])
        self.assertEqual('three', cfg['TEST_SETTING_3'])

    def test_module_from_package(self):
        cfg = config.from_object('settings.module')
        self.assertEqual(3, len(cfg))
        self.assertEqual('one', cfg['TEST_SETTING_1'])
        self.assertEqual('two', cfg['TEST_SETTING_2'])
        self.assertEqual(3, cfg['TEST_SETTING_3'])

    def test_from_module_instance(self):
        import settingsmodule
        cfg = config.from_object(settingsmodule)
        self.assertEqual(3, len(cfg))
        self.assertEqual('one', cfg['TEST_SETTING_1'])
        self.assertEqual('two', cfg['TEST_SETTING_2'])
        self.assertEqual(3, cfg['TEST_SETTING_3'])


class TestFromPyfile(unittest.TestCase):

    def test_from_py_file(self):
        cfg = config.from_pyfile('./settingsmodule.py')
        self.assertEqual(3, len(cfg))
        self.assertEqual('one', cfg['TEST_SETTING_1'])
        self.assertEqual('two', cfg['TEST_SETTING_2'])
        self.assertEqual(3, cfg['TEST_SETTING_3'])

    def test_from_py_file_with_root_path(self):
        rootpath = os.path.join(os.path.dirname(__file__), 'settings')
        cfg = config.from_pyfile('module.py', root=rootpath)
        self.assertEqual(3, len(cfg))
        self.assertEqual('one', cfg['TEST_SETTING_1'])
        self.assertEqual('two', cfg['TEST_SETTING_2'])
        self.assertEqual(3, cfg['TEST_SETTING_3'])


if __name__ == '__main__':
    unittest.main()
