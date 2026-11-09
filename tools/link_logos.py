"""Делает логотипы в бегущих строках ссылками на сайты партнёров и чистит их подписи.

Адреса берутся из site-source/partners/partners.json (страница партнёров старого сайта),
из страниц мероприятий старого сайта (подпись под логотипом) и из словаря MANUAL ниже.
Запуск из корня проекта после сборки страниц: python3 -I tools/link_logos.py index.html o-nas-v2.html events/*.html
Логотипы без известного адреса остаются без ссылки; их список печатается.
"""
import glob
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent

# Короткие названия с главной и из «О компании» → официальные сайты
MANUAL = {
    'Минпромторг России': 'https://minpromtorg.gov.ru/',
    'Минстрой России': 'https://minstroyrf.gov.ru/',
    'Министерство здравоохранения Российской Федерации': 'https://minzdrav.gov.ru/',
    'Министерство обороны Российской Федерации': 'https://mil.ru/',
    'Федеральная служба войск национальной гвардии Российской Федерации': 'https://rosgvard.ru/',
    'Министерство сельского хозяйства Российской Федерации': 'https://mcx.gov.ru/',
    'Государственный совет Республики Крым': 'http://crimea.gov.ru/',
    'Минпромторг Крыма': 'https://minprom.rk.gov.ru/',
    'Минсельхоз Республики Крым': 'https://msh.rk.gov.ru/',
    'Главное управление МЧС России по Республике Крым': 'https://82.mchs.gov.ru/',
    'Министерство экономического развития Республики Крым': 'https://minek.rk.gov.ru/',
    'Совет министров Республики Крым': 'https://rk.gov.ru/',
    'Министерство здравоохранения Республики Крым': 'https://mzdrav.rk.gov.ru/',
    'Министерство курортов и туризма Республики Крым': 'https://mtur.rk.gov.ru/',
    'РСПП': 'https://rspp.ru/',
    'КФУ им. В. И. Вернадского': 'https://cfuv.ru/',
}


def clean(n):
    n = html.unescape(n).replace('\xa0', ' ')
    n = re.sub(r'^[>\s]+', '', n)
    n = re.sub(r'\s*<.*$', '', n)
    n = re.sub(r'^(Официальный сайт|Сайт|сайт)\s+', '', n)
    words = n.split()
    half = len(words) // 2  # «Вести Крым Вести Крым» → «Вести Крым»
    if half and words[:half] == words[half:2 * half]:
        n = ' '.join(words[:half])
    return n.replace('“', '«').replace('”', '»').strip()


def norm(n):
    return re.sub(r'[^а-яёa-z0-9]', '', clean(n).lower())


def root_if_article(u):
    """Ссылку на статью заменяем главной страницей сайта."""
    p = urlsplit(u.strip())
    if re.search(r'/(news|article|\d{4}/\d\d)/', p.path):
        return f'{p.scheme}://{p.netloc}/'
    return u.strip()


def url_map():
    m = {}
    for k, v in MANUAL.items():
        m[norm(k)] = v
    for i in json.loads((ROOT / 'site-source/partners/partners.json').read_text(encoding='utf-8')):
        if i['url']:
            m.setdefault(norm(i['name']), root_if_article(i['url']))
    for f in glob.glob(str(ROOT / 'site-source/events/*.html')):
        s = Path(f).read_text(encoding='utf-8')
        for blk in re.findall(r'<div class="partner">(.*?)</div>\s*</div>\s*</div>\s*</div>', s, re.S):
            t = re.search(r'<div class="text"><a href="([^"]+)"[^>]*>(.*?)</a>', blk, re.S)
            if t and 'expocrimea' not in t.group(1):
                m.setdefault(norm(t.group(2)), root_if_article(t.group(1)))
    return m


def process(path, m, missing):
    s = Path(path).read_text(encoding='utf-8')

    def repl(x):
        tag, img, alt, tail = x.group(1), x.group(2), x.group(3), x.group(4)
        name = clean(alt)
        img = img.replace(f'alt="{alt}"', f'alt="{html.escape(name)}"')
        img = re.sub(r'title="[^"]*"', f'title="{html.escape(name)}"', img)
        u = m.get(norm(name))
        if not u:
            missing.add(name)
            return f'<div class="plogo">{img}</div>'
        return f'<a class="plogo" href="{html.escape(u)}" target="_blank" rel="noopener">{img}</a>'
    s2 = re.sub(r'<(div|a) class="plogo"[^>]*>(<img[^>]*alt="([^"]*)"[^>]*>)</(div|a)>', repl, s)
    Path(path).write_text(s2, encoding='utf-8')
    return s2.count('<a class="plogo"'), s2.count('class="plogo"')


if __name__ == '__main__':
    m = url_map()
    missing = set()
    for f in sys.argv[1:]:
        print(f, *process(f, m, missing))
    print('без адреса:', len(missing))
    for n in sorted(missing):
        print('  ', n)
