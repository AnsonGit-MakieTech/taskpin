# TaskPin Build Checklist

## Task 1 — Project Setup & Configuration

- [x] Register `base` app in `INSTALLED_APPS` inside `taskpin/settings.py`
- [x] Install `psycopg2-binary` and switch `DATABASES` from SQLite to PostgreSQL
- [x] Set `TIME_ZONE = 'Asia/Manila'` in `taskpin/settings.py`
- [x] Configure `TEMPLATES['DIRS']` to point to a top-level `templates/` folder
- [x] Add `STATIC_ROOT` and `MEDIA_ROOT` settings
- [x] Create `requirements.txt` listing all installed packages and their versions

---

## Task 2 — Data Models

- [x] Define `UserProfile` model in `base/models.py` — one-to-one with Django `User`, stores initials and role
- [x] Define `Task` model — fields: title, description, status (`unassigned` / `assigned` / `done`), priority (`normal` / `important` / `urgent`), due_date, created_by (FK), assigned_to (FK nullable), completed_at
- [x] Define `ActivityLog` model — fields: actor (FK User), action (text), task (FK Task), timestamp
- [x] Register all three models in `base/admin.py`
- [x] Run `python manage.py makemigrations` and `python manage.py migrate`

---

## Task 3 — Authentication (Login / Logout)

- [x] Wire Django's built-in `auth` login and logout views in `taskpin/urls.py`
- [x] Create top-level `templates/` folder and a `templates/base.html` layout template
- [x] Add sidebar navigation in `base.html` with links: Team Board, My Board, Done, Team, Settings
- [x] Apply theme styles in `base.html`: Inter font, `#F8F6F0` background, `#2E2E2E` text, warm accent colors
- [x] Create `templates/registration/login.html` styled to match the theme
- [x] Add `@login_required` decorator to all app views

---

## Task 4 — Team Board Page (Main Dashboard)

- [x] Create a `team_board` view in `base/views.py` that fetches all users and their active (non-done) tasks
- [x] Register the URL in `base/urls.py` and include `base.urls` in `taskpin/urls.py`
- [x] Create `templates/board/team_board.html` — horizontal column layout, one column per team member
- [x] Add user column header: name, initials avatar, active task count
- [x] Create sticky note card partial `templates/board/_task_card.html` with:
  - Background color by priority: yellow `#FFE082` (normal), orange `#FFB74D` (important), red `#EF5350` (urgent)
  - Soft shadow, rounded corners, task title, priority label, optional due date, Done button
- [x] Show a friendly empty state message in columns that have no tasks

---

## Task 5 — Create Task & Quick Assignment

- [x] Create `TaskCreateView` in `base/views.py` with a minimal form: title, priority, due date, assign_to
- [x] Create `templates/board/task_form.html` for the create form, styled as a simple modal or page
- [x] Add a "Create Note" button to the Team Board page that opens the create form
- [x] On form save: set `status = assigned` if `assigned_to` is filled, otherwise `status = unassigned`
- [x] Write an entry to `ActivityLog` on every task creation
- [x] Redirect back to the Team Board after successful task creation

---

## Task 6 — My Board (Personal Task View)

- [x] Create a `my_board` view in `base/views.py` — shows only tasks assigned to the logged-in user with `status = assigned`
- [x] Register URL `my/` → `my_board` in `base/urls.py`
- [x] Create `templates/board/my_board.html` — clean single-column layout with the same sticky note cards
- [x] Add active state highlight to the "My Board" sidebar link
- [x] Show task count in the page header
- [x] Show a friendly empty state when the user has no active tasks

---

## Task 7 — Done / Completed Tasks Page

- [x] Create a `done_tasks` view in `base/views.py` — fetches all tasks with `status = done`, ordered by `completed_at` descending
- [x] Register URL `done/` → `done_tasks` in `base/urls.py`
- [x] Create `templates/board/done_tasks.html` — list view with task title, who created it, who completed it, and the completion date
- [x] Style completed task rows with the `--green` color (`#81C784`) and a strikethrough on the title
- [x] Add active state highlight to the "Done" sidebar link
- [x] Show a friendly empty state when no tasks have been completed yet

---

## Task 8 — Reassign / Move Task

