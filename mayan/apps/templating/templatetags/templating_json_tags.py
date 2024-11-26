import json

from django.template import Library

register = Library()


@register.filter
def json_load(value):
    """
    Deserialize string to a Python object.
    """
    obj = json.loads(s=value)

    return obj
