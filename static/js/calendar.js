(function () {
  document.querySelectorAll('.calendar-day--empty-click[data-create-url]').forEach(function (cell) {
    cell.addEventListener('click', function (event) {
      if (event.target.closest('.calendar-chip, .calendar-day-add, a')) {
        return;
      }
      window.location.href = cell.dataset.createUrl;
    });
  });
})();
