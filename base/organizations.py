"""Organization membership helpers and query scoping."""

from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from functools import wraps

from .models import Organization, OrganizationMembership, Task, UserProfile


def get_membership(user):
    if not user.is_authenticated:
        return None
    return getattr(user, 'organization_membership', None)


def get_user_organization(user):
    membership = get_membership(user)
    return membership.organization if membership else None


def get_org_members(organization):
    return (
        User.objects
        .filter(organization_membership__organization=organization, is_active=True)
        .select_related('profile', 'organization_membership')
        .order_by('first_name', 'username')
    )


def users_share_organization(user_a, user_b):
    if not user_a.is_authenticated or not user_b.is_authenticated:
        return False
    membership_a = get_membership(user_a)
    membership_b = get_membership(user_b)
    if not membership_a or not membership_b:
        return False
    return membership_a.organization_id == membership_b.organization_id


def create_organization_with_admin(name, user):
    organization = Organization.objects.create(
        name=name.strip(),
        slug=Organization.unique_slug(name),
        created_by=user,
    )
    OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        role=OrganizationMembership.ROLE_ADMIN,
    )
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = 'admin'
    profile.save(update_fields=['role'])
    return organization


def add_user_to_organization(organization, user, role=OrganizationMembership.ROLE_MEMBER):
    membership, created = OrganizationMembership.objects.get_or_create(
        user=user,
        defaults={'organization': organization, 'role': role},
    )
    if not created and membership.organization_id != organization.pk:
        raise ValueError('User already belongs to another organization.')
    if not created:
        membership.role = role
        membership.save(update_fields=['role'])
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save(update_fields=['role'])
    return membership


def organization_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        organization = get_user_organization(request.user)
        if organization is None:
            return HttpResponseForbidden(
                'Your account is not linked to an organization. Contact your admin for an invite.'
            )
        request.organization = organization
        return view_func(request, *args, **kwargs)
    return wrapper


def get_org_task(user, task_id):
    organization = get_user_organization(user)
    return get_object_or_404(Task, pk=task_id, organization=organization)


def tasks_for_organization(organization):
    return Task.objects.filter(organization=organization)


def activity_logs_for_organization(organization):
    from .models import ActivityLog
    return ActivityLog.objects.filter(organization=organization)
