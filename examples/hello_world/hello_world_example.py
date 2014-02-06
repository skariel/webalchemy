from webalchemy import server

class HellowWorldApp:
    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.print_hi = self.rdoc.translate(self.print_hi)
        self.rdoc.body.element(h1='Hello World!').events.add(click=self.clicked, translate=True)
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
        srv(self.print_hi)()

    def handle_click_on_backend(self, sender_id, m1, m2):
        self.rdoc.body.element(h1=m1+m2)

    def print_hi(self):
        print('hi!')

if __name__ == '__main__':
    # this import is necessary because of the live editing. Everything else works OK without it
    from hello_world_example import HellowWorldApp
    server.run(HellowWorldApp)


