"""
Custom template filters for CashScanExplorer
"""
from django import template
import json

register = template.Library()


@register.filter(name='dict_get')
def dict_get(dictionary, key):
    """Get value from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter(name='json_dumps')
def json_dumps(value):
    """Convert Python object to JSON string"""
    return json.dumps(value)
