// Small accessibility helpers for skip link and form message focus
document.addEventListener('DOMContentLoaded', function () {
  // When skip link is used, focus the main content
  var skipLink = document.querySelector('.skip-link');
  if (skipLink) {
    skipLink.addEventListener('click', function (e) {
      var main = document.getElementById('main-content');
      if (main) {
        main.setAttribute('tabindex', '-1');
        main.focus();
      }
    });
  }

  // If there's a form message, focus it for screen reader users
  var msg = document.getElementById('form-message');
  if (msg) {
    msg.setAttribute('tabindex', '-1');
    msg.focus();
  }
});
