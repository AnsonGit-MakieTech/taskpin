"""Shared permission helpers for views and templates."""

from .organizations import get_membership, get_user_organization, users_share_organization


def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    membership = get_membership(user)
    if membership and membership.role == 'admin':
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


def user_can_access_task(user, task):
    organization = get_user_organization(user)
    return organization is not None and task.organization_id == organization.pk


def is_task_owner(user, task):
    """Task creator (owner who pinned the note)."""
    return user.is_authenticated and task.created_by_id == user.id


def can_manage_task(user, task):
    """Admin, task creator, or assignee may edit or mark done."""
    if not user_can_access_task(user, task):
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
    if not user_can_access_task(user, task):
        return False
    if is_admin(user):
        return True
    return is_task_owner(user, task)


def can_message_user(user, other_user):
    return users_share_organization(user, other_user)