- [x] Create a `task_reassign` view in `base/views.py` — accepts POST with a new `assigned_to` user ID
- [x] Register URL `task/<int:task_id>/reassign/` in `base/urls.py`
- [x] Add a small "Move" dropdown or button to each task card in `_task_card.html`
- [x] On save: update `assigned_to` and `status`, write to `ActivityLog`
- [x] Redirect back to Team Board after reassignment
- [x] Show an inline reassign form only to the task creator or admin role

---

## Task 9 — Edit & Delete Task

- [x] Create a `task_edit` view in `base/views.py` — pre-fills `TaskCreateForm` with existing task data
- [x] Create a `task_delete` view — POST-only, soft-deletes or hard-deletes the task
- [x] Register URLs: `task/<int:task_id>/edit/` and `task/<int:task_id>/delete/`
- [x] Add Edit and Delete options to the small menu on each task card in `_task_card.html`
- [x] Reuse `templates/board/task_form.html` for the edit page (pass `task` to context for the heading)
- [x] Write an entry to `ActivityLog` on edit and delete
- [x] Redirect back to Team Board after edit or delete

---

## Task 10 — Team Management (Admin)

- [x] Create a `team_list` view in `base/views.py` — lists all active users with their role and task count
- [x] Create an `invite_member` view — creates a new Django `User` and their `UserProfile`
- [x] Register URLs: `team/` → `team_list`, `team/invite/` → `invite_member`
- [x] Create `templates/team/team_list.html` — card grid of team members with avatar, name, role, and active task count
- [x] Create `templates/team/invite_form.html` — simple form: username, first name, last name, role, password
- [x] Restrict `invite_member` to admin-role users only
- [x] Add active state highlight to the "Team" sidebar link

---

## Task 11 — Bug Fixes & Revisions

- [x] Replace browser `confirm()` on Delete with a friendly in-app confirmation modal
- [x] Restrict task move/reassign (menu + drag-and-drop) to admin-role users only
- [x] Add a friendly confirmation modal before marking a task as Done
- [x] Add a registration page at `/accounts/register/` with themed UI and login link

---

## Task 12 — Docker & Realtime (WebSocket)

- [x] Create a `Dockerfile` for the Django app (Python, dependencies, Gunicorn/Daphne entrypoint)
- [x] Create `docker-compose.yml` with services: `web`, `db` (PostgreSQL), and `redis`
- [x] Add `.env.example` with required environment variables (DB, Redis, Django secret key)
- [x] Document setup steps in comments or README — **do not run Docker or migrations** (user will run and migrate manually)
- [x] Install and configure Django Channels for ASGI/WebSocket support
- [x] Add `channels` and `channels-redis` to `requirements.txt`
- [x] Configure `ASGI_APPLICATION`, channel layers (Redis), and routing in `taskpin/asgi.py`
- [x] Create a base WebSocket consumer (e.g. board updates) wired for future realtime task actions
- [x] Add a simple client-side WebSocket hook in the frontend (connect only; no full realtime UI yet)

---

## Task 13 — Static Assets & Realtime Boards

- [x] Move shared CSS from templates into `static/css/base.css`
- [x] Move page CSS into `static/css/` (`board-team.css`, `board-my.css`, `board-done.css`, `forms.css`, `auth.css`, `team.css`)
- [x] Move shared JS into `static/js/app.js` and `static/js/realtime.js`
- [x] Update all templates to use `{% static %}` instead of inline styles/scripts
- [x] Broadcast task events over WebSocket from views (create, done, move, edit, delete)
- [x] Auto-refresh Team Board, My Board, and Done pages when another user changes tasks
- [x] Show a brief toast before refresh so users know the board is updating

---

## Task 14 — Realtime Reliability

- [x] Use in-memory channel layer for local `runserver`; use Redis only inside Docker (or when `REDIS_HOST` is localhost)
- [x] Default `ALLOWED_HOSTS` in `DEBUG` so WebSocket origin validation works locally
- [x] Connect WebSocket only on board pages (Team, My, Done) — not on forms or team admin pages
- [x] Add auto-reconnect with backoff when the WebSocket drops unexpectedly
- [x] Refresh all open board tabs when any user changes tasks (including same user in another tab)
- [x] Log broadcast failures in `notify_board_update()` instead of failing silently
- [x] Document local vs Docker env vars in `.env.example` (`REDIS_HOST`, `POSTGRES_HOST`)

