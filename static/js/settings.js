/**
 * Settings page — live profile photo preview before save.
 */
(function () {
  const fileInput = document.getElementById('id_avatar_image');
  if (!fileInput) {
    return;
  }

  const previewWraps = document.querySelectorAll('.js-avatar-preview');
  const removeCheckbox = document.getElementById('id_remove_avatar');

  function storeInitialState() {
    previewWraps.forEach(function (wrap) {
      if (!wrap.dataset.initialHtml) {
        wrap.dataset.initialHtml = wrap.innerHTML;
      }
    });
  }

  function applyPhotoPreview(dataUrl) {
    previewWraps.forEach(function (wrap) {
      const avatar = wrap.querySelector('.avatar');
      if (!avatar) {
        return;
      }
      avatar.classList.add('avatar--photo');
      avatar.removeAttribute('style');
      avatar.innerHTML = '<img src="' + dataUrl + '" alt="" class="avatar-img">';
    });
    if (removeCheckbox) {
      removeCheckbox.checked = false;
    }
  }

  function restoreInitials() {
    previewWraps.forEach(function (wrap) {
      if (wrap.dataset.initialHtml) {
        wrap.innerHTML = wrap.dataset.initialHtml;
      }
    });
  }

  storeInitialState();

  fileInput.addEventListener('change', function () {
    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      return;
    }
    if (!file.type.match(/^image\/(jpeg|png|webp)$/)) {
      return;
    }
    const reader = new FileReader();
    reader.onload = function (e) {
      applyPhotoPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  });

  if (removeCheckbox) {
    removeCheckbox.addEventListener('change', function () {
      if (removeCheckbox.checked) {
        restoreInitials();
        fileInput.value = '';
      }
    });
  }
})();
