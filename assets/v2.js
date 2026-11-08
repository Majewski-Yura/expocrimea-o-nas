// Версия 2: общие анимации и поведение страниц (главная и далее)
const $ = (s, c = document) => c.querySelector(s), $$ = (s, c = document) => [...c.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

// Меню на мобильном
const header = $('.header'), burger = $('.burger');
if (burger) {
  burger.addEventListener('click', () => burger.setAttribute('aria-expanded', header.classList.toggle('is-open')));
  $$('.nav a').forEach(a => a.addEventListener('click', () => header.classList.remove('is-open')));
}

// Фильтры с бегущей плашкой: .chips[data-for="#grid"], кнопки data-f, карточки data-f
$$('.chips[data-for]').forEach(box => {
  const btns = $$('.chip', box), ind = $('.chips__ind', box), grid = $(box.dataset.for);
  const moveInd = () => { const on = $('.chip.is-on', box); if (!on) return; ind.style.width = on.offsetWidth + 'px'; ind.style.transform = `translateX(${on.offsetLeft}px)`; };
  btns.forEach(b => b.addEventListener('click', () => {
    btns.forEach(c => c.classList.toggle('is-on', c === b));
    moveInd();
    let i = 0;
    [...grid.children].forEach(p => {
      p.hidden = b.dataset.f !== 'all' && p.dataset.f !== b.dataset.f;
      p.classList.remove('pop', 'rv'); p.classList.add('in');
      if (!p.hidden && !reduce) { void p.offsetWidth; p.style.setProperty('--i', i++); p.classList.add('pop'); }
    });
  }));
  new ResizeObserver(moveInd).observe(box); addEventListener('load', moveInd); moveInd();
});

// Видео в шапке: звук и пауза для тех, кто просит меньше движения
const vid = $('.hero-v__video'), snd = $('.hero-v__snd');
if (vid) {
  if (reduce) vid.pause();
  if (snd) snd.addEventListener('click', () => {
    vid.muted = !vid.muted;
    if (!vid.muted) vid.play();
    snd.setAttribute('aria-pressed', !vid.muted);
    $('span', snd).textContent = vid.muted ? 'Включить звук' : 'Выключить звук';
  });
}

// Подписка: форма-заглушка до переноса на сайт
$$('.sub__f').forEach(f => f.addEventListener('submit', e => { e.preventDefault(); f.closest('.sub').classList.add('is-sent'); }));

// Отзывы: слайдер с автопрокруткой по полосе
const slides = $$('.slide'), revN = $('#rev-n'), bar = $('.rev__bar i');
let cur = 0;
function go(i) {
  slides[cur].classList.remove('on');
  cur = (i + slides.length) % slides.length;
  slides[cur].classList.add('on');
  revN.textContent = String(cur + 1).padStart(2, '0');
  if (!reduce) { bar.classList.remove('run'); void bar.offsetWidth; bar.classList.add('run'); }
}
if (slides.length) {
  $('#rev-prev').addEventListener('click', () => go(cur - 1));
  $('#rev-next').addEventListener('click', () => go(cur + 1));
  bar.addEventListener('animationend', () => go(cur + 1));
}

// Прокрутка: полоса прогресса, тень шапки, кнопка наверх, манифест по словам
const up = $('.fab--up'), prog = $('.progress'), manifest = $('.manifest__text');
let words = [];
function update() {
  const vh = innerHeight, docH = document.documentElement.scrollHeight - vh;
  if (prog) prog.style.setProperty('--sp', docH > 0 ? scrollY / docH : 0);
  if (header) header.classList.toggle('is-scrolled', scrollY > 10);
  if (up) up.classList.toggle('is-visible', scrollY > 600);
  if (reduce || !words.length) return;
  const mr = manifest.getBoundingClientRect();
  const k = clamp((vh * 0.85 - mr.top) / (mr.height + vh * 0.25));
  const n = Math.round(k * words.length);
  words.forEach((w, i) => w.classList.toggle('on', i < n));
}
let ticking = false;
addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; update(); }); } }, {passive: true});
addEventListener('resize', update);

