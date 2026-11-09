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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # запуск с -I не добавляет папку скрипта
import event_data  # noqa: E402

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
        'offer': ['Для крымских производителей действует спецпредложение на участие.'],
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

ICONS.update(event_data.ICONS_EXTRA)

# Расписание 2027 — порядок как на главной. slug=None: страница на отдельном сайте, ведём туда
ALL = [
    ('АгроЭкспоКрым', 'agro', 'https://expocrimea.com/events/agro/', '2021/08/1000h800-1-2.jpg', '10–12 февраля', 'Симферополь'),
    ('РестоОтельМаркет', 'rhm', 'https://expocrimea.com/events/rhm/', '2021/08/frame-1241.png', '25–27 марта', 'Ялта, «Ялта-Интурист»'),
    ('РосЭкспоКрым', 'ros', 'https://expocrimea.com/events/ros/', '2021/09/frame-1243.png', '25–27 марта', 'Ялта, «Ялта-Интурист»'),
    ('Чемпионат национальной кухни', 'chempionat-naczionalnoj-kuhni', 'https://expocrimea.com/events/chempionat-naczionalnoj-kuhni/', '2026/10/group-10.jpg', '25–26 марта', 'Ялта, «Ялта-Интурист»'),
    ('Форум эстетической медицины', None, 'https://fem.expocrimea.com/', '2025/10/1000h800_4-1.png', '8–9 апреля', 'Алушта, MORE SPA & Resort 5*'),
    ('КрымУрбанФорум', None, 'https://cuf.expocrimea.com/', '2022/05/1000-h-801-1.jpg', '8–10 сентября', 'Симферополь'),
    ('СтройЭкспоКрым', 'stroy', 'https://expocrimea.com/events/stroy/', '2021/09/img_2463.webp', '8–10 сентября', 'Симферополь'),
    ('Выставка мебели', 'mvmk', 'https://expocrimea.com/events/mvmk/', '2021/09/frame-1229.png', '8–10 сентября', 'Симферополь'),
    ('Ярмарка недвижимости', 'm2', 'https://expocrimea.com/events/m2/', '2022/01/frame-1233.png', '8–10 сентября', 'Симферополь'),
    ('Безопасность. Крым', 'safety', 'https://expocrimea.com/events/safety/', '2021/08/frame-1227.png', '8–10 сентября', 'Симферополь'),
    ('КрымУрбанПремия', None, 'https://cuf.expocrimea.com/cua', '2021/10/frame-1237.png', '9 сентября', 'Симферополь'),
    ('Здравоохранение.Крым', 'med', 'https://expocrimea.com/events/med/', '2021/09/1000h800_1-3.png', '23–25 сентября', 'Ялта, «Ялта-Интурист»'),
    ('Ефетовские чтения', 'efetovskie-chteniya', 'https://expocrimea.com/events/efetovskie-chteniya/', '2026/03/1000h800_2-2.png', '24–25 сентября', 'Ялта, «Ялта-Интурист»'),
    ('ТуристЭкспо. Крым', 'turistekspo-krym', 'https://expocrimea.com/events/turistekspo-krym/', '2025/03/1000h800-3-1-e1775042579557.jpg', '14–16 октября', 'Ялта, «Ялта-Интурист»'),
]
BUILT = [s for _, s, *_ in ALL if s]


def get_event(slug):
    return EVENTS[slug] if slug in EVENTS else event_data.from_json(slug)


def esc(s):
    return html.escape(s, quote=True)


