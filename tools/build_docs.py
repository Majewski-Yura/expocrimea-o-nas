"""Собирает страницу dokumenty/index.html — документы компании, документы мероприятий и схемы.

Данные:
- документы мероприятий — поле docs в data/events/<slug>.json (разбор старых страниц);
- схемы проезда и залов — старые страницы site-source/docs/*.html (картинки на expocrimea.com);
- документы компании (карточка, презентация, договор) файлами пока не переданы — кнопка «Запросить» пишет письмо.
Запуск из корня проекта: python3 -I tools/build_docs.py, затем typograf.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ALL, ROOT, esc, shared_parts  # noqa: E402

U = 'https://expocrimea.com/wp-content/uploads/'
MAIL = 'info@expocrimea.com'

COMPANY = [
    ('Карточка предприятия', 'Реквизиты ЭКСПОКРЫМ для договоров и счетов'),
    ('Презентация компании', 'О компании, проектах и форматах участия'),
    ('Типовой договор участника', 'Договор на участие в выставке'),
]

ROUTES = [
    ('Экс-терминал «B» аэропорта «Симферополь»', 'Выставки в Симферополе', [], [U + '2022/04/shema-proezda-k-terminalu-v.jpg']),
    ('ГК «Ялта-Интурист», хоздвор', 'Выставки в Ялте', [
        'Жителям Ялты и прибывающим на автовокзал — автобус № 29А (точную схему маршрута на дату приезда уточните на автовокзале).',
        'На личном транспорте по шоссе Симферополь — Ялта: после моста в пгт Массандра поверните направо на шоссе Туристов.',
    ], [U + '2021/09/1-2-1.jpg', U + '2021/09/2-2.jpg']),
]

HALLS = [
    ('Терминал «B»', 'Аэропорт «Симферополь»', U + '2022/04/aeroport.jpg'),
    ('«Хрустальный»', 'ГК «Ялта-Интурист»', U + '2021/09/hrustalnyj.jpg'),
    ('«Санта-Барбара»', 'ГК «Ялта-Интурист»', U + '2021/09/santa-barbara.jpg'),
]

ICONS = '''  <symbol id="i-book" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14zM4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></symbol>
  <symbol id="i-cal" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></symbol>
  <symbol id="i-mic" viewBox="0 0 24 24"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5M8 22h8"/></symbol>
  <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></symbol>
'''


def doc_icon(name):
    n = name.lower()
    if 'каталог' in n:
        return 'i-book'
    if 'программ' in n:
        return 'i-cal'
    if 'сми' in n:
        return 'i-mic'
    if 'безопасн' in n:
        return 'i-shield'
    return 'i-doc'


def doc_kind(url):
    return 'PDF' if url.lower().endswith('.pdf') else 'Форма' if 'forms.yandex' in url else 'Страница'


def event_docs():
    out = []
    for name, slug, *_ in ALL:
        if not slug:
            continue
        f = ROOT / 'data' / 'events' / f'{slug}.json'
        if not f.exists():
            continue
        docs = json.loads(f.read_text(encoding='utf-8')).get('docs', [])
        if not docs:
            continue
        page = (ROOT / 'events' / f'{slug}.html').read_text(encoding='utf-8')
        m = re.search(r'<body[^>]*style="--ev:([^";]+)', page)
        clean = []
        for n, u in docs:
            u = u.strip()
            if u.startswith('/'):
                u = 'https://expocrimea.com' + u
            clean.append((n.strip(), u))
        out.append((name, slug, m.group(1) if m else 'var(--red)', clean))
    return out


def build():
    company = '\n'.join(f'''        <a class="dcard rv" href="mailto:{MAIL}?subject={quote('Запрос документа: ' + n)}">
          <span class="dcard__ic"><svg><use href="#i-doc"/></svg></span>
          <span class="dcard__t">{n}</span>
          <span class="dcard__d">{d}</span>
          <span class="dcard__go">Запросить по почте<svg><use href="#i-arrow"/></svg></span>
        </a>''' for n, d in COMPANY)

    evs = []
    for name, slug, color, docs in event_docs():
        links = '\n'.join(f'''            <a class="dl" href="{esc(u)}" target="_blank" rel="noopener"><span class="dl__ic"><svg><use href="#{doc_icon(n)}"/></svg></span><span class="dl__t">{esc(n)}</span><small>{doc_kind(u)}</small><span class="dl__go"><svg><use href="#i-arrow"/></svg></span></a>''' for n, u in docs)
        evs.append(f'''        <div class="dev rv" style="--ev:{color}">
          <a class="dev__h" href="../events/{slug}.html"><i></i>{esc(name)}</a>
          <div class="dev__l">
{links}
          </div>
        </div>''')

    routes = []
    for title, sub, notes, imgs in ROUTES:
        ps = ''.join(f'<p>{esc(x)}</p>' for x in notes)
        im = ''.join(f'<a class="dimg" href="{u}" target="_blank" rel="noopener"><img src="{u}" alt="{esc("Схема проезда: " + title)}" loading="lazy"><span>Открыть крупно</span></a>' for u in imgs)
        routes.append(f'''        <div class="droute rv">
          <div class="droute__h"><span class="dcard__ic"><svg><use href="#i-pin"/></svg></span><div><b>{esc(title)}</b><small>{esc(sub)}</small></div></div>
          {ps}
          <div class="droute__imgs droute__imgs--{len(imgs)}">{im}</div>
        </div>''')
    halls = '\n'.join(f'''        <a class="dhall rv" href="{u}" target="_blank" rel="noopener"><span class="dhall__ph"><img src="{u}" alt="{esc('Схема зала ' + t)}" loading="lazy"></span><b>{esc(t)}</b><small>{esc(s)}</small></a>''' for t, s, u in HALLS)

    nav = [('company', 'Компания'), ('events', 'Мероприятия'), ('route', 'Как добраться'), ('halls', 'Схемы залов')]
    navh = ''.join(f'<a href="#{a}">{t}</a>' for a, t in nav)

    head, sprite, header, footer, tail = shared_parts()
    sprite = sprite.replace('</svg>', ICONS + '</svg>', 1)
    head = re.sub(r'<title>.*?</title>', '<title>Документы — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Документы ЭКСПОКРЫМ: каталоги и деловые программы выставок, схемы проезда и выставочных залов.">', head)
    header = header.replace(' aria-current="page"', '')
    html = f'''{head}</head>
<body class="page-docs">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Документы</nav>
      <div class="eyebrow">Участникам и посетителям</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Документы</span></span><span class="ln ln--indent" style="--i:1"><span><em>и схемы</em></span></span></h1>
      <p class="hero-n__lead">Каталоги и деловые программы выставок, схемы проезда и выставочных залов, документы компании.</p>
    </div>
  </section>

  <div class="dnav"><div class="container"><nav class="dnav__in">{navh}</nav></div></div>

  <section class="ds" id="company">
    <div class="container">
      <h2 class="h2 rv rv--clip">Компания</h2>
      <div class="dgrid">
{company}
      </div>
      <a class="ct-req rv" href="../o-nas-v2.html#contacts"><span>Реквизиты компании</span><span class="ct-soc__go"><svg><use href="#i-arrow"/></svg></span></a>
    </div>
  </section>

  <section class="ds ds--w" id="events">
    <div class="container">
      <h2 class="h2 rv rv--clip">Мероприятия</h2>
      <p class="ds__lead rv">Официальные каталоги, деловые программы и правила выставок.</p>
      <div class="devs">
{chr(10).join(evs)}
      </div>
    </div>
  </section>

  <section class="ds" id="route">
    <div class="container">
      <h2 class="h2 rv rv--clip">Как добраться</h2>
      <div class="droutes">
{chr(10).join(routes)}
      </div>
    </div>
  </section>

  <section class="ds ds--w" id="halls">
    <div class="container">
      <h2 class="h2 rv rv--clip">Схемы залов</h2>
      <div class="dhalls">
{halls}
      </div>
    </div>
  </section>
</main>

{footer}

{tail}
</body>
</html>
'''
    (ROOT / 'dokumenty').mkdir(exist_ok=True)
    (ROOT / 'dokumenty' / 'index.html').write_text(html, encoding='utf-8')
    return len(evs)


if __name__ == '__main__':
    print('мероприятий с документами:', build())