---

## Task 15 — Activity Log & History

- [x] Create an `activity_log` view in `base/views.py` — lists recent `ActivityLog` entries, newest first
- [x] Register URL `activity/` → `activity_log` in `base/urls.py`
- [x] Create `templates/activity/activity_log.html` — simple timeline: actor, action text, task link, timestamp
- [x] Paginate or limit to the most recent entries (e.g. last 50)
- [x] Add an "Activity" link to the sidebar (or a section on Team Board)
- [x] Style the page to match the theme (muted timestamps, friendly empty state)

---

## Task 16 — Settings & User Profile

- [x] Create a `settings` view in `base/views.py` — profile form for name and optional avatar initials
- [x] Add a password-change form using Django's built-in password change views
- [x] Register URLs: `settings/` → settings page, password change under `settings/password/`
- [x] Create `templates/settings/settings.html` and `static/css/settings.css`
- [x] Wire the sidebar **Settings** link to the new page (replace the `#` placeholder)
- [x] Self-registration assigns `admin` role — first user is creating their own team
- [x] Show current role (read-only) on the settings page

---

## Task 17 — Mobile-Responsive Layout

- [x] Add responsive breakpoints in `static/css/base.css` and board CSS files
- [x] Collapse sidebar to a compact or slide-out menu on small screens
- [x] On mobile Team Board: show one member column at a time (tabs or horizontal snap scroll)
- [x] Ensure sticky notes and action buttons remain tappable (min touch target size)
- [x] Keep drag-and-drop on desktop; use existing Move dropdown as the primary mobile reassignment path
- [x] Test My Board, Done, and login pages at phone-width viewports

---

## Task 18 — Revisions, Features & Bug Fixes

### Revisions & additions
- [x] Paginate the Activity page so users can browse past events (20 per page)
- [x] Expand long task descriptions on cards with **Show more / Show less**
- [x] Change deadline to **date & time** (`DateTimeField`) with datetime picker on create/edit
- [x] Color-code deadline badges: due within 24h, due today, overdue
- [x] Add a **Legend** on Team Board for priority note colors and deadline badge colors

### Bug fixes
- [x] Restrict **Done**, **Edit**, and **Delete** to admin, task creator, or assignee only (server + UI)
- [x] Hide task action menu when the user has no permitted actions

---

## Task 19 — Done Remarks & Delete Permissions

### Revisions & additions
- [x] Optional **remarks** field when marking a task done (modal textarea, saved on task)
- [x] Show completion remarks on the **Done** page
- [x] Include remarks preview in the **Activity** log when provided

### Permission revision
- [x] **Delete** restricted to admin and task owner (creator) only — assignees cannot delete
- [x] Assignees may still **Edit** and mark **Done**; enforced in views and card menu UI

---

## Task 20 — Team Board Member Grid & Task Panel

### Layout revision (scales to ~100 members)
- [x] Replace wide task columns with a compact **member grid** — tiles show name, avatar, and task count only
- [x] Add **member search** to filter the grid on large teams
- [x] Click a member or **Unassigned** tile to open an integrated **task panel** on the right (split layout, not a modal)
- [x] Task panel lists all notes for that member/unassigned bucket; member grid stays visible for drag-and-drop

### Drag-and-drop revision
- [x] Drag tasks from the open panel and drop onto any member/unassigned tile to reassign
- [x] Highlight drop targets while dragging (admin only, desktop)
- [x] Keep **Move** dropdown on mobile when drag-and-drop is disabled

---

## Task 21 — Assignment Notifications

- [x] When a task is assigned to a member (drag-and-drop, Move menu, or create with assignee), notify the assignee in real time via WebSocket
- [x] Play `static/assets/notification.mp3` in the assignee's browser when they receive a new assignment
- [x] Update the assignee's browser tab title to indicate a new task was assigned to them
- [x] Connect realtime notifications on all authenticated pages (not only board pages)
- [x] Skip notification when the assignee performed the action themselves

---

## Task 22 — Live Board Sync & Due Date Reminders

### Realtime without full page reload
- [x] Add task card and done-row HTML fragment endpoints for incremental DOM updates
- [x] Enrich WebSocket payloads with `previous_assigned_to_id`, `status`, and `priority`
- [x] `board-sync.js` updates Team Board, My Board, and Done pages in place (no reload)
- [x] Team board sync integrates with member grid counts and open task panel
- [x] Brief “Board updated” toast when another user changes tasks

