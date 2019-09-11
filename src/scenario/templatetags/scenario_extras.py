from django import template

register = template.Library()

@register.filter
def percentage(value):
    try:
        return format(float(value), ".2%")
    except (ValueError, ZeroDivisionError):
        return "pcterr"

def as_percentage_of(part, whole):
    try:
        return "%d%%" % (float(part) / whole * 100)
    except (ValueError, ZeroDivisionError):
        return "ze"