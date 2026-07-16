import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class BoardConsumer(AsyncWebsocketConsumer):
    """Broadcast channel for organization-scoped board updates."""

    async def connect(self):
        user = self.scope.get('user')
        if user is None or user.is_anonymous:
            await self.close()
            return

        org_id = await self._get_user_org_id(user)
        if org_id is None:
            await self.close()
            return

        self.org_group = f'board:{org_id}'

        try:
            await self.channel_layer.group_add(self.org_group, self.channel_name)
        except Exception:
            logger.exception('WebSocket failed to join Redis channel group')
            await self.close(code=1011)
            return

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection.established',
            'message': 'Connected to TaskPin board updates.',
            'organization_id': org_id,
        }))

    async def disconnect(self, close_code):
        org_group = getattr(self, 'org_group', None)
        if not org_group:
            return
        try:
            await self.channel_layer.group_discard(org_group, self.channel_name)
        except Exception:
            logger.exception('WebSocket failed to leave Redis channel group')

    async def board_update(self, event):
        """Handler for group_send events of type board.update."""
        await self.send(text_data=json.dumps(event['payload']))

    @database_sync_to_async
    def _get_user_org_id(self, user):
        from .organizations import get_user_organization
        organization = get_user_organization(user)
        return organization.pk if organization else None
