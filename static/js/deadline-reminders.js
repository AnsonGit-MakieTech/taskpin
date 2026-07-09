/**
 * TaskPin — Due date reminders (browser notification + in-app alert).
 */
(function () {
  if (document.body.dataset.userAuth !== 'true') {
    return;
  }

  const CHECK_INTERVAL_MS = 60000;
  const STORAGE_PREFIX = 'taskpin-deadline-';
  let permissionRequested = false;

  function reminderKey(item) {
    return STORAGE_PREFIX + item.task_id + '-' + item.urgency;
  }

  function showInAppReminder(item) {
    let toast = document.getElementById('deadline-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'deadline-toast';
      toast.className = 'realtime-toast deadline-toast deadline-toast--' + item.urgency;
      document.body.appendChild(toast);
    }
    toast.className = 'realtime-toast deadline-toast deadline-toast--visible deadline-toast--' + item.urgency;
    toast.innerHTML =
      '<strong>' + item.label + '</strong><br>' +
      item.title + '<br><span class="deadline-toast-due">' + item.due_date + '</span>';
    clearTimeout(showInAppReminder._timer);
    showInAppReminder._timer = setTimeout(function () {
      toast.classList.remove('deadline-toast--visible');
    }, 8000);
  }

  function showBrowserNotification(item) {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      return;
    }
    try {
      new Notification('TaskPin — ' + item.label, {
        body: item.title + ' · ' + item.due_date,
        tag: reminderKey(item),
      });
    } catch (err) {
      console.warn('[TaskPin] Browser notification failed', err);
    }
  }

  function updateMyBoardBanner(reminders) {
    const banner = document.getElementById('myboard-deadline-banner');
    if (!banner) {
      return;
    }
    if (!reminders.length) {
      banner.hidden = true;
      banner.innerHTML = '';
      return;
    }
    const top = reminders[0];
    const extra = reminders.length > 1 ? ' (+ ' + (reminders.length - 1) + ' more)' : '';
    banner.hidden = false;
    banner.className = 'deadline-banner deadline-banner--' + top.urgency;
    banner.textContent = top.label + ': ' + top.title + ' — ' + top.due_date + extra;
  }

  function notifyReminder(item) {
    if (sessionStorage.getItem(reminderKey(item))) {
      return;
    }
    sessionStorage.setItem(reminderKey(item), '1');
    showInAppReminder(item);
    showBrowserNotification(item);
  }

  function requestNotificationPermission() {
    if (permissionRequested || !('Notification' in window)) {
      return;
    }
    permissionRequested = true;
    if (Notification.permission === 'default') {
      Notification.requestPermission().catch(function () {});
    }
  }

  function checkReminders() {
    fetch('/api/my/deadline-reminders/', {
      headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin',
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Reminder fetch failed');
        }
        return response.json();
      })
      .then(function (data) {
        const reminders = data.reminders || [];
        updateMyBoardBanner(reminders);
        reminders.forEach(notifyReminder);
      })
      .catch(function (err) {
        console.warn('[TaskPin] Deadline reminders failed', err);
      });
  }

  document.addEventListener('click', requestNotificationPermission, { once: true, capture: true });
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') {
      checkReminders();
    }
  });

  setInterval(checkReminders, CHECK_INTERVAL_MS);
  checkReminders();
})();
