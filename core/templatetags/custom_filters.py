# core/templatetags/custom_filters.py
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def get_item(mapping, key):
    """
    dict から key で取り出す。無ければ空リストを返す。
    events_by_date は {date: [Event,...]} を想定。
    """
    try:
        return mapping.get(key, [])
    except AttributeError:
        return []

@register.filter
def time_range(ev):
    """
    Event -> 'HH:MM–HH:MM' / 'HH:MM〜' / '' を返す（ローカル時刻に変換して表示）
    """
    if not ev or not getattr(ev, "start", None):
        return ""
    s = timezone.localtime(ev.start)
    if getattr(ev, "end", None):
        e = timezone.localtime(ev.end)
        if s.time() == e.time():
            return f"{s:%H:%M}"
        return f"{s:%H:%M}–{e:%H:%M}"
    return f"{s:%H:%M}〜"
