/**
 * TaskPin — Assignment notifications (sound + browser tab alert).
 * Listens for WebSocket board updates when a task is assigned to the current user.
 */
(function () {
  if (document.body.dataset.userAuth !== 'true') {
    return;
  }

  const currentUserId = document.body.dataset.userId;
  const soundUrl = document.body.dataset.notificationSound;
  const originalTitle = document.title;
  let pendingCount = 0;
  let audio = null;

  if (soundUrl) {
    audio = new Audio(soundUrl);
    audio.preload = 'auto';

    document.addEventListener('click', function unlockAudio() {
      if (!audio) {
        return;
      }
      audio.volume = 0;
      audio.play().then(function () {
        audio.pause();
        audio.currentTime = 0;
        audio.volume = 1;
      }).catch(function () {});
    }, { once: true, capture: true });
  }

  function playNotificationSound() {
    if (!audio) {
      return Promise.resolve();
    }

    return new Promise(function (resolve) {
      let finished = false;

      function finish() {
        if (finished) {
          return;
        }
        finished = true;
        audio.removeEventListener('ended', finish);
        resolve();
      }

      audio.addEventListener('ended', finish);
      audio.currentTime = 0;

      audio.play().then(function () {
        const durationMs = audio.duration && isFinite(audio.duration)
          ? Math.ceil(audio.duration * 1000) + 150
          : 2500;
        setTimeout(finish, durationMs);
      }).catch(finish);
    });
  }

  function updateTabTitle() {
    pendingCount += 1;
    const label = pendingCount === 1
      ? 'New task assigned'
      : pendingCount + ' new tasks assigned';
    document.title = '(' + pendingCount + ') ' + label + ' — ' + originalTitle;
  }

  function clearTabTitle() {
    if (pendingCount === 0) {
      return;
    }
    pendingCount = 0;
    document.title = originalTitle;
  }

  function isAssignmentForMe(data) {
    if (!currentUserId || !data.assigned_to_id) {
      return false;
    }
    if (String(data.assigned_to_id) !== String(currentUserId)) {
      return false;
    }
    if (data.actor_id && String(data.actor_id) === String(currentUserId)) {
      return false;
    }
    return data.action === 'task.moved' || data.action === 'task.created';
  }

  function notifyAssignment(data) {
    updateTabTitle();
    return playNotificationSound();
  }

  window.TaskPinNotify = {
    isAssignmentForMe: isAssignmentForMe,
    notifyAssignment: notifyAssignment,
  };

  document.addEventListener('taskpin:board-update', function (e) {
    const data = e.detail;
    if (!data || data.type === 'connection.established') {
      return;
    }
    if (!isAssignmentForMe(data)) {
      return;
    }
    notifyAssignment(data);
  });

  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') {
      clearTabTitle();
    }
  });

  window.addEventListener('focus', clearTabTitle);
})();
