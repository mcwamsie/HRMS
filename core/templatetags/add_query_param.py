from django import template
from urllib.parse import urlencode, parse_qs

register = template.Library()


@register.simple_tag
def add_query_param(url, key, value):
    """Adds or overrides a query parameter in a URL."""
    uri_parts = list(url.split('?'))
    query_dict = parse_qs(uri_parts[1]) if len(uri_parts) > 1 else {}
    query_dict[key] = value
    new_query_str = urlencode(query_dict, doseq=True)
    return uri_parts[0] + '?' + new_query_str
