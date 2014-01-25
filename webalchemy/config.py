import imp
import os.path


DEFAULT_SETTINGS = {
        'SERVER_STATIC_PATH': 'static',
        'SERVER_WS_ROUTE': 'websocket',
        'SERVER_HOST': '127.0.0.1',
        'SERVER_PORT': 8080,
        'SERVER_SSL_CERT': None,
        'SERVER_SSL_KEY': None,
        'SERVER_MONITORED_FILES': None,
        'SERVER_MAIN_ROUTE': None,
        'FREEZE_OUTPUT': None,
}


def read_config_from_app(app):
    settings = DEFAULT_SETTINGS.copy()
    if hasattr(app, 'config'):
        settings.update(app.config)
    return settings

def from_object(obj):
    if isinstance(obj, str):
        obj = _import_object(obj)
    cfg = Config()
    for key in dir(obj):
        if key.isupper():
            cfg[key] = getattr(obj, key)
    return cfg

def _import_object(objname):
    if '.' in objname:
        module, objname = objname.rsplit('.', 1)
        return getattr(__import__(module, None, None, [objname]), objname)
    else:
        return __import__(objname)

def from_pyfile(filename, root=None):
    if not (root is None):
        filename = os.path.join(root, filename)
    mod = imp.new_module('config')
    mod.__file__ = filename
    with open(filename) as config_file:
        exec(compile(config_file.read(), filename, 'exec'), mod.__dict__)
    return from_object(mod)

def from_envvar(variable_name):
    value = os.environ.get(variable_name)
    if not value:
        return dict()
    return from_pyfile(value)

def from_dict(d):
    cfg = Config()
    cfg.update(d)
    return cfg


class Config(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

