# core/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """辞書から key に対応する値を取り出す"""
    if dictionary:
        return dictionary.get(key, [])
    return []
