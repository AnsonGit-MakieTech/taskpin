# Project Description: TaskPin Sticky Task Board

## Product Overview

TaskPin is a simple team task management system designed around the idea of digital sticky notes. Instead of using complicated project management tools, users can create small task notes and paste them onto another team member’s task board through drag-and-drop.

The system helps small teams quickly assign responsibilities, track simple tasks, and see who is currently handling what. It is built for offices, small businesses, service teams, admin teams, and local operations that need an easy way to organize daily work without learning complex software.

## Problem It Solves

Many small teams still assign tasks through chat messages, verbal instructions, notebooks, or scattered reminders. Because of this, tasks are easily forgotten, duplicated, delayed, or assigned without clear ownership.

TaskPin solves this by giving every team member their own visual task board. A manager or team member can create a sticky note, drag it to a person’s board, and instantly make that person responsible for the task.

The system answers three simple questions:

* What needs to be done?
* Who is responsible for it?
* Is it already done?

## Core Concept

The system works like a physical office wall with sticky notes.

A user creates a task note, then drags and drops it onto another user’s board. Once the task is completed, the assigned user can mark it as done.

The main workflow is:

Create a note → Pin it to a teammate → Complete the task → View history

## Target Users

TaskPin is designed for small teams that need simple task coordination, including:

* Small offices
* Gasoline station teams
* ISP admin and support teams
* Repair shops
* Clinics
* Schools
* Barangay or local office teams
* Family businesses
* Freelance teams
* Service-based businesses

## Main Features

The first version of the system will focus only on the most important features:

* User login
* Team member boards
* Create sticky task notes
* Drag-and-drop task assignment
* Move task from one user to another
* Mark task as done
* View completed task history
* Simple task priority
* Optional due date
* Basic activity log

## Main Screens

The system will include a simple set of screens:

### Team Board

This is the main dashboard where all team members are displayed as columns or boards. Tasks appear as sticky notes. Users can drag a task note from one board to another.

### My Board

Each user has a personal task board showing only the tasks assigned to them.

### Done Tasks

This screen shows completed tasks so the team can review what has already been finished.

### Team Management

This screen allows the admin to add or manage team members.

## Task Information

Each sticky note will contain simple task details:

* Task title
* Optional description
* Assigned user
* Status
* Priority
* Optional due date
* Created by
* Date completed

## Task Statuses

The system will use simple task statuses:

* Unassigned
* Assigned
* Done

This keeps the system easy to understand and prevents users from being overwhelmed by too many workflow stages.

## Design Direction

TaskPin should feel like a digital corkboard or sticky-note wall. The interface must be clean, friendly, and easy to understand.

The design should focus on:

* Large readable sticky notes
* Clear user boards
* Simple drag-and-drop movement
* Minimal buttons
* Fast task creation
* Mobile-friendly layout
* No complicated project management terms

## Technology Stack

The recommended technology stack is:

* Backend: Django
* API: Django REST Framework
* Database: PostgreSQL
* Frontend: Django templates or simple JavaScript first
* Drag-and-drop: JavaScript drag-and-drop library
* Deployment: Ubuntu, Nginx, Gunicorn, systemd
* Future realtime updates: Redis and Django Channels

## Business Goal

TaskPin aims to become a lightweight task assignment tool for small teams that do not want complex project management software. The goal is to help businesses stop losing small tasks in chat messages and replace them with a simple visual board.

The product can later be offered as a SaaS with free and paid plans based on the number of users, active tasks, task history, and team boards.

## Product Promise

TaskPin keeps task management simple.

Create a note.
Pin it to someone.
Get it done.
