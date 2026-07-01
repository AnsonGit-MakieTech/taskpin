"""Shared permission helpers for views and templates."""


def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


def can_manage_task(user, task):
    """Admin, task creator, or assignee may edit, delete, or mark done."""
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    if task.created_by_id == user.id:
        return True
    if task.assigned_to_id == user.id:
        return True
    return False
