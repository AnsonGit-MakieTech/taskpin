"""Conversation helpers, unread counts, and message sending."""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from .models import Conversation, ConversationParticipant, Message
from .organizations import get_org_members, get_user_organization, users_share_organization
from .realtime import notify_board_update

MESSAGE_RATE_LIMIT = 30
MESSAGE_RATE_WINDOW = 60


def _ordered_users(user_one, user_two):
    if user_one.pk <= user_two.pk:
        return user_one, user_two
    return user_two, user_one


def ensure_participant(conversation, user):
    participant, _ = ConversationParticipant.objects.get_or_create(
        conversation=conversation,
        user=user,
    )
    return participant


def get_team_conversation(organization):
    conversation, _ = Conversation.objects.get_or_create(
        conversation_type=Conversation.TYPE_TEAM,
        organization=organization,
    )
    for user in get_org_members(organization):
        ensure_participant(conversation, user)
    return conversation


def sync_team_participants(user):
    """Add any organization members missing from the team conversation."""
    organization = get_user_organization(user)
    if organization is None:
        return None
    conversation = get_team_conversation(organization)
    member_ids = set(get_org_members(organization).values_list('pk', flat=True))
    existing_ids = set(conversation.participants.values_list('user_id', flat=True))
    for user_id in member_ids - existing_ids:
        ensure_participant(conversation, User.objects.get(pk=user_id))
    return conversation


def get_or_create_direct_conversation(user, other_user):
    if user.pk == other_user.pk:
        raise ValueError('Cannot create a direct chat with yourself.')
    if not users_share_organization(user, other_user):
        raise PermissionError('You can only message members of your organization.')
    organization = get_user_organization(user)
    user_a, user_b = _ordered_users(user, other_user)
    conversation, created = Conversation.objects.get_or_create(
        conversation_type=Conversation.TYPE_DIRECT,
        user_a=user_a,
        user_b=user_b,
        defaults={'organization': organization},
    )
    if conversation.organization_id != organization.pk:
        raise PermissionError('You cannot access this conversation.')
    ensure_participant(conversation, user_a)
    ensure_participant(conversation, user_b)
    return conversation


def user_display_name(user):
    if hasattr(user, 'profile') and user.profile:
        return user.profile.display_name()
    full = user.get_full_name()
    return full if full else user.username


def conversation_title(conversation, viewer):
    if conversation.conversation_type == Conversation.TYPE_TEAM:
        return 'Team'
    other = conversation.user_b if conversation.user_a_id == viewer.pk else conversation.user_a
    if other:
        return user_display_name(other)
    return 'Direct message'


def conversation_avatar_context(conversation, viewer):
    if conversation.conversation_type == Conversation.TYPE_TEAM:
        return {
            'is_team': True,
            'initials': 'TM',
            'color': '#FFB74D',
        }
    other = conversation.user_b if conversation.user_a_id == viewer.pk else conversation.user_a
    profile = getattr(other, 'profile', None)
    return {
        'is_team': False,
        'initials': profile.initials() if profile else other.username[:2].upper(),
        'color': profile.avatar_color() if profile else '#64B5F6',
    }


def other_user_in_direct(conversation, viewer):
    if conversation.conversation_type != Conversation.TYPE_DIRECT:
        return None
    if conversation.user_a_id == viewer.pk:
        return conversation.user_b
    return conversation.user_a


def is_participant(conversation, user):
    organization = get_user_organization(user)
    if organization is None or conversation.organization_id != organization.pk:
        return False
    return conversation.participants.filter(user=user).exists()


def unread_count_for_user(user):
    organization = get_user_organization(user)
    if organization is None:
        return 0
    participants = (
        ConversationParticipant.objects
        .filter(user=user, conversation__organization=organization)
        .select_related('conversation')
    )
    total = 0
    for participant in participants:
        qs = Message.objects.filter(conversation=participant.conversation).exclude(sender=user)
        if participant.last_read_at:
            qs = qs.filter(created_at__gt=participant.last_read_at)
        total += qs.count()
    return total


