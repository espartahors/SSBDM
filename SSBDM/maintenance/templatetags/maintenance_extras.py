from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces and capitalize each word"""
    return value.replace('_', ' ').title()

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0
    
@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using key"""
    return dictionary.get(key, '')

@register.filter
def get_file_extension(filename):
    """Get the file extension from a filename"""
    try:
        import os
        return os.path.splitext(filename)[1][1:].lower()
    except:
        return ""

@register.filter
def endswith(text, suffix):
    """Check if string ends with suffix"""
    return text.endswith(suffix)