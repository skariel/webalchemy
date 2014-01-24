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

