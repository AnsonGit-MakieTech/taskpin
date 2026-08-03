(function () {
  'use strict';

  function formatElapsed(totalSeconds) {
    var hours = Math.floor(totalSeconds / 3600);
    var minutes = Math.floor((totalSeconds % 3600) / 60);
    if (hours && minutes) return hours + 'h ' + minutes + 'm';
    if (hours) return hours + 'h';
    return minutes + 'm';
  }

  function lockForm(form, label) {
    if (!form || form.dataset.submitting === 'true') return false;
    form.dataset.submitting = 'true';
    form.querySelectorAll('button').forEach(function (el) {
      el.disabled = true;
    });
    var btn = form.querySelector('.dtr-btn');
    if (btn && label) btn.textContent = label;
    return true;
  }

  function initElapsedTimer() {
    var card = document.getElementById('dtr-clock-card');
    if (!card || !card.dataset.clockIn) return null;

    var elapsedEl = document.getElementById('dtr-elapsed');
    if (!elapsedEl) return null;

    var clockIn = new Date(card.dataset.clockIn);

    function tick() {
      var seconds = Math.max(0, Math.floor((Date.now() - clockIn.getTime()) / 1000));
      elapsedEl.textContent = formatElapsed(seconds);
    }

    tick();
    setInterval(tick, 30000);
    return { elapsedEl: elapsedEl, clockIn: clockIn, tick: tick };
  }

  function initClockOutConfirm(timer) {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.dtr-clock-out-btn');
      if (!btn) return;

      e.preventDefault();
      e.stopPropagation();

      var form = btn.closest('.dtr-clock-out-form');
      if (!form || form.dataset.submitting === 'true') return;

      var modal = document.getElementById('confirm-modal');
      if (modal && !modal.hidden) return;

      if (!window.TaskPinConfirm) return;

      if (timer && timer.tick) timer.tick();
      var elapsedText = timer && timer.elapsedEl ? timer.elapsedEl.textContent : '';
      var breakMinutes = form.querySelector('[name="break_minutes"]');
      var breakVal = breakMinutes ? parseInt(breakMinutes.value, 10) || 0 : 0;

      var message = 'End your shift now?';
      if (elapsedText) {
        message += ' You have been clocked in for ' + elapsedText + '.';
      }
      if (breakVal > 0) {
        message += ' ' + breakVal + ' minute' + (breakVal === 1 ? '' : 's') + ' break will be deducted.';
      }
      message += ' Your entry will be sent for approval.';

      window.TaskPinConfirm.open({
        title: 'Clock out?',
        message: message,
        okLabel: 'Yes, clock out',
        okClass: 'btn-confirm-ok',
        form: form,
      });
    });
  }

  function initClockInGuard() {
    var form = document.getElementById('dtr-clock-in-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      if (form.dataset.submitting === 'true') {
        e.preventDefault();
        return;
      }
      lockForm(form, 'Clocking in…');
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var timer = initElapsedTimer();
    initClockOutConfirm(timer);
    initClockInGuard();
  });
})();
