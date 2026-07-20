/**
 * Task form — multi-file attachments (upload before save).
 */
(function () {
  const form = document.getElementById('task-form');
  if (!form) {
    return;
  }

  const fileInput = document.getElementById('task-file-input');
  const attachBtn = document.getElementById('task-attach-btn');
  const queue = document.getElementById('task-attach-queue');
  const taskId = form.dataset.taskId || '';
  const pending = [];
  const removedExisting = new Set();

  function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
  }

  function renderQueue() {
    if (!queue) {
      return;
    }
    queue.innerHTML = '';

    document.querySelectorAll('.task-existing-attach').forEach(function (row) {
      const id = row.dataset.attachmentId;
      if (removedExisting.has(id)) {
        row.classList.add('task-existing-attach--removed');
      } else {
        row.classList.remove('task-existing-attach--removed');
      }
    });

    pending.forEach(function (item, index) {
      const chip = document.createElement('div');
      chip.className = 'task-attach-chip' + (item.uploading ? ' task-attach-chip--uploading' : '');
      chip.innerHTML =
        '<span class="task-attach-chip-name">' + (item.uploading ? 'Uploading…' : item.name) + '</span>' +
        (item.uploading ? '' : '<button type="button" class="task-attach-chip-remove" aria-label="Remove">&times;</button>');
      if (!item.uploading) {
        chip.querySelector('.task-attach-chip-remove').addEventListener('click', function () {
          pending.splice(index, 1);
          renderHiddenInputs();
          renderQueue();
        });
      }
      queue.appendChild(chip);
    });

    queue.hidden = pending.length === 0 &&
      !document.querySelector('.task-existing-attach:not(.task-existing-attach--removed)');
  }

  function renderHiddenInputs() {
    form.querySelectorAll('.task-attachment-id-input, .task-remove-attachment-input').forEach(function (el) {
      el.remove();
    });

    pending.forEach(function (item) {
      if (!item.id || item.uploading) {
        return;
      }
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'attachment_ids';
      input.value = String(item.id);
      input.className = 'task-attachment-id-input';
      form.appendChild(input);
    });

    removedExisting.forEach(function (id) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'remove_attachment_ids';
      input.value = id;
      input.className = 'task-remove-attachment-input';
      form.appendChild(input);
    });
  }

  function uploadFiles(fileList) {
    if (!fileList || !fileList.length) {
      return;
    }

    const placeholders = [];
    for (let i = 0; i < fileList.length; i++) {
      placeholders.push({ uploading: true, name: fileList[i].name });
    }
    pending.push.apply(pending, placeholders);
    renderQueue();

    const payload = new FormData();
    if (taskId) {
      payload.append('task_id', taskId);
    }
    for (let i = 0; i < fileList.length; i++) {
      payload.append('files', fileList[i]);
    }

    fetch('/task/upload/', {
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
        pending.splice(pending.length - placeholders.length, placeholders.length);
        if (!data.ok) {
          alert(data.error || 'Upload failed.');
          renderQueue();
          return;
        }
        (data.attachments || []).forEach(function (item) {
          pending.push({
            id: item.id,
            name: item.name,
            uploading: false,
          });
        });
        renderHiddenInputs();
        renderQueue();
      })
      .catch(function () {
        pending.splice(pending.length - placeholders.length, placeholders.length);
        alert('Upload failed.');
        renderQueue();
      });
  }

  if (attachBtn && fileInput) {
    attachBtn.addEventListener('click', function () {
      fileInput.click();
    });
    fileInput.addEventListener('change', function () {
      uploadFiles(fileInput.files);
      fileInput.value = '';
    });
  }

  document.querySelectorAll('.task-existing-attach-remove').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const row = btn.closest('.task-existing-attach');
      if (!row) {
        return;
      }
      removedExisting.add(row.dataset.attachmentId);
      renderHiddenInputs();
      renderQueue();
    });
  });

  renderHiddenInputs();
  renderQueue();
})();