if (!reduce) {
  document.documentElement.classList.add('js-anim');

  if (manifest) (function split(node) {
    [...node.childNodes].forEach(n => {
      if (n.nodeType === 1) return split(n);
      if (n.nodeType !== 3) return;
      const frag = document.createDocumentFragment();
      n.textContent.split(/([ \n\t]+)/).forEach(p => {
        if (!p) return;
        if (/^[ \n\t]+$/.test(p)) { frag.append(' '); return; }
        const s = document.createElement('span'); s.className = 'w'; s.textContent = p;
        frag.append(s); words.push(s);
      });
      n.replaceWith(frag);
    });
  })(manifest);

  slides.forEach(sl => {
    const q = $('blockquote', sl);
    q.innerHTML = q.textContent.split(/[ \n\t]+/).filter(Boolean).map((w, i) => `<span class="w2" style="--i:${i}">${w}</span>`).join(' ');
  });
  if (bar) bar.classList.add('run');

  // Одометры
  $$('.odo').forEach(b => {
    const txt = b.textContent, nd = txt.replace(/\D/g, '').length;
    let k = 0;
    b.setAttribute('aria-label', txt); b.textContent = '';
    [...txt].forEach(ch => {
      if (/\d/.test(ch)) {
        const o = document.createElement('span'), c = document.createElement('span');
        o.className = 'od'; c.className = 'od__c';
        c.innerHTML = Array.from({length: 20}, (_, i) => `<i>${i % 10}</i>`).join('');
        c.dataset.t = 10 + +ch;
        c.style.transitionDelay = ((nd - 1 - k++) * 0.09) + 's';
        o.append(c); o.setAttribute('aria-hidden', 'true'); b.append(o);
      } else {
        const s = document.createElement('span'); s.className = 'od-s'; s.textContent = ch === ' ' ? ' ' : ch; s.setAttribute('aria-hidden', 'true'); b.append(s);
      }
    });
  });

  // Появление при прокрутке; заголовки со шторкой отслеживаем по родителю
  $$('.rv').forEach(el => {
    if (el.style.getPropertyValue('--d')) return;
    const sib = [...el.parentElement.children].filter(c => c.classList.contains('rv'));
    el.style.setProperty('--d', (sib.indexOf(el) % 6) * 0.08 + 's');
  });
  const watch = new Map();
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    (watch.get(e.target) || []).forEach(el => {
      el.classList.add('in');
      $$('.od__c', el).forEach(c => c.style.transform = `translateY(${-c.dataset.t * 5}%)`);
    });
  }), {threshold: 0.12, rootMargin: '0px 0px -40px 0px'});
  $$('.rv').forEach(el => {
    const t = el.classList.contains('rv--clip') ? el.parentElement : el;
    if (!watch.has(t)) { watch.set(t, []); io.observe(t); }
    watch.get(t).push(el);
  });

  // Бегущие строки логотипов
  $$('.mq').forEach(mq => {
    const set = [...mq.children];
    while (mq.scrollWidth < innerWidth * 1.3) set.forEach(n => mq.append(n.cloneNode(true)));
    [...mq.children].forEach(n => { const c = n.cloneNode(true); c.setAttribute('aria-hidden', 'true'); mq.append(c); });
  });

  // Магнитная кнопка
  const wrap = $('.magnet-wrap');
  if (fine && wrap) {
    const sec = wrap.closest('section'), mg = $('.magnet', wrap), mgs = $('.magnet span', wrap);
    sec.addEventListener('mousemove', e => {
      const r = wrap.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
      if (Math.hypot(dx, dy) < 300) { mg.style.transform = `translate(${dx * .3}px,${dy * .3}px)`; mgs.style.transform = `translate(${dx * .12}px,${dy * .12}px)`; }
      else { mg.style.transform = mgs.style.transform = ''; }
    });
    sec.addEventListener('mouseleave', () => { mg.style.transform = mgs.style.transform = ''; });
  }
}
update();
