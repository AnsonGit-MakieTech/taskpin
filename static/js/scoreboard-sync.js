/**
 * Scoreboard — live refresh on task completion via WebSocket.
 */
(function () {
  if (document.body.dataset.realtimePage !== 'scoreboard') {
    return;
  }

  let refreshTimer = null;

  function fetchLiveFragment() {
    const query = window.location.search.replace(/^\?/, '');
    const url = '/scoreboard/fragment/' + (query ? '?' + query : '');
    return fetch(url, {
      headers: {
        Accept: 'text/html',
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
    }).then(function (response) {
      if (!response.ok) {
        throw new Error('Scoreboard refresh failed');
      }
      return response.text();
    });
  }

  function patchMonthlyGoalFromPayload(data) {
    if (typeof data.monthly_goal_current !== 'number') {
      return;
    }
    const countEl = document.getElementById('scoreboard-goal-count');
    const barEl = document.getElementById('scoreboard-goal-bar-fill');
    const pctEl = document.getElementById('scoreboard-goal-pct');
    const target = data.monthly_goal_target || 50;
    const current = data.monthly_goal_current;
    const pct = target ? Math.min(100, Math.round(current / target * 100)) : 100;

    if (countEl) {
      countEl.innerHTML = '<strong>' + current + '</strong> / ' + target + ' completed';
    }
    if (barEl) {
      barEl.style.width = pct + '%';
    }
    if (pctEl) {
      pctEl.textContent = pct + '%';
    }
  }

  function refreshScoreboard(data) {
    if (data && data.action === 'task.done') {
      patchMonthlyGoalFromPayload(data);
    }

    return fetchLiveFragment().then(function (html) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const nextLive = doc.getElementById('scoreboard-live');
      const currentLive = document.getElementById('scoreboard-live');
      if (!nextLive || !currentLive) {
        return;
      }
      currentLive.replaceWith(nextLive);
      nextLive.classList.remove('scoreboard-live--refreshing');
      nextLive.classList.add('scoreboard-live--updated');
      window.setTimeout(function () {
        nextLive.classList.remove('scoreboard-live--updated');
      }, 600);
    });
  }

  function scheduleRefresh(data) {
    if (refreshTimer) {
      window.clearTimeout(refreshTimer);
    }
    refreshTimer = window.setTimeout(function () {
      refreshTimer = null;
      const live = document.getElementById('scoreboard-live');
      if (live) {
        live.classList.add('scoreboard-live--refreshing');
      }
      refreshScoreboard(data).catch(function () {
        if (live) {
          live.classList.remove('scoreboard-live--refreshing');
        }
      });
    }, 350);
  }

  document.addEventListener('taskpin:board-update', function (event) {
    const data = event.detail || {};
    if (data.action === 'task.done') {
      scheduleRefresh(data);
    }
  });
})();
