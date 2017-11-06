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
