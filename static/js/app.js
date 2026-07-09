(function () {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const canMove = document.body.dataset.canMove === 'true';

  function dragEnabled() {
    return canMove && !window.matchMedia('(max-width: 768px)').matches;
  }

  function refreshDraggability() {
    const enabled = dragEnabled();
    document.querySelectorAll('.task-card[draggable]').forEach(function (card) {
      if (enabled) {
        card.setAttribute('draggable', 'true');
        card.classList.remove('task-card--no-drag');
      } else {
        card.setAttribute('draggable', 'false');
        card.classList.add('task-card--no-drag');
      }
    });
  }

  window.TaskPinBoard = {
    refreshDraggability: refreshDraggability,
    initCardMenus: function (root) {
      const scope = root || document;
      scope.querySelectorAll('.card-menu-dropdown').forEach(function (el) {
        document.body.appendChild(el);
      });
    },
  };

  document.addEventListener('DOMContentLoaded', function () {
    refreshDraggability();
    window.TaskPinBoard.initCardMenus();
  });

  /* ─────────────────────────────────────────────
     0. CONFIRM MODAL
  ───────────────────────────────────────────── */
  const modal = document.getElementById('confirm-modal');
  const modalTitle = document.getElementById('confirm-title');
  const modalMessage = document.getElementById('confirm-message');
  const modalOk = document.getElementById('confirm-ok');
  const modalCancel = document.getElementById('confirm-cancel');
  const remarksWrap = document.getElementById('confirm-remarks-wrap');
  const remarksField = document.getElementById('confirm-remarks');
  let pendingForm = null;

  function openConfirm(opts) {
    modalTitle.textContent = opts.title;
    modalMessage.textContent = opts.message;
    modalOk.textContent = opts.okLabel;
    modalOk.className = 'btn-confirm-ok' + (opts.okClass ? ' ' + opts.okClass : '');
    pendingForm = opts.form;
    if (remarksWrap && remarksField) {
      if (opts.showRemarks) {
        remarksWrap.hidden = false;
        remarksField.value = '';
      } else {
        remarksWrap.hidden = true;
        remarksField.value = '';
      }
    }
    modal.hidden = false;
    document.body.classList.add('modal-open');
  }

  function closeConfirm() {
    modal.hidden = true;
    document.body.classList.remove('modal-open');
    pendingForm = null;
    modalOk.className = 'btn-confirm-ok';
    if (remarksWrap) {
      remarksWrap.hidden = true;
    }
    if (remarksField) {
      remarksField.value = '';
    }
  }

  modalCancel.addEventListener('click', closeConfirm);
  modal.querySelector('.confirm-backdrop').addEventListener('click', closeConfirm);

  modalOk.addEventListener('click', function () {
    if (pendingForm) {
      if (remarksField && !remarksWrap.hidden) {
        let remarksInput = pendingForm.querySelector('input[name="completion_remarks"]');
        if (!remarksInput) {
          remarksInput = document.createElement('input');
          remarksInput.type = 'hidden';
          remarksInput.name = 'completion_remarks';
          pendingForm.appendChild(remarksInput);
        }
        remarksInput.value = remarksField.value.trim();
      }
      pendingForm.submit();
    }
    closeConfirm();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.hidden) closeConfirm();
  });

  document.addEventListener('click', function (e) {
    const toggleBtn = e.target.closest('.task-description-toggle');
    if (toggleBtn) {
      const wrap = toggleBtn.closest('.task-description-wrap');
      const desc = wrap.querySelector('.task-description');
      const expanded = desc.classList.toggle('task-description--expanded');
      desc.classList.toggle('task-description--collapsed', !expanded);
      toggleBtn.textContent = expanded ? 'Show less' : 'Show more';
      return;
    }

    const doneBtn = e.target.closest('.btn-done-confirm');
    if (doneBtn) {
      e.preventDefault();
      closeAllMenus();
      openConfirm({
        title: 'Mark as done?',
        message: 'Mark "' + doneBtn.dataset.taskTitle + '" as completed? You can still find it on the Done page.',
        okLabel: 'Yes, mark done',
        okClass: 'btn-confirm-ok--success',
        form: doneBtn.closest('form'),
        showRemarks: true,
      });
      return;
    }

    const deleteBtn = e.target.closest('.btn-delete-task');
    if (deleteBtn) {
      e.preventDefault();
      closeAllMenus();
      openConfirm({
        title: 'Delete this note?',
        message: 'Delete "' + deleteBtn.dataset.taskTitle + '"? This action cannot be undone.',
        okLabel: 'Delete note',
        okClass: 'btn-confirm-ok--danger',
        form: deleteBtn.closest('form'),
      });
    }
  });

  /* ─────────────────────────────────────────────
     1. DROPDOWN FIX
     Move every .card-menu-dropdown to <body> so
     it is never trapped inside a transformed parent.
  ───────────────────────────────────────────── */

  window.toggleMenu = function (id, trigger) {
    const dropdown = document.getElementById('menu-' + id);
    const isOpen = dropdown.classList.contains('open');

    closeAllMenus();

    if (!isOpen) {
      const rect = trigger.getBoundingClientRect();
      dropdown.style.top    = (rect.bottom + 6) + 'px';
      dropdown.style.left   = 'auto';
      dropdown.style.right  = (window.innerWidth - rect.right) + 'px';
      dropdown.style.transform = '';

      if (window.innerHeight - rect.bottom < 230) {
        dropdown.style.top       = (rect.top - 6) + 'px';
        dropdown.style.transform = 'translateY(-100%)';
      }

      dropdown.classList.add('open');
    }
  };

  function closeAllMenus() {
    document.querySelectorAll('.card-menu-dropdown.open').forEach(function (el) {
      el.classList.remove('open');
    });
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.card-menu') && !e.target.closest('.card-menu-dropdown')) {
      closeAllMenus();
    }
  });

  document.addEventListener('scroll', closeAllMenus, true);

  /* ─────────────────────────────────────────────
     2. DRAG AND DROP (Team Board only)
  ───────────────────────────────────────────── */
  let draggedTaskId = null;

  document.addEventListener('dragstart', function (e) {
    if (!dragEnabled()) {
      e.preventDefault();
      return;
    }
    if (e.target.closest('.card-menu, .done-form, button, select, a, input')) {
      e.preventDefault();
      return;
    }
    const card = e.target.closest('.task-card[data-task-id]');
    if (!card) return;
    draggedTaskId = card.dataset.taskId;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', draggedTaskId);
  });

  document.addEventListener('dragend', function (e) {
    document.querySelectorAll('.task-card.dragging').forEach(function (el) {
      el.classList.remove('dragging');
    });
    document.querySelectorAll('.drop-column.drag-over').forEach(function (el) {
      el.classList.remove('drag-over');
    });
    draggedTaskId = null;
  });

  document.addEventListener('dragover', function (e) {
    if (!dragEnabled()) return;
    const col = e.target.closest('.drop-column');
    if (col && draggedTaskId) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      document.querySelectorAll('.drop-column.drag-over').forEach(function (el) {
        if (el !== col) el.classList.remove('drag-over');
      });
      col.classList.add('drag-over');
    }
  });

  document.addEventListener('dragleave', function (e) {
    const col = e.target.closest('.drop-column');
    if (col && !col.contains(e.relatedTarget)) {
      col.classList.remove('drag-over');
    }
  });

  document.addEventListener('drop', function (e) {
    if (!dragEnabled()) return;
    const col = e.target.closest('.drop-column');
    if (!col || !draggedTaskId) return;
    e.preventDefault();
    col.classList.remove('drag-over');

    const userId = col.dataset.userId;
    const taskId = draggedTaskId;

    if (window.TaskPinTeamBoard && window.TaskPinTeamBoard.markDragDrop) {
      window.TaskPinTeamBoard.markDragDrop();
    }

    fetch('/task/' + taskId + '/reassign/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new URLSearchParams({
        csrfmiddlewaretoken: csrfToken,
        assigned_to: userId,
      }),
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Reassign failed');
        }
        return response.json();
      })
      .then(function (data) {
        if (data.ok && window.TaskPinTeamBoard && window.TaskPinTeamBoard.onTaskMoved) {
          window.TaskPinTeamBoard.onTaskMoved(data.task_id, data.assigned_to_id);
        }
      })
      .catch(function () {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/task/' + taskId + '/reassign/';

        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = csrfToken;
        form.appendChild(csrf);

        const field = document.createElement('input');
        field.type = 'hidden';
        field.name = 'assigned_to';
        field.value = userId;
        form.appendChild(field);

        document.body.appendChild(form);
        form.submit();
      });
  });
})();