### Due date reminders
- [x] API endpoint for current user’s overdue / due today / due within 24h tasks
- [x] In-app toast alerts when a deadline threshold is reached
- [x] Browser notifications when permission is granted (after first click)
- [x] Persistent banner on My Board showing the most urgent deadline
- [x] Remind once per task per urgency level per browser session

---

## Task 23 — Team Messaging (Messenger-style)

A built-in messaging system so teammates can chat without leaving TaskPin — similar to Messenger, but kept simple and friendly to match the sticky-note board theme. **All members and admins** can send messages, not just admins.

### Data model
- [x] Add `Conversation` model — types: `team` (one shared team room) and `direct` (1-on-1 between two users); unique pair for direct chats
- [x] Add `Message` model — fields: `conversation` (FK), `sender` (FK User), `body` (plain text, max ~2000 chars), `created_at`, `read_at` (nullable; for DMs)
- [x] Add `ConversationParticipant` or track `last_read_at` per user per conversation for unread counts
- [x] Auto-create the **Team** conversation on first use (every active user is a participant)
- [x] Get or create a **direct** conversation when a user opens a chat with a teammate
- [x] Register models in `base/admin.py`

### Messenger UI — inbox & threads
- [x] Add **Messages** link in sidebar with unread badge when the user has unread messages
- [x] **Inbox page** (`/messages/`) — two-pane layout on desktop: conversation list (left) + active thread (right)
- [x] Conversation list shows **Team** at top, then direct chats sorted by most recent message
- [x] Each row shows avatar/initials, name, last message preview, timestamp, and unread dot
- [x] **New message** button — pick a teammate to start or open a direct chat
- [x] **Thread view** — chat bubbles (mine vs theirs), sender name in team chat, timestamps grouped by day
- [x] Sticky compose bar at bottom: textarea + Send button; Enter to send, Shift+Enter for new line
- [x] Mobile: inbox list first, tap conversation to open full-screen thread with back button

### Who can message whom
- [x] Any logged-in **member or admin** can send messages in **Team** chat
- [x] Any logged-in **member or admin** can start a **direct** chat with any other active teammate
- [x] Users cannot message themselves; inactive users hidden from picker

### Realtime delivery
- [x] Broadcast `message.new` over existing WebSocket (`conversation_id`, `message_id`, `sender_id`, preview text)
- [x] Client appends new messages to open thread instantly without reload (`messages.js`)
- [x] Update inbox preview and unread counts in realtime
- [x] Optional: reuse `notification.mp3` + tab title alert for new DMs (skip when user is sender or thread is open)
- [x] Mark conversation as read when user opens the thread (update `last_read_at`)

### Notifications & badges
- [x] Sidebar **Messages** link shows total unread count
- [x] Browser notification for new DM when permission granted and thread is not open
- [x] In-app toast when a new message arrives on another page (brief: “New message from …”)

### Optional team announcement banner
- [x] Pin the latest **Team** chat message (or admin-only “announcement”) as a slim banner on all pages — dismissible per session
- [x] “View in Messages” link on banner opens Team chat

### Activity & safety
- [x] Log significant events to `ActivityLog` only if needed (e.g. first message of day optional — avoid noise)
- [x] Plain text only — no HTML; escape on render
- [x] Validate message length; basic rate limit per user (e.g. max 30 messages/minute)
- [x] Server-side permission checks: user must be participant of conversation to read/post

### Empty states & polish
- [x] Inbox empty state: “No conversations yet — say hello to a teammate”
- [x] Team chat empty state: “Start the conversation for your team”
- [x] Style messages page to match theme (warm background, rounded bubbles, friendly typography)
- [x] Paginate or lazy-load older messages when scrolling up in a thread

---

## Task 24 — Online presence & read receipts

### Online presence
- [x] Track online users per organization via cache (WebSocket connect/disconnect + heartbeat)
- [x] Broadcast `presence.update` over existing WebSocket with current online user IDs
- [x] Green presence dot on **Team Board** member tiles
- [x] Green presence dot on **Team** list member cards
- [x] API: `GET /api/presence/online/`, `POST /api/presence/heartbeat/`

