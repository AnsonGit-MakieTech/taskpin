/**
 * TaskPin — Team board member grid and integrated task panel.
 */
(function () {
  const boardPage = document.querySelector('.board-page');
  const panel = document.getElementById('task-panel');
  if (!boardPage || !panel) {
    return;
  }

  const closeBtn = document.getElementById('task-panel-close');
  const panelBody = document.getElementById('task-panel-body');
  const panelTitle = document.getElementById('task-panel-title');
  const panelSub = document.getElementById('task-panel-sub');
  const storesRoot = document.getElementById('task-stores-root');
  const searchInput = document.getElementById('member-search');

  let activeStore = null;
  let activeTile = null;
  let suppressTileClickUntil = 0;

  const PRIORITY_ORDER = ['urgent', 'important', 'normal'];
  const PRIORITY_LABELS = {
    urgent: 'Urgent',
    important: 'Important',
    normal: 'Normal',
  };

  function cardPriority(card) {
    if (card.classList.contains('task-card--urgent')) {
      return 'urgent';
    }
    if (card.classList.contains('task-card--important')) {
      return 'important';
    }
    return 'normal';
  }

  function findPriorityGroup(store, priority) {
    return store.querySelector('.task-priority-group[data-priority="' + priority + '"]');
  }

  function ensurePriorityGroup(store, priority) {
    let group = findPriorityGroup(store, priority);
    if (group) {
      return group;
    }

    group = document.createElement('div');
    group.className = 'task-priority-group';
    group.dataset.priority = priority;
    group.innerHTML =
      '<div class="task-priority-label">' +
      '<span class="priority-star priority-star--' + priority + '" aria-hidden="true">★</span>' +
      (PRIORITY_LABELS[priority] || priority) +
      '</div>';

    const priorityIndex = PRIORITY_ORDER.indexOf(priority);
    let inserted = false;
    for (let i = priorityIndex + 1; i < PRIORITY_ORDER.length; i += 1) {
      const nextGroup = findPriorityGroup(store, PRIORITY_ORDER[i]);
      if (nextGroup) {
        store.insertBefore(group, nextGroup);
        inserted = true;
        break;
      }
    }
    if (!inserted) {
      const empty = store.querySelector('.empty-state');
      if (empty) {
        store.insertBefore(group, empty);
      } else {
        store.appendChild(group);
      }
    }
    return group;
  }

  function appendCardToStore(store, card, priority) {
    const group = ensurePriorityGroup(store, priority || cardPriority(card));
    group.hidden = false;
    group.appendChild(card);
  }

  function refreshPriorityGroups(store) {
    store.querySelectorAll('.task-priority-group').forEach(function (group) {
      group.hidden = !group.querySelector('.task-card');
    });
  }

  function moveDropdownsToBody(root) {
    if (!root) {
      return;
    }
    root.querySelectorAll('.card-menu-dropdown').forEach(function (el) {
      document.body.appendChild(el);
    });
  }

  function setActiveTile(tile) {
    document.querySelectorAll('.member-tile--active').forEach(function (el) {
      el.classList.remove('member-tile--active');
    });
    activeTile = tile || null;
    if (activeTile) {
      activeTile.classList.add('member-tile--active');
    }
  }

  function refreshPanelMeta() {
    if (!activeStore) {
      return;
    }
    const name = activeStore.dataset.memberName || 'Tasks';
    const taskCount = activeStore.querySelectorAll('.task-card').length;
    panelTitle.textContent = name;
    panelSub.textContent = taskCount + ' open note' + (taskCount === 1 ? '' : 's');
  }

  function updateTileCount(tile) {
    const storeId = tile.dataset.storeId;
    const store = storeId && document.getElementById(storeId);
    const count = store ? store.querySelectorAll('.task-card').length : 0;
    const countEl = tile.querySelector('.member-tile-count');
    const badge = tile.querySelector('.count-badge');
    if (countEl) {
      countEl.textContent = count + ' open note' + (count === 1 ? '' : 's');
    }
    if (badge) {
      badge.textContent = count;
      badge.classList.toggle('count-badge--empty', count === 0);
    }
  }

  function updateAllTileCounts() {
    document.querySelectorAll('.member-tile').forEach(updateTileCount);
  }

  function findStoreByUserId(userId) {
    const storeId = userId ? ('task-store-' + userId) : 'task-store-unassigned';
    return document.getElementById(storeId);
  }

  function ensureEmptyState(store) {
    refreshPriorityGroups(store);
    if (store.querySelector('.task-card')) {
      const empty = store.querySelector('.empty-state');
      if (empty) {
        empty.remove();
      }
      return;
    }
    if (store.querySelector('.empty-state')) {
      return;
    }
    const empty = document.createElement('div');
    empty.className = 'empty-state empty-state--panel';
    const isUnassigned = !store.dataset.userId;
    empty.innerHTML =
      '<p class="empty-state-title">' + (isUnassigned ? 'No unassigned tasks' : 'No tasks yet') + '</p>' +
      '<p class="empty-state-hint">' + (isUnassigned
        ? 'Create a note and assign it to someone.'
        : 'Drag a note here to assign work.') + '</p>';
    store.appendChild(empty);
  }

  function openPanel(storeEl, tile) {
    if (!storeEl) {
      return;
    }

    const wasOpen = boardPage.classList.contains('board-page--panel-open');

    if (activeStore && activeStore !== storeEl && storesRoot) {
      storesRoot.appendChild(activeStore);
    }

    activeStore = storeEl;
    panelBody.replaceChildren(storeEl);

    refreshPanelMeta();
    setActiveTile(tile);
    moveDropdownsToBody(panelBody);

    if (!wasOpen) {
      boardPage.classList.add('board-page--panel-open');
    }
    panel.setAttribute('aria-hidden', 'false');

    if (window.TaskPinBoard && window.TaskPinBoard.refreshDraggability) {
      window.TaskPinBoard.refreshDraggability();
    }
  }

  function closePanel() {
    if (activeStore && storesRoot) {
      storesRoot.appendChild(activeStore);
    }
    panelBody.replaceChildren();
    activeStore = null;
    setActiveTile(null);

    boardPage.classList.remove('board-page--panel-open');
    panel.setAttribute('aria-hidden', 'true');
  }

  function onTaskMoved(taskId, assignedToId) {
    const card = document.querySelector('.task-card[data-task-id="' + taskId + '"]');
    if (!card) {
      return;
    }

    const sourceStore = card.closest('.task-store');
    const targetStore = findStoreByUserId(assignedToId || '');
    if (!sourceStore || !targetStore || sourceStore === targetStore) {
      return;
    }

    appendCardToStore(targetStore, card);
    refreshPriorityGroups(sourceStore);
    ensureEmptyState(sourceStore);
    ensureEmptyState(targetStore);
    updateAllTileCounts();

    if (activeStore === sourceStore) {
      refreshPanelMeta();
    }

    suppressTileClickUntil = Date.now() + 400;

    if (window.TaskPinBoard && window.TaskPinBoard.refreshDraggability) {
      window.TaskPinBoard.refreshDraggability();
    }
  }

  function removeTaskCard(taskId) {
    const card = document.querySelector('.task-card[data-task-id="' + taskId + '"]');
    if (!card) {
      return;
    }
    const menu = document.getElementById('menu-' + taskId);
    if (menu) {
      menu.remove();
    }
    const store = card.closest('.task-store');
    card.remove();
    if (store) {
      refreshPriorityGroups(store);
      ensureEmptyState(store);
    }
    updateAllTileCounts();
    if (activeStore === store) {
      refreshPanelMeta();
    }
  }

  function syncTaskCard(taskId, html, data) {
    removeTaskCard(taskId);

    if (!html || data.status === 'done') {
      if (data.previous_assigned_to_id !== undefined) {
        const prevStore = findStoreByUserId(data.previous_assigned_to_id || '');
        if (prevStore) {
          ensureEmptyState(prevStore);
          updateAllTileCounts();
        }
      }
      return;
    }

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const card = wrapper.firstElementChild;
    if (!card) {
      return;
    }

    const targetStore = findStoreByUserId(data.assigned_to_id || '');
    if (!targetStore) {
      return;
    }

    appendCardToStore(targetStore, card, data.priority || cardPriority(card));

    if (data.previous_assigned_to_id !== undefined) {
      const prevStore = findStoreByUserId(data.previous_assigned_to_id || '');
      if (prevStore && prevStore !== targetStore) {
        ensureEmptyState(prevStore);
      }
    }

    ensureEmptyState(targetStore);
    updateAllTileCounts();

    if (activeStore === targetStore) {
      refreshPanelMeta();
    }

    moveDropdownsToBody(activeStore === targetStore ? panelBody : storesRoot);
    if (window.TaskPinBoard && window.TaskPinBoard.initCardMenus) {
      window.TaskPinBoard.initCardMenus(card);
    }
    if (window.TaskPinBoard && window.TaskPinBoard.refreshDraggability) {
      window.TaskPinBoard.refreshDraggability();
    }
  }

  window.TaskPinTeamBoard = {
    onTaskMoved: onTaskMoved,
    syncTaskCard: syncTaskCard,
    removeTaskCard: removeTaskCard,
    suppressTileClick: function () {
      return Date.now() < suppressTileClickUntil;
    },
    markDragDrop: function () {
      suppressTileClickUntil = Date.now() + 400;
    },
  };

  document.querySelectorAll('.member-tile-open').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (window.TaskPinTeamBoard.suppressTileClick()) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      e.stopPropagation();
      const tile = btn.closest('.member-tile');
      const storeId = tile && tile.dataset.storeId;
      const storeEl = storeId && document.getElementById(storeId);
      if (!storeEl) {
        return;
      }
      if (activeTile === tile && boardPage.classList.contains('board-page--panel-open')) {
        closePanel();
        return;
      }
      openPanel(storeEl, tile);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', closePanel);
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && boardPage.classList.contains('board-page--panel-open')) {
      closePanel();
    }
  });

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const query = searchInput.value.trim().toLowerCase();
      document.querySelectorAll('.member-tile').forEach(function (tile) {
        const haystack = (tile.dataset.search || tile.dataset.memberName || '').toLowerCase();
        tile.classList.toggle('member-tile--hidden', query.length > 0 && haystack.indexOf(query) === -1);
      });
    });
  }

  moveDropdownsToBody(storesRoot);
})();
