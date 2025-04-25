from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Умножает значение на аргумент.
    Используется в шаблонах для вычисления стоимости (цена * количество).
    """
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0