def shared_parts():
    """Шапка, подвал, иконки и кнопки с главной, ссылки переведены на ../"""
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    head = s[:s.index('</head>')]
    sprite = s[s.index('<svg width="0"'):s.index('</svg>', s.index('<svg width="0"')) + 6]
    sprite = sprite.replace('</svg>', '  <symbol id="i-gift" viewBox="0 0 24 24"><path d="M20 12v9H4v-9M2 7h20v5H2zM12 21V7M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7z"/></symbol>\n  <symbol id="i-bed" viewBox="0 0 24 24"><path d="M3 18V6M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="1.8"/></symbol>\n</svg>')
    header = s[s.index('<header class="header">'):s.index('</header>') + 9]
    footer = s[s.index('<footer'):s.index('</footer>') + 9]
    fabs = s[s.index('<a class="fab fab--chat"'):s.index('<script src="assets/v2.js')]
    ver = re.search(r'assets/v2\.js(\?v=\d+)?', s).group(1) or ''

    def fix(x):
        x = x.replace('src="site-source/', 'src="../site-source/').replace('href="assets/', 'href="../assets/')
        x = x.replace('href="news/', 'href="../news/').replace('href="partners/', 'href="../partners/').replace('href="vakansii/', 'href="../vakansii/').replace('href="kontakty/', 'href="../kontakty/').replace('href="meropriyatiya/', 'href="../meropriyatiya/').replace('href="dokumenty/', 'href="../dokumenty/').replace('href="politika/', 'href="../politika/').replace('href="events/', 'href="../events/')
        x = x.replace('href="index.html"', 'href="../index.html"').replace('href="o-nas-v2.html', 'href="../o-nas-v2.html')
        x = x.replace('href="#events"', 'href="../index.html#events"').replace('href="#news"', 'href="../index.html#news"')
        return x
    header = fix(header).replace('<a href="../meropriyatiya/index.html">', '<a href="../meropriyatiya/index.html" aria-current="page">', 1)
    return fix(head), sprite, header, fix(footer), fix(fabs) + f'<script src="../assets/v2.js{ver}"></script>'


def logo_strip(items):
    return '\n'.join(f'      <div class="plogo"><img src="{esc(u)}" alt="{esc(n)}" title="{esc(n)}" loading="lazy"></div>' for u, n, *_ in items)


def partner_groups(e):
    if 'partner_groups' in e:
        g = e['partner_groups']
        return [('Официальная поддержка', g['support'], ''), ('Партнёры', g['partners'], ' mq--rev'), ('Информационные партнёры', g['info'], '')]
    pj = json.loads((ROOT / e['partners_json']).read_text(encoding='utf-8'))
    clean = lambda lst: [(u, re.sub(r'^(>\s*)?(Сайт |Официальный сайт )?', '', n).split(' <div')[0].strip()) for u, n, *_ in lst]
    return [('Официальная поддержка', clean(pj.get('Официальная поддержка:', [])), ''),
            ('Официальные партнёры', clean(pj.get('Партнер загородной жизни', []) + pj.get('Официальные партнеры:', [])), ' mq--rev'),
            ('Информационные партнёры', clean(pj.get('Информационные партнеры:', [])), '')]


