"""List filter helpers for Done and Activity views."""

from datetime import datetime
from urllib.parse import urlencode

from django.db.models import Q
from django.utils import timezone

DONE_PAGE_SIZE = 25
ACTIVITY_PAGE_SIZE = 20

FILTER_KEYS = ('assignee', 'actor', 'from', 'to', 'q')


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None


def filter_params(request):
    """Current filter values from the query string."""
    return {key: request.GET.get(key, '').strip() for key in FILTER_KEYS}


def filter_query_string(request, page=None):
    """Build a query string preserving active filters."""
    params = {}
    for key, value in filter_params(request).items():
        if value:
            params[key] = value
    if page is not None:
        params['page'] = page
    return urlencode(params)


def filter_done_tasks(queryset, request):
    params = filter_params(request)

    assignee = params.get('assignee')
    if assignee and assignee.isdigit():
        queryset = queryset.filter(assigned_to_id=int(assignee))

    from_date = parse_date(params.get('from'))
    to_date = parse_date(params.get('to'))
    if from_date:
        queryset = queryset.filter(completed_at__date__gte=from_date)
    if to_date:
        queryset = queryset.filter(completed_at__date__lte=to_date)

    search = params.get('q')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search),
        )

    return queryset


def filter_activity_logs(queryset, request):
    params = filter_params(request)

    actor = params.get('actor')
    if actor and actor.isdigit():
        queryset = queryset.filter(actor_id=int(actor))

    from_date = parse_date(params.get('from'))
    to_date = parse_date(params.get('to'))
    if from_date:
        start = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
        queryset = queryset.filter(timestamp__gte=start)
    if to_date:
        end = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))
        queryset = queryset.filter(timestamp__lte=end)

    return queryset
