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


