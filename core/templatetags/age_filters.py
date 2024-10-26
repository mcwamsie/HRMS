from dateutil.relativedelta import relativedelta
from django import template


from django.utils import timezone

register = template.Library()


@register.filter
def relative_time(date_time):
    now = timezone.now()
    age_difference = relativedelta(now, date_time)

    years = age_difference.years
    months = age_difference.months
    days = age_difference.days
    hours = age_difference.hours
    minutes = age_difference.minutes

    if years >= 1:
        return f"{years} yrs"

    if months >= 1:
        if months == 1:
            return f"month"
        else:
            return f"{months} months"

    if days >= 1:
        if days == 1:
            return f"day"
        else:
            return f"{days} days"
    if hours >= 1:
        if hours == 1:
            return f"hour"
        else:
            return f"{hours} hours"
    if minutes >= 1:
        if minutes == 1:
            return f"minute"
        else:
            return f"{minutes} minutes"
    return "just now"


@register.filter
def calculate_age(birthdate):
    today = timezone.now().today()
    age_difference = relativedelta(today, birthdate)

    age_str = ""
    years = age_difference.years
    months = age_difference.months
    days = age_difference.days

    if years >= 1:
        age_str += f"{years} yrs"

    if months >= 1:
        if years >= 1:
            age_str += f", {months} months"
        else:
            age_str += f"{months} months"

    if days >= 1:
        if years >= 1 or (months >= 1):
            age_str += f", {days} days"
        else:
            age_str += f"{days} days"
    return age_str
