/**
 * TaskPin — Online presence indicators (team board, team list).
 */
(function () {
  if (document.body.dataset.userAuth !== 'true') {
    return;
  }

  const HEARTBEAT_MS = 45000;
  let heartbeatTimer = null;

  function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
  }

  function applyOnlineSet(onlineIds) {
    const onlineSet = new Set((onlineIds || []).map(String));
    document.querySelectorAll('[data-presence-user-id]').forEach(function (el) {
      const userId = String(el.dataset.presenceUserId);
      if (onlineSet.has(userId)) {
        el.hidden = false;
        el.classList.add('presence-dot--online');
      } else {
        el.hidden = true;
        el.classList.remove('presence-dot--online');
      }
    });
  }

  function fetchOnlineUsers() {
    return fetch('/api/presence/online/', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (Array.isArray(data.online_user_ids)) {
          applyOnlineSet(data.online_user_ids);
        }
      })
      .catch(function () {});
  }

  function sendHeartbeat() {
    return fetch('/api/presence/heartbeat/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        Accept: 'application/json',
      },
    }).catch(function () {});
  }

  function startHeartbeat() {
    if (heartbeatTimer) {
      return;
    }
    heartbeatTimer = setInterval(sendHeartbeat, HEARTBEAT_MS);
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer);
      heartbeatTimer = null;
    }
  }

  document.addEventListener('taskpin:board-update', function (e) {
    const data = e.detail;
    if (!data || data.action !== 'presence.update') {
      return;
    }
    const orgId = document.body.dataset.orgId;
    if (orgId && data.organization_id && String(data.organization_id) !== String(orgId)) {
      return;
    }
    if (Array.isArray(data.online_user_ids)) {
      applyOnlineSet(data.online_user_ids);
    }
  });

  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') {
      sendHeartbeat();
    }
  });

  fetchOnlineUsers();
  sendHeartbeat();
  startHeartbeat();

  window.addEventListener('beforeunload', stopHeartbeat);

  window.TaskPinPresence = {
    applyOnlineSet: applyOnlineSet,
    fetchOnlineUsers: fetchOnlineUsers,
  };
})();
