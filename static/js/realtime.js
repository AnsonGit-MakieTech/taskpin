/**
 * TaskPin — WebSocket connection; board pages sync via board-sync.js (no reload).
 */
(function () {
  if (document.body.dataset.userAuth !== 'true') {
    return;
  }

  let socket = null;
  let reconnectTimer = null;
  let reconnectDelay = 1000;
  let intentionallyClosing = false;
  const MAX_RECONNECT_DELAY = 30000;

  function wsUrl() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return wsProtocol + '//' + window.location.host + '/ws/board/';
  }

  function connect() {
    if (
      socket &&
      (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    socket = new WebSocket(wsUrl());

    socket.onopen = function () {
      console.info('[TaskPin] Realtime connected');
      reconnectDelay = 1000;
    };

    socket.onmessage = function (event) {
      try {
        const data = JSON.parse(event.data);
        console.info('[TaskPin] Board update:', data);
        document.dispatchEvent(new CustomEvent('taskpin:board-update', { detail: data }));
      } catch (err) {
        console.warn('[TaskPin] Invalid websocket message', err);
      }
    };

    socket.onclose = function (event) {
      if (intentionallyClosing) {
        return;
      }
      console.info(
        '[TaskPin] Realtime disconnected',
        '(code',
        event.code + (event.reason ? ', ' + event.reason : '') + ')'
      );
      scheduleReconnect();
    };

    socket.onerror = function () {
      console.warn('[TaskPin] Realtime connection error');
    };
  }

  function scheduleReconnect() {
    if (reconnectTimer) {
      return;
    }
    reconnectTimer = setTimeout(function () {
      reconnectTimer = null;
      console.info('[TaskPin] Reconnecting…');
      connect();
      reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
    }, reconnectDelay);
  }

  function ensureConnected() {
    if (
      intentionallyClosing ||
      (socket && socket.readyState === WebSocket.OPEN)
    ) {
      return;
    }
    if (socket && socket.readyState === WebSocket.CONNECTING) {
      return;
    }
    connect();
  }

  window.addEventListener('beforeunload', function () {
    intentionallyClosing = true;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close();
    }
  });

  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible') {
      ensureConnected();
    }
  });

  connect();
})();
