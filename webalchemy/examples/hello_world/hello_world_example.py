class HellowWorldApp:
    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        h1 = self.rdoc.body.element(h1='Hello World!!!')
        h1.events.add(click=self.clicked, translate=True)
        self.rdoc.body.element(h2='--------------')
        self.rdoc.stylesheet.rule('h1').style(
            color='#FF0000',
            marginLeft='75px',
            marginTop='75px',
            background='#00FF00'
        )

    def clicked(self):
        self.textContent = self.textContent[1:]

if __name__ == '__main__':
    from webalchemy import server
    from webalchemy.examples.hello_world.hello_world_example import HellowWorldApp
    server.run(HellowWorldApp)