### Read receipts (Messenger-style)
- [x] Use `ConversationParticipant.last_read_at` to compute read status
- [x] Direct chats: show **Seen** on your messages when the other person has read them
- [x] Team chat: show **Seen**, **Seen by [name]**, or **Seen by N** when teammates have read
- [x] Broadcast `conversation.read` when a user catches up on unread messages
- [x] Realtime receipt updates in open thread via `messages.js`

---

## Task 25 — Attachments, filters, pagination, profile photo

### Done & Activity
- [x] Paginate Done tasks (e.g. 25/page)
- [x] Done filters: date range, assignee, title search
- [x] Activity filters: date range, actor
- [x] Preserve filters across pagination

### Task attachments
- [x] TaskAttachment model + migration
- [x] Upload on task create/edit (multi-file)
- [x] Show/download attachments on task cards
- [x] Show on Done rows

### Profile photo
- [x] avatar_image on UserProfile
- [x] Upload/remove in Settings
- [x] Show photo across app with initials fallback



---

## Task 26 — Team Scoreboard (gamified rankings)

### Scoring & stats engine
- [x] Create `base/scoreboard.py` — aggregate member stats from existing `Task` data (no new model for MVP)
- [x] Define XP weights: normal = 10, important = 25, urgent = 50
- [x] Optional bonus XP: on-time completion (+5), early completion (+10)
- [x] Level formula from total XP (thresholds: 0 → 100 → 250 → 500 → …)
- [x] Per-member stats: `done_count`, `pending_count`, `overdue_count`, `xp`, `level`, `level_progress_pct`
- [x] Optional: completion streak (consecutive days with ≥1 done task in filter range)
- [x] Optional: on-time rate (% completed before `due_date`)
- [x] Scope all queries to current organization via `request.organization`

### Filters
- [x] Time range: this week / this month / all time / custom date range
- [x] Sort metric: XP (default) / completions / pending load / overdue count
- [x] Priority filter: all / urgent only / important+ / normal only (for completion stats)
- [x] Preserve filter query params across page reloads (reuse `base/filters.py` pattern from Done/Activity)

### View & URL
- [x] Create `scoreboard` view in `base/views.py` with `@organization_required`
- [x] Register URL `scoreboard/` → `scoreboard` in `base/urls.py`
- [x] Pass ranked member list + chart dataset + filter state to template
- [x] Highlight logged-in user's row (“You” badge)

### Page template & UI (game-ish, TaskPin theme)
- [x] Create `templates/scoreboard/scoreboard.html`
- [x] Create `static/css/scoreboard.css` — warm cards, XP bars, level badges (cozy RPG, not dark esports)
- [x] Page header: title (e.g. **Team Scoreboard** or **Quest Log**) + filter bar
- [x] **Podium** section for top 3 (🥇🥈🥉) with avatar, name, level, XP
- [x] **Bar chart**: completions (or XP) per member for selected period — CSS bars or Chart.js
- [x] **Full leaderboard table/list**: rank, avatar, name, level + progress bar, done / pending / overdue counts
- [x] Friendly empty state when no completed tasks in selected period
- [x] Mobile-responsive layout (stack podium + chart on small screens)

### Navigation & polish
- [x] Add **Scoreboard** link to sidebar in `templates/base.html` (icon + active state)
- [x] Reuse `{% user_avatar %}` for all member avatars
- [x] Tooltips or hints explaining XP / level (avoid confusing new users)
- [x] Do not shame low ranks — neutral styling for pending/overdue (workload, not “loser”)

### MVP launch criteria
- [x] Leaderboard sorts correctly by XP with time filter
- [x] Chart reflects same filtered data as leaderboard
- [x] Only org members appear; admins and members see the same board
- [x] Page loads in reasonable time for teams up to ~20 members (single aggregated query or annotate)

### V2 — Badges & streaks (optional follow-up)
- [x] Badge definitions: First Blood, Fire Streak, Urgent Responder, Team Player (computed, no DB table)
- [x] Show badge icons on leaderboard rows
- [x] “My stats” summary card at top for logged-in user

### V2 — Realtime & team goals (optional follow-up)
- [x] Bump scoreboard stats on task completion via existing WebSocket (`task.updated` / done event)
- [x] Team monthly goal banner (e.g. “42 / 50 tasks cleared this month”)
- [x] Optional: log milestone to `ActivityLog` (e.g. someone hits Level 5 — keep low noise)

