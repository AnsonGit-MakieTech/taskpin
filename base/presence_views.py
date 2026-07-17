from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .organizations import organization_required
from .presence import get_online_user_ids, refresh_user_online


@organization_required
@require_GET
def presence_online(request):
    return JsonResponse({
        'online_user_ids': get_online_user_ids(request.organization),
    })


@organization_required
@require_POST
def presence_heartbeat(request):
    refresh_user_online(request.organization.pk, request.user.pk)
    return JsonResponse({'ok': True})
