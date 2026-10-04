/* R.A.P MOULD — site interactions */
(function () {
  'use strict';

  /* Mobile nav */
  var burger = document.querySelector('.burger');
  var navLinks = document.querySelector('.nav-links');
  if (burger && navLinks) {
    burger.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.closest('a')) navLinks.classList.remove('open');
    });
  }

  /* FAQ accordion */
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var q = item.querySelector('.faq-q');
    if (!q) return;
    q.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.faq-item.open').forEach(function (o) {
        o.classList.remove('open');
        o.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        q.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* Contact / RFQ form */
  var form = document.getElementById('contact-form');
  if (!form) return;

  var statusBox = document.getElementById('form-status');
  var submitBtn = form.querySelector('[type="submit"]');

  function setInvalid(input, bad) {
    var field = input.closest('.field');
    if (field) field.classList.toggle('invalid', bad);
    return !bad;
  }

  function validEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var name = form.querySelector('#cf-name');
    var email = form.querySelector('#cf-email');
    var subject = form.querySelector('#cf-subject');
    var message = form.querySelector('#cf-message');

    var ok = true;
    ok = setInvalid(name, name.value.trim().length < 2) && ok;
    ok = setInvalid(email, !validEmail(email.value.trim())) && ok;
    ok = setInvalid(message, message.value.trim().length < 10) && ok;
    if (!ok) {
      showStatus('bad', 'Please complete the highlighted fields before sending.');
      return;
    }

    // Cloudflare Turnstile captcha token
    var captchaErr = document.getElementById('cf-captcha-err');
    var token = '';
    try {
      if (typeof turnstile !== 'undefined') token = turnstile.getResponse() || '';
    } catch (e) { token = ''; }
    if (!token) {
      if (captchaErr) captchaErr.style.display = 'block';
      showStatus('bad', 'Please complete the captcha verification.');
      return;
    }
    if (captchaErr) captchaErr.style.display = 'none';

    // Honeypot: silently "succeed" for bots
    var hp = form.querySelector('#cf-website');
    if (hp && hp.value) { showStatus('ok', 'Thank you. Your message has been received.'); form.reset(); return; }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending...';
    hideStatus();

    fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value.trim(),
        email: email.value.trim(),
        subject: subject ? subject.value.trim() : '',
        message: message.value.trim(),
        captcha: token
      })
    })
      .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, data: d }; }); })
      .then(function (r) {
        if (r.ok) {
          showStatus('ok', 'Thank you, your message has been sent. Our engineering team will reply within one business day.');
          form.reset();
          try { if (typeof turnstile !== 'undefined') turnstile.reset(); } catch (e) {}
        } else {
          showStatus('bad', (r.data && r.data.error) || 'Something went wrong while sending. Please try again or email us directly.');
        }
      })
      .catch(function () {
        showStatus('bad', 'Could not reach the server. Please check your connection or email us directly at adss_2012@yahoo.com.');
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Message';
      });
  });

  function showStatus(kind, text) {
    statusBox.textContent = text;
    statusBox.className = 'form-status show ' + kind;
    statusBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function hideStatus() {
    statusBox.className = 'form-status';
    statusBox.textContent = '';
  }

  /* Live-clear validation */
  form.querySelectorAll('input, textarea').forEach(function (el) {
    el.addEventListener('input', function () {
      var field = el.closest('.field');
      if (field) field.classList.remove('invalid');
    });
  });
})();
