from webalchemy.Stacker import Stacker
import sympy

examples = [
    ('Take the derivative of sin(x)ex.', 'diff(sin(x)*exp(x), x)'),
    ('Compute ?(exsin(x)+excos(x))dx.', 'integrate(exp(x)*sin(x) + exp(x)*cos(x), x)'),
    ('Compute ????sin(x2)dx.', 'integrate(sin(x**2), (x, -oo, oo))'),
    ('Find limx?0sin(x)x.', 'limit(sin(x)/x, x, 0)'),
    ('Solve x2?2=0.', 'solve(x**2 - 2, x)'),
    ('Solve the differential equation y??y=et.', '''y = Function('y'); dsolve(Eq(y(t).diff(t, t) - y(t), exp(t)), y(t))'''),
    ('Find the eigenvalues of [1222].', 'Matrix([[1, 2], [2, 2]]).eigenvals()'),
    ('Rewrite the Bessel function J?(z) in terms of the spherical Bessel function j?(z).','besselj(nu, z).rewrite(jn)')
]

functions = ['diff', 'integrate', 'limit', ]

class MathExplorer:
    """Application to explore math from the browser"""

    include = ['//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js',
               '//netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js',
               'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML']
    stylesheets = ['//netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css']

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        s = Stacker(self.rdoc.body)
        with s.div(cls='container'):
            with s.div(cls='row'):
                with s.div(cls='col-md-12 page-header'):
                    with s.h1(text="The Math Exploerer"):
                        s.small(text=" use it for... uhm... exploring math?")
            with s.div(cls='row'):
                # left column
                with s.div(cls='col-md-7'):
                    with s.div(cls='row'):
                        with s.div(cls='col-md-12 panel panel-default'):
                            self.pbody = s.div(cls='panel-body', style={'minHeight':'500px', 'overflowY':'auto'})
                    with s.div(cls='row'):
                        with s.div(cls='col-md-12 well'):
                            self.inp = s.input(cls='form-control', att={'placeholder': "Enter Math here (see examples)"})
                            self.inp.events.add(keydown=self.execute, translate=True)
                # right column
                with s.div(cls='col-md-5'):
                    with s.div(cls='row'):
                        with s.div(cls='col-md-12'):
                            with s.div(cls='panel panel-success'):
                                with s.div(text="Examples:", cls='panel-heading'):
                                    s.button(text="toggle", att={'data-toggle':"collapse", 'data-target':"#examples_body"},  cls="btn btn-xs btn-default pull-right")
                                with s.div(customvarname='examples_body', cls='panel-body collapse in'):
                                    with s.ul():
                                        for desc, codes in examples:
                                            with s.li(text=desc):
                                                for code in codes.split(';'):
                                                    s.br()
                                                    c = s.code(text=code)
                                                    c.events.add(click=lambda: self.inp.prop(value=c.text))
                    with s.div(cls='row'):
                        with s.div(cls='col-md-12'):
                            with s.div(cls='panel panel-info'):
                                s.div(text="Symbols:", cls='panel-heading')
                                s.div(text="x", cls='panel-body')
                    with s.div(cls='row'):
                        with s.div(cls='col-md-12'):
                            with s.div(cls='panel panel-info'):
                                s.div(text="Functions:", cls='panel-heading')
                                s.div(text="bla bla", cls='panel-body')

    def execute(e):
        if e.keyCode == weba.KeyCode.ENTER:
            rpc(self.calc_with_sympy, self.value)

    def calc_with_sympy(self, sender_id, text):
        try:
            self.pbody.element(p=str(sympy.N(text)))
        except Exception as e:
            self.pbody.element('p').prop.innerHTML = str(e).replace("\n", '<br>')


if __name__ == "__main__":
    from webalchemy import server
    from math_explorer import MathExplorer
    server.run(MathExplorer)




