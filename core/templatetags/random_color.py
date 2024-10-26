import random

from django import template

register = template.Library()

BG_COLORS = [
    'bg-danger-dark', 'bg-info-darker', 'bg-success-dark',
    'bg-warning-dark', 'bg-primary-dark', 'bg-secondary-dark'
]

@register.simple_tag
def random_color():
    return random.choice(BG_COLORS)

@register.simple_tag(takes_context=True)
def random_user_color(context):
    request = context['request']

    # Check if the color is already in the session
    if 'bg_color' not in request.session:
        # If not, select a random color and store it in the session
        bg_color = random.choice(BG_COLORS)
        request.session['bg_color'] = bg_color
    else:
        # Retrieve the color from the session
        bg_color = request.session['bg_color']
    return bg_color
