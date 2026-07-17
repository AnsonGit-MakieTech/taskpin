"""Online presence tracking via cache (WebSocket + heartbeat)."""

from django.core.cache import cache

from .organizations import get_org_members

ONLINE_TTL = 90
HEARTBEAT_INTERVAL = 45


def _presence_key(organization_id, user_id):
    return f'taskpin:online:{organization_id}:{user_id}'


def set_user_online(organization_id, user_id):
    cache.set(_presence_key(organization_id, user_id), True, ONLINE_TTL)


def set_user_offline(organization_id, user_id):
    cache.delete(_presence_key(organization_id, user_id))


def refresh_user_online(organization_id, user_id):
    cache.set(_presence_key(organization_id, user_id), True, ONLINE_TTL)


def is_user_online(organization_id, user_id):
    return bool(cache.get(_presence_key(organization_id, user_id)))


def get_online_user_ids(organization):
    member_ids = get_org_members(organization).values_list('pk', flat=True)
    return [user_id for user_id in member_ids if cache.get(_presence_key(organization.pk, user_id))]
