/**
 * TaskPin — Live board sync over WebSocket (no full page reload).
 */
(function () {
  const PAGE = document.body.dataset.realtimePage;
  if (!PAGE || document.body.dataset.userAuth !== 'true') {
    return;
  }

  const PRIORITY_LABELS = {
    urgent: 'Urgent',
    important: 'Important',
    normal: 'Normal',
  };

  function showToast(message) {
    let toast = document.getElementById('realtime-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'realtime-toast';
      toast.className = 'realtime-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('realtime-toast--visible');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(function () {
      toast.classList.remove('realtime-toast--visible');
    }, 2200);
  }

  function fetchFragment(url) {
    return fetch(url, {
      headers: {
        Accept: 'text/html',
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
    }).then(function (response) {
      if (response.status === 404) {
        return '';
      }
      if (!response.ok) {
        throw new Error('Fragment fetch failed');
      }
      return response.text();
    });
  }

  function parseHtml(html) {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    return wrapper.firstElementChild;
  }

  function initCardMenus(root) {
    if (window.TaskPinBoard && window.TaskPinBoard.initCardMenus) {
      window.TaskPinBoard.initCardMenus(root);
    }
    if (window.TaskPinBoard && window.TaskPinBoard.refreshDraggability) {
      window.TaskPinBoard.refreshDraggability();
    }
  }

  function removeTaskCard(taskId) {
    if (PAGE === 'team_board' && window.TaskPinTeamBoard && window.TaskPinTeamBoard.removeTaskCard) {
      window.TaskPinTeamBoard.removeTaskCard(taskId);
      return;
    }
    const card = document.querySelector('.task-card[data-task-id="' + taskId + '"]');
    if (!card) {
      return;
    }
    const menu = document.getElementById('menu-' + taskId);
    if (menu) {
      menu.remove();
    }
    card.remove();
  }

  function syncTeamBoard(taskId, html, data) {
    if (!window.TaskPinTeamBoard) {
      return;
    }
    if (data.action === 'task.deleted' || data.status === 'done') {
      window.TaskPinTeamBoard.removeTaskCard(taskId);
      return;
    }
    if (!html) {
      window.TaskPinTeamBoard.removeTaskCard(taskId);
      return;
    }
    window.TaskPinTeamBoard.syncTaskCard(taskId, html, data);
  }

  function ensureMyPriorityGroup(priority) {
    let group = document.querySelector('.priority-group[data-priority="' + priority + '"]');
    if (group) {
      return group;
    }
    const tasksRoot = document.getElementById('myboard-tasks');
    if (!tasksRoot) {
      return null;
    }
    group = document.createElement('div');
    group.className = 'priority-group';
    group.dataset.priority = priority;
    group.innerHTML =
      '<div class="priority-group-label">' +
      '<span class="priority-dot priority-dot--' + priority + '"></span>' +
      (PRIORITY_LABELS[priority] || priority) +
      '</div><div class="priority-group-cards"></div>';
    tasksRoot.appendChild(group);
    return group;
  }

  function updateMyBoardCount() {
    const count = document.querySelectorAll('#myboard-tasks .task-card').length;
    const pill = document.getElementById('myboard-count-pill');
    const text = document.getElementById('myboard-count-text');
    const tasksRoot = document.getElementById('myboard-tasks');
    const empty = document.getElementById('myboard-empty');
    if (text) {
      text.textContent = count + ' active task' + (count === 1 ? '' : 's');
    }
    if (pill) {
      pill.hidden = count === 0;
    }
    if (tasksRoot) {
      tasksRoot.hidden = count === 0;
    }
    if (empty) {
      empty.hidden = count > 0;
    }
  }

  function syncMyBoard(taskId, html, data) {
    const currentUserId = document.body.dataset.userId;
    removeTaskCard(taskId);

    if (data.action === 'task.deleted' || data.status === 'done') {
      updateMyBoardCount();
      return;
    }
    if (String(data.assigned_to_id) !== String(currentUserId)) {
      updateMyBoardCount();
      return;
    }
    if (!html) {
      updateMyBoardCount();
      return;
    }

    const card = parseHtml(html);
    if (!card) {
      return;
    }

    const priority = data.priority || 'normal';
    const group = ensureMyPriorityGroup(priority);
    const cardsHost = group && group.querySelector('.priority-group-cards');
    if (!cardsHost) {
      return;
    }

    group.hidden = false;
    cardsHost.appendChild(card);
    initCardMenus(card);
    updateMyBoardCount();
  }

  function updateDoneCount() {
    const list = document.getElementById('done-list');
    const count = list ? list.querySelectorAll('.done-row').length : 0;
    const pill = document.getElementById('done-count-pill');
    const text = document.getElementById('done-count-text');
    const empty = document.getElementById('done-empty');
    if (text) {
      text.textContent = count + ' completed';
    }
    if (pill) {
      pill.hidden = count === 0;
    }
    if (list) {
      list.hidden = count === 0;
    }
    if (empty) {
      empty.hidden = count > 0;
    }
  }

  function syncDonePage(taskId, html, data) {
    if (data.action !== 'task.done') {
      if (data.action === 'task.deleted') {
        const row = document.querySelector('.done-row[data-task-id="' + taskId + '"]');
        if (row) {
          row.remove();
          updateDoneCount();
        }
      }
      return;
    }
    if (!html) {
      return;
    }
    const list = document.getElementById('done-list');
    if (!list) {
      return;
    }
    const existing = list.querySelector('.done-row[data-task-id="' + taskId + '"]');
    if (existing) {
      existing.remove();
    }
    const row = parseHtml(html);
    if (!row) {
      return;
    }
    list.insertBefore(row, list.firstChild);
    updateDoneCount();
  }

  function applyBoardUpdate(data) {
    const taskId = data.task_id;
    if (!taskId) {
      return Promise.resolve();
    }

    if (data.action === 'task.deleted') {
      removeTaskCard(taskId);
      if (PAGE === 'my_board') {
        updateMyBoardCount();
      }
      if (PAGE === 'done_tasks') {
        syncDonePage(taskId, '', data);
      }
      return Promise.resolve();
    }

    if (data.action === 'task.done') {
      removeTaskCard(taskId);
      if (PAGE === 'my_board') {
        updateMyBoardCount();
      }
      if (PAGE === 'done_tasks') {
        return fetchFragment('/task/' + taskId + '/done-row/').then(function (html) {
          syncDonePage(taskId, html, data);
        });
      }
      if (PAGE === 'team_board' && window.TaskPinTeamBoard) {
        window.TaskPinTeamBoard.removeTaskCard(taskId);
      }
      return Promise.resolve();
    }

    return fetchFragment('/task/' + taskId + '/card/').then(function (html) {
      if (PAGE === 'team_board') {
        syncTeamBoard(taskId, html, data);
      } else if (PAGE === 'my_board') {
        syncMyBoard(taskId, html, data);
      }
    });
  }

  function isBoardTaskEvent(data) {
    return Boolean(data && data.task_id && data.action && data.action.indexOf('task.') === 0);
  }

  document.addEventListener('taskpin:board-update', function (e) {
    const data = e.detail;
    if (!data || data.type === 'connection.established') {
      return;
    }
    if (!isBoardTaskEvent(data)) {
      return;
    }

    const orgId = document.body.dataset.orgId;
    if (orgId && data.organization_id && String(data.organization_id) !== String(orgId)) {
      return;
    }

    applyBoardUpdate(data)
      .then(function () {
        const currentUserId = document.body.dataset.userId;
        const isOwnAction = currentUserId && data.actor_id &&
          String(data.actor_id) === String(currentUserId);
        if (!isOwnAction) {
          showToast('Board updated');
        }
      })
      .catch(function (err) {
        console.warn('[TaskPin] Board sync failed', err);
      });
  });
})();
