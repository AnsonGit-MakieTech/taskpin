from django import template

from base.permissions import can_manage_task, can_delete_task

register = template.Library()


@register.filter
def can_manage_task_filter(task, user):
    return can_manage_task(user, task)


@register.filter
def can_delete_task_filter(task, user):
    return can_delete_task(user, task)


@register.simple_tag
def user_can_delete_task(user, task):
    return can_delete_task(user, task)


@register.simple_tag
def user_can_manage_task(user, task):
    return can_manage_task(user, task)


@register.inclusion_tag('components/_avatar.html')
def user_avatar(user, css_class='', size=''):
    profile = getattr(user, 'profile', None) if user else None
    if profile:
        initials = profile.initials()
        color = profile.avatar_color()
        image_url = profile.avatar_photo_url
    elif user:
        initials = user.username[:2].upper()
        color = '#FFB74D'
        image_url = None
    else:
        initials = '?'
        color = '#64B5F6'
        image_url = None
    return {
        'css_class': css_class,
        'size': size,
        'initials': initials,
        'color': color,
        'image_url': image_url,
    }


@register.simple_tag(takes_context=True)
def filter_query(context, page=None):
    request = context.get('request')
    if not request:
        return ''
    from base.filters import filter_query_string
    return filter_query_string(request, page=page)
