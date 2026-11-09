"""Собирает страницу partners/index.html — все партнёры мероприятий со старого сайта.

Данные: site-source/partners/partners.json (разбор https://expocrimea.com/partners/).
Шапка и подвал — с главной (build_event.shared_parts).
Запуск из корня проекта: python3 -I tools/build_partners.py, затем typograf по partners/index.html.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, esc, shared_parts  # noqa: E402
from link_logos import norm, url_map  # noqa: E402

RAW = json.loads((ROOT / 'site-source' / 'partners' / 'partners.json').read_text(encoding='utf-8'))
CATS = [('gos', 'Государственные'), ('assoc', 'Ассоциации'), ('media', 'СМИ'), ('biz', 'Компании')]


def cat(c):
    if c == 'gos':
        return 'gos'
    if c == 'association':
        return 'assoc'
    if 'media' in c:
        return 'media'
    return 'biz'


def clean(name):
    name = name.replace('“', '«').replace('”', '»').replace('"', '«', 1).replace('"', '»', 1)
    return re.sub(r'\s+', ' ', name).strip()


def plural(n, forms):
    return forms[2] if 11 <= n % 100 <= 14 else forms[0] if n % 10 == 1 else forms[1] if 2 <= n % 10 <= 4 else forms[2]


def build():
    urls = url_map()
    items = [dict(i, c=cat(i['cat']), name=clean(i['name'])) for i in RAW if i['img'] and i['name']]
    for i in items:
        i['url'] = i['url'].strip() or urls.get(norm(i['name']), '')
    order = {'gos': 0, 'assoc': 1, 'biz': 2, 'media': 3}
    items.sort(key=lambda i: order[i['c']])  # государственные сверху, внутри групп — порядок старого сайта
    cnt = {c: sum(i['c'] == c for i in items) for c, _ in CATS}
    total = len(items)

    cards = []
    for i in items:
        tag, attrs = ('a', f' href="{esc(i["url"])}" target="_blank" rel="noopener"') if i['url'] else ('div', '')
        cards.append(f'''        <{tag} class="pcard" data-f="{i['c']}" data-n="{esc(i['name'].lower())}"{attrs}>
          <span class="pcard__l"><img src="{esc(i['img'])}" alt="{esc(i['name'])}" loading="lazy"></span>
          <span class="pcard__n">{esc(i['name'])}</span>
        </{tag}>''')
    chips = '\n'.join(f'          <button class="chip" role="tab" data-f="{c}">{t} <small>{cnt[c]}</small></button>' for c, t in CATS)
    stats = [(total, 'партнёров мероприятий'), (cnt['gos'], 'органов власти и ведомств'), (cnt['assoc'], plural(cnt['assoc'], ['ассоциация и союз', 'ассоциации и союза', 'ассоциаций и союзов'])), (cnt['media'], plural(cnt['media'], ['информационный партнёр', 'информационных партнёра', 'информационных партнёров']))]
    stat_html = '\n'.join(f'        <div class="pstat rv"><b class="odo">{n}</b><span>{t}</span></div>' for n, t in stats)

    head, sprite, header, footer, tail = shared_parts()
    head = re.sub(r'<title>.*?</title>', '<title>Партнёры — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="Партнёры мероприятий ЭКСПОКРЫМ: органы власти, отраслевые ассоциации, компании и СМИ — {total} организаций.">', head)
    header = header.replace(' aria-current="page"', '').replace('<a href="../partners/index.html">', '<a href="../partners/index.html" aria-current="page">', 1)
    html = f'''{head}</head>
<body class="page-partners">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Партнёры</nav>
      <div class="eyebrow">Партнёры мероприятий</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Нам</span></span><span class="ln ln--indent" style="--i:1"><span><em>доверяют</em></span></span></h1>
      <p class="hero-n__lead">Органы власти, отраслевые ассоциации, компании и СМИ, вместе с которыми мы проводим выставки и форумы в Крыму.</p>
      <div class="pstats">
{stat_html}
      </div>
    </div>
  </section>

  <section class="nl pl">
    <div class="container">
      <div class="nl__bar pl__bar">
        <div class="chips chips--scroll rv" role="tablist" data-ptabs>
          <span class="chips__ind"></span>
          <button class="chip is-on" role="tab" data-f="all">Все <small>{total}</small></button>
{chips}
        </div>
        <label class="psearch rv"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input type="search" placeholder="Найти партнёра" aria-label="Найти партнёра" data-psearch></label>
      </div>
      <div class="pgrid" id="pgrid">
{chr(10).join(cards)}
      </div>
      <p class="pl__empty" hidden>Никого не нашли. Попробуйте другое название.</p>
      <div class="pl__more"><button class="btn btn--line" type="button" data-pmore>Показать ещё</button><span class="pl__count" data-pcount></span></div>
    </div>
  </section>

  <section class="pcta">
    <div class="container pcta__in">
      <h2 class="h2 rv rv--clip">Станьте<br><em>партнёром</em></h2>
      <div class="rv">
        <p>Расскажем о форматах партнёрства на выставках и форумах ЭКСПОКРЫМ и подберём подходящий проект.</p>
        <div class="pcta__btns">
          <a class="btn" href="mailto:info@expocrimea.com?subject={esc('Партнёрство')}">Написать нам</a>
          <a class="btn btn--line" href="tel:+79789009090">+7 (978) 900 90 90</a>
        </div>
      </div>
    </div>
  </section>
</main>

{footer}

{tail}
</body>
</html>
'''
    (ROOT / 'partners').mkdir(exist_ok=True)
    (ROOT / 'partners' / 'index.html').write_text(html, encoding='utf-8')
    return total, cnt


if __name__ == '__main__':
    print(build())
