import io
import os
import sys
import unittest

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from webalchemy import server
BASE_DIR = os.path.realpath(os.path.dirname(__file__))


TEMPLATE_DEFAULT = os.path.join(BASE_DIR, 'data/template_input.html')
TEMPLATE_REPLACEMENTS_INPUT = os.path.join(BASE_DIR, 'data/replacement_input.txt')
TEMPLATE_REPLACEMENTS_OUTPUT = os.path.join(BASE_DIR, 'data/replacement_output.txt')


class AppDummyWithFilePath:

    main_html_file_path = TEMPLATE_DEFAULT

    def initialize(self, **kwargs):
        pass


class AppDummyWithoutFilePath:

    def initialize(self, **kwargs):
        pass


class TestHtmlWriter(unittest.TestCase):

    def setUp(self):
        self.output = io.StringIO()
        self.writer = server.HtmlWriter(self.output)

    def test_write(self):
        self.writer.writeline('<html>')
        self.writer.write('</html>')
        self.verify_output('<html>\n</html>')

    def test_write_script_tag(self):
        self.writer.writeline('<html>')
        self.writer.write_script_tag('static/app.js')
        self.writer.writeline('</html>')
        expected = '<html>\n<script type="text/javascript" src="static/app.js"></script>\n</html>\n'
        self.verify_output(expected)

    def test_write_meta_tag(self):
        self.writer.writeline('<html>')
        self.writer.write_meta_tag([('charset', 'utf-8')])
        self.writer.write_meta_tag([('http-equiv', 'Content-Type'), ('content', 'text/html; charset=utf-8')])
        self.writer.writeline('</html>')
        expected = '''<html>
<meta charset="utf-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</html>
'''
        self.verify_output(expected)

    def test_include_absfile(self):
        self.writer.writeline('<html>')
        self.writer.include(TEMPLATE_REPLACEMENTS_OUTPUT)
        self.writer.writeline('</html>')
        expected = '''<html>
Text #1: replacement_input.txt
Text #2: replacement_input.txt
Text #3: replacement_input.txt
Text #4: replacement_input.txt

</html>
'''
        self.verify_output(expected)

    def verify_output(self, expected):
        self.assertEqual(expected, self.output.getvalue())


class TestMainHtml(unittest.TestCase):

    def test_get_file_path_from_app_class(self):
        expected_file_path = AppDummyWithFilePath.main_html_file_path
        main_html = server.get_main_html_for_app(AppDummyWithFilePath)
        self.assertEqual(expected_file_path, main_html.file_path)

    def test_get_default_file_path(self):
        main_dir = os.path.realpath(server.__file__)
        main_dir = os.path.dirname(main_dir)
        expected_file_path = os.path.join(main_dir, 'main.html')
        main_html = server.get_main_html_for_app(AppDummyWithoutFilePath)
        self.assertEqual(expected_file_path, main_html.file_path)

    def test_apply_template(self):
        def translator(writer, app, tag, basedir):
            writer.writeline(tag.replace('item ', 'Text #'))

        AppDummyWithFilePath.main_html_file_path = TEMPLATE_DEFAULT
        main_html = server.get_main_html_for_app(AppDummyWithFilePath)
        output = io.StringIO()
        writer = server.HtmlWriter(output)
        main_html.translate(writer, translator)
        self.verify_file_content(TEMPLATE_DEFAULT, output)

    def test_apply_template_with_replacements(self):
        def translator(writer, app, tag, basedir):
            prefix = tag.replace('item', 'Text #')
            file_name = os.path.basename(app.main_html_file_path)
            writer.writeline(prefix + ': ' + file_name)

        AppDummyWithFilePath.main_html_file_path = TEMPLATE_REPLACEMENTS_INPUT
        main_html = server.get_main_html_for_app(AppDummyWithFilePath)
        output = io.StringIO()
        writer = server.HtmlWriter(output)
        main_html.translate(writer, translator)
        self.verify_file_content(TEMPLATE_REPLACEMENTS_OUTPUT, output)

    def verify_file_content(self, expected_file_path, output):
        with open(expected_file_path, 'r') as f:
            self.assertEqual(f.read(), output.getvalue())


def templateItem1(writer, app):
    pass


if __name__ == '__main__':
    unittest.main()
