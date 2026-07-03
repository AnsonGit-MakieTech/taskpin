from django import template

from base.permissions import can_manage_task, can_delete_task

register = template.Library()


@register.filter
def can_manage_task_filter(task, user):
    return can_manage_task(user, task)


@register.filter
def can_delete_task_filter(task, user):
    return can_delete_task(user, task)
