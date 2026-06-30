"""Helpers for broadcasting realtime board events (future use from views)."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_board_update(action, task_id=None, extra=None):
    """Send a board update event to all connected WebSocket clients."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {'action': action, 'task_id': task_id}
    if extra:
        payload.update(extra)

    async_to_sync(channel_layer.group_send)(
        'board',
        {'type': 'board.update', 'payload': payload},
    )
