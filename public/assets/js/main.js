(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');

  /* Sticky header shadow */
  var header = document.querySelector('.site-header');
  var onScroll = function () { header && header.classList.toggle('is-scrolled', window.scrollY > 8); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Mobile navigation */
  var toggle = document.querySelector('.nav-toggle');
  var setNav = function (open) {
    doc.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menü bezárása' : 'Menü megnyitása');
  };
  if (toggle) {
    toggle.addEventListener('click', function () { setNav(!doc.classList.contains('nav-open')); });
    window.matchMedia('(min-width: 1121px)').addEventListener('change', function (e) { if (e.matches) setNav(false); });
  }

  /* Dropdowns */
  var items = document.querySelectorAll('.nav-item.has-sub');
  var closeAll = function (except) {
    items.forEach(function (it) {
      if (it === except) return;
      it.classList.remove('is-open');
      it.querySelector('.nav-link').setAttribute('aria-expanded', 'false');
    });
  };
  items.forEach(function (item) {
    var btn = item.querySelector('.nav-link');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !item.classList.contains('is-open');
      closeAll(item);
      item.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.nav-item.has-sub')) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    closeAll();
    if (doc.classList.contains('nav-open')) { setNav(false); toggle.focus(); }
  });

  /* Product galleries */
  document.querySelectorAll('[data-gallery]').forEach(function (g) {
    var main = g.querySelector('.gallery__main img');
    var caption = g.querySelector('.gallery__caption');
    var thumbs = g.querySelectorAll('.gallery__thumb');
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () {
        main.src = t.dataset.src;
        main.srcset = t.dataset.srcset || '';
        main.alt = t.dataset.alt;
        if (caption) caption.textContent = t.dataset.alt;
        thumbs.forEach(function (o) { o.setAttribute('aria-current', String(o === t)); });
      });
    });
  });

  /* Reveal on scroll */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Quote form: preselect topic and show server-side errors */
  var form = document.getElementById('ajanlatkero-urlap');
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var topic = params.get('targy');
    var select = form.querySelector('#targy');
    if (topic && select && select.querySelector('option[value="' + topic + '"]')) select.value = topic;
    var err = params.get('hiba');
    var box = document.getElementById('urlap-hiba');
    if (err && box) {
      box.querySelector('span').textContent = err === 'kuldes'
        ? 'Az üzenetet most nem sikerült elküldeni. Kérjük, próbálja újra, vagy írjon közvetlenül az aed@emcrem.hu címre.'
        : 'Kérjük, adja meg a nevét, egy érvényes e-mail-címet, és fogadja el az adatkezelési tájékoztatót.';
      box.hidden = false;
    }

    /* Static hosting without PHP: open the visitor's mail client with the filled-in request */
    if (form.dataset.mailto) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (form.weboldal && form.weboldal.value) return;
        var val = function (name) { var f = form.elements[name]; return f && f.value.trim() ? f.value.trim() : '–'; };
        var topicText = select ? select.options[select.selectedIndex].text : '';
        var body = [
          'Téma: ' + topicText,
          'Név: ' + val('nev'),
          'E-mail: ' + val('email'),
          'Telefon: ' + val('telefon'),
          'Cég: ' + val('ceg'),
          'Létszám: ' + val('letszam'),
          '',
          val('uzenet')
        ].join('\r\n');
        window.location.href = 'mailto:' + form.dataset.mailto +
          '?subject=' + encodeURIComponent('Ajánlatkérés: ' + topicText + ' – ' + val('nev')) +
          '&body=' + encodeURIComponent(body);
      });
    }
  }

  /* Current year */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
