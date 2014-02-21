from webalchemy.Stacker import Stacker, HtmlShortcuts
from webalchemy.stacker_wrappers.bootstrap_3.bootstrap3_wrapper import BootstrapShortcuts
from sympy import *

examples = [
    (r'Take the derivative of \(\sin{(x)}e^x\)', 'diff(sin(x)*exp(x), x)'),
    (r'Compute \(\int(e^x\sin{(x)} + e^x\cos{(x)})\,dx\)', 'integrate(exp(x)*sin(x) + exp(x)*cos(x), x)'),
    (r'Compute \(\int_{-\infty}^\infty \sin{(x^2)}\,dx\)', 'integrate(sin(x**2), (x, -oo, oo))'),
    (r'Find \(\lim_{x\to 0}\frac{\sin{(x)}}{x}\)', 'limit(sin(x)/x, x, 0)'),
    (r'Solve \(x^2 - 2 = 0\)', 'solve(x**2 - 2, x)'),
    (r'Solve the differential equation \(y'' - y = e^t\)', '''y = Function('y'); dsolve(Eq(y(t).diff(t, t) - y(t), exp(t)), y(t))'''),
    (r'Find the eigenvalues of \(\left[\begin{smallmatrix}1 & 2\\2 & 2\end{smallmatrix}\right]\)', 'Matrix([[1, 2], [2, 2]]).eigenvals()'),
    (r'Rewrite the Bessel function \(J_{\nu}\left(z\right)\) in terms of the spherical Bessel function \(j_\nu(z)\)','besselj(nu, z).rewrite(jn)')
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
        h = HtmlShortcuts(s)
        b = BootstrapShortcuts(s)
        with b.container(), b.row(), b.col(md=12):
            with h.div(cls='page-header'):
                with h.h1(text="The Math Exploerer"):
                    h.small(text=" use it for... uhm... exploring math?")
            with b.row(), b.col(md=12):
                with b.alert(dismissable=True):
                    h.h4(text="Warning:")
                    h.p(innerHtml="This example uses SymPy's sympify to parse user input which is <strong>unsafe</strong> - use at your own risk and please consider before running it on a web server...")
            with b.row():
                # left column
                with b.col(md=7):
                    with b.panel():
                        self.pbody = b.panel_body(style={'minHeight':'500px', 'overflowY':'auto'})
                    with h.div(cls='well'):
                        self.inp = h.input(cls='form-control', att={'placeholder': "Enter Math here (see examples)"})
                        self.inp.events.add(keydown=self.execute, translate=True)
                # right column
                with b.col(md=5):
                    with b.panel(flavor='success'):
                        with b.panel_heading(text="Examples:"):
                            b.button(text="toggle", att={'data-toggle':"collapse", 'data-target':"#examples_body"},
                                     size='xs',
                                     cls="pull-right")
                        with b.list_group(customvarname='examples_body', cls='collapse in'):
                            for desc, codes in examples:
                                with b.list_group_item(text=desc.replace('\\', '\\\\')):
                                    for code in codes.split(';'):
                                        h.br()
                                        h.code(text=code).events.add(click=lambda: self.inp.prop(value=code))
                    with b.panel(flavor='info'):
                        b.panel_heading(text="Symbols:")
                        b.panel_body(text="x")
                    with b.panel(flavor='info'):
                        b.panel_heading(text="Functions:")
                        b.panel_body(text="bla bla")
        self.rdoc.JS('MathJax.Hub.Queue(["Typeset",MathJax.Hub, "examples_body"]);')

    def execute(e):
        if e.keyCode == weba.KeyCode.ENTER:
            rpc(self.calc_with_sympy, self.value)

    def calc_with_sympy(self, sender_id, text):
        try:
            self.pbody.element(p=str(sympify(text)))
        except Exception as e:
            self.pbody.element('p').prop.innerHTML = str(e).replace("\n", '<br>')


if __name__ == "__main__":
    from webalchemy import server
    from math_explorer import MathExplorer
    server.run(MathExplorer)




