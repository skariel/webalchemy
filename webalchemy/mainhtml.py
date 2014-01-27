import io
import os.path

from .remotedocument import RemoteDocument


class HtmlWriter:

    def __init__(self, output):
        self.output = output

    def write(self, text):
        self.output.write(text)

    def writeline(self, line):
        self.write(line + '\n')

    def write_script_tag(self, source, type='text/javascript'):
        line = '<script type="' + type + '" src="' + source + '"></script>'
        self.writeline(line)

    def write_meta_tag(self, attributes):
        self.write('<meta')
        for attr, value in attributes:
            self.write(' ' + attr + '="' + value + '"')
        self.writeline('>')
        
    def write_stylesheet_tag(self, source):
        line = '<link rel="stylesheet" href="' + source + '">'
        self.writeline(line)

    def include(self, file_path):
        with open(file_path, 'r') as f:
            self.writeline(f.read())


class MainHtml:

    @staticmethod
    def _default_translator(writer, app, tag, basedir):
        return

    def __init__(self, app, file_path):
        self.app = app
        self.file_path = file_path
        self.basedir = os.path.dirname(__file__)

    def translate(self, writer, translator=_default_translator,
            line_processor=None):
        with open(self.file_path, 'r') as input_file:
            for line in input_file:
                if not (line_processor is None):
                    line = line_processor(line)
                if line.lstrip().startswith('-->'):
                    tag = line.split()[1].strip()
                    translator(writer, self.app, tag, self.basedir)
                else:
                    writer.writeline(line.rstrip('\r\n'))


def get_main_html_for_app(app):
    main_html_file_path = get_main_html_file_path(app)
    return MainHtml(app, main_html_file_path)


def get_main_html_file_path(app):
    if hasattr(app, 'main_html_file_path'):
        return app.main_html_file_path

    main_dir = os.path.realpath(__file__)
    main_dir = os.path.dirname(main_dir)
    return os.path.join(main_dir, 'main.html')


def generate_main_html_for_server(app, ws_explicit_route, ssl):
    def main_html_translator(writer, app, tag, basedir):
        if tag == 'websocket':
            return
        if tag == 'include':
            if hasattr(app, 'include'):
                for i in app.include:
                    writer.write_script_tag(i)
            return
        if tag == 'meta':
            if hasattr(app, 'meta'):
                for m in app.meta:
                    writer.write_meta_tag(m.items())
            return
        if tag == 'stylesheets':
            if hasattr(app, 'stylesheets'):
                for s in app.stylesheets:
                    writer.write_stylesheet_tag(s)
            return
        writer.include(os.path.join(basedir, tag))

    template = get_main_html_for_app(app)
    output = io.StringIO()
    writer = HtmlWriter(output)
    template.translate(writer, main_html_translator)
    main_html = output.getvalue()
    main_html = main_html.replace('__WEBSOCKET__', ws_explicit_route)
    if ssl:
        main_html = main_html.replace('ws://', 'wss://')
    return main_html


def generate_static_main_html(App):
    def main_html_translator(writer, app, tag, basedir):
        if tag == 'include':
            if hasattr(app, 'include'):
                for i in app.include:
                    writer.write_script_tag(i)
            return
        if tag == 'meta':
            if hasattr(app, 'meta'):
                for m in app.meta:
                    writer.write_meta_tag(m.items())
            return
        if tag in ['js/classy.js', 'js/weba.js']:
            writer.include(os.path.join(basedir, tag))
            return
        if tag == 'websocket':
            writer.writeline('--> ' + tag)
            return

    def line_processor(line):
        if line.strip() == '<body onload="init_communication()">':
            return '<body>'
        return line

    template = get_main_html_for_app(App)
    output = io.StringIO()
    writer = HtmlWriter(output)
    template.translate(writer, main_html_translator, line_processor)
    main_html = output.getvalue()
    lines = main_html.split('\n')

    static_html = []
    for l in lines:
        if l.lstrip().startswith('-->'):
            rdoc = RemoteDocument()
            app = App()
            app.initialize(remote_document=rdoc, main_html=main_html)
            l = rdoc.pop_all_code()
        static_html.append(l + '\n')
    return ''.join(static_html)

