import random
import string

from django import template

register = template.Library()


@register.filter(name='concat')
def concat(value, arg):
    """Concatenates the value with the argument."""
    return f"{value}{arg}"


@register.filter(name="generate_password")
def generate_password(size):
    return random_password_generator(size)

def random_password_generator(size=10, chars=string.ascii_letters + string.digits + "!#$%&@"):
    return ''.join(random.choice(chars) for _ in range(size))
