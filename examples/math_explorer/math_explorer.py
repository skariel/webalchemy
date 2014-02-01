# -*- encoding: utf-8 -*-

from webalchemy.Stacker import Stacker

def div(cont, *classes):
    '''add div with classes'''
    return cont.element('div', cls=classes)


examples = [
    ('Take the derivative of sin(x)ex.', 'diff(sin(x)*exp(x), x)'),
    ('Compute ∫(exsin(x)+excos(x))dx.', 'integrate(exp(x)*sin(x) + exp(x)*cos(x), x)'),
    ('Compute ∫∞−∞sin(x2)dx.', 'integrate(sin(x**2), (x, -oo, oo))'),
    ('Find limx→0sin(x)x.', 'limit(sin(x)/x, x, 0)'),
    ('Solve x2−2=0.', 'solve(x**2 - 2, x)'),
    ('Solve the differential equation y″−y=et.', '''y = Function('y'); dsolve(Eq(y(t).diff(t, t) - y(t), exp(t)), y(t))'''),
    ('Find the eigenvalues of [1222].', 'Matrix([[1, 2], [2, 2]]).eigenvals()'),
    ('Rewrite the Bessel function Jν(z) in terms of the spherical Bessel function jν(z).','besselj(nu, z).rewrite(jn)')
]


functions = ['diff', 'integrate', 'limit', ]

class MathExplorer:
    '''Application to explore math from the browser'''

    include = ['//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js',
            '//netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js',
            'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML']
    stylesheets = ['//netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css']

    def initialize(self, **kwargs):
        try:
            self.rdoc = kwargs['remote_document']
            s = Stacker(self.rdoc.body)
            with s.element('div', cls='container'):
                with s.element('div', cls='row'):
                    with s.element('div', cls='col-md-12 page-header'):
                        with s.element(h1="The Math Exploerer"):
                            s.element(small=" use it for... uhm... exploring math?")
                with s.element('div', cls='row'):
                    with s.element('div', cls='col-md-7'):
                        with s.element('div', cls='row'):
                            with s.element('div', cls='col-md-12 panel panel-default'):
                                s.element('div', cls='panel-body', style={'minHeight':'500px', 'overflowY':'auto'})
                        with s.element('div', cls='row'):
                            with s.element('div', cls='col-md-12 well'):
                                with s.element('form'):
                                    s.element('input', cls='form-control', att={'placeholder': "Enter Math here (see examples)"})
                    with s.element('div', cls='col-md-5'):
                        with s.element('div', cls='row'):
                            with s.element('div', cls='col-md-12'):
                                with s.element('div', cls='panel panel-success'):
                                    with s.element('div', text="Examples:", cls='panel-heading'):
                                        s.element(button="toggle", att={'data-toggle':"collapse", 'data-target':"#examples_body"},  cls="btn btn-xs btn-default pull-right")
                                    with s.element('div', customvarname='examples_body', cls='panel-body collapse in'):
                                        with s.element('ul'):
                                            for desc, codes in examples:
                                                with s.element('li', text=desc):
                                                    for code in codes.split(';'):
                                                        s.element('br')
                                                        s.element('code', text=code)
                        with s.element('div', cls='row'):
                            with s.element('div', cls='col-md-12'):
                                with s.element('div', cls='panel panel-info'):
                                    s.element('div', text="Symbols:", cls='panel-heading')
                                    s.element('div', text="x", cls='panel-body')
                        
                        with s.element('div', cls='row'):
                            with s.element('div', cls='col-md-12'):
                                with s.element('div', cls='panel panel-info'):
                                    s.element('div', text="Functions:", cls='panel-heading')
                                    s.element('div', text="bla bla", cls='panel-body')    

        except Exception:
            import traceback
            print(traceback.format_exc())

    
if __name__ == "__main__":
    from webalchemy import server
    server.run(MathExplorer)




