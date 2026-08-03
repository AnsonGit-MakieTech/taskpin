/**
 * DTR — live refresh over WebSocket (Team DTR admin + member timesheet pages).
 */
(function () {
  'use strict';

  var PAGE = document.body.dataset.realtimePage;
  if (!PAGE || PAGE.indexOf('dtr_') !== 0 || document.body.dataset.userAuth !== 'true') {
    return;
  }

  var refreshTimer = null;

  function isDtrEvent(data) {
    return Boolean(data && data.action && data.action.indexOf('dtr.') === 0);
  }

  function isSameOrg(data) {
    var orgId = document.body.dataset.orgId;
    return !(orgId && data.organization_id && String(data.organization_id) !== String(orgId));
  }

  function isCurrentMember(data) {
    var currentUserId = document.body.dataset.userId;
    return Boolean(
      currentUserId && data.user_id && String(data.user_id) === String(currentUserId)
    );
  }

  function isOwnAction(data) {
    var currentUserId = document.body.dataset.userId;
    return Boolean(
      currentUserId && data.actor_id && String(data.actor_id) === String(currentUserId)
    );
  }

  function showToast(message) {
    var toast = document.getElementById('realtime-toast');
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
      if (!response.ok) {
        throw new Error('DTR refresh failed');
      }
      return response.text();
    });
  }

  function flashElement(el) {
    if (!el) return;
    el.classList.add('dtr-team-live--updated');
    window.setTimeout(function () {
      el.classList.remove('dtr-team-live--updated');
    }, 600);
  }

  function replaceById(fragmentDoc, elementId, addRefreshingClass) {
    var next = fragmentDoc.getElementById(elementId);
    var current = document.getElementById(elementId);
    if (!next || !current) {
      return false;
    }
    if (addRefreshingClass) {
      current.classList.add('dtr-team-live--refreshing');
    }
    current.replaceWith(next);
    next.classList.remove('dtr-team-live--refreshing');
    flashElement(next);
    return true;
  }

  function patchMemberStats(fragmentDoc) {
    var stats = fragmentDoc.getElementById('dtr-member-stats');
    if (!stats) return;
    var todayEl = document.getElementById('dtr-stat-today');
    var weekEl = document.getElementById('dtr-stat-week');
    if (todayEl && stats.dataset.today) {
      todayEl.textContent = stats.dataset.today;
    }
    if (weekEl && stats.dataset.week) {
      weekEl.textContent = stats.dataset.week;
    }
  }

  function memberToast(data) {
    if (isOwnAction(data)) return;
    if (data.action === 'dtr.approved') {
      showToast('Your time entry was approved');
    } else if (data.action === 'dtr.rejected') {
      showToast('Your time entry was rejected');
    }
  }

  function teamToast(data) {
    if (isOwnAction(data)) return;
    if (data.action === 'dtr.clock_in') {
      showToast('A teammate clocked in');
    } else if (data.action === 'dtr.clock_out') {
      showToast('A teammate clocked out');
    } else {
      showToast('Team DTR updated');
    }
  }

  function refreshTeamDtr(data) {
    var query = window.location.search.replace(/^\?/, '');
    var url = '/dtr/team/fragment/' + (query ? '?' + query : '');
    var live = document.getElementById('dtr-team-live');
    if (live) live.classList.add('dtr-team-live--refreshing');

    return fetchFragment(url).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      replaceById(doc, 'dtr-team-live', false);
      teamToast(data);
    }).catch(function () {
      if (live) live.classList.remove('dtr-team-live--refreshing');
    });
  }

  function refreshMyDtr(data) {
    return fetchFragment('/dtr/my/fragment/').then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      patchMemberStats(doc);
      replaceById(doc, 'dtr-my-recent-live', true);
      memberToast(data);
    });
  }

  function refreshTimesheet(data) {
    var query = window.location.search.replace(/^\?/, '');
    var url = '/dtr/timesheet/fragment/' + (query ? '?' + query : '');
    return fetchFragment(url).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      replaceById(doc, 'dtr-timesheet-live', true);
      memberToast(data);
    });
  }

  function shouldRefresh(data) {
    if (!isDtrEvent(data) || !isSameOrg(data)) {
      return false;
    }

    if (PAGE === 'dtr_team') {
      return true;
    }

    if (PAGE === 'dtr_my' || PAGE === 'dtr_timesheet') {
      if (data.action === 'dtr.approved' || data.action === 'dtr.rejected') {
        return isCurrentMember(data);
      }
      if (data.action === 'dtr.clock_in' || data.action === 'dtr.clock_out') {
        return isCurrentMember(data);
      }
    }

    return false;
  }

  function runRefresh(data) {
    if (PAGE === 'dtr_team') {
      return refreshTeamDtr(data);
    }
    if (PAGE === 'dtr_my') {
      return refreshMyDtr(data);
    }
    if (PAGE === 'dtr_timesheet') {
      return refreshTimesheet(data);
    }
    return Promise.resolve();
  }

  function scheduleRefresh(data) {
    if (refreshTimer) {
      window.clearTimeout(refreshTimer);
    }
    refreshTimer = window.setTimeout(function () {
      refreshTimer = null;
      runRefresh(data);
    }, 300);
  }

  document.addEventListener('taskpin:board-update', function (event) {
    var data = event.detail || {};
    if (shouldRefresh(data)) {
      scheduleRefresh(data);
    }
  });
})();
