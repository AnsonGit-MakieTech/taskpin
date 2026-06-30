"""Helpers for broadcasting realtime board events."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def notify_board_update(action, task_id=None, actor_id=None, extra=None):
    """Send a board update event to all connected WebSocket clients."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        'type': 'board.update',
        'action': action,
        'task_id': task_id,
        'actor_id': actor_id,
    }
    if extra:
        payload.update(extra)

    try:
        async_to_sync(channel_layer.group_send)(
            'board',
            {'type': 'board.update', 'payload': payload},
        )
    except Exception:
        logger.exception('Failed to broadcast board update (%s)', action)
