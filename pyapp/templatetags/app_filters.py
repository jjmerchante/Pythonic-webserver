from django import template
import time


register = template.Library()


@register.filter(name='to_date_string')
def to_date_string(value):
    return time.strftime('%d %b %Y %H:%M:%S', time.localtime(int(value))) + " UTC"

@register.filter(name='percentage')
def percentage(value, arg):
    return 100.0 * value/arg

@register.filter(name='parse_repository')
def parse_repository(repo_url):
    repo_name = repo_url.split('/')[-1][:-4]
    user_name = repo_url.split('/')[-2]
    return user_name + '/' + repo_name

@register.filter(name='pygment_file')
def pygment_file(file):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    try:
        with open(file, 'r') as f:
            code = f.read()
            return highlight(code, PythonLexer(), HtmlFormatter())
    except IOError as e:
        print e
        return "<pre>INTERNAL ERROR: Cannot load the code</pre>"
