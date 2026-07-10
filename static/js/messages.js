/**
 * TaskPin — Team messaging (inbox, compose, realtime updates, badges).
 */
(function () {
  if (document.body.dataset.userAuth !== 'true') {
    return;
  }

  const currentUserId = document.body.dataset.userId;
  const isInboxPage = document.body.dataset.messagesPage === 'inbox';
  const activeConversationId = document.body.dataset.activeConversationId || null;
  const activeConversationType = document.body.dataset.activeConversationType || null;
  const TEAM_TOAST_DISMISS_KEY = 'taskpin:team-toast-dismissed';
  let teamSlideHideTimer = null;

  function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
  }

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
    }, 2800);
  }

  function updateUnreadBadge(count) {
    const badge = document.getElementById('sidebar-unread-messages');
    if (!badge) {
      return;
    }
    if (count > 0) {
      badge.textContent = count > 99 ? '99+' : String(count);
      badge.hidden = false;
    } else {
      badge.hidden = true;
    }
  }

  function fetchUnreadCount() {
    return fetch('/api/messages/unread-count/', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (typeof data.unread_message_count === 'number') {
          updateUnreadBadge(data.unread_message_count);
        }
        return data.unread_message_count;
      })
      .catch(function () {});
  }

  function isThreadOpen(conversationId) {
    return isInboxPage && String(activeConversationId) === String(conversationId);
  }

  function isDirectMessageForMe(data) {
    if (data.action !== 'message.new') {
      return false;
    }
    if (String(data.actor_id) === String(currentUserId)) {
      return false;
    }
    if (data.conversation_type !== 'direct') {
      return false;
    }
    if (data.recipient_user_id && String(data.recipient_user_id) !== String(currentUserId)) {
      return false;
    }
    return true;
  }

  function notifyDirectMessage(data) {
    if (window.TaskPinNotify && window.TaskPinNotify.notifyDirectMessage) {
      window.TaskPinNotify.notifyDirectMessage(data);
      return;
    }
    showToast('New message from ' + (data.sender_name || 'a teammate'));
  }

  function showBrowserNotification(data) {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      return;
    }
    if (data.conversation_type !== 'direct') {
      return;
    }
    const title = data.sender_name || 'New message';
    const body = data.preview || 'You have a new direct message';
    try {
      new Notification(title, { body: body, tag: 'taskpin-dm-' + data.message_id });
    } catch (err) {
      /* ignore */
    }
  }

  function updateConvoRowPreview(conversationId, data) {
    const row = document.querySelector('.msg-convo-row[data-conversation-id="' + conversationId + '"]');
    if (!row) {
      return;
    }
    const preview = row.querySelector('.msg-convo-preview');
    const timeEl = row.querySelector('.msg-convo-time');
    if (preview) {
      const prefix = String(data.actor_id) === String(currentUserId) ? 'You: ' : '';
      preview.textContent = prefix + (data.preview || '');
    }
    if (timeEl && data.created_at) {
      const d = new Date(data.created_at);
      timeEl.textContent = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    } else if (timeEl) {
      timeEl.textContent = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    }

    const list = document.getElementById('messages-convo-list');
    if (list && row.parentNode === list && !row.classList.contains('msg-convo-row--team')) {
      const teamRow = list.querySelector('.msg-convo-row--team');
      if (teamRow && teamRow.nextSibling) {
        list.insertBefore(row, teamRow.nextSibling);
      } else if (teamRow) {
        list.appendChild(row);
      } else {
        list.insertBefore(row, list.firstChild);
      }
    }
  }

  function appendMessageHtml(html) {
    const list = document.getElementById('messages-thread-list');
    if (!list) {
      return;
    }
    const empty = document.getElementById('messages-thread-empty');
    if (empty) {
      empty.remove();
    }
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const bubble = wrapper.firstElementChild;
    if (!bubble) {
      return;
    }
    const existing = list.querySelector('[data-message-id="' + bubble.dataset.messageId + '"]');
    if (existing) {
      return;
    }
    list.appendChild(bubble);
    scrollThreadToBottom();
  }

  function scrollThreadToBottom() {
    const scroll = document.getElementById('messages-thread-scroll');
    if (scroll) {
      scroll.scrollTop = scroll.scrollHeight;
    }
  }

  function fetchBubbleFragment(messageId) {
    return fetch('/messages/bubble/' + messageId + '/', {
      credentials: 'same-origin',
      headers: {
        Accept: 'text/html',
        'X-Requested-With': 'XMLHttpRequest',
      },
    }).then(function (response) {
      if (!response.ok) {
        throw new Error('Bubble fetch failed');
      }
      return response.text();
    });
  }

  function markConversationRead(conversationId) {
    const body = new FormData();
    body.append('conversation_id', conversationId);
    return fetch('/messages/mark-read/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: body,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok) {
          updateUnreadBadge(data.unread_message_count);
          const row = document.querySelector('.msg-convo-row[data-conversation-id="' + conversationId + '"]');
          const unread = row && row.querySelector('.msg-convo-unread');
          if (unread) {
            unread.remove();
          }
        }
      })
      .catch(function () {});
  }

  function handleMessageNew(data) {
    const conversationId = data.conversation_id;
    const isSender = String(data.actor_id) === String(currentUserId);
    const threadOpen = isThreadOpen(conversationId);

    updateConvoRowPreview(conversationId, data);

    if (threadOpen) {
      if (!isSender) {
        fetchBubbleFragment(data.message_id)
          .then(appendMessageHtml)
          .catch(function () {});
      }
      markConversationRead(conversationId);
    } else if (!isSender) {
      fetchUnreadCount();
      if (data.conversation_type === 'team') {
        showTeamSlideNotification({
          messageId: data.message_id,
          conversationId: data.conversation_id,
          senderId: data.actor_id,
          senderName: data.sender_name,
          preview: data.preview,
        });
      } else if (isDirectMessageForMe(data)) {
        notifyDirectMessage(data);
        showBrowserNotification(data);
        if (!isInboxPage) {
          showToast('New message from ' + (data.sender_name || 'a teammate'));
        }
      } else if (!isInboxPage) {
        showToast('New message from ' + (data.sender_name || 'a teammate'));
      }
    }
  }

  /* ── Inbox page: compose, load older, new menu, mobile ── */
  function initInboxPage() {
    const form = document.getElementById('messages-compose-form');
    const input = document.getElementById('messages-compose-input');
    const newBtn = document.getElementById('messages-new-btn');
    const newMenu = document.getElementById('messages-new-menu');
    const loadOlderBtn = document.getElementById('messages-load-older');

    if (input) {
      input.addEventListener('input', function () {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
      });

      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          if (form) {
            form.requestSubmit();
          }
        }
      });
    }

    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const body = input ? input.value.trim() : '';
        if (!body) {
          return;
        }
        const sendBtn = form.querySelector('.messages-send-btn');
        if (sendBtn) {
          sendBtn.disabled = true;
        }

        const payload = new FormData(form);
        payload.set('body', body);

        fetch('/messages/send/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': csrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: payload,
        })
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (!data.ok) {
              showToast(data.error || 'Could not send message');
              return;
            }
            if (input) {
              input.value = '';
              input.style.height = 'auto';
            }
            appendMessageHtml(data.html);
            if (activeConversationId) {
              updateConvoRowPreview(activeConversationId, {
                actor_id: currentUserId,
                preview: data.preview,
                created_at: data.created_at,
              });
            }
          })
          .catch(function () {
            showToast('Could not send message');
          })
          .finally(function () {
            if (sendBtn) {
              sendBtn.disabled = false;
            }
            if (input) {
              input.focus();
            }
          });
      });
    }

    if (newBtn && newMenu) {
      newBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const open = newMenu.hidden;
        newMenu.hidden = !open;
        newBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      document.addEventListener('click', function () {
        newMenu.hidden = true;
        newBtn.setAttribute('aria-expanded', 'false');
      });
    }

    if (loadOlderBtn) {
      loadOlderBtn.addEventListener('click', function () {
        const convId = loadOlderBtn.dataset.conversationId;
        const beforeId = loadOlderBtn.dataset.before;
        if (!convId || !beforeId) {
          return;
        }
        loadOlderBtn.disabled = true;
        fetch('/messages/' + convId + '/history/?before=' + beforeId, {
          credentials: 'same-origin',
          headers: { Accept: 'application/json' },
        })
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (!data.ok || !data.html) {
              loadOlderBtn.remove();
              return;
            }
            const list = document.getElementById('messages-thread-list');
            const scroll = document.getElementById('messages-thread-scroll');
            const prevHeight = scroll ? scroll.scrollHeight : 0;
            list.insertAdjacentHTML('afterbegin', data.html);
            if (data.has_more && data.oldest_id) {
              loadOlderBtn.dataset.before = data.oldest_id;
            } else {
              loadOlderBtn.remove();
            }
            if (scroll) {
              scroll.scrollTop = scroll.scrollHeight - prevHeight;
            }
          })
          .catch(function () {
            showToast('Could not load older messages');
          })
          .finally(function () {
            loadOlderBtn.disabled = false;
          });
      });
    }

    scrollThreadToBottom();

    if (activeConversationId) {
      markConversationRead(activeConversationId);
    }
  }

  function isTeamThreadOpen(conversationId) {
    if (!isInboxPage || !activeConversationId) {
      return false;
    }
    if (String(activeConversationId) !== String(conversationId)) {
      return false;
    }
    return activeConversationType === 'team';
  }

  function isTeamToastDismissed(messageId) {
    return sessionStorage.getItem(TEAM_TOAST_DISMISS_KEY) === String(messageId);
  }

  function dismissTeamToast(messageId) {
    sessionStorage.setItem(TEAM_TOAST_DISMISS_KEY, String(messageId));
  }

  function hideTeamSlide(slide) {
    if (!slide) {
      return;
    }
    slide.classList.remove('team-msg-slide--visible');
    clearTimeout(teamSlideHideTimer);
    teamSlideHideTimer = setTimeout(function () {
      slide.hidden = true;
    }, 400);
  }

  function revealTeamSlide(slide) {
    if (!slide) {
      return;
    }
    slide.hidden = false;
    requestAnimationFrame(function () {
      slide.classList.add('team-msg-slide--visible');
    });
    clearTimeout(teamSlideHideTimer);
    teamSlideHideTimer = setTimeout(function () {
      hideTeamSlide(slide);
    }, 12000);
  }

  function wireTeamSlide(slide) {
    if (slide.dataset.wired === 'true') {
      return;
    }
    slide.dataset.wired = 'true';
    const dismissBtn = slide.querySelector('.team-msg-slide-dismiss');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', function () {
        dismissTeamToast(slide.dataset.messageId);
        hideTeamSlide(slide);
      });
    }
    const viewLink = slide.querySelector('.team-msg-slide-link');
    if (viewLink) {
      viewLink.addEventListener('click', function () {
        dismissTeamToast(slide.dataset.messageId);
        hideTeamSlide(slide);
      });
    }
  }

  function showTeamSlideNotification(payload) {
    const messageId = payload.messageId;
    const conversationId = payload.conversationId;
    if (!messageId || !conversationId) {
      return;
    }
    if (String(payload.senderId || '') === String(currentUserId)) {
      return;
    }
    if (isTeamThreadOpen(conversationId)) {
      return;
    }
    if (isTeamToastDismissed(messageId)) {
      return;
    }

    let slide = document.getElementById('team-msg-slide');
    if (!slide) {
      slide = document.createElement('div');
      slide.id = 'team-msg-slide';
      slide.className = 'team-msg-slide';
      slide.hidden = true;
      slide.setAttribute('role', 'status');
      slide.setAttribute('aria-live', 'polite');
      document.body.appendChild(slide);
    }

    slide.dataset.messageId = messageId;
    slide.dataset.conversationId = conversationId;
    slide.innerHTML =
      '<div class="team-msg-slide-icon" aria-hidden="true">' +
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" ' +
      'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>' +
      '<circle cx="9" cy="7" r="4"/>' +
      '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>' +
      '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>' +
      '</svg></div>' +
      '<div class="team-msg-slide-body">' +
      '<p class="team-msg-slide-label">New team message</p>' +
      '<p class="team-msg-slide-text"><strong></strong><span></span></p>' +
      '</div>' +
      '<a href="/messages/' + conversationId + '/" class="team-msg-slide-link">View</a>' +
      '<button type="button" class="team-msg-slide-dismiss" aria-label="Dismiss">&times;</button>';

    const nameEl = slide.querySelector('.team-msg-slide-text strong');
    const previewEl = slide.querySelector('.team-msg-slide-text span');
    if (nameEl) {
      nameEl.textContent = payload.senderName || 'Teammate';
    }
    if (previewEl) {
      previewEl.textContent = payload.preview || '';
    }

    slide.dataset.wired = 'false';
    wireTeamSlide(slide);
    revealTeamSlide(slide);
  }

  function initTeamSlideNotification() {
    const slide = document.getElementById('team-msg-slide');
    if (!slide) {
      return;
    }
    const messageId = slide.dataset.messageId;
    const conversationId = slide.dataset.conversationId;
    if (isTeamToastDismissed(messageId) || isTeamThreadOpen(conversationId)) {
      slide.remove();
      return;
    }
    wireTeamSlide(slide);
    revealTeamSlide(slide);
  }

  /* ── Request notification permission once (non-blocking) ── */
  function maybeRequestNotificationPermission() {
    if (!('Notification' in window) || Notification.permission !== 'default') {
      return;
    }
    document.addEventListener('click', function requestOnce() {
      Notification.requestPermission().catch(function () {});
    }, { once: true, capture: true });
  }

  document.addEventListener('taskpin:board-update', function (e) {
    const data = e.detail;
    if (!data || data.type === 'connection.established') {
      return;
    }
    if (data.action === 'message.new') {
      handleMessageNew(data);
    }
  });

  if (isInboxPage) {
    initInboxPage();
  }
  initTeamSlideNotification();
  maybeRequestNotificationPermission();

  window.TaskPinMessages = {
    updateUnreadBadge: updateUnreadBadge,
    fetchUnreadCount: fetchUnreadCount,
  };
})();
