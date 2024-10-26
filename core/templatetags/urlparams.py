from django import template
from urllib.parse import urlencode

from django import template
from django.core.handlers.wsgi import WSGIRequest

register = template.Library()


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v not in [None, '']}
    if safe_args:
        return '?{}'.format(urlencode(safe_args))
    return ''


@register.simple_tag(takes_context=True)
def url_params_add(context, **kwargs):
    request: WSGIRequest = context['request']
    params = request.GET.copy()  # Make a copy of the current GET parameters
    for k, v in kwargs.items():
        if v not in [None, '']:
            params[k] = v
        else:
            del params[k]
    if params:
        return request.path + '?{}'.format(urlencode(params))
    return '?'
