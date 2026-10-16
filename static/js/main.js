/**
 * LocalShare Client-Side Enhancements & Validation
 */
$(document).ready(function () {

  /* ── Register Form Validation ─────────────────────────────────────────── */
  $('#registerForm').on('submit', function (e) {
    var valid = true;
    var name = $('#name').val().trim();
    var email = $('#email').val().trim();
    var pwd = $('#password').val();
    var loc = $('#location').val().trim();
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!name || name.length < 2) {
      $('#name').addClass('is-invalid'); valid = false;
    } else {
      $('#name').removeClass('is-invalid').addClass('is-valid');
    }

    if (!email || !emailRegex.test(email)) {
      $('#email').addClass('is-invalid'); valid = false;
    } else {
      $('#email').removeClass('is-invalid').addClass('is-valid');
    }

    if (pwd.length < 6 || !/[A-Z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      $('#password').addClass('is-invalid'); valid = false;
    } else {
      $('#password').removeClass('is-invalid').addClass('is-valid');
    }

    if (!loc || loc.length < 2) {
      $('#location').addClass('is-invalid'); valid = false;
    } else {
      $('#location').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) {
      e.preventDefault();
      // Focus first invalid field
      $('.is-invalid').first().focus();
    }
  });

  /* ── Password Strength Meter ──────────────────────────────────────────── */
  $('#password').on('input', function () {
    var val = $(this).val();
    var score = 0;
    if (val.length >= 6)           score++;
    if (/[A-Z]/.test(val))         score++;
    if (/[0-9]/.test(val))         score++;
    if (/[^A-Za-z0-9]/.test(val))  score++;

    var colors = ['', 'bg-danger', 'bg-warning', 'bg-info', 'bg-success'];
    var labels = ['', 'Weak: Add capital & numbers', 'Fair', 'Good', 'Strong'];

    $('#strengthBar')
      .css('width', (score / 4 * 100) + '%')
      .removeClass('bg-danger bg-warning bg-info bg-success')
      .addClass(colors[score] || '');
    $('#strengthLabel').text(score ? labels[score] : '');
  });

  /* ── Login Form Validation ────────────────────────────────────────────── */
  $('#loginForm').on('submit', function (e) {
    var valid = true;
    var email = $('#loginEmail').val().trim();
    var pwd = $('#loginPassword').val();
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email || !emailRegex.test(email)) {
      $('#loginEmail').addClass('is-invalid'); valid = false;
    } else {
      $('#loginEmail').removeClass('is-invalid').addClass('is-valid');
    }

    if (!pwd) {
      $('#loginPassword').addClass('is-invalid'); valid = false;
    } else {
      $('#loginPassword').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) {
      e.preventDefault();
      $('.is-invalid').first().focus();
    }
  });

  /* ── New Post Form Validation ─────────────────────────────────────────── */
  $('#postForm').on('submit', function (e) {
    var valid = true;

    if (!$('#category').val()) {
      $('#category').addClass('is-invalid'); valid = false;
    } else {
      $('#category').removeClass('is-invalid').addClass('is-valid');
    }

    var title = $('#postTitle').val().trim();
    if (!title || title.length < 4) {
      $('#postTitle').addClass('is-invalid'); valid = false;
    } else {
      $('#postTitle').removeClass('is-invalid').addClass('is-valid');
    }

    var desc = $('#postDesc').val().trim();
    if (!desc || desc.length < 10) {
      $('#postDesc').addClass('is-invalid'); valid = false;
    } else {
      $('#postDesc').removeClass('is-invalid').addClass('is-valid');
    }

    var loc = $('#postLocation').val().trim();
    if (!loc || loc.length < 2) {
      $('#postLocation').addClass('is-invalid'); valid = false;
    } else {
      $('#postLocation').removeClass('is-invalid').addClass('is-valid');
    }

    if (!valid) {
      e.preventDefault();
      $('.is-invalid').first().focus();
    }
  });

  /* ── Title Character Counter ──────────────────────────────────────────── */
  $('#postTitle').on('input', function () {
    $('#titleCount').text($(this).val().length);
  });

  /* ── Remove invalid class on user edit ────────────────────────────────── */
  $('input, select, textarea').on('input change', function () {
    $(this).removeClass('is-invalid');
  });

});
