from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from base.models import Task
from base.organizations import add_user_to_organization, create_organization_with_admin
from base.scoreboard import (
    PRIORITY_FILTER_IMPORTANT_PLUS,
    PRIORITY_FILTER_URGENT,
    PERIOD_MONTH,
    PERIOD_WEEK,
    SORT_DONE,
    SORT_XP,
    ScoreboardDateRange,
    ScoreboardFilters,
    build_scoreboard_rows,
    completion_streak_for_user,
    get_scoreboard_stats,
    get_team_monthly_goal,
    level_from_xp,
    level_milestone_crossed,
    parse_scoreboard_filters,
    resolve_scoreboard_date_range,
    sort_scoreboard_stats,
    xp_for_completed_task,
)


class ScoreboardEngineTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.org = create_organization_with_admin('Acme', self.admin)
        self.member = User.objects.create_user(
            username='member',
            password='pass',
            first_name='Mo',
            last_name='Lee',
        )
        add_user_to_organization(self.org, self.member)

    def _done_task(self, **kwargs):
        defaults = {
            'title': 'Task',
            'organization': self.org,
            'status': Task.STATUS_DONE,
            'priority': Task.PRIORITY_NORMAL,
            'assigned_to': self.member,
            'created_by': self.admin,
            'completed_at': timezone.now(),
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    def test_xp_weights_and_on_time_bonus(self):
        now = timezone.now()
        task = Task(
            priority=Task.PRIORITY_URGENT,
            due_date=now + timedelta(days=2),
            completed_at=now,
        )
        self.assertEqual(xp_for_completed_task(task), 60)

    def test_xp_early_bonus(self):
        now = timezone.now()
        task = Task(
            priority=Task.PRIORITY_NORMAL,
            due_date=now + timedelta(days=3),
            completed_at=now,
        )
        self.assertEqual(xp_for_completed_task(task), 20)

    def test_level_thresholds(self):
        self.assertEqual(level_from_xp(0).level, 1)
        self.assertEqual(level_from_xp(99).level, 1)
        self.assertEqual(level_from_xp(100).level, 2)
        self.assertEqual(level_from_xp(249).level, 2)
        self.assertEqual(level_from_xp(250).level, 3)
        self.assertEqual(level_from_xp(500).level, 4)

    def test_level_progress_pct(self):
        info = level_from_xp(150)
        self.assertEqual(info.level, 2)
        self.assertEqual(info.progress_pct, 33.3)

    def test_get_scoreboard_stats_scoped_to_organization(self):
        other_admin = User.objects.create_user(username='other', password='pass')
        other_org = create_organization_with_admin('Other Co', other_admin)
        Task.objects.create(
            title='Foreign',
            organization=other_org,
            status=Task.STATUS_DONE,
            assigned_to=other_admin,
            created_by=other_admin,
            completed_at=timezone.now(),
        )
        self._done_task()
        stats = get_scoreboard_stats(self.org)
        usernames = {entry.user.username for entry in stats}
        self.assertIn('admin', usernames)
        self.assertIn('member', usernames)
        self.assertNotIn('other', usernames)
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.done_count, 1)
        self.assertEqual(member_stats.xp, 10)

    def test_pending_and_overdue_counts(self):
        Task.objects.create(
            title='Pending',
            organization=self.org,
            status=Task.STATUS_ASSIGNED,
            assigned_to=self.member,
            created_by=self.admin,
            due_date=timezone.now() - timedelta(days=1),
        )
        Task.objects.create(
            title='Future',
            organization=self.org,
            status=Task.STATUS_ASSIGNED,
            assigned_to=self.member,
            created_by=self.admin,
            due_date=timezone.now() + timedelta(days=2),
        )
        stats = get_scoreboard_stats(self.org)
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.pending_count, 2)
        self.assertEqual(member_stats.overdue_count, 1)

    def test_date_range_filters_completions(self):
        today = timezone.localdate()
        self._done_task(completed_at=timezone.now())
        self._done_task(
            title='Old',
            completed_at=timezone.now() - timedelta(days=40),
        )
        stats = get_scoreboard_stats(
            self.org,
            date_range=ScoreboardDateRange(
                date_from=today - timedelta(days=7),
                date_to=today,
            ),
        )
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.done_count, 1)

    def test_priority_filter(self):
        self._done_task(priority=Task.PRIORITY_NORMAL)
        self._done_task(title='Urgent', priority=Task.PRIORITY_URGENT)
        stats = get_scoreboard_stats(self.org, priority_filter=PRIORITY_FILTER_URGENT)
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.done_count, 1)
        self.assertEqual(member_stats.xp, 50)

        stats = get_scoreboard_stats(self.org, priority_filter=PRIORITY_FILTER_IMPORTANT_PLUS)
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.done_count, 1)

    def test_completion_streak(self):
        today = timezone.localdate()
        dates = {today, today - timedelta(days=1), today - timedelta(days=2)}
        self.assertEqual(completion_streak_for_user(dates, end_date=today), 3)
        self.assertEqual(completion_streak_for_user(set(), end_date=today), 0)

    def test_on_time_rate(self):
        now = timezone.now()
        self._done_task(due_date=now + timedelta(hours=1), completed_at=now)
        self._done_task(
            title='Late',
            due_date=now - timedelta(hours=1),
            completed_at=now,
        )
        stats = get_scoreboard_stats(self.org)
        member_stats = next(entry for entry in stats if entry.user.username == 'member')
        self.assertEqual(member_stats.on_time_rate, 50.0)


class ScoreboardFilterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.org = create_organization_with_admin('Acme', self.admin)

    def _request(self, query_string=''):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get(f'/scoreboard/{query_string}')
        request.user = self.admin
        return request

    def test_default_filters(self):
        filters = parse_scoreboard_filters(self._request())
        self.assertEqual(filters.period, PERIOD_MONTH)
        self.assertEqual(filters.sort, SORT_XP)
        self.assertEqual(filters.priority, 'all')

    def test_week_period_resolves_dates(self):
        filters = parse_scoreboard_filters(self._request('?period=week'))
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        self.assertEqual(filters.date_from, week_start)
        self.assertEqual(filters.date_to, today)

    def test_sort_by_completions(self):
        member_a = User.objects.create_user(username='alice', password='pass')
        member_b = User.objects.create_user(username='bob', password='pass')
        add_user_to_organization(self.org, member_a)
        add_user_to_organization(self.org, member_b)
        for _ in range(2):
            Task.objects.create(
                title='Done',
                organization=self.org,
                status=Task.STATUS_DONE,
                assigned_to=member_a,
                created_by=self.admin,
                completed_at=timezone.now(),
            )
        Task.objects.create(
            title='Single',
            organization=self.org,
            status=Task.STATUS_DONE,
            assigned_to=member_b,
            created_by=self.admin,
            completed_at=timezone.now(),
        )
        stats = get_scoreboard_stats(self.org, date_range=ScoreboardDateRange())
        ranked = sort_scoreboard_stats(stats, SORT_DONE)
        self.assertEqual(ranked[0].user.username, 'alice')

    def test_resolve_custom_range(self):
        custom_from = timezone.localdate() - timedelta(days=10)
        custom_to = timezone.localdate()
        date_range = resolve_scoreboard_date_range('custom', custom_from, custom_to)
        self.assertEqual(date_range.date_from, custom_from)
        self.assertEqual(date_range.date_to, custom_to)


class ScoreboardBadgeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.org = create_organization_with_admin('Acme', self.admin)
        self.member = User.objects.create_user(username='member', password='pass')
        add_user_to_organization(self.org, self.member)

    def test_first_blood_badge(self):
        now = timezone.now()
        Task.objects.create(
            title='First',
            organization=self.org,
            status=Task.STATUS_DONE,
            assigned_to=self.member,
            created_by=self.admin,
            completed_at=now - timedelta(hours=2),
        )
        Task.objects.create(
            title='Second',
            organization=self.org,
            status=Task.STATUS_DONE,
            assigned_to=self.admin,
            created_by=self.admin,
            completed_at=now,
        )
        filters = ScoreboardFilters(
            period='all', sort='xp', priority='all',
            date_from=None, date_to=None, custom_from='', custom_to='',
        )
        rows, _ = build_scoreboard_rows(self.org, filters)
        member_row = next(row for row in rows if row['entry'].user.username == 'member')
        admin_row = next(row for row in rows if row['entry'].user.username == 'admin')
        member_badges = {badge.id for badge in member_row['badges']}
        admin_badges = {badge.id for badge in admin_row['badges']}
        self.assertIn('first_blood', member_badges)
        self.assertNotIn('first_blood', admin_badges)

    def test_fire_streak_badge(self):
        today = timezone.localdate()
        for offset in range(5):
            Task.objects.create(
                title=f'Day {offset}',
                organization=self.org,
                status=Task.STATUS_DONE,
                assigned_to=self.member,
                created_by=self.admin,
                completed_at=timezone.make_aware(
                    datetime.combine(today - timedelta(days=offset), datetime.min.time())
                ),
            )
        filters = ScoreboardFilters(
            period='all', sort='xp', priority='all',
            date_from=None, date_to=None, custom_from='', custom_to='',
        )
        rows, _ = build_scoreboard_rows(self.org, filters)
        member_row = next(row for row in rows if row['entry'].user.username == 'member')
        badge_ids = {badge.id for badge in member_row['badges']}
        self.assertIn('fire_streak', badge_ids)

    def test_urgent_responder_badge(self):
        for index in range(10):
            Task.objects.create(
                title=f'Urgent {index}',
                organization=self.org,
                status=Task.STATUS_DONE,
                priority=Task.PRIORITY_URGENT,
                assigned_to=self.member,
                created_by=self.admin,
                completed_at=timezone.now(),
            )
        filters = ScoreboardFilters(
            period='all', sort='xp', priority='all',
            date_from=None, date_to=None, custom_from='', custom_to='',
        )
        rows, _ = build_scoreboard_rows(self.org, filters)
        member_row = next(row for row in rows if row['entry'].user.username == 'member')
        badge_ids = {badge.id for badge in member_row['badges']}
        self.assertIn('urgent_responder', badge_ids)

    def test_team_player_badge(self):
        for index in range(5):
            Task.objects.create(
                title=f'Helped {index}',
                organization=self.org,
                status=Task.STATUS_DONE,
                assigned_to=self.member,
                created_by=self.admin,
                completed_at=timezone.now(),
            )
        filters = ScoreboardFilters(
            period='all', sort='xp', priority='all',
            date_from=None, date_to=None, custom_from='', custom_to='',
        )
        rows, _ = build_scoreboard_rows(self.org, filters)
        member_row = next(row for row in rows if row['entry'].user.username == 'member')
        badge_ids = {badge.id for badge in member_row['badges']}
        self.assertIn('team_player', badge_ids)


class ScoreboardGoalsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.org = create_organization_with_admin('Acme', self.admin)
        self.member = User.objects.create_user(username='member', password='pass')
        add_user_to_organization(self.org, self.member)

    def test_monthly_goal_counts_current_month_completions(self):
        Task.objects.create(
            title='Done',
            organization=self.org,
            status=Task.STATUS_DONE,
            assigned_to=self.member,
            created_by=self.admin,
            completed_at=timezone.now(),
        )
        goal = get_team_monthly_goal(self.org)
        self.assertEqual(goal.current, 1)
        self.assertEqual(goal.target, 50)
        self.assertFalse(goal.reached)

    def test_level_milestone_crossed_at_level_five(self):
        level_five_xp = level_from_xp(875).xp_for_current_level
        self.assertEqual(level_five_xp, 875)
        self.assertIsNone(level_milestone_crossed(850, 870))
        self.assertEqual(level_milestone_crossed(850, 875), 5)

    def test_mark_done_logs_level_milestone(self):
        from base.models import ActivityLog
        from django.test import Client

        for index in range(85):
            Task.objects.create(
                title=f'Task {index}',
                organization=self.org,
                status=Task.STATUS_DONE,
                priority=Task.PRIORITY_NORMAL,
                assigned_to=self.member,
                created_by=self.admin,
                completed_at=timezone.now(),
            )
        task = Task.objects.create(
            title='Level up',
            organization=self.org,
            status=Task.STATUS_ASSIGNED,
            priority=Task.PRIORITY_URGENT,
            assigned_to=self.member,
            created_by=self.admin,
        )
        client = Client()
        client.force_login(self.admin)
        response = client.post(f'/task/{task.pk}/done/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ActivityLog.objects.filter(
                organization=self.org,
                actor=self.member,
                action__contains='reached Level 5',
            ).exists()
        )

    def test_scoreboard_fragment_requires_login(self):
        from django.test import Client

        client = Client()
        response = client.get('/scoreboard/fragment/')
        self.assertEqual(response.status_code, 302)

    def test_scoreboard_fragment_returns_live_block(self):
        from django.test import Client

        client = Client()
        client.force_login(self.admin)
        response = client.get('/scoreboard/fragment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'scoreboard-live')
        self.assertContains(response, 'scoreboard-monthly-goal')
