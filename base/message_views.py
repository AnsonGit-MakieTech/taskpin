from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Conversation, Message
from . import messaging
from .organizations import get_org_members, get_user_organization, organization_required
from .permissions import can_message_user

MESSAGES_PAGE_SIZE = 50


def _conversation_or_403(conversation_id, user):
    organization = get_user_organization(user)
    conversation = get_object_or_404(
        Conversation.objects.select_related('user_a', 'user_b', 'user_a__profile', 'user_b__profile'),
        pk=conversation_id,
        organization=organization,
    )
    if not messaging.is_participant(conversation, user):
        return None, HttpResponseForbidden('You cannot access this conversation.')
    return conversation, None


@organization_required
def messages_inbox(request, conversation_id=None):
    messaging.sync_team_participants(request.user)
    inbox_entries = messaging.get_inbox_entries(request.user)
    active_conversation = None
    thread_messages = []
    page_obj = None

    if conversation_id:
        active_conversation, denied = _conversation_or_403(conversation_id, request.user)
        if denied:
            return denied

    if active_conversation:
        messaging.mark_conversation_read(active_conversation, request.user)
        queryset = (
            active_conversation.messages
            .select_related('sender', 'sender__profile')
            .order_by('-created_at')
        )
        paginator = Paginator(queryset, MESSAGES_PAGE_SIZE)
        page_obj = paginator.get_page(request.GET.get('page'))
        thread_messages = list(reversed(page_obj.object_list))

    teammates = (
        get_org_members(request.organization)
        .exclude(pk=request.user.pk)
    )

    return render(request, 'messages/inbox.html', {
        'inbox_entries': inbox_entries,
        'active_conversation': active_conversation,
        'active_title': messaging.conversation_title(active_conversation, request.user) if active_conversation else '',
        'active_avatar': messaging.conversation_avatar_context(active_conversation, request.user) if active_conversation else None,
        'is_team_chat': active_conversation.conversation_type == Conversation.TYPE_TEAM if active_conversation else False,
        'thread_messages': thread_messages,
        'page_obj': page_obj,
        'teammates': teammates,
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })


@organization_required
def message_start_direct(request, user_id):
    other_user = get_object_or_404(
        User,
        pk=user_id,
        is_active=True,
        organization_membership__organization=request.organization,
    )
    if other_user.pk == request.user.pk:
        return redirect('messages_inbox')
    if not can_message_user(request.user, other_user):
        return HttpResponseForbidden('You can only message members of your organization.')
    conversation = messaging.get_or_create_direct_conversation(request.user, other_user)
    return redirect('messages_conversation', conversation_id=conversation.pk)


@organization_required
@require_POST
def message_send(request):
    conversation_id = request.POST.get('conversation_id')
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied

    try:
        body = request.POST.get('body', '')
        message = messaging.send_message(conversation, request.user, body)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
    except PermissionError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=429)

    html = render(request, 'messages/_message_bubble.html', {
        'message': message,
        'show_sender': conversation.conversation_type == Conversation.TYPE_TEAM,
    }).content.decode('utf-8')

    return JsonResponse({
        'ok': True,
        'message_id': message.id,
        'html': html,
        'created_at': message.created_at.isoformat(),
        'preview': message.preview,
    })


@organization_required
@require_POST
def message_mark_read(request):
    conversation_id = request.POST.get('conversation_id')
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied
    messaging.mark_conversation_read(conversation, request.user)
    return JsonResponse({
        'ok': True,
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })


@organization_required
def message_history(request, conversation_id):
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied

    before_id = request.GET.get('before')
    qs = (
        conversation.messages
        .select_related('sender', 'sender__profile')
        .order_by('-created_at')
    )
    if before_id:
        qs = qs.filter(pk__lt=before_id)

    messages = list(reversed(qs[:MESSAGES_PAGE_SIZE]))
    html_parts = []
    for message in messages:
        html_parts.append(render(request, 'messages/_message_bubble.html', {
            'message': message,
            'show_sender': conversation.conversation_type == Conversation.TYPE_TEAM,
        }).content.decode('utf-8'))

    return JsonResponse({
        'ok': True,
        'html': ''.join(html_parts),
        'has_more': qs.count() > MESSAGES_PAGE_SIZE,
        'oldest_id': messages[0].pk if messages else None,
    })


@organization_required
def message_bubble_fragment(request, message_id):
    organization = get_user_organization(request.user)
    message = get_object_or_404(
        Message.objects.select_related('sender', 'sender__profile', 'conversation'),
        pk=message_id,
        conversation__organization=organization,
    )
    conversation = message.conversation
    if not messaging.is_participant(conversation, request.user):
        return HttpResponseForbidden('You cannot access this message.')
    html = render(request, 'messages/_message_bubble.html', {
        'message': message,
        'show_sender': conversation.conversation_type == Conversation.TYPE_TEAM,
    }).content.decode('utf-8')
    return HttpResponse(html)


@organization_required
def unread_count_api(request):
    return JsonResponse({
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })
