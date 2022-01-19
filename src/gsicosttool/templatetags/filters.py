from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def var_exists(context, name):
    """

    I found this https://stackoverflow.com/questions/12924865/how-to-check-if-django-template-variable-is-defined
    to avoid Key errors when testing for variables in templates

    """
    dicts = context.dicts  # array of dicts
    if dicts:
        for d in dicts:
            if name in d:
                return True
    return False

@register.simple_tag(takes_context=True)
def key_exists(context, dict, key):
    """

    assuming the dict exists, test if the key exists in it

    """
    dicts = context.dicts  # array of dicts
    if dicts:
        for d in dicts:
            if dict in d:
                if key in dict:
                    return True
    return False
