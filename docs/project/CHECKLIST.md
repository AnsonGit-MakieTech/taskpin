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

- [ ] Wire Django's built-in `auth` login and logout views in `taskpin/urls.py`
- [ ] Create top-level `templates/` folder and a `templates/base.html` layout template
- [ ] Add sidebar navigation in `base.html` with links: Team Board, My Board, Done, Team, Settings
- [ ] Apply theme styles in `base.html`: Inter font, `#F8F6F0` background, `#2E2E2E` text, warm accent colors
- [ ] Create `templates/registration/login.html` styled to match the theme
- [ ] Add `@login_required` decorator to all app views

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

- [ ] Create `TaskCreateView` in `base/views.py` with a minimal form: title, priority, due date, assign_to
- [ ] Create `templates/board/task_form.html` for the create form, styled as a simple modal or page
- [ ] Add a "Create Note" button to the Team Board page that opens the create form
- [ ] On form save: set `status = assigned` if `assigned_to` is filled, otherwise `status = unassigned`
- [ ] Write an entry to `ActivityLog` on every task creation
- [ ] Redirect back to the Team Board after successful task creation
