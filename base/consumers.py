import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class BoardConsumer(AsyncWebsocketConsumer):
    """Broadcast channel for team board realtime updates (future use)."""

    GROUP_NAME = 'board'

    async def connect(self):
        # if self.scope['user'].is_anonymous:
        #     await self.close()
        #     return

        try:
            await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        except Exception:
            logger.exception('WebSocket failed to join Redis channel group')
            await self.close(code=1011)
            return

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection.established',
            'message': 'Connected to TaskPin board updates.',
        }))

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)
        except Exception:
            logger.exception('WebSocket failed to leave Redis channel group')

    async def board_update(self, event):
        """Handler for group_send events of type board.update."""
        await self.send(text_data=json.dumps(event['payload']))
