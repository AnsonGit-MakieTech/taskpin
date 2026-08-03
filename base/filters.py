"""List filter helpers for Done and Activity views."""

from datetime import datetime
from urllib.parse import urlencode

from django.db.models import Q
from django.utils import timezone

DONE_PAGE_SIZE = 25
ACTIVITY_PAGE_SIZE = 20

FILTER_KEYS = ('assignee', 'actor', 'from', 'to', 'q')
SCOREBOARD_FILTER_KEYS = ('period', 'from', 'to', 'sort', 'priority')
DTR_FILTER_KEYS = ('from', 'to', 'status')
DTR_TEAM_FILTER_KEYS = ('date', 'member', 'status')
CALENDAR_FILTER_KEYS = (
    'scope', 'assignee', 'priority', 'include_done', 'show_completed_on',
    'view', 'date', 'week_start', 'year', 'month',
)


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


def scoreboard_filter_params(request):
    """Current scoreboard filter values from the query string."""
    return {key: request.GET.get(key, '').strip() for key in SCOREBOARD_FILTER_KEYS}


def scoreboard_filter_query_string(request):
    """Build a query string preserving active scoreboard filters."""
    params = {}
    for key, value in scoreboard_filter_params(request).items():
        if value:
            params[key] = value
    return urlencode(params)


def calendar_filter_params(request):
    """Current calendar filter values from the query string."""
    return {key: request.GET.get(key, '').strip() for key in CALENDAR_FILTER_KEYS}


def calendar_filter_query_string(request, *, year=None, month=None, date=None):
    """Build a query string preserving active calendar filters and month/week anchor."""
    params = {}
    for key in CALENDAR_FILTER_KEYS:
        if key in ('year', 'month', 'date'):
            continue
        value = request.GET.get(key, '').strip()
        if value:
            params[key] = value
    if date is not None:
        params['date'] = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
    elif request.GET.get('date', '').strip():
        params['date'] = request.GET.get('date', '').strip()
    if year is not None:
        params['year'] = year
    elif request.GET.get('year', '').strip():
        params['year'] = request.GET.get('year', '').strip()
    if month is not None:
        params['month'] = month
    elif request.GET.get('month', '').strip():
        params['month'] = request.GET.get('month', '').strip()
    return urlencode(params)


def dtr_filter_params(request):
    return {key: request.GET.get(key, '').strip() for key in DTR_FILTER_KEYS}


def dtr_team_filter_params(request):
    return {key: request.GET.get(key, '').strip() for key in DTR_TEAM_FILTER_KEYS}


def dtr_filter_query_string(request, page=None):
    params = {}
    for key, value in dtr_filter_params(request).items():
        if value:
            params[key] = value
    if page is not None:
        params['page'] = page
    return urlencode(params)


def dtr_team_filter_query_string(request):
    params = {}
    for key, value in dtr_team_filter_params(request).items():
        if value:
            params[key] = value
    return urlencode(params)


def filter_dtr_entries(queryset, request):
    params = dtr_filter_params(request)

    from_date = parse_date(params.get('from'))
    to_date = parse_date(params.get('to'))
    if from_date:
        start = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
        queryset = queryset.filter(clock_in__gte=start)
    if to_date:
        end = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))
        queryset = queryset.filter(clock_in__lte=end)

    status = params.get('status')
    if status:
        queryset = queryset.filter(status=status)

    return queryset


def filter_dtr_team_entries(queryset, request, default_date):
    params = dtr_team_filter_params(request)

    entry_date = parse_date(params.get('date')) or default_date
    start = timezone.make_aware(datetime.combine(entry_date, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(entry_date, datetime.max.time()))
    queryset = queryset.filter(clock_in__gte=start, clock_in__lte=end)

    member = params.get('member')
    if member and member.isdigit():
        queryset = queryset.filter(user_id=int(member))

    status = params.get('status')
    if status:
        queryset = queryset.filter(status=status)

    return queryset, entry_date
