"""Собирает страницы мероприятий events/<slug>.html в стиле версии 2.

Шапку, подвал, иконки и плавающие кнопки берёт из index.html, чтобы страницы
не расходились с главной. Данные мероприятия — в словаре EVENTS ниже.
Запуск из корня проекта: python3 -I tools/build_event.py [slug ...]
После сборки прогоните tools/typograf.py по созданным страницам.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
U = 'https://expocrimea.com/wp-content/uploads/'
NB = ' '

EVENTS = {
    'agro': {
        'name': 'АгроЭкспоКрым',
        'title_lines': ['Агро', '<em>Экспо</em>Крым'],
        'eyebrow': 'XV юбилейная аграрная выставка',
        'bgnum': 'XV',
        'color': '#42924B',
        'logo': '../logos/agro.png',
        'dates': '10–12 февраля 2027',
        'start': '2027-02-10',
        'city': 'Симферополь',
        'place_short': 'Экс-терминал аэропорта',
        'lead': 'Главная деловая площадка производителей, дистрибьюторов и оптовиков сельхозтехники Крыма и Юга России. 15 лет мы собираем профессионалов АПК, чтобы обсуждать тренды аграрных рынков и находить новых партнёров.',
        'photo': '2021/08/img_3402-2-2.jpg',
        'photo_cap': ['Открытие АгроЭкспоКрым', 'Симферополь'],
        'about': 'АгроЭкспоКрым — событие, где <em>инновации встречаются с возможностями</em>, а традиции сельского хозяйства — с передовыми технологиями. Здесь лидеры агропромышленного комплекса обмениваются опытом, показывают достижения и заключают контракты.',
        'about_p': 'Выставка ориентирована и на крупные агрохолдинги, и на небольшие фермерские хозяйства: прямой диалог с экспертами, производителями оборудования и разработчиками технологий.',
        'tasks': ['Дилерство', 'Представительство', 'Контракты', 'Прямые поставки', 'Инвестиции', 'Субсидии', 'Инновации', 'Кадровые ресурсы'],
        'mission_label': 'Почему Крым',
        'mission': 'Плодородные земли, благоприятный климат и государственная поддержка делают Крым центром притяжения для аграриев со всей России.',
        'offer': 'Для крымских производителей действует спецпредложение на участие.',
        'nums_title': 'АгроЭкспоКрым-2025 <em>в цифрах</em>',
        'nums': [('15', 'лет выставке', 'XV юбилейная выставка пройдёт в 2027 году.'),
                 ('200+', 'успешных компаний', 'экспонентов из Крыма и регионов России'),
                 ('7000+', 'целевой аудитории', 'аграрии, переработчики, закупщики'),
                 ('70+', 'партнёров и спикеров', 'деловая программа и круглые столы'),
                 ('50+', 'профильных СМИ', 'федеральные и отраслевые издания')],
        'expo': ['Сельхозтехника и оборудование', 'Системы полива, орошение', 'Растениеводство, средства защиты растений',
                 'Животноводство, ветеринария, комбикорма, пчеловодство', 'Виноделие и виноградарство', 'Аквакультура',
                 'Оборудование для пищевой и перерабатывающей промышленности', 'Готовая сельхозпродукция, продукты питания',
                 'Научная и исследовательская деятельность'],
        # иконка на каждую экспозицию, по порядку — ключи из ICONS
        'expo_icons': ['tractor', 'drop', 'sprout', 'cow', 'grapes', 'fish', 'factory', 'wheat', 'flask'],
        'aud': [('Фермерам', 'Новые технологии, которые помогут увеличить урожайность и снизить затраты.'),
                ('Агрохолдингам', 'Надёжные поставщики оборудования и технологий для эффективности бизнеса.'),
                ('Инвесторам', 'Перспективные проекты и вход в динамично развивающийся рынок АПК Крыма.'),
                ('Экспертам', 'Актуальные проблемы и тренды отрасли на конференциях и круглых столах.')],
        'who': ['Предприятия агропромышленного комплекса', 'Производители сопутствующей продукции',
                'Фермерские и рыбоводные хозяйства', 'Перерабатывающие производства и зерновые компании',
                'Садоводы и фермеры', 'Научные сотрудники АПК'],
        'docs': [('Официальный каталог 2026', 'Онлайн', 'https://expocrimea.com/katalog_agro/'),
                 ('Деловая программа', 'Онлайн', 'https://expocrimea.com/programma-agro/'),
                 ('Аккредитация СМИ', 'Форма', 'https://forms.yandex.ru/cloud/68b1660049363915adc1bc99/'),
                 ('Положение по обеспечению безопасности', 'PDF', U + '2021/08/pravila_soblyudeniya_mer_bezopasnosti_agroekspokrym_2026.pdf')],
        'videos': ['https://rutube.ru/play/embed/09eae6cd3f232aa4dd060295caf007cc',
                   'https://rutube.ru/play/embed/77d02362c547d8a959df0873b1334a16/',
                   'https://rutube.ru/play/embed/49973d7f25cfcfec58ca90a2667fda9b/'],
        'gallery': ['2021/08/7bp87qevt1m-1024x683.jpg', '2021/08/dedfdsv2_r0-1024x683.jpg', '2021/08/tbxrtgxj_zq-1024x683.jpg',
                    '2021/08/ot8v9f0yf4q-1024x683.jpg', '2021/08/zin8ruy8bra-1024x683.jpg', '2021/08/ybqmwplj63o.jpg'],
        'venue_photo': '2021/08/aeroport-e1698951824910.jpeg',
        'venue_title': 'Экс-терминал аэропорта «Симферополь»',
        'venue_addr': 'Республика Крым, г. Симферополь, пгт Аэрофлотский, площадь Аэропорта, 14',
        'venue_points': ['Крытые павильоны и открытая площадка для крупной техники', 'Конференц-зал для деловой программы', 'Удобный подъезд и парковка'],
        'venue_map': 'https://yandex.ru/maps/?text=' + 'Симферополь, площадь Аэропорта, 14',
        'partners_json': 'site-source/events/agro_partners.json',
        'cta_title': ['Станьте', 'участником'],
        'cta_text': 'Забронируйте стенд на главной аграрной выставке года. Менеджер ответит на вопросы и подберёт формат участия.',
    },
}

# Линейные иконки экспозиций (viewBox 0 0 24 24, обводка задаётся в CSS)
ICONS = {
    'tractor': '<circle cx="7" cy="16.5" r="3.5"/><circle cx="18" cy="18" r="2"/><path d="M3.5 13V8h6l2 6h6.5l2 4M9.5 8V4.5h4.5V14M14 11h4"/>',
    'drop': '<path d="M12 3s-5.5 6.2-5.5 10.5a5.5 5.5 0 0 0 11 0C17.5 9.2 12 3 12 3z"/><path d="M9.5 14a2.5 2.5 0 0 0 2.5 2.5"/>',
    'sprout': '<path d="M12 21v-9"/><path d="M12 12C12 8 9.5 5.5 5 5.5c0 4 2.5 6.5 7 6.5zM12 14.5c0-4 2.5-6.5 7-6.5 0 4-2.5 6.5-7 6.5z"/><path d="M8 21h8"/>',
    'cow': '<path d="M4 6.5 7.5 8h9L20 6.5"/><path d="M7.5 8v6.5a4.5 4.5 0 0 0 9 0V8"/><path d="M10 17.5h4"/><circle cx="10.2" cy="11.5" r=".6"/><circle cx="13.8" cy="11.5" r=".6"/>',
    'grapes': '<circle cx="9" cy="10" r="2"/><circle cx="13" cy="10" r="2"/><circle cx="11" cy="13.5" r="2"/><circle cx="15" cy="13.5" r="2"/><circle cx="13" cy="17" r="2"/><path d="M11 8c0-2.5 1.5-4 4-5M13 6.5l3-.5"/>',
    'fish': '<path d="M3 12c2.8-3.8 6.8-5 10.5-4.2 2.3.5 4.3 2 5.5 4.2-1.2 2.2-3.2 3.7-5.5 4.2C9.8 17 5.8 15.8 3 12z"/><path d="M19 12l2.5-3v6z"/><circle cx="8" cy="11" r=".6"/>',
    'factory': '<path d="M3 21V11l5 3v-3l5 3v-3l5 3V4h3v17z"/><path d="M7 18h2M12 18h2M17 18h1"/>',
    'wheat': '<path d="M12 21V5"/><path d="M12 9c-2-1-3-2.8-3-5 2 1 3 2.8 3 5zM12 9c2-1 3-2.8 3-5-2 1-3 2.8-3 5zM12 14c-2-1-3-2.8-3-5 2 1 3 2.8 3 5zM12 14c2-1 3-2.8 3-5-2 1-3 2.8-3 5z"/>',
    'flask': '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3"/><path d="M7.5 15h9"/>',
}

# Карточки «Другие мероприятия» — порядок как на главной
ALL = [
    ('АгроЭкспоКрым', 'agro', 'https://expocrimea.com/events/agro/', '2021/08/1000h800-1-2.jpg', '10–12 февраля', 'Симферополь'),
    ('РестоОтельМаркет', None, 'https://expocrimea.com/events/rhm/', '2021/08/frame-1241.png', '25–27 марта', 'Ялта, «Ялта-Интурист»'),
    ('РосЭкспоКрым', None, 'https://expocrimea.com/events/ros/', '2021/09/frame-1243.png', '25–27 марта', 'Ялта, «Ялта-Интурист»'),
    ('Чемпионат национальной кухни', None, 'https://expocrimea.com/events/chempionat-naczionalnoj-kuhni/', '2026/10/group-10.jpg', '25–26 марта', 'Ялта, «Ялта-Интурист»'),
    ('Форум эстетической медицины', None, 'https://fem.expocrimea.com/', '2025/10/1000h800_4-1.png', '8–9 апреля', 'Алушта, MORE SPA & Resort 5*'),
    ('КрымУрбанФорум', None, 'https://cuf.expocrimea.com/', '2022/05/1000-h-801-1.jpg', '8–10 сентября', 'Симферополь'),
]


def esc(s):
    return html.escape(s, quote=True)


def shared_parts():
    """Шапка, подвал, иконки и кнопки с главной, ссылки переведены на ../"""
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    head = s[:s.index('</head>')]
    sprite = s[s.index('<svg width="0"'):s.index('</svg>', s.index('<svg width="0"')) + 6]
    sprite = sprite.replace('</svg>', '  <symbol id="i-gift" viewBox="0 0 24 24"><path d="M20 12v9H4v-9M2 7h20v5H2zM12 21V7M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7z"/></symbol>\n  <symbol id="i-pin2" viewBox="0 0 24 24"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></symbol>\n</svg>')
    header = s[s.index('<header class="header">'):s.index('</header>') + 9]
    footer = s[s.index('<footer'):s.index('</footer>') + 9]
    fabs = s[s.index('<a class="fab fab--chat"'):s.index('<script src="assets/v2.js')]
    ver = re.search(r'assets/v2\.js(\?v=\d+)?', s).group(1) or ''

    def fix(x):
        x = x.replace('src="site-source/', 'src="../site-source/').replace('href="assets/', 'href="../assets/')
        x = x.replace('href="index.html"', 'href="../index.html"').replace('href="o-nas-v2.html', 'href="../o-nas-v2.html')
        x = x.replace('href="#events"', 'href="../index.html#events"').replace('href="#news"', 'href="../index.html#news"')
        return x
    header = fix(header).replace('<a href="../index.html#events">', '<a href="../index.html#events" aria-current="page">', 1)
    return fix(head), sprite, header, fix(footer), fix(fabs) + f'<script src="../assets/v2.js{ver}"></script>'


def logo_strip(items):
    return '\n'.join(f'      <div class="plogo"><img src="{esc(u)}" alt="{esc(n)}" title="{esc(n)}" loading="lazy"></div>' for u, n, *_ in items)


def build(slug):
    e = EVENTS[slug]
    head, sprite, header, footer, fabs = shared_parts()
    head = re.sub(r'<title>[^<]*</title>', f'<title>{e["name"]}{NB}— ЭКСПОКРЫМ</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(e["eyebrow"])} {esc(e["name"])}: {esc(e["dates"])}, {esc(e["city"])}.">', head)

    lines = '\n'.join(f'        <span class="ln{" ln--indent" if i else ""}"><span style="--i:{i}">{t}</span></span>' for i, t in enumerate(e['title_lines']))
    tasks = ''.join(f'<span>{t}</span>' for t in e['tasks'])
    n0 = e['nums'][0]
    tiles = [f'''        <div class="tile tile--hero rv">
          <img src="../site-source/logo.svg" alt="" aria-hidden="true">
          <div><b class="odo">{n0[0]}</b><span>{n0[1]}</span></div>
          <p>{n0[2]}</p>
        </div>''']
    for k, (v, t, d) in enumerate(e['nums'][1:]):
        cls = ' tile--light' if k == 2 else ''
        tiles.append(f'        <div class="tile{cls} rv"><b class="odo">{v}</b><span>{t}<small>{d}</small></span></div>')
    icons = e.get('expo_icons') or []
    mark = lambda k: (f'<svg class="prow__ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[icons[k]]}</svg>' if k < len(icons) else f'{k + 1:02d}')
    expo = '\n'.join(f'        <li><div class="prow rv"><span class="prow__n">{mark(k)}</span><span class="prow__t">{t}</span><span class="prow__a"></span></div></li>' for k, t in enumerate(e['expo']))
    aud = '\n'.join(f'''        <div class="aud__c rv"><span class="aud__n">{k + 1:02d}</span><span class="aud__t">{t}</span><p class="aud__d">{d}</p></div>''' for k, (t, d) in enumerate(e['aud']))
    who = ''.join(f'<li>{w}</li>' for w in e['who'])
    docs = '\n'.join(f'          <a class="doc rv" href="{esc(h)}" target="_blank" rel="noopener"><svg class="doc__i"><use href="#i-doc"/></svg><span><b>{t}</b><small>{f}</small></span><svg class="doc__a" viewBox="0 0 24 24"><path d="M7 7l10 10M17 8v9H8"/></svg></a>' for t, f, h in e['docs'])
    vids = '\n'.join(f'        <div class="vid rv"><iframe data-src="{esc(v)}" title="Видео {e["name"]} {k + 1}" allow="clipboard-write; autoplay" allowfullscreen loading="lazy"></iframe></div>' for k, v in enumerate(e['videos']))
    gal = '\n'.join(f'        <figure><img src="{U}{g}" alt="" loading="lazy"></figure>' for g in e['gallery'])
    points = ''.join(f'<li>{p}</li>' for p in e['venue_points'])

    pj = json.loads((ROOT / e['partners_json']).read_text(encoding='utf-8'))
    support = pj.get('Официальная поддержка:', [])
    partners = pj.get('Партнер загородной жизни', []) + pj.get('Официальные партнеры:', [])
    info = pj.get('Информационные партнеры:', [])
    clean = lambda lst: [(u, re.sub(r'^(>\s*)?(Сайт |Официальный сайт )?', '', n).split(' <div')[0].strip()) for u, n, *_ in lst]
    groups = [('Официальная поддержка', clean(support), ''), ('Официальные партнёры', clean(partners), ' mq--rev'), ('Информационные партнёры', clean(info), '')]
    part = '\n'.join(f'''    <div class="container"><div class="part__label rv">{lab}</div></div>
    <div class="mq-wrap rv"><div class="mq{rev}">
{logo_strip(items)}
    </div></div>''' for lab, items, rev in groups if items)

    more = []
    for n, s2, h, i, d, a in ALL:
        if s2 == slug:
            continue
        href = f'{s2}.html' if s2 in EVENTS else h
        ext = '' if s2 in EVENTS else ' target="_blank" rel="noopener"'
        more.append(f'''        <a class="ecard rv" href="{href}"{ext}>
          <span class="ecard__ph"><img src="{U}{i}" alt="" loading="lazy"></span>
          <span class="ecard__date">{d.replace(' ', NB)} 2027</span>
          <span class="ecard__go"><svg><use href="#i-arrow"/></svg></span>
          <span class="ecard__b"><span class="ecard__n">{n}</span><span class="ecard__a">{a}</span></span>
        </a>''')
    more = '\n'.join(more[:4])

    body = f'''</head>
<body class="page-ev" style="--ev:{e['color']}">

<div class="progress" aria-hidden="true"></div>

{sprite}

{header}

<main>
  <!-- 1. Первый экран -->
  <section class="hero hero-e">
    <div class="hero__bgnum" aria-hidden="true">{e['bgnum']}</div>
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span><a href="../index.html#events">Мероприятия</a><span>/</span>{e['name']}</nav>
      <div class="eyebrow">{e['eyebrow']}</div>
      <h1 class="hero__title">
{lines}
      </h1>
      <div class="hero__row">
        <div>
          <p class="hero__sub">{e['lead']}</p>
          <div class="hero__btns">
            <a class="btn" href="#apply">Участвовать</a>
            <a class="btn btn--line" href="#apply">Посетить</a>
          </div>
        </div>
        <a class="seal e-seal" href="#about" aria-label="Листайте вниз">
          <svg class="seal__ring" viewBox="0 0 168 168" aria-hidden="true">
            <defs><path id="ring" d="M84 84m-70 0a70 70 0 1 1 140 0a70 70 0 1 1-140 0"/></defs>
            <text><textPath href="#ring">{e['name']} • {e['dates']} • {e['name']} • </textPath></text>
          </svg>
          <span class="seal__core"><img src="{e['logo']}" alt=""></span>
        </a>
      </div>
      <div class="e-meta">
        <div class="e-meta__it e-meta__it--ev"><small>Даты</small><b>{e['dates']}</b></div>
        <div class="e-meta__it"><small>{e['city']}</small><b>{e['place_short']}</b></div>
        <div class="e-meta__it"><small>До открытия</small><b class="e-meta__cd" data-countdown="{e['start']}">—</b></div>
      </div>
    </div>
  </section>

  <!-- 2. Фото -->
  <section class="e-photo">
    <div class="container">
      <div class="e-photo__f"><img src="{U}{e['photo']}" alt=""><div class="e-photo__cap"><span>{e['photo_cap'][0]}</span><span>{e['photo_cap'][1]}</span></div></div>
    </div>
  </section>

  <!-- 3. О выставке -->
  <section class="manifest e-about" id="about">
    <div class="container">
      <div class="eyebrow rv">О выставке</div>
      <p class="manifest__text">{e['about']}</p>
      <div class="manifest__foot">
        <div class="rv">
          <p>{e['about_p']}</p>
          <div class="tags">{tasks}</div>
        </div>
        <div class="rv" style="--d:.1s">
          <div class="mission"><small>{e['mission_label']}</small><p>{e['mission']}</p></div>
          <div class="e-offer"><svg viewBox="0 0 24 24"><use href="#i-gift"/></svg>{e['offer']}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- 4. Цифры -->
  <section class="facts e-num">
    <div class="container">
      <div class="facts__head">
        <h2 class="facts__t rv rv--clip">{e['nums_title']}</h2>
        <p class="rv">Итоги прошлой выставки — аргументы для участия в следующей.</p>
      </div>
      <div class="bento">
{chr(10).join(tiles)}
      </div>
    </div>
  </section>

  <!-- 5. Экспозиции -->
  <section class="pidx e-expo">
    <div class="container">
      <div class="pidx__head">
        <h2 class="h2 rv rv--clip">Экспозиции<br>выставки</h2>
        <p class="rv">{len(e['expo'])} тематических разделов: от техники и орошения до готовой продукции и науки.</p>
      </div>
      <ol class="plist">
{expo}
      </ol>
    </div>
  </section>

  <!-- 6. Кому стоит прийти -->
  <section class="aud">
    <div class="container">
      <h2 class="h2 rv rv--clip">Кому стоит<br>прийти</h2>
      <div class="aud__grid">
{aud}
      </div>
      <div class="aud__who rv"><small>Целевая аудитория</small><ul>{who}</ul></div>
    </div>
  </section>

  <!-- 7. Участникам -->
  <section class="e-docs">
    <div class="container">
      <h2 class="h2 rv rv--clip">Участникам<br>и партнёрам</h2>
      <div class="docs">
{docs}
      </div>
    </div>
  </section>

  <!-- 8. Как это было -->
  <section class="e-was">
    <div class="container">
      <div class="eyebrow rv">Как это было</div>
      <h2 class="h2 rv rv--clip">{e['name']}<br>в кадре</h2>
      <div class="vids">
{vids}
      </div>
      <div class="gal rv">
{gal}
      </div>
    </div>
  </section>

  <!-- 9. Место проведения -->
  <section class="venue2">
    <div class="container">
      <h2 class="h2 rv rv--clip">Место<br>проведения</h2>
      <div class="venue2__grid">
        <div class="venue2__ph rv"><img src="{U}{e['venue_photo']}" alt="{esc(e['venue_title'])}" loading="lazy"></div>
        <div class="rv">
          <div class="venue2__t">{e['venue_title']}</div>
          <p class="venue2__a">{e['venue_addr']}</p>
          <ul class="venue2__list">{points}</ul>
          <a class="btn btn--line" href="{esc(e['venue_map'])}" target="_blank" rel="noopener">Показать на карте</a>
        </div>
      </div>
    </div>
  </section>

  <!-- 10. Партнёры -->
  <section class="part e-part" id="partners">
    <div class="container"><h2 class="h2 rv rv--clip">Партнёры<br>выставки</h2></div>
{part}
  </section>

  <!-- 11. Заявка -->
  <section class="e-cta" id="apply">
    <img class="jobs__bg" src="../site-source/logo.svg" alt="" aria-hidden="true">
    <div class="container jobs__in">
      <div>
        <h2 class="rv rv--clip">{e['cta_title'][0]}<br>{e['cta_title'][1]}</h2>
        <p class="rv">{e['cta_text']}</p>
        <div class="e-cta__c rv">
          <a class="chip-l" href="tel:+79789009090"><svg><use href="#i-phone"/></svg>+7 (978) 900 90 90</a>
          <a class="chip-l" href="mailto:info@expocrimea.com?subject={esc(e['name'])}"><svg><use href="#i-mail"/></svg>info@expocrimea.com</a>
        </div>
      </div>
      <div class="magnet-wrap rv"><a class="magnet" href="mailto:info@expocrimea.com?subject={esc('Заявка на участие: ' + e['name'])}"><span>Оставить<br>заявку<svg viewBox="0 0 24 24"><use href="#i-arrow"/></svg></span></a></div>
    </div>
  </section>

  <!-- 12. Другие мероприятия -->
  <section class="e-more">
    <div class="container">
      <div class="news__head">
        <h2 class="h2 rv rv--clip">Другие<br>мероприятия</h2>
        <a class="lnk rv" href="../index.html#events">Всё расписание<span><svg><use href="#i-arrow"/></svg></span></a>
      </div>
      <div class="egrid">
{more}
      </div>
    </div>
  </section>
</main>

{footer}

{fabs}
</body>
</html>
'''
    out = ROOT / 'events' / f'{slug}.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(head + body, encoding='utf-8')
    print('собрано:', out.relative_to(ROOT))


if __name__ == '__main__':
    for slug in (sys.argv[1:] or EVENTS):
        build(slug)
