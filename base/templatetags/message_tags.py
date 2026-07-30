import re

from django import template
from django.utils.html import escape, urlize
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def message_body(value):
    """Escape message text, linkify URLs, and preserve line breaks."""
    if not value:
        return ''
    linked = urlize(escape(value), nofollow=True, autoescape=False)
    linked = re.sub(
        r'<a ',
        '<a class="msg-link" target="_blank" rel="noopener noreferrer" ',
        linked,
    )
    return mark_safe(linked.replace('\n', '<br>'))


@register.inclusion_tag('messages/_read_receipt.html')
def message_read_receipt(message, viewer):
    from base import messaging
    return messaging.read_receipt_context(message, viewer)
