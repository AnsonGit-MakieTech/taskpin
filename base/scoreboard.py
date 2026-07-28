"""Team scoreboard stats — XP, levels, and member aggregates from Task data."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Count, F, Q
from django.utils import timezone

from .models import Organization, Task
from .organizations import get_org_members, tasks_for_organization

XP_BY_PRIORITY = {
    Task.PRIORITY_NORMAL: 10,
    Task.PRIORITY_IMPORTANT: 25,
    Task.PRIORITY_URGENT: 50,
}

XP_BONUS_ON_TIME = 5
XP_BONUS_EARLY = 10
EARLY_COMPLETION_HOURS = 24

PRIORITY_FILTER_ALL = 'all'
PRIORITY_FILTER_URGENT = 'urgent'
PRIORITY_FILTER_IMPORTANT_PLUS = 'important_plus'
PRIORITY_FILTER_NORMAL = 'normal'

LEVEL_THRESHOLDS = [0, 100, 250, 500]


def _extend_level_thresholds(max_levels: int = 50) -> list[int]:
    thresholds = list(LEVEL_THRESHOLDS)
    while len(thresholds) < max_levels:
        gap = thresholds[-1] - thresholds[-2]
        next_gap = max(int(gap * 1.5), gap + 50)
        thresholds.append(thresholds[-1] + next_gap)
    return thresholds


LEVEL_THRESHOLDS = _extend_level_thresholds()


@dataclass(frozen=True)
class LevelInfo:
    level: int
    xp_for_current_level: int
    xp_for_next_level: int
    progress_pct: float


@dataclass(frozen=True)
class MemberScoreboardStats:
    user: User
    done_count: int
    pending_count: int
    overdue_count: int
    xp: int
    level: int
    level_progress_pct: float
    xp_for_current_level: int
    xp_for_next_level: int
    completion_streak: int
    on_time_rate: Optional[float]


@dataclass(frozen=True)
class ScoreboardDateRange:
    date_from: Optional[date] = None
    date_to: Optional[date] = None


def base_xp_for_priority(priority: str) -> int:
    return XP_BY_PRIORITY.get(priority, XP_BY_PRIORITY[Task.PRIORITY_NORMAL])


def completion_bonus_xp(due_date: Optional[datetime], completed_at: Optional[datetime]) -> int:
    if not due_date or not completed_at:
        return 0
    if completed_at > due_date:
        return 0
    early_cutoff = due_date - timedelta(hours=EARLY_COMPLETION_HOURS)
    if completed_at <= early_cutoff:
        return XP_BONUS_EARLY
    return XP_BONUS_ON_TIME


def xp_for_completed_task(task: Task) -> int:
    return base_xp_for_priority(task.priority) + completion_bonus_xp(task.due_date, task.completed_at)


def level_from_xp(xp: int) -> LevelInfo:
    xp = max(0, xp)
    level = 1
    for index in range(len(LEVEL_THRESHOLDS) - 1):
        if xp >= LEVEL_THRESHOLDS[index + 1]:
            level = index + 2
        else:
            break

    current_threshold = LEVEL_THRESHOLDS[level - 1]
    if level < len(LEVEL_THRESHOLDS):
        next_threshold = LEVEL_THRESHOLDS[level]
    else:
        next_threshold = LEVEL_THRESHOLDS[-1]

    span = next_threshold - current_threshold
    progress = ((xp - current_threshold) / span * 100) if span > 0 else 100.0
    progress = min(100.0, max(0.0, progress))

    return LevelInfo(
        level=level,
        xp_for_current_level=current_threshold,
        xp_for_next_level=next_threshold,
        progress_pct=round(progress, 1),
    )


def priority_filter_q(priority_filter: str) -> Q:
    if priority_filter == PRIORITY_FILTER_URGENT:
        return Q(priority=Task.PRIORITY_URGENT)
    if priority_filter == PRIORITY_FILTER_IMPORTANT_PLUS:
        return Q(priority__in=[Task.PRIORITY_IMPORTANT, Task.PRIORITY_URGENT])
    if priority_filter == PRIORITY_FILTER_NORMAL:
        return Q(priority=Task.PRIORITY_NORMAL)
    return Q()


def _completed_at_range_q(date_range: ScoreboardDateRange) -> Q:
    filters = Q()
    if date_range.date_from:
        filters &= Q(completed_at__date__gte=date_range.date_from)
    if date_range.date_to:
        filters &= Q(completed_at__date__lte=date_range.date_to)
    return filters


def _completion_dates_by_user(
    done_tasks: list[Task],
) -> dict[int, set[date]]:
    by_user: dict[int, set[date]] = defaultdict(set)
    for task in done_tasks:
        if task.assigned_to_id and task.completed_at:
            by_user[task.assigned_to_id].add(timezone.localtime(task.completed_at).date())
    return by_user


def completion_streak_for_user(
    completion_dates: set[date],
    *,
    end_date: date,
) -> int:
    if not completion_dates:
        return 0
    streak = 0
    cursor = end_date
    while cursor in completion_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def on_time_rate_for_tasks(done_tasks: list[Task]) -> Optional[float]:
    with_due = [task for task in done_tasks if task.due_date and task.completed_at]
    if not with_due:
        return None
    on_time = sum(1 for task in with_due if task.completed_at <= task.due_date)
    return round(on_time / len(with_due) * 100, 1)


def get_scoreboard_stats(
    organization: Organization,
    *,
    date_range: Optional[ScoreboardDateRange] = None,
    priority_filter: str = PRIORITY_FILTER_ALL,
    members=None,
) -> list[MemberScoreboardStats]:
    """
    Build per-member scoreboard stats scoped to one organization.

    Done count and XP respect date_range and priority_filter.
    Pending and overdue reflect current workload (assigned, not done).
    """
    date_range = date_range or ScoreboardDateRange()
    members = list(members if members is not None else get_org_members(organization))
    member_ids = {member.pk for member in members}
    now = timezone.now()

    base_qs = tasks_for_organization(organization).filter(assigned_to_id__in=member_ids)

    done_qs = (
        base_qs
        .filter(status=Task.STATUS_DONE)
        .filter(_completed_at_range_q(date_range))
        .filter(priority_filter_q(priority_filter))
        .select_related('assigned_to')
    )
    done_by_user: dict[int, list[Task]] = defaultdict(list)
    for task in done_qs:
        done_by_user[task.assigned_to_id].append(task)

    pending_qs = base_qs.filter(status=Task.STATUS_ASSIGNED)
    pending_by_user: dict[int, int] = defaultdict(int)
    overdue_by_user: dict[int, int] = defaultdict(int)
    for task in pending_qs.only('assigned_to_id', 'due_date'):
        pending_by_user[task.assigned_to_id] += 1
        if task.due_date and task.due_date < now:
            overdue_by_user[task.assigned_to_id] += 1

    streak_end = date_range.date_to or timezone.localdate()
    completion_dates = _completion_dates_by_user(
        [task for tasks in done_by_user.values() for task in tasks],
    )

    results: list[MemberScoreboardStats] = []
    for member in members:
        user_done = done_by_user.get(member.pk, [])
        xp = sum(xp_for_completed_task(task) for task in user_done)
        level_info = level_from_xp(xp)
        results.append(
            MemberScoreboardStats(
                user=member,
                done_count=len(user_done),
                pending_count=pending_by_user.get(member.pk, 0),
                overdue_count=overdue_by_user.get(member.pk, 0),
                xp=xp,
                level=level_info.level,
                level_progress_pct=level_info.progress_pct,
                xp_for_current_level=level_info.xp_for_current_level,
                xp_for_next_level=level_info.xp_for_next_level,
                completion_streak=completion_streak_for_user(
                    completion_dates.get(member.pk, set()),
                    end_date=streak_end,
                ),
                on_time_rate=on_time_rate_for_tasks(user_done),
            ),
        )

    return results


SORT_XP = 'xp'
SORT_DONE = 'done'
SORT_PENDING = 'pending'
SORT_OVERDUE = 'overdue'
SORT_CHOICES = (SORT_XP, SORT_DONE, SORT_PENDING, SORT_OVERDUE)

PERIOD_ALL = 'all'
PERIOD_WEEK = 'week'
PERIOD_MONTH = 'month'
PERIOD_CUSTOM = 'custom'
PERIOD_CHOICES = (PERIOD_ALL, PERIOD_WEEK, PERIOD_MONTH, PERIOD_CUSTOM)


@dataclass(frozen=True)
class ScoreboardFilters:
    period: str
    sort: str
    priority: str
    date_from: Optional[date]
    date_to: Optional[date]
    custom_from: str
    custom_to: str

    def as_template_dict(self) -> dict[str, str]:
        return {
            'period': self.period,
            'sort': self.sort,
            'priority': self.priority,
            'from': self.custom_from,
            'to': self.custom_to,
        }


def resolve_scoreboard_date_range(
    period: str,
    custom_from: Optional[date],
    custom_to: Optional[date],
) -> ScoreboardDateRange:
    today = timezone.localdate()
    if period == PERIOD_WEEK:
        week_start = today - timedelta(days=today.weekday())
        return ScoreboardDateRange(date_from=week_start, date_to=today)
    if period == PERIOD_MONTH:
        return ScoreboardDateRange(date_from=today.replace(day=1), date_to=today)
    if period == PERIOD_CUSTOM:
        return ScoreboardDateRange(date_from=custom_from, date_to=custom_to)
    return ScoreboardDateRange()


def parse_scoreboard_filters(request) -> ScoreboardFilters:
    from .filters import parse_date, scoreboard_filter_params

    params = scoreboard_filter_params(request)
    period = params.get('period') or PERIOD_MONTH
    if period not in PERIOD_CHOICES:
        period = PERIOD_MONTH

    sort = params.get('sort') or SORT_XP
    if sort not in SORT_CHOICES:
        sort = SORT_XP

    priority = params.get('priority') or PRIORITY_FILTER_ALL
    if priority not in {
        PRIORITY_FILTER_ALL,
        PRIORITY_FILTER_URGENT,
        PRIORITY_FILTER_IMPORTANT_PLUS,
        PRIORITY_FILTER_NORMAL,
    }:
        priority = PRIORITY_FILTER_ALL

    custom_from = parse_date(params.get('from'))
    custom_to = parse_date(params.get('to'))
    date_range = resolve_scoreboard_date_range(period, custom_from, custom_to)

    return ScoreboardFilters(
        period=period,
        sort=sort,
        priority=priority,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
        custom_from=params.get('from', ''),
        custom_to=params.get('to', ''),
    )


def sort_scoreboard_stats(
    stats: list[MemberScoreboardStats],
    sort_key: str,
) -> list[MemberScoreboardStats]:
    def sort_tuple(entry: MemberScoreboardStats):
        name = entry.user.first_name.lower() or entry.user.username.lower()
        if sort_key == SORT_DONE:
            return (-entry.done_count, -entry.xp, name)
        if sort_key == SORT_PENDING:
            return (-entry.pending_count, -entry.done_count, name)
        if sort_key == SORT_OVERDUE:
            return (-entry.overdue_count, -entry.pending_count, name)
        return (-entry.xp, -entry.done_count, name)

    return sorted(stats, key=sort_tuple)


def chart_value_for_entry(entry: MemberScoreboardStats, sort_key: str) -> int:
    if sort_key == SORT_DONE:
        return entry.done_count
    if sort_key == SORT_PENDING:
        return entry.pending_count
    if sort_key == SORT_OVERDUE:
        return entry.overdue_count
    return entry.xp


def build_scoreboard_leaderboard(
    organization: Organization,
    filters: ScoreboardFilters,
    *,
    members=None,
) -> tuple[list[MemberScoreboardStats], int]:
    stats = get_scoreboard_stats(
        organization,
        date_range=ScoreboardDateRange(
            date_from=filters.date_from,
            date_to=filters.date_to,
        ),
        priority_filter=filters.priority,
        members=members,
    )
    ranked = sort_scoreboard_stats(stats, filters.sort)
    chart_max = max((chart_value_for_entry(entry, filters.sort) for entry in ranked), default=0)
    return ranked, chart_max


BADGE_FIRST_BLOOD = 'first_blood'
BADGE_FIRE_STREAK = 'fire_streak'
BADGE_URGENT_RESPONDER = 'urgent_responder'
BADGE_TEAM_PLAYER = 'team_player'

FIRE_STREAK_DAYS = 5
URGENT_RESPONDER_COUNT = 10
TEAM_PLAYER_COUNT = 5


@dataclass(frozen=True)
class ScoreboardBadge:
    id: str
    label: str
    icon: str
    title: str


BADGE_CATALOG = {
    BADGE_FIRST_BLOOD: ScoreboardBadge(
        id=BADGE_FIRST_BLOOD,
        label='First Blood',
        icon='⚡',
        title='First completion in this period',
    ),
    BADGE_FIRE_STREAK: ScoreboardBadge(
        id=BADGE_FIRE_STREAK,
        label='Fire Streak',
        icon='🔥',
        title=f'{FIRE_STREAK_DAYS}+ day completion streak',
    ),
    BADGE_URGENT_RESPONDER: ScoreboardBadge(
        id=BADGE_URGENT_RESPONDER,
        label='Urgent Responder',
        icon='🚨',
        title=f'{URGENT_RESPONDER_COUNT}+ urgent tasks completed (all time)',
    ),
    BADGE_TEAM_PLAYER: ScoreboardBadge(
        id=BADGE_TEAM_PLAYER,
        label='Team Player',
        icon='🤝',
        title=f'{TEAM_PLAYER_COUNT}+ tasks completed for teammates (all time)',
    ),
}


@dataclass(frozen=True)
class ScoreboardBadgeContext:
    first_blood_user_id: Optional[int]
    urgent_counts: dict[int, int]
    team_player_counts: dict[int, int]


def _fetch_badge_context(
    organization: Organization,
    date_range: ScoreboardDateRange,
    member_ids: set[int],
) -> ScoreboardBadgeContext:
    done_in_org = tasks_for_organization(organization).filter(
        status=Task.STATUS_DONE,
        assigned_to_id__isnull=False,
    )

    first_blood_user_id = (
        done_in_org
        .filter(_completed_at_range_q(date_range))
        .order_by('completed_at')
        .values_list('assigned_to_id', flat=True)
        .first()
    )

    urgent_counts = dict(
        done_in_org
        .filter(priority=Task.PRIORITY_URGENT, assigned_to_id__in=member_ids)
        .values('assigned_to_id')
        .annotate(total=Count('id'))
        .values_list('assigned_to_id', 'total')
    )

    team_player_counts = dict(
        done_in_org
        .filter(assigned_to_id__in=member_ids)
        .exclude(created_by_id__isnull=True)
        .exclude(created_by_id=F('assigned_to_id'))
        .values('assigned_to_id')
        .annotate(total=Count('id'))
        .values_list('assigned_to_id', 'total')
    )

    return ScoreboardBadgeContext(
        first_blood_user_id=first_blood_user_id,
        urgent_counts=urgent_counts,
        team_player_counts=team_player_counts,
    )


def badges_for_member(
    entry: MemberScoreboardStats,
    badge_context: ScoreboardBadgeContext,
) -> list[ScoreboardBadge]:
    badges: list[ScoreboardBadge] = []
    user_id = entry.user.pk

    if badge_context.first_blood_user_id == user_id and entry.done_count > 0:
        badges.append(BADGE_CATALOG[BADGE_FIRST_BLOOD])

    if entry.completion_streak >= FIRE_STREAK_DAYS:
        badges.append(BADGE_CATALOG[BADGE_FIRE_STREAK])

    if badge_context.urgent_counts.get(user_id, 0) >= URGENT_RESPONDER_COUNT:
        badges.append(BADGE_CATALOG[BADGE_URGENT_RESPONDER])

    if badge_context.team_player_counts.get(user_id, 0) >= TEAM_PLAYER_COUNT:
        badges.append(BADGE_CATALOG[BADGE_TEAM_PLAYER])

    return badges


def build_scoreboard_rows(
    organization: Organization,
    filters: ScoreboardFilters,
    *,
    members=None,
) -> tuple[list[dict], int]:
    ranked, chart_max = build_scoreboard_leaderboard(organization, filters, members=members)
    member_ids = {entry.user.pk for entry in ranked}
    badge_context = _fetch_badge_context(
        organization,
        ScoreboardDateRange(date_from=filters.date_from, date_to=filters.date_to),
        member_ids,
    )

    rows = []
    for index, entry in enumerate(ranked):
        rows.append({
            'rank': index + 1,
            'entry': entry,
            'chart_value': chart_value_for_entry(entry, filters.sort),
            'badges': badges_for_member(entry, badge_context),
        })

    return rows, chart_max or 1


MONTHLY_GOAL_TARGET = 50
MILESTONE_LEVELS = (5, 10, 15, 20, 25, 30)


@dataclass(frozen=True)
class TeamMonthlyGoal:
    current: int
    target: int
    progress_pct: float
    month_label: str
    reached: bool


def get_team_monthly_goal(organization: Organization) -> TeamMonthlyGoal:
    today = timezone.localdate()
    month_start = today.replace(day=1)
    current = (
        tasks_for_organization(organization)
        .filter(status=Task.STATUS_DONE, completed_at__date__gte=month_start)
        .count()
    )
    target = MONTHLY_GOAL_TARGET
    progress = min(100.0, round(current / target * 100, 1)) if target else 100.0
    return TeamMonthlyGoal(
        current=current,
        target=target,
        progress_pct=progress,
        month_label=today.strftime('%B %Y'),
        reached=current >= target,
    )


def member_all_time_xp(organization: Organization, user_id: int) -> int:
    done_tasks = (
        tasks_for_organization(organization)
        .filter(status=Task.STATUS_DONE, assigned_to_id=user_id)
        .only('priority', 'due_date', 'completed_at')
    )
    return sum(xp_for_completed_task(task) for task in done_tasks)


def level_milestone_crossed(old_xp: int, new_xp: int) -> Optional[int]:
    old_level = level_from_xp(old_xp).level
    new_level = level_from_xp(new_xp).level
    crossed = None
    for milestone in MILESTONE_LEVELS:
        if old_level < milestone <= new_level:
            crossed = milestone
    return crossed


def milestone_activity_message(user: User, level: int) -> str:
    profile = getattr(user, 'profile', None)
    if profile:
        name = profile.display_name()
    else:
        name = user.get_full_name() or user.username
    return f'🎉 {name} reached Level {level}!'
