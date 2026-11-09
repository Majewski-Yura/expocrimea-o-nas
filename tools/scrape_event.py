"""Разбирает сохранённую страницу мероприятия со старого сайта в JSON.

Вход:  site-source/events/<slug>.html (скачана curl с https://expocrimea.com/events/<slug>/)
Выход: data/events/<slug>.json — сырые данные для tools/build_event.py.
Запуск из корня проекта: python3 -I tools/scrape_event.py slug [slug ...]
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def text(x):
    x = re.sub(r'<svg.*?</svg>', ' ', x, flags=re.S)
    x = re.sub(r'<br\s*/?>', ' ', x)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def section(s, cls):
    """Содержимое <section class="cls ..."> до следующей секции."""
    m = re.search(r'<section class="' + re.escape(cls) + r'[^"]*"[^>]*>(.*?)</section>', s, re.S)
    return m.group(1) if m else ''


def lists(s):
    """Списки блока «Ключевые задачи / Экспозиции / Целевая аудитория» по заголовкам."""
    out = {}
    for m in re.finditer(r'<div class="title">\s*([^<:]+):?\s*</div>\s*<ul class="list">(.*?)</ul>', section(s, 'event-thematic'), re.S):
        out[m.group(1).strip()] = [text(li) for li in re.findall(r'<li>(.*?)</li>', m.group(2), re.S) if text(li)]
    return out


def partners(s):
    groups = {}
    labels = list(re.finditer(r'(Официальная поддержка|Партнер[^:<]{0,40}|Официальные партнеры|Генеральный партнер|Информационные партнеры)\s*:?\s*</div>', s))
    for k, lab in enumerate(labels):
        seg = s[lab.end():labels[k + 1].start() if k + 1 < len(labels) else s.find('Посмотреть всех партнеров', lab.end()) if s.find('Посмотреть всех партнеров', lab.end()) > 0 else lab.end() + 200000]
        items = []
        for p in seg.split('class="partner"')[1:]:
            img = re.search(r'<img[^>]+src="([^"]+)"', p)
            if not img or any(i[0] == img.group(1) for i in items):
                continue
            name = re.sub(r'^(Сайт |Официальный сайт )', '', text(p.split('<div class="link">')[0] if '<div class="link">' in p else p).lstrip('> ')).strip()
            name = re.sub(r'^(Сайт |Официальный сайт )', '', text(re.sub(r'<img[^>]*>', '', p)))[:80]
            items.append([img.group(1), name])
        key = lab.group(1).strip()
        if items:
            groups.setdefault(key, []).extend(i for i in items if i not in groups.get(key, []))
    return groups


def scrape(slug):
    raw = (ROOT / 'site-source' / 'events' / f'{slug}.html').read_text(encoding='utf-8')
    s = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    body = s[s.find('</header>'):s.find('class="footer')]
    d = {'slug': slug}
    m = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    d['name'] = text(m.group(1)) if m else slug
    m = re.search(r'<h4 class="main__title">(.*?)</h4>', body, re.S)
    d['eyebrow'] = text(m.group(1)) if m else ''
    for key, lab in [('dates', 'Дата проведения'), ('place', 'Место проведения')]:
        m = re.search(re.escape(lab) + r'</div>.*?<span class="text">(.*?)</span>', body, re.S)
        d[key] = text(m.group(1)) if m else ''
    m = re.search(r'<img[^>]+src="([^"]+)"[^>]+alt="' + re.escape(d['name'][:8]), body)
    d['promo'] = m.group(1) if m else ''
    # вводный текст — первый абзац elementor до кнопок «Участвовать/Посетить»
    mc = body[body.find('main__content'):]
    mc = mc[:mc.find('Участвовать')] if 'Участвовать' in mc else mc[:6000]
    paras = [text(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', mc, re.S)]
    d['lead'] = [p for p in paras if len(p) > 40]
    d['lists'] = lists(body)
    part = section(body, 'event-participants')
    d['docs'] = [[text(a.group(2)), a.group(1)] for a in re.finditer(r'<a class="text[^"]*" href="([^"]+)"[^>]*>(.*?)</a>', part, re.S)]
    facts = section(body, 'event-few-facts')
    m = re.search(r'<h4[^>]*>(.*?)</h4>', facts, re.S)
    d['facts_title'] = text(m.group(1)) if m else ''
    d['facts'] = [[f.group(1), text(f.group(2)), text(f.group(3))] for f in re.finditer(
        r'data-to="(\d+)"[^>]*>.*?</div>\s*<span class="prefix-to-count">(.*?)</span>.*?<div class="text">(.*?)</div>', facts, re.S)]
    if not d['facts']:  # вариант разметки АгроЭкспоКрым: «200 + успешных компаний»
        d['facts'] = [[a, b, c] for a, b, c in re.findall(r'(\d[\d ]*)\s*(\+|лет)?\s*([а-яё][^0-9]{3,40}?)(?=\s+\d|$)', text(facts))]
    d['videos'] = re.findall(r'<iframe[^>]+src="(https://(?:rutube\.ru/play/embed|www\.youtube\.com/embed|vk\.com/video_ext)[^"]+)"', body)
    loc = section(body, 'event-location')
    m = re.search(r'main__location.*?<span>(.*?)</span>', loc, re.S)
    d['venue_addr'] = text(m.group(1)) if m else d['place']
    m = re.search(r'<a href="([^"]+)"[^>]*>\s*Показать на карте', loc)
    d['venue_map'] = html.unescape(m.group(1)) if m else ''
    d['venue_photos'] = re.findall(r'background-image:\s*url\(([^)]+)\)', loc)
    # длинное описание: заголовки h2 и текст под ними
    long = []
    for h in re.finditer(r'<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|Даю согласие|$)', body, re.S):
        t = text(h.group(1))
        if 'Хотите быть в курсе' in t:
            continue
        items = [text(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', h.group(2), re.S)]
        ps = [text(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', h.group(2), re.S) if text(p)]
        long.append({'h': t, 'p': ps, 'li': [i for i in items if i]})
    d['long'] = long
    d['partners'] = partners(body)
    out = ROOT / 'data' / 'events' / f'{slug}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    return d


if __name__ == '__main__':
    for slug in sys.argv[1:]:
        d = scrape(slug)
        print(f"{slug}: {d['name']} | {d['dates']} | лид {len(d['lead'])} | списки {list(d['lists'])} | док {len(d['docs'])} | цифры {len(d['facts'])} | видео {len(d['videos'])} | фото {len(d['venue_photos'])} | партнёры { {k: len(v) for k, v in d['partners'].items()} } | разделов {len(d['long'])}")
