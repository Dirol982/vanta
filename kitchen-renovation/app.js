/* Vanta Surfaces — kitchen renovation landing.
   Functional parts (scope builder, before/after, form) work in every mode;
   decorative motion runs only without "reduce motion" (class .m on <html>). */
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* Lead endpoint: define window.VANTA_FORM_ENDPOINT before this script to POST JSON.
     Without it the form opens a pre-filled email to the office. */
  var ENDPOINT = window.VANTA_FORM_ENDPOINT || '';

  /* ── Scope builder ──
     lvl 1 = Refresh, 2 = Reface, 3 = Replace, 0 = building logistics (no effect on path).
     Refresh figure is from the Bay Ridge job; Reface / Replace are typical ranges to be confirmed. */
  var PATHS = { 1: { name: 'Refresh', days: '0 days' }, 2: { name: 'Reface', days: '3–5 days' }, 3: { name: 'Replace', days: '4–8 wks' } };
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var list = document.querySelector('[data-list]');
  var pathOut = document.querySelector('[data-path]');
  var daysOut = document.querySelector('[data-days]');
  var total = document.querySelector('.check__total');
  var pathLine = document.querySelector('.check__path');
  var scopeField = document.querySelector('[data-scope-field]');
  var lastPath = '';

  function selected() { return chips.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }); }
  function currentPath() {
    var lvl = selected().reduce(function (m, c) { return Math.max(m, +c.dataset.lvl); }, 0);
    return PATHS[lvl] || null;
  }
  function renderCheck() {
    var sel = selected();
    var p = currentPath();
    list.innerHTML = sel.length ? sel.map(function (c) {
      var tag = { 0: 'Building', 1: 'Refresh', 2: 'Reface', 3: 'Replace' }[c.dataset.lvl];
      return '<li>' + c.textContent.trim() + '<span>' + tag + '</span></li>';
    }).join('') : '<li class="check__empty">Nothing selected yet</li>';
    pathOut.textContent = p ? p.name : (sel.length ? 'Not sure yet' : '—');
    daysOut.textContent = p ? p.days : '—';
    var name = p ? p.name : '';
    if (name !== lastPath && pathLine) { pathLine.classList.remove('ping'); void pathLine.offsetWidth; pathLine.classList.add('ping'); }
    lastPath = name;
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      renderCheck();
    });
  });
  var reset = document.querySelector('[data-reset]');
  if (reset) reset.addEventListener('click', function () { chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); }); renderCheck(); });

  // "Send this scope" carries the selection into the form
  var send = document.querySelector('[data-send]');
  if (send) send.addEventListener('click', function () {
    var sel = selected().map(function (c) { return c.textContent.trim(); });
    if (sel.length && scopeField) scopeField.value = 'Scope: ' + sel.join(', ') + '.' + (scopeField.value ? '\n' + scopeField.value.replace(/^Scope:.*\n?/, '') : '');
    var p = currentPath();
    if (p) { var r = document.querySelector('.booking__paths input[value="' + p.name + '"]'); if (r) r.checked = true; }
  });

  /* ── Before / after ── */
  var ba = document.querySelector('.ba');
  if (ba) {
    var range = ba.querySelector('.ba__range');
    range.addEventListener('input', function () { ba.style.setProperty('--pos', range.value + '%'); });
  }

  /* ── Form ── */
  var form = document.getElementById('estimate-form');
  if (form) {
    var f = form.elements, status = form.querySelector('.form-status');
    var sms = form.querySelector('[data-sms]');
    var smsBody = function () {
      var opt = form.querySelector('input[name="option"]:checked');
      return 'Hi Vanta, I need a kitchen estimate (' + (opt ? opt.value : 'not sure') + ').' + (f.message.value ? ' ' + f.message.value.trim() : '');
    };
    if (sms) sms.addEventListener('click', function () { sms.href = 'sms:+16466641696?&body=' + encodeURIComponent(smsBody()); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = f.name.value.trim(), phone = f.phone.value.trim();
      f.name.setAttribute('aria-invalid', name ? 'false' : 'true');
      f.phone.setAttribute('aria-invalid', phone ? 'false' : 'true');
      if (!name || !phone) { status.textContent = 'Add your name and phone so we can call you back.'; (name ? f.phone : f.name).focus(); return; }
      var opt = form.querySelector('input[name="option"]:checked');
      var data = { name: name, phone: phone, zip: f.zip.value.trim(), option: opt ? opt.value : '', message: f.message.value.trim(), page: location.href };
      if (ENDPOINT) {
        status.textContent = 'Sending…';
        fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); status.textContent = 'Thank you. We\'ll call you to schedule the walkthrough.'; })
          .catch(function () { status.textContent = 'This didn\'t send. Call (646) 664-1696 or email alex@vantasurfaces.com.'; });
        return;
      }
      var body = 'Name: ' + data.name + '\nPhone: ' + data.phone + '\nZIP: ' + data.zip + '\nPath: ' + data.option + '\n\n' + data.message;
      location.href = 'mailto:alex@vantasurfaces.com?subject=' + encodeURIComponent('Kitchen estimate: ' + data.option) + '&body=' + encodeURIComponent(body);
      status.textContent = 'Your email app should open with the request filled in. Or call (646) 664-1696.';
    });
  }

  /* ── Mobile sticky call-to-action ── */
  var mc = document.querySelector('.mobile-cta'), hero = document.querySelector('.hero'), book = document.getElementById('book');
  if (mc && hero && 'IntersectionObserver' in window) {
    var heroIn = true, bookIn = false;
    var upd = function () { mc.classList.toggle('show', !heroIn && !bookIn); };
    new IntersectionObserver(function (e) { heroIn = e[0].isIntersecting; upd(); }).observe(hero);
    if (book) new IntersectionObserver(function (e) { bookIn = e[0].isIntersecting; upd(); }).observe(book);
  }

  if (reduce) return;
  root.classList.add('m');

  /* ── Letters of the big word rise one by one ── */
  var l1 = document.querySelector('.mega__l1');
  if (l1) {
    l1.setAttribute('aria-hidden', 'true');
    l1.innerHTML = l1.textContent.split('').map(function (c, i) {
      return '<span class="ch" style="--i:' + i + '">' + (c === ' ' ? '&nbsp;' : c) + '</span>';
    }).join('');
  }

  /* ── Scroll progress bar ── */
  var bar = document.createElement('div');
  bar.className = 'progress';
  bar.setAttribute('aria-hidden', 'true');
  bar.innerHTML = '<span></span>';
  document.body.prepend(bar);

  /* ── Reveal on scroll, staggered inside each group ── */
  var targets = '.sec__head > *, .bento--three > .tile, .calc > *, .visit > *, .steps li, .work > *, .work__side > *, .faq > *, .book__head > *, .booking, .book__call, .note';
  var groups = new Map();
  document.querySelectorAll(targets).forEach(function (el) {
    var p = el.parentElement, n = groups.get(p) || 0;
    groups.set(p, n + 1);
    el.setAttribute('data-in', '');
    el.style.setProperty('--d', Math.min(n, 8));
  });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  document.querySelectorAll('[data-in]').forEach(function (el) { io.observe(el); });

  /* ── Ticker speeds up with scroll velocity; progress; fallback reveal after anchor jumps ── */
  var track = document.querySelector('.ticker__track'), tickerAnim = null;
  if (track && track.animate) {
    track.innerHTML += track.innerHTML;
    tickerAnim = track.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(-50%)' }], { duration: 38000, iterations: Infinity });
  }
  var lastY = scrollY, lastT = performance.now(), boost = 1, ticking = false;
  var frame = function () {
    ticking = false;
    var max = root.scrollHeight - innerHeight;
    bar.style.setProperty('--p', max > 0 ? (scrollY / max).toFixed(4) : 0);
    document.querySelectorAll('[data-in]:not(.in)').forEach(function (el) {
      if (el.getBoundingClientRect().top < innerHeight * 0.92) { el.classList.add('in'); io.unobserve(el); }
    });
  };
  addEventListener('scroll', function () {
    var t = performance.now(), dy = Math.abs(scrollY - lastY) / Math.max(16, t - lastT);
    lastY = scrollY; lastT = t;
    boost = Math.min(6, 1 + dy * 4);
    if (!ticking) { ticking = true; requestAnimationFrame(frame); }
  }, { passive: true });
  if (tickerAnim) {
    (function decay() {
      tickerAnim.playbackRate += (boost - tickerAnim.playbackRate) * 0.12;
      boost += (1 - boost) * 0.06;
      requestAnimationFrame(decay);
    })();
  }
  frame();

  /* ── Spotlight and magnetic buttons (precise pointers only) ── */
  if (fine) {
    document.addEventListener('pointermove', function (e) {
      var t = e.target.closest && e.target.closest('.tile');
      if (!t) return;
      var r = t.getBoundingClientRect();
      t.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      t.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
    document.querySelectorAll('.tile--cta, .top .btn, [data-send], .booking .btn').forEach(function (b) {
      b.classList.add('magnet');
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) / r.width, y = (e.clientY - r.top - r.height / 2) / r.height;
        b.style.transform = 'translate(' + (x * 8).toFixed(1) + 'px,' + (y * 6).toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }

  /* ── A picked scope item flies into the work order ── */
  var check = document.querySelector('.check');
  document.querySelector('.calc__panel').addEventListener('click', function (e) {
    var c = e.target.closest('.chip');
    if (!c || c.getAttribute('aria-pressed') === 'true' || !check) return; // runs before the toggle (capture)
    var tr = (total || check).getBoundingClientRect();
    if (!tr.width || tr.top > innerHeight || tr.bottom < 0) return;
    var cr = c.getBoundingClientRect();
    var fl = document.createElement('span');
    fl.className = 'fly';
    fl.textContent = '+ ' + c.textContent.trim();
    fl.style.left = cr.left + 'px';
    fl.style.top = cr.top + 'px';
    document.body.append(fl);
    var dx = tr.left + 10 - cr.left, dy = tr.top - cr.top;
    fl.animate([
      { transform: 'translate(0,0) scale(1)', opacity: 1 },
      { transform: 'translate(' + dx * 0.55 + 'px,' + (dy * 0.55 - 60) + 'px) scale(1.04)', opacity: 1, offset: 0.55 },
      { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(.6)', opacity: 0 }
    ], { duration: 720, easing: 'cubic-bezier(.4,0,.2,1)' }).onfinish = function () {
      fl.remove();
      if (total) { total.classList.remove('ping'); void total.offsetWidth; total.classList.add('ping'); }
    };
  }, true);
})();
