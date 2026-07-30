(function () {
  const note = document.getElementById('task-form-note');
  if (!note) {
    return;
  }

  const priorityRadios = document.querySelectorAll('input[name="priority"]');
  const dueInput = document.getElementById('id_due_date');
  const quickBtns = document.querySelectorAll('.task-form-due-quick-btn');

  function updateNotePriority() {
    note.classList.remove('task-form-note--normal', 'task-form-note--important', 'task-form-note--urgent');
    priorityRadios.forEach(function (radio) {
      if (radio.checked) {
        note.classList.add('task-form-note--' + radio.value);
      }
    });
  }

  function formatDatetimeLocal(date) {
    const pad = function (n) { return String(n).padStart(2, '0'); };
    return (
      date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate()) +
      'T' + pad(date.getHours()) + ':' + pad(date.getMinutes())
    );
  }

  function setDueDate(daysFromToday, hour, minute) {
    if (!dueInput) {
      return;
    }
    const date = new Date();
    date.setDate(date.getDate() + daysFromToday);
    date.setHours(hour, minute, 0, 0);
    dueInput.value = formatDatetimeLocal(date);
    dueInput.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function clearQuickActive() {
    quickBtns.forEach(function (btn) {
      btn.classList.remove('is-active');
    });
  }

  priorityRadios.forEach(function (radio) {
    radio.addEventListener('change', updateNotePriority);
  });
  updateNotePriority();

  quickBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const pick = btn.dataset.duePick;
      clearQuickActive();
      btn.classList.add('is-active');
      if (pick === 'today') {
        setDueDate(0, 17, 0);
      } else if (pick === 'tomorrow') {
        setDueDate(1, 17, 0);
      } else if (pick === 'next_week') {
        setDueDate(7, 17, 0);
      }
    });
  });

  if (dueInput) {
    dueInput.addEventListener('change', clearQuickActive);
    dueInput.addEventListener('input', clearQuickActive);
  }
})();