def build(slug):
    e = get_event(slug)
    head, sprite, header, footer, fabs = shared_parts()
    head = re.sub(r'<title>[^<]*</title>', f'<title>{e["name"]}{NB}— ЭКСПОКРЫМ</title>', head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(e["eyebrow"])}. {esc(e["name"])}: {esc(e["dates"])}, {esc(e["city"])}.">', head)

    lines = '\n'.join(f'        <span class="ln{" ln--indent" if i % 2 else ""}"><span style="--i:{i}">{t}</span></span>' for i, t in enumerate(e['title_lines']))
    tasks = f'<div class="tags">{"".join(f"<span>{t}</span>" for t in e["tasks"])}</div>' if e.get('tasks') else ''
    mission = f'<div class="mission"><small>{e["mission_label"]}</small><p>{e["mission"]}</p></div>' if e.get('mission') else ''
    offer = ''.join(f'<div class="e-offer"><svg viewBox="0 0 24 24"><use href="#{"i-bed" if "проживание" in o else "i-gift"}"/></svg>{o}</div>' for o in e.get('offer') or [])

    # 4. Цифры: большая плитка + до четырёх обычных, без пустых клеток
    sec_nums = ''
    if e.get('nums'):
        n0, rest = e['nums'][0], e['nums'][1:5]
        tiles = [f'''        <div class="tile tile--hero rv">
          <img src="../site-source/logo.svg" alt="" aria-hidden="true">
          <div><b class="odo">{n0[0]}</b><span>{n0[1]}</span></div>
          <p>{n0[2]}</p>
        </div>''']
        for k, (v, t, d) in enumerate(rest):
            wide = len(rest) == 2 or (len(rest) == 3 and k == 2) or len(rest) == 1
            cls = (' tile--wide' if wide else '') + (' tile--light' if k == 2 or (len(rest) == 2 and k == 1) else '')
            small = f'<small>{d}</small>' if d else ''
            tiles.append(f'        <div class="tile{cls} rv"><b class="odo">{v}</b><span>{t}{small}</span></div>')
        sec_nums = f'''
  <!-- 4. Цифры -->
  <section class="facts e-num">
    <div class="container">
      <div class="facts__head">
        <h2 class="facts__t rv rv--clip">{e['nums_title']}</h2>
        <p class="rv">Итоги прошлых выставок — аргументы для участия в следующей.</p>
      </div>
      <div class="bento">
{chr(10).join(tiles)}
      </div>
    </div>
  </section>
'''

    # 5. Экспозиции
    sec_expo = ''
    if e.get('expo'):
        icons = e.get('expo_icons') or []
        mark = lambda k: (f'<svg class="prow__ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[icons[k]]}</svg>' if k < len(icons) else f'{k + 1:02d}')
        rows = '\n'.join(f'        <li><div class="prow rv"><span class="prow__n">{mark(k)}</span><span class="prow__t">{t}</span><span class="prow__a"></span></div></li>' for k, t in enumerate(e['expo']))
        n = len(e['expo'])
        word = 'тематический раздел' if n % 10 == 1 and n % 100 != 11 else ('тематических раздела' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'тематических разделов')
        sec_expo = f'''
  <!-- 5. Экспозиции -->
  <section class="pidx e-expo">
    <div class="container">
      <div class="pidx__head">
        <h2 class="h2 rv rv--clip">Экспозиции<br>выставки</h2>
        <p class="rv">{n} {word} — найдите свой и забронируйте стенд.</p>
      </div>
      <ol class="plist">
{rows}
      </ol>
    </div>
  </section>
'''

    # 6. Кому стоит прийти: карточки, если есть; иначе — целевая аудитория крупным списком
    sec_aud = ''
    who = ''.join(f'<li>{w}</li>' for w in e.get('who') or [])
    if e.get('aud'):
        cards = '\n'.join(f'''        <div class="aud__c rv"><span class="aud__n">{k + 1:02d}</span><span class="aud__t">{t}</span><p class="aud__d">{d}</p></div>''' for k, (t, d) in enumerate(e['aud']))
        sec_aud = f'''
  <!-- 6. Кому стоит прийти -->
  <section class="aud">
    <div class="container">
      <h2 class="h2 rv rv--clip">Кому стоит<br>прийти</h2>
      <div class="aud__grid">
{cards}
      </div>
      <div class="aud__who rv"><small>Целевая аудитория</small><ul>{who}</ul></div>
    </div>
  </section>
'''
    elif who:
        sec_aud = f'''
  <!-- 6. Целевая аудитория -->
  <section class="aud">
    <div class="container">
      <h2 class="h2 rv rv--clip">Кому стоит<br>прийти</h2>
      <ul class="who-big rv">{who}</ul>
    </div>
  </section>
'''

    # 7. Документы
    sec_docs = ''
    if e.get('docs'):
        docs = '\n'.join(f'          <a class="doc rv" href="{esc(h)}" target="_blank" rel="noopener"><svg class="doc__i"><use href="#i-doc"/></svg><span><b>{t}</b><small>{f}</small></span><svg class="doc__a" viewBox="0 0 24 24"><path d="M7 7l10 10M17 8v9H8"/></svg></a>' for t, f, h in e['docs'])
        sec_docs = f'''
  <!-- 7. Участникам -->
  <section class="e-docs">
    <div class="container">
      <h2 class="h2 rv rv--clip">Участникам<br>и партнёрам</h2>
      <div class="docs">
{docs}
      </div>
    </div>
  </section>
'''

    # 8. Как это было
    sec_was = ''
    if e.get('videos') or e.get('gallery'):
        nv = len(e.get('videos') or [])
        vids = '\n'.join(f'        <div class="vid rv"><iframe data-src="{esc(v)}" title="Видео {e["name"]} {k + 1}" allow="clipboard-write; autoplay" allowfullscreen loading="lazy"></iframe></div>' for k, v in enumerate(e.get('videos') or []))
        gal = '\n'.join(f'        <figure><img src="{U}{g}" alt="" loading="lazy"></figure>' for g in e.get('gallery') or [])
        sec_was = f'''
  <!-- 8. Как это было -->
  <section class="e-was">
    <div class="container">
      <div class="eyebrow rv">Как это было</div>
      <h2 class="h2 rv rv--clip">{e['name'].replace('.', '.<wbr>')}<br>в кадре</h2>
      {f'<div class="vids vids--{nv}">{chr(10)}{vids}{chr(10)}      </div>' if nv else ''}
      {f'<div class="gal rv">{chr(10)}{gal}{chr(10)}      </div>' if gal else ''}
    </div>
  </section>
'''

    points = ''.join(f'<li>{p}</li>' for p in e.get('venue_points') or [])
    points = f'<ul class="venue2__list">{points}</ul>' if points else ''

    groups = partner_groups(e)
    sec_part = ''
    if any(items for _, items, _ in groups):
        strips = '\n'.join(f'''    <div class="container"><div class="part__label rv">{lab}</div></div>
    <div class="mq-wrap rv"><div class="mq{rev}">
{logo_strip(items)}
    </div></div>''' for lab, items, rev in groups if items)
        sec_part = f'''
  <!-- 10. Партнёры -->
  <section class="part e-part" id="partners">
    <div class="container"><h2 class="h2 rv rv--clip">Партнёры<br>выставки</h2></div>
{strips}
  </section>
'''

    tel, tel_t = e.get('cta_phone') or ('+79789009090', '+7 (978) 900 90 90')

    # 12. Другие мероприятия — следующие четыре по расписанию
    idx = next(k for k, a in enumerate(ALL) if a[1] == slug)
    more = []
    for n, s2, h, i, d, a in (ALL[idx + 1:] + ALL[:idx])[:4]:
        href = f'{s2}.html' if s2 in BUILT else h
        ext = '' if s2 in BUILT else ' target="_blank" rel="noopener"'
        more.append(f'''        <a class="ecard rv" href="{href}"{ext}>
          <span class="ecard__ph"><img src="{U}{i}" alt="" loading="lazy"></span>
          <span class="ecard__date">{d.replace(' ', NB)} 2027</span>
          <span class="ecard__go"><svg><use href="#i-arrow"/></svg></span>
          <span class="ecard__b"><span class="ecard__n">{n}</span><span class="ecard__a">{a}</span></span>
        </a>''')
    more = '\n'.join(more)

    bgnum = f'\n    <div class="hero__bgnum" aria-hidden="true">{e["bgnum"]}</div>' if e.get('bgnum') else ''

    body = f'''</head>
<body class="page-ev" style="--ev:{e['color']}">

<div class="progress" aria-hidden="true"></div>

{sprite}

{header}

<main>
  <!-- 1. Первый экран -->
  <section class="hero hero-e">{bgnum}
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
            <text><textPath href="#ring">{e['name']} • {e['dates']} • </textPath></text>
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
      <div class="eyebrow rv">О мероприятии</div>
      <p class="manifest__text">{e['about']}</p>
      <div class="manifest__foot">
        <div class="rv">
          <p>{e['about_p']}</p>
          {tasks}
        </div>
        <div class="rv" style="--d:.1s">
          {mission}
          {offer}
        </div>
      </div>
    </div>
  </section>
{sec_nums}{sec_expo}{sec_aud}{sec_docs}{sec_was}
  <!-- 9. Место проведения -->
  <section class="venue2">
    <div class="container">
      <h2 class="h2 rv rv--clip">Место<br>проведения</h2>
      <div class="venue2__grid">
        <div class="venue2__ph rv"><img src="{U}{e['venue_photo']}" alt="{esc(e['venue_title'])}" loading="lazy"></div>
        <div class="rv">
          <div class="venue2__t">{e['venue_title']}</div>
          <p class="venue2__a">{e['venue_addr']}</p>
          {points}
          <a class="btn btn--line" href="{esc(e['venue_map'])}" target="_blank" rel="noopener">Показать на карте</a>
        </div>
      </div>
    </div>
  </section>
{sec_part}
  <!-- 11. Заявка -->
  <section class="e-cta" id="apply">
    <img class="jobs__bg" src="../site-source/logo.svg" alt="" aria-hidden="true">
    <div class="container jobs__in">
      <div>
        <h2 class="rv rv--clip">{e['cta_title'][0]}<br>{e['cta_title'][1]}</h2>
        <p class="rv">{e['cta_text']}</p>
        <div class="e-cta__c rv">
          <a class="chip-l" href="tel:{tel}"><svg><use href="#i-phone"/></svg>{tel_t}</a>
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
    for slug in (sys.argv[1:] or BUILT):
        build(slug)
