from django import template

register = template.Library()


@register.inclusion_tag('messages/_read_receipt.html')
def message_read_receipt(message, viewer):
    from base import messaging
    return messaging.read_receipt_context(message, viewer)
