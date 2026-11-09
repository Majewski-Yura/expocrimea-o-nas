"""Собирает раздел новостей: news/index.html (список с фильтром) и news/<slug>.html (статьи).

Данные: data/news.json (tools/scrape_news.py). Шапка и подвал — с главной (build_event.shared_parts).
Заодно обновляет блок «Новости» на главной: 4 последние статьи.
Запуск из корня проекта: python3 -I tools/build_news.py, затем typograf по news/*.html и index.html.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, esc, shared_parts  # noqa: E402

NEWS = json.loads((ROOT / 'data' / 'news.json').read_text(encoding='utf-8'))
MON_SHORT = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

# Рубрики фильтра: ключ → подпись
CATS = [('agro', 'АПК'), ('hosp', 'Гостеприимство'), ('urban', 'Стройка'), ('med', 'Медицина'), ('company', 'Компания')]
# Метка мероприятия: (слова в тегах или заголовке, подпись, ссылка от корня, рубрика)
EVENT_TAGS = [
    (('КрымУрбанПремия', 'Урбан Прем', 'УРБАН ПРЕМИ'), 'Крым Урбан Премия', 'https://cuf.expocrimea.com/cua', 'urban'),
    (('КрымУрбанФорум', 'Урбан Форум', 'CrimeaUrban'), 'Крым Урбан Форум', 'https://cuf.expocrimea.com/', 'urban'),
    (('СтройЭкспоКрым', 'ремонт'), 'СтройЭкспоКрым', 'events/stroy.html', 'urban'),
    (('МебельЭкспоКрым', 'мебел'), 'Выставка мебели', 'events/mvmk.html', 'urban'),
    (('АгроЭкспоКрым', 'АПК', 'урожа', 'аграри', 'сельхоз'), 'АгроЭкспоКрым', 'events/agro.html', 'agro'),
    (('РосЭкспоКрым',), 'РосЭкспоКрым', 'events/ros.html', 'agro'),
    (('РестоОтельМаркет', 'гостеприимств'), 'РестоОтельМаркет', 'events/rhm.html', 'hosp'),
    (('ТуризмЭкспоКрым', 'ТуристЭкспо', 'Туризм'), 'ТуристЭкспо. Крым', 'events/turistekspo-krym.html', 'hosp'),
    (('Здравоохранение', 'медиц', 'Мурашко'), 'Здравоохранение.Крым', 'events/med.html', 'med'),
    (('ФЭМ',), 'Форум эстетической медицины', 'https://fem.expocrimea.com/', 'med'),
]


def meta(n):
    hay = ' '.join(n['tags']) + ' ' + n['title']
    for keys, label, link, cat in EVENT_TAGS:
        if any(k in hay for k in keys):
            return label, link, cat
    return 'ЭКСПОКРЫМ', 'o-nas-v2.html', 'company'


def link(href, up):
    return href if href.startswith('http') else up + href


def card(n, up, big=False, rv=True):
    label, _, cat = meta(n)
    lead = f'\n          <span class="ncard__l">{esc(n["lead"][:220].rsplit(" ", 1)[0] + "…" if len(n["lead"]) > 220 else n["lead"])}</span>' if big else ''
    img = n['image'] if big else (n['thumb'] or n['image'])
    return f'''        <a class="ncard{' ncard--big' if big else ''}{' rv' if rv else ''}" data-f="{cat}" href="{up}news/{n['slug']}.html">
          <span class="ncard__ph"><img src="{esc(img)}" alt="" loading="lazy"></span>
          <span class="ncard__b">
          <span class="ncard__m"><span class="ncard__d">{n['date_h']}</span><span class="ncard__tag">{esc(label)}</span></span>
          <span class="ncard__t">{esc(n['title'])}</span>{lead}
          </span>
        </a>'''


def page(title, desc, body_cls, main):
    head, sprite, header, footer, tail = shared_parts()
    head = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head)
    header = header.replace(' aria-current="page"', '').replace('<a href="../news/index.html">', '<a href="../news/index.html" aria-current="page">', 1)
    return f'''{head}</head>
<body class="{body_cls}">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
{main}
</main>

{footer}

{tail}
</body>
</html>
'''


def build_list():
    counts = {c: sum(meta(n)[2] == c for n in NEWS) for c, _ in CATS}
    chips = '\n'.join(f'          <button class="chip" role="tab" data-f="{c}">{t}</button>' for c, t in CATS if counts[c])
    cards = '\n'.join(card(n, '../', big=(i == 0)) for i, n in enumerate(NEWS))
    main = f'''  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Новости</nav>
      <div class="eyebrow">Пресс-центр ЭКСПОКРЫМ</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Новости</span></span><span class="ln ln--indent" style="--i:1"><span><em>и события</em></span></span></h1>
      <p class="hero-n__lead">Итоги выставок, анонсы, деловая программа и жизнь отраслей Крыма — от организатора крупнейших выставок полуострова.</p>
    </div>
  </section>

  <section class="nl">
    <div class="container">
      <div class="nl__bar">
        <div class="chips chips--scroll rv" role="tablist" data-for="#news-grid">
          <span class="chips__ind"></span>
          <button class="chip is-on" role="tab" data-f="all">Все</button>
{chips}
        </div>
        <a class="lnk rv" href="https://t.me/expocrimea" target="_blank" rel="noopener">Наш телеграм<span><svg><use href="#i-arrow"/></svg></span></a>
      </div>
      <div class="ngrid ngrid--all" id="news-grid">
{cards}
      </div>
      <p class="nl__arch">Новости до&nbsp;октября 2024 года — в&nbsp;<a href="https://expocrimea.com/news/page/3/" target="_blank" rel="noopener">архиве старого сайта</a>.</p>
    </div>
  </section>'''
    (ROOT / 'news').mkdir(exist_ok=True)
    (ROOT / 'news' / 'index.html').write_text(page('Новости — ЭКСПОКРЫМ', 'Новости ЭКСПОКРЫМ: итоги выставок, анонсы мероприятий и события отраслей Крыма.', 'page-news', main), encoding='utf-8')


def build_article(i):
    n = NEWS[i]
    label, ev_link, _ = meta(n)
    more = [NEWS[(i + k) % len(NEWS)] for k in (1, 2, 3)]
    same = [x for x in NEWS if x is not n and meta(x)[0] == label][:3]
    more = (same + [m for m in more if m not in same])[:3]
    prev_n, next_n = (NEWS[i - 1] if i > 0 else None), (NEWS[i + 1] if i + 1 < len(NEWS) else None)
    body = n['body']
    if n['lead'] and n['lead'][:40] in re.sub(r'<[^>]+>', '', body.split('</p>')[0]):
        body = body.split('</p>', 1)[1].strip()  # первый абзац уже стоит лидом
    url = f'https://majewski-yura.github.io/expocrimea-o-nas/news/{n["slug"]}.html'
    nav = ''
    if prev_n or next_n:
        nav = '\n      <nav class="art__pn">' + (f'<a class="art__pv" href="{prev_n["slug"]}.html"><small>Новее</small>{esc(prev_n["title"])}</a>' if prev_n else '<span></span>') + (f'<a class="art__nx" href="{next_n["slug"]}.html"><small>Раньше</small>{esc(next_n["title"])}</a>' if next_n else '') + '</nav>'
    main = f'''  <article class="art">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span><a href="index.html">Новости</a><span>/</span>{n['date_h']}</nav>
      <div class="art__head">
        <div class="art__meta rv"><time datetime="{n['date']}">{n['date_h']}</time><a class="ncard__tag" href="{link(ev_link, '../')}">{esc(label)}</a></div>
        <h1 class="art__t rv">{esc(n['title'])}</h1>
        <p class="art__lead rv">{esc(n['lead'])}</p>
      </div>
      <figure class="art__ph e-photo__f"><img src="{esc(n['image'])}" alt=""></figure>
      <div class="art__grid">
        <aside class="art__side">
          <a class="art__back" href="index.html"><span><svg><use href="#i-arrow"/></svg></span>Все новости</a>
          <div class="art__share">
            <small>Поделиться</small>
            <a href="https://t.me/share/url?url={esc(url)}" target="_blank" rel="noopener" aria-label="Телеграм">TG</a>
            <a href="https://vk.com/share.php?url={esc(url)}" target="_blank" rel="noopener" aria-label="ВКонтакте">VK</a>
            <button type="button" data-copy="{esc(url)}" aria-label="Скопировать ссылку">Ссылка</button>
          </div>
        </aside>
        <div class="art__body">
{body}
        </div>
      </div>{nav}
    </div>
  </article>

  <section class="news-s news-s--more">
    <div class="container">
      <div class="news__head">
        <h2 class="h2 rv rv--clip">Ещё новости</h2>
        <a class="lnk rv" href="index.html">Все новости<span><svg><use href="#i-arrow"/></svg></span></a>
      </div>
      <div class="ngrid ngrid--3">
{chr(10).join(card(m, '../') for m in more)}
      </div>
    </div>
  </section>'''
    (ROOT / 'news' / f'{n["slug"]}.html').write_text(page(f'{n["title"]} — ЭКСПОКРЫМ', n['lead'][:160], 'page-news page-art', main), encoding='utf-8')


def update_index():
    """Блок «Новости» на главной: 4 последние статьи, ссылки на новый раздел."""
    p = ROOT / 'index.html'
    s = p.read_text(encoding='utf-8')
    a = s.index('<div class="ngrid">') + len('<div class="ngrid">')
    b = s.index('</div>\n    </div>\n  </section>', a)
    s = s[:a] + '\n' + '\n'.join(card(n, '') for n in NEWS[:4]) + '\n      ' + s[b:]
    s = s.replace('<a class="lnk rv" href="https://expocrimea.com/news/" target="_blank" rel="noopener">Все новости', '<a class="lnk rv" href="news/index.html">Все новости')
    p.write_text(s, encoding='utf-8')


if __name__ == '__main__':
    build_list()
    for i in range(len(NEWS)):
        build_article(i)
    update_index()
    print('новостей:', len(NEWS))
