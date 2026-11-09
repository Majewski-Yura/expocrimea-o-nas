"""Собирает страницу meropriyatiya/index.html — календарь мероприятий по месяцам.

Карточки берутся из блока «Мероприятия» на главной (#ev-grid), чтобы данные жили в одном месте.
Шапка и подвал — с главной. Запуск из корня проекта: python3 -I tools/build_events_list.py, затем typograf.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, shared_parts  # noqa: E402

MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
MONTHS_NOM = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


def plural(n, f):
    return f[2] if 11 <= n % 100 <= 14 else f[0] if n % 10 == 1 else f[1] if 2 <= n % 10 <= 4 else f[2]


def cards_from_index():
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    g = s[s.index('id="ev-grid"'):]
    g = g[g.index('>') + 1:g.index('</section>')]
    out = []
    for m in re.finditer(r'<a class="ecard[^"]*" href="([^"]+)"([^>]*)>(.*?)</a>', g, re.S):
        href, attrs, body = m.groups()
        date = re.sub(r'<[^>]+>', '', re.search(r'ecard__date">(.*?)</span>', body).group(1)).replace('\xa0', ' ')
        d = re.match(r'(\d+)(?:[–-](\d+))?\s+(\S+)\s+(\d{4})', date)
        mon = MONTHS.index(d.group(3)) + 1
        city = re.search(r'data-f="([^"]+)"', attrs).group(1)
        if not href.startswith('http'):
            href = '../' + href
        body = body.replace('src="site-source/', 'src="../site-source/').replace('src="logos/', 'src="../logos/')
        out.append({'href': href, 'attrs': attrs, 'body': body, 'mon': mon, 'year': int(d.group(4)), 'day': int(d.group(1)), 'city': city,
                    'name': re.sub(r'<[^>]+>', '', re.search(r'ecard__n">(.*?)</span>', body).group(1)), 'date': date})
    out.sort(key=lambda c: (c['year'], c['mon'], c['day']))
    return out


def card_html(c):
    attrs = re.sub(r'\s*target="_blank"|\s*rel="noopener"', '', c['attrs'])
    ext = ' target="_blank" rel="noopener"' if c['href'].startswith('http') else ''
    return f'          <a class="ecard rv" href="{c["href"]}"{ext}{attrs}>{c["body"]}</a>'


def build():
    cards = cards_from_index()
    year = cards[0]['year']
    cities = []
    for c in cards:
        if c['city'] not in cities:
            cities.append(c['city'])
    months = []
    for c in cards:
        if not months or months[-1][0] != c['mon']:
            months.append((c['mon'], []))
        months[-1][1].append(c)
    nxt = cards[0]
    nxt_iso = f'{nxt["year"]}-{nxt["mon"]:02d}-{nxt["day"]:02d}'

    chips = '\n'.join(f'          <button class="chip" data-f="{c}">{c} <small>{sum(x["city"] == c for x in cards)}</small></button>' for c in cities)
    rows = []
    for mon, cs in months:
        n = len(cs)
        rows.append(f'''      <div class="cal-m">
        <div class="cal-m__h rv"><b>{mon:02d}</b><span>{MONTHS_NOM[mon - 1]}</span><small data-cnt>{n} {plural(n, ['событие', 'события', 'событий'])}</small></div>
        <div class="egrid cal-m__g">
{chr(10).join(card_html(c) for c in cs)}
        </div>
      </div>''')

    head, sprite, header, footer, tail = shared_parts()
    head = re.sub(r'<title>.*?</title>', '<title>Мероприятия — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="Календарь мероприятий ЭКСПОКРЫМ на {year} год: выставки, форумы и премии в Симферополе, Ялте и Алуште.">', head)
    html = f'''{head}</head>
<body class="page-cal">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Мероприятия</nav>
      <div class="eyebrow">Каталог мероприятий</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Календарь</span></span><span class="ln ln--indent" style="--i:1"><span><em>{year}</em></span></span></h1>
      <div class="cal-h">
        <p class="hero-n__lead">{len(cards)} {plural(len(cards), ['выставка, форум и премия', 'выставки, форума и премии', 'выставок, форумов и премий'])} в {', '.join(x.replace('Симферополь', 'Симферополе').replace('Ялта', 'Ялте').replace('Алушта', 'Алуште') for x in cities[:-1])} и {cities[-1].replace('Симферополь', 'Симферополе').replace('Ялта', 'Ялте').replace('Алушта', 'Алуште')}.</p>
        <a class="cal-next" href="{nxt['href']}"{' target="_blank" rel="noopener"' if nxt['href'].startswith('http') else ''}>
          <small>Ближайшее</small>
          <b>{nxt['name']}</b>
          <span>{nxt['date']} · {nxt['city']}</span>
          <span class="cal-next__cd"><i>До открытия</i><em data-countdown="{nxt_iso}">&nbsp;</em></span>
        </a>
      </div>
    </div>
  </section>

  <section class="cal-s">
    <div class="container">
      <div class="cal-bar">
        <div class="chips chips--scroll rv" role="tablist" data-cal="#cal">
          <span class="chips__ind"></span>
          <button class="chip is-on" data-f="all">Все <small>{len(cards)}</small></button>
{chips}
        </div>
      </div>
      <div class="cal" id="cal">
{chr(10).join(rows)}
      </div>
    </div>
  </section>
</main>

{footer}

{tail}
</body>
</html>
'''
    (ROOT / 'meropriyatiya').mkdir(exist_ok=True)
    (ROOT / 'meropriyatiya' / 'index.html').write_text(html, encoding='utf-8')
    return len(cards), [m for m, _ in months]


if __name__ == '__main__':
    print(build())
