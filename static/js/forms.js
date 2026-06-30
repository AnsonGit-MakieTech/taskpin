(function () {
  const stripe = document.getElementById('priority-stripe');
  if (!stripe) return;

  const radios = document.querySelectorAll('input[name="priority"]');

  function updateStripe() {
    stripe.className = 'form-card-top';
    radios.forEach(function (r) {
      if (r.checked) stripe.classList.add('priority-' + r.value);
    });
  }

  radios.forEach(function (r) {
    r.addEventListener('change', updateStripe);
  });
  updateStripe();
})();
