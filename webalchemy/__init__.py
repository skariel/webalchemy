import os, sys
if '--pythonjs' in sys.argv:
	assert os.path.isdir( os.path.expanduser('~/PythonJS') )
	try:
		import sockjs
	except ImportError:
		assert os.path.isdir( os.path.expanduser('~/sockjs-tornado'))
		sys.path.append( os.path.expanduser('~/sockjs-tornado') )
else:
	from .monkeypatch import monkeypatch
	monkeypatch()

version = "0.3.8"

