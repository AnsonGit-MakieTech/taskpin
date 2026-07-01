/**
 * TaskPin — mobile sidebar and team board column tabs.
 */
(function () {
  const MOBILE_QUERY = window.matchMedia('(max-width: 768px)');

  function isMobile() {
    return MOBILE_QUERY.matches;
  }

  /* ── Sidebar slide-out ── */
  const menuBtn = document.getElementById('mobile-menu-btn');
  const closeBtn = document.getElementById('sidebar-close-btn');
  const backdrop = document.getElementById('sidebar-backdrop');
  const sidebar = document.getElementById('sidebar');

  function openSidebar() {
    document.body.classList.add('sidebar-open');
    if (menuBtn) {
      menuBtn.setAttribute('aria-expanded', 'true');
    }
    if (backdrop) {
      backdrop.setAttribute('aria-hidden', 'false');
    }
  }

  function closeSidebar() {
    document.body.classList.remove('sidebar-open');
    if (menuBtn) {
      menuBtn.setAttribute('aria-expanded', 'false');
    }
    if (backdrop) {
      backdrop.setAttribute('aria-hidden', 'true');
    }
  }

  if (menuBtn) {
    menuBtn.addEventListener('click', openSidebar);
  }
  if (closeBtn) {
    closeBtn.addEventListener('click', closeSidebar);
  }
  if (backdrop) {
    backdrop.addEventListener('click', closeSidebar);
  }
  if (sidebar) {
    sidebar.querySelectorAll('.nav-item').forEach(function (link) {
      link.addEventListener('click', closeSidebar);
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.body.classList.contains('sidebar-open')) {
      closeSidebar();
    }
  });

  MOBILE_QUERY.addEventListener('change', function () {
    if (!isMobile()) {
      closeSidebar();
    }
    updateBoardColumns();
    updateDraggability();
  });

  /* ── Team board column tabs ── */
  const tabBar = document.querySelector('.board-column-tabs');
  const columns = document.querySelectorAll('.board-columns .board-column');

  function activateColumn(index) {
    if (!tabBar || !columns.length) {
      return;
    }

    tabBar.querySelectorAll('.board-column-tab').forEach(function (tab) {
      const active = tab.dataset.columnIndex === String(index);
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    columns.forEach(function (col) {
      const active = col.dataset.columnIndex === String(index);
      col.classList.toggle('board-column--active', active);
    });
  }

  function updateBoardColumns() {
    if (!columns.length) {
      return;
    }

    if (isMobile()) {
      const activeTab = tabBar && tabBar.querySelector('.board-column-tab.active');
      const index = activeTab ? activeTab.dataset.columnIndex : '0';
      activateColumn(index);
    } else {
      columns.forEach(function (col) {
        col.classList.add('board-column--active');
      });
    }
  }

  if (tabBar) {
    tabBar.addEventListener('click', function (e) {
      const tab = e.target.closest('.board-column-tab');
      if (!tab || !isMobile()) {
        return;
      }
      activateColumn(tab.dataset.columnIndex);
      tab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    });
  }

  /* ── Disable drag on mobile ── */
  function updateDraggability() {
    const mobile = isMobile();
    document.querySelectorAll('.task-card[draggable]').forEach(function (card) {
      if (mobile) {
        card.setAttribute('draggable', 'false');
        card.classList.add('task-card--no-drag');
      } else {
        card.setAttribute('draggable', 'true');
        card.classList.remove('task-card--no-drag');
      }
    });
  }

  updateBoardColumns();
  updateDraggability();
})();
