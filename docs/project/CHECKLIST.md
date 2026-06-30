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

- [ ] Create a `my_board` view in `base/views.py` — shows only tasks assigned to the logged-in user with `status = assigned`
- [ ] Register URL `my/` → `my_board` in `base/urls.py`
- [ ] Create `templates/board/my_board.html` — clean single-column layout with the same sticky note cards
- [ ] Add active state highlight to the "My Board" sidebar link
- [ ] Show task count in the page header
- [ ] Show a friendly empty state when the user has no active tasks

---

## Task 7 — Done / Completed Tasks Page

- [ ] Create a `done_tasks` view in `base/views.py` — fetches all tasks with `status = done`, ordered by `completed_at` descending
- [ ] Register URL `done/` → `done_tasks` in `base/urls.py`
- [ ] Create `templates/board/done_tasks.html` — list view with task title, who created it, who completed it, and the completion date
- [ ] Style completed task rows with the `--green` color (`#81C784`) and a strikethrough on the title
- [ ] Add active state highlight to the "Done" sidebar link
- [ ] Show a friendly empty state when no tasks have been completed yet

---

## Task 8 — Reassign / Move Task

- [ ] Create a `task_reassign` view in `base/views.py` — accepts POST with a new `assigned_to` user ID
- [ ] Register URL `task/<int:task_id>/reassign/` in `base/urls.py`
- [ ] Add a small "Move" dropdown or button to each task card in `_task_card.html`
- [ ] On save: update `assigned_to` and `status`, write to `ActivityLog`
- [ ] Redirect back to Team Board after reassignment
- [ ] Show an inline reassign form only to the task creator or admin role

---

## Task 9 — Edit & Delete Task

- [ ] Create a `task_edit` view in `base/views.py` — pre-fills `TaskCreateForm` with existing task data
- [ ] Create a `task_delete` view — POST-only, soft-deletes or hard-deletes the task
- [ ] Register URLs: `task/<int:task_id>/edit/` and `task/<int:task_id>/delete/`
- [ ] Add Edit and Delete options to the small menu on each task card in `_task_card.html`
- [ ] Reuse `templates/board/task_form.html` for the edit page (pass `task` to context for the heading)
- [ ] Write an entry to `ActivityLog` on edit and delete
- [ ] Redirect back to Team Board after edit or delete

---

## Task 10 — Team Management (Admin)

- [ ] Create a `team_list` view in `base/views.py` — lists all active users with their role and task count
- [ ] Create an `invite_member` view — creates a new Django `User` and their `UserProfile`
- [ ] Register URLs: `team/` → `team_list`, `team/invite/` → `invite_member`
- [ ] Create `templates/team/team_list.html` — card grid of team members with avatar, name, role, and active task count
- [ ] Create `templates/team/invite_form.html` — simple form: username, first name, last name, role, password
- [ ] Restrict `invite_member` to admin-role users only
- [ ] Add active state highlight to the "Team" sidebar link
