import os.path

from bs4 import BeautifulSoup

from .remotedocument import RemoteDocument


def get_main_html_file_path(app):
    if hasattr(app, 'main_html_file_path'):
        return app.main_html_file_path

    main_dir = os.path.realpath(__file__)
    main_dir = os.path.dirname(main_dir)
    return os.path.join(main_dir, 'main.html')

# js files to be injected to main html, in this order:
js_files_to_inject_to_live_app = [
    'js/reconnecting_ws.js',
    'js/cookie.js',
    'js/vendor.js',
    'js/comm.js',
    'js/reconnection_overlay.js',
    'js/classy.js',
    'js/weba.js',
]

js_files_to_inject_to_frozen_app = [
    'js/classy.js',
    'js/weba.js',
]


def get_soup_head_body_and_scripts(app):
    with open(get_main_html_file_path(app), 'r') as f:
        html = f.read()
    s = BeautifulSoup(html)
    if not s.html.head:
        s.html.insert(0, s.new_tag('head'))
    head = s.html.head
    script = s.new_tag('script')
    s.html.append(script)
    if not s.html.body:
        s.html.append(s.new_tag('body'))
    body = s.html.body
    return s, head, body, script


def fill_head(app, s, head):
    head.append(s.new_tag('script', src='http://cdn.sockjs.org/sockjs-0.3.min.js'))
    if hasattr(app, 'include'):
        for i in app.include:
            head.append(s.new_tag('script', src=i))
    if hasattr(app, 'meta'):
        for m in app.meta:
            head.append(s.new_tag('meta', **m))
    if hasattr(app, 'stylesheets'):
        for stl in app.stylesheets:
            head.append(s.new_tag('link', rel='stylesheet', href=stl))


def generate_main_html_for_server(app, ssl):
    s, head, body, script = get_soup_head_body_and_scripts(app)

    # filling in the script tag with all contents from js files:
    basedir = os.path.dirname(__file__)
    for fn in js_files_to_inject_to_live_app:
        full_fn = os.path.join(basedir, fn)
        with open(full_fn, 'r') as f:
            text = f.read()
            if fn == 'js/comm.js':
                # socket url...
                if ssl:
                    text = text.replace('__SOCKET_URL__', "'https://'+location.host+'/app'")
                else:
                    text = text.replace('__SOCKET_URL__', "'http://'+location.host+'/app'")
            script.append(text+'\n')

    fill_head(app, s, head)
    body.attrs['onload'] = 'init_communication()'

    return s.prettify()


def generate_static_main_html(app):
    s, head, body, script = get_soup_head_body_and_scripts(app)

    # filling in the script tag with all contents from js files:
    basedir = os.path.dirname(__file__)
    for fn in js_files_to_inject_to_frozen_app:
        full_fn = os.path.join(basedir, fn)
        with open(full_fn, 'r') as f:
            script.append(f.read()+'\n')

    fill_head(app, s, head)

    rdoc = RemoteDocument()
    app().initialize(remote_document=rdoc, main_html=s.prettify())
    generated_scripts = rdoc.pop_all_code()
    script.append('\n\n'+generated_scripts+'\n\n')

    return s.prettify()


