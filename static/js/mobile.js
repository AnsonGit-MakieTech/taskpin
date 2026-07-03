/**
 * TaskPin — mobile navigation sidebar only.
 * Team board uses member grid + task panel (board-team.js).
 */
(function () {
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

  if (window.TaskPinBoard && window.TaskPinBoard.refreshDraggability) {
    window.matchMedia('(max-width: 768px)').addEventListener('change', function () {
      window.TaskPinBoard.refreshDraggability();
    });
    window.TaskPinBoard.refreshDraggability();
  }
})();
