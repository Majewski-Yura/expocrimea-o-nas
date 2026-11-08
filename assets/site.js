// Анимации: появление блоков при прокрутке, счётчики, шапка
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!('IntersectionObserver' in window) || reduce) return;
  document.documentElement.classList.add('js-anim');
  const groups = [
    ['.h2, .lead, .note, .partners-label', ''],
    ['.fact, .feat, .proj, .event, .news-card, .about-teaser__logos img, .step, .leader, .ceo, .person, .venue, .value, .review, .partner, .req, .dl a', ''],
    ['.jobs', 'reveal--zoom'],
    ['.chip, .footer__grid > div, .footer__bottom, .swipe-hint', '']
  ];
  groups.forEach(([sel, mod]) => document.querySelectorAll(sel).forEach(el => {
    el.classList.add('reveal'); if (mod) el.classList.add(mod);
    const i = [...el.parentElement.children].filter(c => c.matches(sel)).indexOf(el);
    el.style.setProperty('--d', (i % 8) * 0.07 + 's');
  }));
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('is-in'); io.unobserve(e.target);
    if (e.target.matches('.fact')) countUp(e.target.querySelector('b'));
  }), {threshold: 0.15, rootMargin: '0px 0px -40px 0px'});
  document.querySelectorAll('.reveal, .timeline').forEach(el => io.observe(el));

  // «Кто мы»: шторка, бейдж-счётчик, параллакс фото
  const about = document.querySelector('.about');
  if (about) {
    const badge = about.querySelector('.about__badge b'), img = about.querySelector('.about__frame img');
    const aio = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      about.classList.add('is-in'); aio.disconnect();
      const end = +badge.textContent, t0 = performance.now() + 1200;
      badge.textContent = '0';
      const tick = t => {
        const k = Math.max(0, Math.min((t - t0) / 1400, 1));
        badge.textContent = Math.round(end * (1 - Math.pow(1 - k, 3)));
        if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      setTimeout(() => img.classList.add('is-settled'), 2500);
    }, {threshold: 0.25});
    aio.observe(about);
    const par = () => {
      const r = about.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      const k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
      img.style.setProperty('--py', (k * -30).toFixed(1) + 'px');
    };
    addEventListener('scroll', par, {passive: true}); par();
  }

  function countUp(b) {
    const m = b.textContent.match(/^([\d\s\u00a0]+)(.*)$/);
    if (!m) return;
    const end = +m[1].replace(/\D/g, ''), tail = m[2], dur = 3200, step = 90;
    const fmt = n => n >= 1000 ? n.toLocaleString('ru-RU').replace(/\s/g, '\u00a0') : String(n);
    let t0 = performance.now(), last = 0;
    const tick = t => {
      const k = Math.min((t - t0) / dur, 1), e = 1 - Math.pow(1 - k, 3);
      if (t - last >= step || k === 1) { b.textContent = fmt(Math.round(end * e)) + tail; last = t; }
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  const header = document.querySelector('.header'), up = document.querySelector('.fab--up');
  const onScroll = () => {
    header.classList.toggle('is-scrolled', scrollY > 10);
    up.classList.toggle('is-visible', scrollY > 600);
  };
  addEventListener('scroll', onScroll, {passive: true}); onScroll();
})();

// Фильтр мероприятий по городу и мобильное меню
(() => {
  const chips = document.querySelectorAll('.filters--events .chip');
  chips.forEach(b => b.addEventListener('click', () => {
    chips.forEach(c => c.classList.toggle('is-on', c === b));
    document.querySelectorAll('.event').forEach(e => e.hidden = b.dataset.city !== 'all' && e.dataset.city !== b.dataset.city);
  }));
  const burger = document.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', () => document.body.classList.toggle('menu-open'));
    document.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', () => document.body.classList.remove('menu-open')));
  }
})();