### Testing & docs
- [x] Unit tests for XP calculation, level thresholds, and date-range filtering
- [x] Mark Task 26 complete in this checklist when MVP ships

---

## Task 27 — Calendar (due-date view)

### Data & query layer
- [x] Create `base/calendar.py` — month/week range helpers and task grouping by due date (no new model for MVP)
- [x] Query tasks scoped to current organization via `tasks_for_organization()`
- [x] Primary date field: `Task.due_date` (datetime, local timezone for day boundaries)
- [x] Optional toggle: show completed tasks on `completed_at` date (off by default)
- [x] Exclude or separately list tasks with no `due_date` (“Unscheduled” bucket)
- [x] Reuse existing priority + `deadline_urgency` (`overdue`, `due_today`, `due_soon`) for styling

### Filters
- [x] Scope: **My tasks** / **Team** (all org tasks with a due date)
- [x] Assignee filter (team view)
- [x] Priority filter: all / urgent / important / normal
- [x] Status filter: active only (default) / include done
- [x] Preserve filter + month/year in query params across navigation

### View & URL
- [x] Create `calendar` view in `base/views.py` with `@organization_required`
- [x] Register URL `calendar/` → `calendar` in `base/urls.py`
- [x] Support `?year=` and `?month=` for month navigation (default: current month)
- [x] Pass grouped tasks, summary counts, and filter state to template

### Page template & UI (TaskPin theme)
- [x] Create `templates/calendar/calendar.html`
- [x] Create `static/css/calendar.css` — warm grid, sticky-note chips on day cells
- [x] Page header: **Calendar** + month/year title + prev/next month controls
- [x] **Month grid** (default view): 7-column week layout, today highlighted
- [x] Task chips on each day: title (truncated), priority color, assignee hint
- [x] Overdue / due-today styling (reuse board priority colors — friendly, not alarming)
- [x] Done tasks muted (strikethrough or reduced opacity) when “include done” is on
- [x] Summary strip: “Due today · Overdue · This week” counts
- [x] Click task chip → link to task edit or quick detail popover
- [x] Friendly empty state when no tasks fall in the visible range
- [x] Mobile-responsive: readable day cells; agenda-style fallback on small screens

### Navigation & polish
- [x] Add **Calendar** link to sidebar in `templates/base.html` (icon + active state)
- [x] “Create note on this day” — link to task create with `due_date` pre-filled (query param)
- [x] Show assignee avatar or initials on chips when space allows

### MVP launch criteria
- [x] Month view shows all org tasks with due dates in selected month
- [x] “My tasks” filter shows only current user’s assigned tasks
- [x] Today and overdue are visually distinct
- [x] Filters persist when changing months
- [x] Page loads efficiently for typical team size (~20 members, ~100 dated tasks/month)

### V1.5 — Week view & agenda (optional follow-up)
- [x] Week view toggle (Mon–Sun or Sun–Sat, match locale)
- [x] Agenda list: “Next 7 days” below or beside the grid
- [x] Unscheduled tasks sidebar: notes without a due date
- [x] Click empty day cell → create task with that date pre-filled

### V2 — Interactions & integrations (optional follow-up)
- [ ] Drag task chip to another day → update `due_date` (respect `can_manage_task` / admin rules)
- [ ] Realtime calendar refresh on task create/edit/done via existing WebSocket
- [ ] Optional iCal feed export (read-only, org or personal)
- [ ] Workload hint: busier days show subtle density indicator

### Testing & docs
- [x] Unit tests for month range, task grouping, and filter logic
- [x] Mark Task 27 complete in this checklist when MVP ships

---

## Task 28 — Daily Time Record (DTR)

A simple clock-in / clock-out attendance system for team members — inspired by FastDTR, but kept lightweight and friendly to match TaskPin. Separate from online presence (`presence.py`): presence means “on the app”; DTR means “officially at work.”

### Data model
- [x] Add `TimeEntry` model — fields: `organization` (FK), `user` (FK), `clock_in`, `clock_out` (nullable), `break_minutes` (default 0), `status` (`open` / `pending` / `approved` / `rejected`), `notes` (employee), `admin_notes`, `approved_by` (FK nullable), `approved_at`, `created_at`
- [x] Enforce one open entry per user per organization (unique constraint or view-level check)
- [x] Register `TimeEntry` in `base/admin.py`
- [x] Run `makemigrations` and `migrate`

