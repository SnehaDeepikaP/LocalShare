$(document).ready(function () {

  /* ── Register Form Validation ─────────────────────────────────────────── */
  $('#registerForm').on('submit', function (e) {
    e.preventDefault();
    var valid = true;

    if (!$('#name').val().trim()) {
      $('#name').addClass('is-invalid'); valid = false;
    } else { $('#name').removeClass('is-invalid').addClass('is-valid'); }

    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test($('#email').val().trim())) {
      $('#email').addClass('is-invalid'); valid = false;
    } else { $('#email').removeClass('is-invalid').addClass('is-valid'); }

    var pwd = $('#password').val();
    if (pwd.length < 6 || !/[A-Z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      $('#password').addClass('is-invalid'); valid = false;
    } else { $('#password').removeClass('is-invalid').addClass('is-valid'); }

    if (!$('#location').val().trim()) {
      $('#location').addClass('is-invalid'); valid = false;
    } else { $('#location').removeClass('is-invalid').addClass('is-valid'); }

    if (valid) { this.submit(); }
  });

  /* ── Password Strength Meter ──────────────────────────────────────────── */
  $('#password').on('input', function () {
    var val = $(this).val(), score = 0;
    if (val.length >= 6)           score++;
    if (/[A-Z]/.test(val))         score++;
    if (/[0-9]/.test(val))         score++;
    if (/[^A-Za-z0-9]/.test(val))  score++;

    var colors = ['', 'bg-danger', 'bg-warning', 'bg-info', 'bg-success'];
    var labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    $('#strengthBar')
      .css('width', (score / 4 * 100) + '%')
      .removeClass('bg-danger bg-warning bg-info bg-success')
      .addClass(colors[score] || '');
    $('#strengthLabel').text(score ? labels[score] : '');
  });

  /* ── Login Form Validation ────────────────────────────────────────────── */
  $('#loginForm').on('submit', function (e) {
    e.preventDefault();
    var valid = true;
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test($('#loginEmail').val().trim())) {
      $('#loginEmail').addClass('is-invalid'); valid = false;
    } else { $('#loginEmail').removeClass('is-invalid').addClass('is-valid'); }

    if (!$('#loginPassword').val()) {
      $('#loginPassword').addClass('is-invalid'); valid = false;
    } else { $('#loginPassword').removeClass('is-invalid').addClass('is-valid'); }

    if (valid) { this.submit(); }
  });

  /* ── New Post Form Validation ─────────────────────────────────────────── */
  $('#postForm').on('submit', function (e) {
    e.preventDefault();
    var valid = true;

    if (!$('#category').val()) {
      $('#category').addClass('is-invalid'); valid = false;
    } else { $('#category').removeClass('is-invalid').addClass('is-valid'); }

    if (!$('#postTitle').val().trim()) {
      $('#postTitle').addClass('is-invalid'); valid = false;
    } else { $('#postTitle').removeClass('is-invalid').addClass('is-valid'); }

    if (!$('#postDesc').val().trim()) {
      $('#postDesc').addClass('is-invalid'); valid = false;
    } else { $('#postDesc').removeClass('is-invalid').addClass('is-valid'); }

    if (!$('#postLocation').val().trim()) {
      $('#postLocation').addClass('is-invalid'); valid = false;
    } else { $('#postLocation').removeClass('is-invalid').addClass('is-valid'); }

    if (valid) { this.submit(); }
  });

  /* ── Title Character Counter ──────────────────────────────────────────── */
  $('#postTitle').on('input', function () {
    $('#titleCount').text($(this).val().length);
  });

  /* ── Close Post Confirmation ──────────────────────────────────────────── */
  $('.close-btn').on('click', function (e) {
    if (!confirm('Mark "' + $(this).data('title') + '" as closed?')) {
      e.preventDefault();
    }
  });

  /* ── Auto-dismiss flash alerts after 4 seconds ───────────────────────── */
  setTimeout(function () { $('.alert').fadeOut('slow'); }, 4000);

  /* ── Clear is-invalid on change ──────────────────────────────────────── */
  $('input, select, textarea').on('input change', function () {
    $(this).removeClass('is-invalid');
  });

});
