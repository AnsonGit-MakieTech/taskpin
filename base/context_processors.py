from .permissions import is_admin
from . import messaging


def permissions(request):
    if not request.user.is_authenticated:
        return {
            'can_move_tasks': False,
            'is_admin_user': False,
            'unread_message_count': 0,
            'team_notify_message': None,
            'team_notify_conversation_id': None,
        }
    admin = is_admin(request.user)
    team_message, team_conversation = messaging.latest_unread_team_message(request.user)
    return {
        'can_move_tasks': admin,
        'is_admin_user': admin,
        'unread_message_count': messaging.unread_count_for_user(request.user),
        'team_notify_message': team_message,
        'team_notify_conversation_id': team_conversation.pk if team_conversation else None,
    }