### Query layer
- [x] Create `base/dtr.py` — org-scoped queries (mirror `scoreboard.py` / `calendar.py` pattern)
- [x] `entries_for_organization()` — filter by date range, user, status
- [x] `get_open_entry(user, org)` — current clocked-in session
- [x] `weekly_hours(user, org, week_start)` — Mon–Sun totals using `Asia/Manila` day boundaries
- [x] `daily_summary(org, date)` — who is in, who is out, pending counts

### Clock actions (views & URLs)
- [x] `dtr/` → **My DTR** page with clock widget and today’s status
- [x] `POST dtr/clock-in/` → start shift (reject if already open)
- [x] `POST dtr/clock-out/` → end shift; optional notes; set status to `pending` (or `approved` if auto-approve is enabled)
- [x] `GET api/dtr/status/` → JSON: open entry, elapsed time, today hours, week total (for widget / header badge)
- [x] All views use `@organization_required`

### My Timesheet (personal history)
- [x] `dtr/timesheet/` → list of the logged-in user’s entries, newest first
- [x] Filters: date range, status — reuse `base/filters.py` pattern from Done/Activity
- [x] Paginate entries (e.g. 25/page); preserve filters across pages
- [x] Show date, clock-in, clock-out, hours, status badge, notes

### Team DTR (admin review)
- [x] `dtr/team/` → admin-only day/week view of all org members’ entries
- [x] Day picker + member rows: avatar, name, in/out times, hours, status
- [x] `POST dtr/<id>/approve/` and `POST dtr/<id>/reject/` (reject requires admin note)
- [x] Log approve/reject to `ActivityLog`
- [x] Restrict team view and approve/reject to admin role

### Page templates & UI (TaskPin theme)
- [x] Create `templates/dtr/my_dtr.html` — main clock widget (Clock In / Clock Out), elapsed timer, weekly hours summary
- [x] Create `templates/dtr/timesheet.html` — personal history table with filters
- [x] Create `templates/dtr/team_dtr.html` — admin review table with approve/reject actions
- [x] Partials: `_clock_widget.html`, `_timesheet_row.html`, `_team_row.html`
- [x] Create `static/css/dtr.css` — warm background, green when clocked in, friendly status badges
- [x] Create `static/js/dtr.js` — live elapsed timer, clock actions via fetch, optional status poll

### Navigation & polish
- [x] Add **Time Record** link to sidebar in `templates/base.html` (clock icon + active state)
- [x] Friendly empty states: “Not clocked in yet”, “No timesheet entries this period”
- [x] Mobile-responsive: large tappable Clock In/Out buttons; stacked timesheet rows

### Permissions
- [x] Members: clock in/out for self only; view own timesheet
- [x] Admins: view team DTR, approve/reject entries, optionally edit past entries with audit note
- [x] Server-side checks on every clock and approval action (not UI-only)

### MVP launch criteria
- [x] Member can clock in, clock out, and see hours on My DTR
- [x] Only one open entry per user at a time
- [x] Admin can review and approve/reject pending entries on Team DTR
- [x] Weekly hours widget shows correct totals for the current week
- [x] All queries scoped to `request.organization`

### V2 — Schedules, breaks & export (optional follow-up)
- [ ] `WorkSchedule` model — per-user day/time windows for auto-approve on clock-out
- [ ] Unscheduled entries stay `pending` until admin approval (FastDTR-style)
- [ ] Break start/end buttons while clocked in (or manual break minutes on clock-out)
- [ ] CSV export for payroll (date, name, in, out, hours, status)
- [x] Realtime Team DTR page refresh on clock in/out and approve/reject via WebSocket
- [x] Realtime member My DTR / My Timesheet refresh when admin approves or rejects their entry
- [ ] Broadcast `dtr.updated` over WebSocket — Team Board “Clocked in” badge on member tiles
- [ ] Optional: “You’re clocked in” banner on My Board (like deadline banner)

### Testing & docs
- [x] Unit tests: open-entry constraint, hour calculation, org scoping, approve/reject flow
- [x] Mark Task 28 complete in this checklist when MVP ships


