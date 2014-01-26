from webalchemy import server

class JQueryMobileExample:

    # Include the jQuery mobile stylesheet and the jQuery/jQuery mobile scripts
    stylesheets = ['http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.css']
    include = ['http://code.jquery.com/jquery-1.10.2.min.js',
               'http://code.jquery.com/mobile/1.4.0/jquery.mobile-1.4.0.min.js']
               
    # Use the modified html
    main_html_file_path = "jquerymobile_example.html"

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        # Grab the main <div> from the html document and inject some elements
        self.main = self.rdoc.getElementById('main')
        self.main.element(h1="Main content")
        self.main.element(button="A button")
        # Force jQuery to redraw (enhance) the document
        self.rdoc.JS('jQuery(#{self.main}).trigger("create")')


if __name__ == '__main__':
    # this import is necessary because of the live editing. Everything else works OK without it
    from jquerymobile_example import JQueryMobileExample
    server.run(JQueryMobileExample)
