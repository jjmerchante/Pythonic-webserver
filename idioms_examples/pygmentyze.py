from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import sys

if len(sys.argv) != 2:
    print "Usage: python {} file.py".format(sys.argv[0])
    exit(-1)
with open(sys.argv[-1], 'r') as f:
    code = f.read()
    print highlight(code, PythonLexer(), HtmlFormatter())
