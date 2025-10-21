# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    # dict.get(key) 相当。存在しなければ空リスト返して for empty が動く
    return d.get(key, [])
