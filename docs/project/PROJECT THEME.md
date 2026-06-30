# Project Theme Description: TaskPin UI/UX

## Theme Overview

TaskPin should look and feel like a clean digital sticky-note board. The system must be simple, friendly, and easy to understand even for non-technical users. The interface should avoid the feeling of a complicated project management tool and instead feel like an online office wall where users can paste task notes onto another person’s board.

The main experience should be:

Create a sticky note → Drag it to a teammate → Mark it as done

The design must focus on clarity, speed, and visual task ownership.

## UI Personality

The visual style should be:

* Friendly
* Clean
* Light
* Simple
* Organized
* Approachable
* Office-inspired
* Slightly playful but still professional

The system should not look too corporate, too technical, or too crowded. It should feel like a productivity tool made for small teams, offices, and daily operations.

## Main Visual Concept

The main visual concept is a **digital corkboard with sticky notes**.

Each team member should have their own board or column. Tasks should appear as sticky notes that can be dragged and dropped onto another user’s board.

The user should immediately understand:

* Which tasks are unassigned
* Which tasks belong to each person
* Which tasks are urgent
* Which tasks are done

## Recommended Color Palette

### Primary Colors

Use warm and friendly colors inspired by sticky notes and office boards.

* Soft Yellow — for normal sticky notes
* Warm Orange — for important notes
* Soft Red — for urgent tasks
* Light Green — for completed tasks
* Calm Blue — for follow-up or information tasks
* Off White — for page background
* Charcoal Gray — for main text

### Suggested Colors

```text
Primary Yellow: #FFE082
Soft Orange: #FFB74D
Urgent Red: #EF5350
Done Green: #81C784
Info Blue: #64B5F6
Background: #F8F6F0
Card Background: #FFFFFF
Text Dark: #2E2E2E
Text Muted: #777777
Border Light: #E0DED8
```

## Typography

The font should be readable and friendly.

Recommended fonts:

```text
Main UI Font: Inter
Alternative: Nunito Sans
Sticky Note Title Font: Nunito or Inter SemiBold
```

Use clean font sizes:

```text
Page title: 24px–28px
Section title: 18px–20px
Sticky note title: 15px–17px
Body text: 14px–15px
Small labels: 12px–13px
```

Avoid decorative handwritten fonts for the main UI because they can reduce readability. A slight handwritten effect can be used only for empty states or small decorative labels.

## Layout Direction

The main dashboard should use a board layout.

Example:

```text
+ Unassigned     + Andrew        + Juan          + Maria
---------------------------------------------------------
[Sticky Note]    [Sticky Note]   [Sticky Note]   [Sticky Note]
[Sticky Note]                   [Sticky Note]
```

Each user board should have:

* User name
* Small avatar or initials
* Number of active tasks
* Sticky note area
* Empty state message when no tasks exist

The layout should feel spacious. Do not overload the screen with too many buttons or menus.

## Sticky Note Design

Task cards should look like sticky notes.

Each note should include:

* Task title
* Optional short description
* Priority label
* Due date if available
* Done button
* Small menu for edit/delete

Sticky note style:

* Slight rounded corners
* Soft shadow
* Paper-like color
* Small pin/tape detail optional
* Clear drag handle or cursor behavior
* Simple hover effect

The sticky note must be readable at a glance.

Example sticky note:

```text
┌─────────────────────┐
│ Call supplier        │
│ Today • Normal       │
│                 Done │
└─────────────────────┘
```

## UX Behavior

The system should feel fast and natural.

Important UX rules:

* Creating a task should take less than 10 seconds.
* Dragging a task should instantly move the note visually.
* Dropping a task onto a user board should assign it to that user.
* Marking a task as done should be one click.
* The user should not need to understand complex status workflows.
* Avoid too many required fields.
* Avoid large forms unless editing full details.

## Main Pages

### 1. Team Board

This is the main screen. It shows all user boards and task notes. This is where drag-and-drop assignment happens.

### 2. My Board

This page shows only the logged-in user’s assigned tasks. It should be very clean and focused.

### 3. Done Tasks

This page shows completed tasks in a simple list or archive view.

### 4. Team Members

This page allows the admin to manage users.

## Navigation Style

Use a simple sidebar or top navigation.

Recommended menu items:

```text
Team Board
My Board
Done
Team
Settings
```

Keep navigation minimal. The product should not feel heavy.

## Empty State Style

Empty states should be friendly and helpful.

Examples:

```text
No tasks yet.
Create a sticky note and pin it to someone’s board.

Andrew has no tasks.
Drop a note here to assign work.
```

Empty boards should encourage action without feeling boring.

## Mobile UX

On mobile, the board should not force users to scroll too much horizontally.

Recommended mobile approach:

* Show team members as tabs or cards
* Show “My Board” first
* Allow task assignment through a simple dropdown
* Drag-and-drop can be optional on mobile
* Prioritize quick viewing and marking tasks as done

Mobile users should be able to:

* View assigned tasks
* Mark tasks as done
* Create a quick task
* Reassign a task if allowed

## Design Principles

The UI/UX must follow these principles:

1. Simple over powerful
2. Visual over text-heavy
3. Fast over feature-rich
4. Friendly over corporate
5. Ownership over complexity
6. One-click actions whenever possible
7. Clear task responsibility at all times

## What to Avoid

Avoid these design mistakes:

* Too many columns
* Too many statuses
* Complicated filters
* Heavy dashboards
* Long forms
* Dark and serious enterprise look
* Too many charts
* Project management jargon
* Complex permission screens in the MVP
* Overdesigned animations

## Overall Feel

TaskPin should feel like a simple office wall where every team member has their own space. The user should feel that managing tasks is as easy as writing a sticky note and placing it on someone’s board.

The final UI should communicate:

Simple. Visual. Friendly. Fast.

TaskPin is not a complicated project management system.
It is a digital sticky-note board for getting small team tasks done.
