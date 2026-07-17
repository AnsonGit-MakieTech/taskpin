"""Helpers for broadcasting realtime board events."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def board_group_name(organization_id):
    """Return a Channels-safe group name (alphanumerics, hyphen, underscore, period only)."""
    return f'board.{organization_id}'


def notify_board_update(action, task_id=None, actor_id=None, extra=None, organization_id=None):
    """Send a board update event to connected WebSocket clients in an organization."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        'type': 'board.update',
        'action': action,
        'task_id': task_id,
        'actor_id': actor_id,
        'organization_id': organization_id,
    }
    if extra:
        payload.update(extra)

    group_name = board_group_name(organization_id) if organization_id else 'board'

    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {'type': 'board.update', 'payload': payload},
        )
    except Exception:
        logger.exception('Failed to broadcast board update (%s)', action)
