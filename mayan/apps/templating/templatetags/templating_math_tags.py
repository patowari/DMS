import math

from django.template import Library

register = Library()


def _process_value(value):
    if str(value) == value:
        try:
            value = float(value)
        except ValueError:
            value = int(value)

    return value


@register.filter
def math_add(value, argument):
    """
    Mathematical addition.
    """

    addends = _process_value(value=value), _process_value(value=argument)
    result = addends[0] + addends[1]
    return result


@register.filter
def math_absolute(value):
    """
    Mathematical absolute.
    """

    value = _process_value(value=value)
    result = abs(value)
    return result


@register.filter
def math_divide(value, argument):
    """
    Mathematical division.
    """

    dividend = _process_value(value=value)
    divisor = _process_value(value=argument)
    quotient = dividend / divisor
    return quotient


@register.filter
def math_exponentiate(value, argument):
    """
    Mathematical exponentiation.
    """

    base = _process_value(value=value)
    exponent = _process_value(value=argument)
    power = base ** exponent
    return power


@register.filter
def math_floor_divide(value, argument):
    """
    Mathematical floor division.
    """

    dividend = _process_value(value=value)
    divisor = _process_value(value=argument)
    quotient = dividend // divisor
    return quotient


@register.filter
def math_modulo(value, argument):
    """
    Mathematical modulo.
    """

    dividend = _process_value(value=value)
    divisor = _process_value(value=argument)
    modulus = dividend % divisor
    return modulus


@register.filter
def math_multiply(value, argument):
    """
    Mathematical multiplication.
    """

    multiplicand = _process_value(value=value)
    multiplier = _process_value(value=argument)
    product = multiplicand * multiplier
    return product


@register.filter
def math_square_root(value):
    """
    Mathematical square root.
    """

    radicand = _process_value(value=value)
    square_root = math.sqrt(radicand)
    return square_root


@register.filter
def math_substract(value, argument):
    """
    Mathematical subtraction.
    """

    minuend = _process_value(value=value)
    subtrahend = _process_value(value=argument)
    difference = minuend - subtrahend
    return difference
