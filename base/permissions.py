"""Shared permission helpers for views and templates."""


def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


def is_task_owner(user, task):
    """Task creator (owner who pinned the note)."""
    return user.is_authenticated and task.created_by_id == user.id


def can_manage_task(user, task):
    """Admin, task creator, or assignee may edit or mark done."""
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    if is_task_owner(user, task):
        return True
    if task.assigned_to_id == user.id:
        return True
    return False


def can_delete_task(user, task):
    """Only admin or task creator may delete — not the assignee."""
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    return is_task_owner(user, task)
