import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BoardConsumer(AsyncWebsocketConsumer):
    """Broadcast channel for team board realtime updates (future use)."""

    GROUP_NAME = 'board'

    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection.established',
            'message': 'Connected to TaskPin board updates.',
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def board_update(self, event):
        """Handler for group_send events of type board.update."""
        await self.send(text_data=json.dumps(event['payload']))