def unread_count_for_conversation(conversation, user):
    participant = conversation.participants.filter(user=user).first()
    if not participant:
        return 0
    qs = Message.objects.filter(conversation=conversation).exclude(sender=user)
    if participant.last_read_at:
        qs = qs.filter(created_at__gt=participant.last_read_at)
    return qs.count()


def mark_conversation_read(conversation, user):
    participant = ensure_participant(conversation, user)
    participant.last_read_at = timezone.now()
    participant.save(update_fields=['last_read_at'])


def check_message_rate_limit(user):
    key = f'taskpin:msg_rate:{user.pk}'
    count = cache.get(key, 0)
    if count >= MESSAGE_RATE_LIMIT:
        return False
    cache.set(key, count + 1, MESSAGE_RATE_WINDOW)
    return True


def get_inbox_entries(user):
    organization = get_user_organization(user)
    if organization is None:
        return []
    sync_team_participants(user)
    participants = (
        ConversationParticipant.objects
        .filter(user=user, conversation__organization=organization)
        .select_related('conversation', 'conversation__user_a', 'conversation__user_b')
        .prefetch_related('conversation__user_a__profile', 'conversation__user_b__profile')
    )
    entries = []
    for participant in participants:
        conversation = participant.conversation
        last_message = (
            conversation.messages
            .select_related('sender', 'sender__profile')
            .order_by('-created_at')
            .first()
        )
        entries.append({
            'conversation': conversation,
            'participant': participant,
            'title': conversation_title(conversation, user),
            'avatar': conversation_avatar_context(conversation, user),
            'last_message': last_message,
            'unread_count': unread_count_for_conversation(conversation, user),
            'is_team': conversation.conversation_type == Conversation.TYPE_TEAM,
        })

    def sort_key(entry):
        if entry['is_team']:
            return (0, entry['conversation'].updated_at)
        if entry['last_message']:
            return (1, entry['last_message'].created_at)
        return (2, entry['conversation'].created_at)

    entries.sort(key=sort_key, reverse=True)
    team_entries = [e for e in entries if e['is_team']]
    direct_entries = [e for e in entries if not e['is_team']]
    direct_entries.sort(
        key=lambda e: e['last_message'].created_at if e['last_message'] else e['conversation'].created_at,
        reverse=True,
    )
    return team_entries + direct_entries


def latest_unread_team_message(user):
    """Latest team chat message the user has not read (excludes own messages)."""
    organization = get_user_organization(user)
    if organization is None:
        return None, None
    sync_team_participants(user)
    conversation = Conversation.objects.filter(
        conversation_type=Conversation.TYPE_TEAM,
        organization=organization,
    ).first()
    if not conversation:
        return None, None
    participant = conversation.participants.filter(user=user).first()
    if not participant:
        return None, conversation
    qs = (
        Message.objects
        .filter(conversation=conversation)
        .exclude(sender=user)
        .select_related('sender', 'sender__profile')
        .order_by('-created_at')
    )
    if participant.last_read_at:
        qs = qs.filter(created_at__gt=participant.last_read_at)
    message = qs.first()
    return message, conversation


def send_message(conversation, sender, body):
    body = body.strip()
    if not body:
        raise ValueError('Message cannot be empty.')
    if len(body) > Message.MAX_BODY_LENGTH:
        raise ValueError(f'Message cannot exceed {Message.MAX_BODY_LENGTH} characters.')
    if not is_participant(conversation, sender):
        raise PermissionError('You are not a participant in this conversation.')
    if not check_message_rate_limit(sender):
        raise PermissionError('You are sending messages too quickly. Please wait a moment.')

    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        body=body,
    )
    Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
    mark_conversation_read(conversation, sender)

    other_user_id = None
    if conversation.conversation_type == Conversation.TYPE_DIRECT:
        other = other_user_in_direct(conversation, sender)
        other_user_id = other.pk if other else None

    notify_board_update('message.new', None, sender.id, {
        'conversation_id': conversation.id,
        'message_id': message.id,
        'conversation_type': conversation.conversation_type,
        'sender_name': user_display_name(sender),
        'preview': message.preview,
        'recipient_user_id': other_user_id,
    }, organization_id=conversation.organization_id)
    return message
