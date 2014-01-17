import sys
import os

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from webalchemy import server


class HellowWorldApp:
    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.rdoc.body.element(h1='Hello World!!!').events.add(click=self.clicked, translate=True)
        self.rdoc.body.element(h2='--------------')
        self.rdoc.stylesheet.rule('h1').style(
            color='#FF0000',
            marginLeft='75px',
            marginTop='75px',
            background='#00FF00'
        )

    def clicked(self):
        self.textContent = self.textContent[1:]
        rpc(self.handle_click_on_backend, 'some message', 'just so you see how to pass paramaters')

    def handle_click_on_backend(self, sender_id, m1, m2):
        self.rdoc.body.element(h1=m1+m2)

if __name__ == '__main__':
    server.run(HellowWorldApp)


