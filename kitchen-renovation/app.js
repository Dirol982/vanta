/* Vanta Surfaces — kitchen renovation landing */
(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Lead form endpoint. Set window.VANTA_FORM_ENDPOINT (e.g. a webhook URL) before this script to
     POST JSON; without it the form opens a pre-filled email to the office. */
  var ENDPOINT = window.VANTA_FORM_ENDPOINT || '';

  /* ---- Options: refresh / reface / replace ----
     Refresh figures come from the Bay Ridge project. Reface and Replace ranges are typical and
     must be confirmed by Vanta before launch (marked sample: true). */
  var OPTIONS = {
    refresh: {
      days: '0', daysLabel: 'days without a working kitchen',
      time: '3 calendar days',
      new: 'A new finish on every visible cabinet surface, including the island',
      stays: 'Cabinet boxes, countertops, appliances, plumbing',
      for: 'Solid cabinets with a tired or dated finish',
      note: 'Based on our Bay Ridge project: uppers, base cabinets, pantry and island refinished with interior film by one installer, no demolition.',
      cta: 'Get a Refresh estimate', caption: 'Two-tone cabinet wrap, Bay Ridge, Brooklyn'
    },
    reface: {
      days: '3–5', daysLabel: 'days without a working kitchen', sample: true,
      time: 'About 1–2 weeks once doors arrive',
      new: 'Doors, drawer fronts, hardware; optional countertop, backsplash and lighting',
      stays: 'Cabinet boxes, layout, plumbing and gas lines',
      for: 'A good layout that needs a new look and better surfaces',
      note: 'Typical range. Your written estimate gives exact dates for your kitchen and building.',
      cta: 'Get a Reface estimate', caption: 'Upper cabinets resurfaced, Gotham West, Manhattan'
    },
    replace: {
      days: '4–8', daysLabel: 'weeks on site, plus board approval and lead times', sample: true,
      time: 'Most of the build is planned before demolition starts',
      new: 'Layout, cabinets, countertops, plumbing, electrical, flooring and lighting',
      stays: 'Only what you choose to keep',
      for: 'Kitchens that need a new layout or are past repair',
      note: 'Typical range. Board review, permits and cabinet lead times usually take longer than the build itself.',
      cta: 'Get a full remodel estimate', caption: 'Full kitchen remodel'
    }
  };

  var buttons = Array.prototype.slice.call(document.querySelectorAll('.switch [data-option]'));
  var heroImgs = Array.prototype.slice.call(document.querySelectorAll('.hero-img'));
  var readout = document.querySelector('.readout');
  var caption = document.querySelector('[data-caption]');
  var select = document.getElementById('f-option');
  var current = 'refresh';
  var userChose = false;

  function showHero(key) {
    heroImgs.forEach(function (img) { img.classList.toggle('is-on', img.getAttribute('data-for') === key); });
    if (caption) caption.textContent = OPTIONS[key].caption;
  }

  function fill(key) {
    var o = OPTIONS[key];
    readout.querySelectorAll('[data-k]').forEach(function (el) {
      var k = el.getAttribute('data-k');
      if (o[k] != null) el.textContent = o[k];
    });
  }

  function choose(key, fromUser) {
    if (!OPTIONS[key]) return;
    current = key;
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-option') === key;
      b.setAttribute('aria-checked', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
    });
    showHero(key);
    if (select) select.value = key.charAt(0).toUpperCase() + key.slice(1);
    if (reduce) { fill(key); return; }
    readout.classList.add('is-swapping');
    setTimeout(function () { fill(key); readout.classList.remove('is-swapping'); }, 260);
    if (fromUser) userChose = true;
  }

  buttons.forEach(function (b, i) {
    b.addEventListener('click', function () { choose(b.getAttribute('data-option'), true); });
    b.addEventListener('keydown', function (e) {
      var dir = (e.key === 'ArrowRight' || e.key === 'ArrowDown') ? 1 : (e.key === 'ArrowLeft' || e.key === 'ArrowUp') ? -1 : 0;
      if (!dir) return;
      e.preventDefault();
      var next = buttons[(i + dir + buttons.length) % buttons.length];
      next.focus();
      choose(next.getAttribute('data-option'), true);
    });
  });
  buttons.forEach(function (b) { b.tabIndex = b.getAttribute('aria-checked') === 'true' ? 0 : -1; });

  /* Signature move: the hero slowly crossfades through the three options until the visitor picks one. */
  if (!reduce && heroImgs.length > 1) {
    var order = ['refresh', 'reface', 'replace'], idx = 0, timer = null;
    var tick = function () {
      if (userChose || document.hidden) return;
      idx = (idx + 1) % order.length;
      showHero(order[idx]);
    };
    var start = function () { if (!timer) timer = setInterval(tick, 6000); };
    var stop = function () { clearInterval(timer); timer = null; };
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
    window.addEventListener('load', function () {
      heroImgs.forEach(function (img) { img.loading = 'eager'; });
      start();
    });
    // Once the visitor reaches the options, the hero follows their choice instead of cycling.
    var opts = document.getElementById('options');
    if ('IntersectionObserver' in window && opts) {
      new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) { stop(); showHero(current); } });
      }, { threshold: 0.3 }).observe(opts);
    }
  }

  /* ---- Before / after ---- */
  var ba = document.querySelector('.ba');
  if (ba) {
    var range = ba.querySelector('.ba-range');
    var set = function (v) { ba.style.setProperty('--pos', v + '%'); };
    range.addEventListener('input', function () { set(range.value); });
  }

  /* ---- Entrances: heading, then text, then picture, staggered per section ---- */
  var reveals = document.querySelectorAll('.reveal');
  if (!reduce && 'IntersectionObserver' in window) {
    document.querySelectorAll('section').forEach(function (sec) {
      sec.querySelectorAll('.reveal').forEach(function (el, i) { el.style.setProperty('--d', Math.min(i * 80, 480) + 'ms'); });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
    setTimeout(function () { reveals.forEach(function (el) { el.classList.add('in'); }); }, 4000); // never leave content hidden
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---- Mobile sticky call-to-action after the hero ---- */
  var mc = document.querySelector('.mobile-cta');
  var hero = document.querySelector('.hero');
  var est = document.getElementById('estimate');
  if (mc && hero && 'IntersectionObserver' in window) {
    var heroIn = true, estIn = false, optIn = false;
    var upd = function () { mc.classList.toggle('show', !heroIn && !estIn && !optIn); };
    var optSec = document.getElementById('options');
    if (optSec) new IntersectionObserver(function (e) { optIn = e[0].isIntersecting; upd(); }).observe(optSec);
    new IntersectionObserver(function (e) { heroIn = e[0].isIntersecting; upd(); }).observe(hero);
    if (est) new IntersectionObserver(function (e) { estIn = e[0].isIntersecting; upd(); }).observe(est);
  }

  /* ---- Form ---- */
  var form = document.getElementById('estimate-form');
  if (form) {
    var status = form.querySelector('.form-status');
    var f = form.elements;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = f.name.value.trim(), phone = f.phone.value.trim();
      f.name.setAttribute('aria-invalid', name ? 'false' : 'true');
      f.phone.setAttribute('aria-invalid', phone ? 'false' : 'true');
      if (!name || !phone) { status.textContent = 'Please add your name and a phone number so we can call you back.'; (name ? f.phone : f.name).focus(); return; }
      var data = { name: name, phone: phone, email: f.email.value.trim(), zip: f.zip.value.trim(), option: f.option.value, message: f.message.value.trim(), page: location.href };
      if (ENDPOINT) {
        status.textContent = 'Sending…';
        fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); status.textContent = 'Thank you. We\'ll call you to schedule the walkthrough.'; })
          .catch(function () { status.textContent = 'This didn\'t send. Please call (646) 664-1696 or email alex@vantasurfaces.com.'; });
        return;
      }
      var body = 'Name: ' + data.name + '\nPhone: ' + data.phone + '\nEmail: ' + data.email + '\nZIP: ' + data.zip + '\nPlan: ' + data.option + '\n\n' + data.message;
      location.href = 'mailto:alex@vantasurfaces.com?subject=' + encodeURIComponent('Kitchen estimate request: ' + data.option) + '&body=' + encodeURIComponent(body);
      status.textContent = 'Your email app should open with the request filled in. If it doesn\'t, call (646) 664-1696.';
    });
  }
})();
