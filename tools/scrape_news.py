"""Разбирает новости со старого сайта в data/news.json.

Вход:  site-source/news/list.json (список: slug, дата, заголовок, превью, теги)
       site-source/news/a-<slug>.html (страницы статей, скачаны curl)
Выход: data/news.json — список статей, новые сверху.
Запуск из корня проекта: python3 -I tools/scrape_news.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'site-source' / 'news'
MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
KEEP = {'p', 'strong', 'b', 'em', 'i', 'a', 'ul', 'ol', 'li', 'h2', 'h3', 'h4', 'blockquote', 'br', 'img', 'figure', 'figcaption'}


def text(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def clean(body):
    """Оставляет простую разметку: абзацы, списки, ссылки, картинки."""
    body = re.sub(r'<(script|style|svg|iframe|form)[^>]*>.*?</\1>', '', body, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)

    def tag(m):
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if name not in KEEP:
            return ''
        if close:
            return f'</{name}>'
        if name == 'a':
            h = re.search(r'href="([^"]+)"', attrs)
            href = html.unescape(h.group(1)).split('#/message')[0] if h else '#'
            ext = '' if href.startswith('mailto:') or href.startswith('tel:') else ' target="_blank" rel="noopener"'
            return f'<a href="{html.escape(href)}"{ext}>'
        if name == 'img':
            s = re.search(r'src="([^"]+)"', attrs)
            return f'<img src="{s.group(1)}" alt="" loading="lazy">' if s else ''
        return f'<{name}>'
    body = re.sub(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', tag, body)
    body = re.sub(r'</strong>\s*<strong>', ' ', body)
    body = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), body)
    for k, v in (('&nbsp;', ' '), ('&laquo;', '«'), ('&raquo;', '»'), ('&mdash;', '—'), ('&ndash;', '–'), ('&quot;', '"')):
        body = body.replace(k, v)
    body = body.replace('\xa0', ' ').replace('“', '«').replace('”', '»')
    # абзац со строками-пунктами через <br> делим на отдельные абзацы
    def split_br(m):
        parts = [x.strip() for x in re.split(r'<br>', m.group(1)) if x.strip()]
        if sum(bool(re.match(r'(?:<\w+>)*\s*(?:[–—-]|▪️|▪|•)\s', x)) for x in parts) < 2:
            return m.group(0)
        return ''.join(f'<p>{x}</p>\n' for x in parts)
    body = re.sub(r'<p>((?:(?!</p>).)*<br>(?:(?!</p>).)*)</p>', split_br, body, flags=re.S)
    # абзацы-пункты («– …», «▪️ …», «• …») подряд превращаем в список
    body = re.sub(r'<p>\s*(?:[–—-]|▪️|▪|•|✅|🔹)\s*', '<p class="li">', body)
    body = re.sub(r'((?:<p class="li">.*?</p>\s*)+)', lambda m: '<ul>' + re.sub(r'<p class="li">(.*?)</p>\s*', r'<li>\1</li>', m.group(1), flags=re.S) + '</ul>\n', body, flags=re.S)
    body = re.sub(r'<(p|strong|li|h\d)>\s*</\1>', '', body)
    body = re.sub(r'<(p|strong|li|h\d)>\s*</\1>', '', body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r'\s*\n\s*', '\n', body).strip()
    return body


def scrape():
    items = json.loads((SRC / 'list.json').read_text(encoding='utf-8'))
    out = []
    for it in items:
        f = SRC / f"a-{it['slug']}.html"
        if not f.exists() or f.stat().st_size < 1000:
            print('нет файла', it['slug'])
            continue
        s = f.read_text(encoding='utf-8')
        m = re.search(r'article:published_time" content="(\d{4})-(\d\d)-(\d\d)', s)
        mon = next(i for i, x in enumerate(MONTHS) if x == it['mon'].lower()) + 1
        if m and int(m.group(2)) == mon:
            year = int(m.group(1))
        else:  # дата публикации в WP иногда отличается от даты новости — берём год загрузки фото
            y = re.search(r'/uploads/(\d{4})/', it['thumb'] or s)
            year = int(y.group(1)) if y else 2025
        img = re.search(r'<img class="new__images" src="([^"]*)"', s)
        b = s[s.find('main__text content'):]
        b = b[b.find('>') + 1:b.find('<div class="share">')]
        body = clean(b)
        paras = [text(p) for p in re.findall(r'<p>(.*?)</p>', body, re.S)]
        lead = next((p for p in paras if len(p) > 60), '')
        out.append({
            'slug': it['slug'],
            'title': re.sub(r'\s+', ' ', it['title'].replace('“', '«').replace('”', '»')).strip(),
            'date': f'{year}-{mon:02d}-{int(it["day"]):02d}',
            'date_h': f'{int(it["day"])} {MONTHS[mon - 1]} {year}',
            'tags': it['tags'],
            'image': img.group(1) if img and img.group(1) else it['thumb'],
            'thumb': it['thumb'],
            'lead': lead,
            'body': body,
            'source': it['url'],
        })
    out.sort(key=lambda x: x['date'], reverse=True)
    (ROOT / 'data').mkdir(exist_ok=True)
    (ROOT / 'data' / 'news.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out


if __name__ == '__main__':
    for n in scrape():
        print(n['date'], len(n['body']), n['tags'], n['title'][:60], '| фото' if n['image'] else '| БЕЗ ФОТО')
