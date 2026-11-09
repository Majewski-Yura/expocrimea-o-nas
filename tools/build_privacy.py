"""Собирает страницу politika/index.html — политика обработки персональных данных.

Текст — со старой страницы https://expocrimea.com/privacy-policy/ (site-source/docs/privacy-policy.html),
переносится без изменений смысла: только собран в разделы, кавычки заменены на «ёлочки».
Запуск из корня проекта: python3 -I tools/build_privacy.py, затем typograf по politika/index.html.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, esc, shared_parts  # noqa: E402


def parse():
    s = (ROOT / 'site-source/docs/privacy-policy.html').read_text(encoding='utf-8')
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>', '', s, flags=re.S)
    b = s[s.find('</header>'):s.find('class="subscribe')]
    if 'class="dialog"' in b:
        b = b[:b.find('class="dialog"')]
    t = html.unescape(re.sub(r'<[^>]+>', '\n', b))
    lines = [re.sub(r'\s+', ' ', x).strip() for x in t.split('\n')]
    lines = [x for x in lines if x and x != 'Политика конфиденциальности' and not x.startswith('<')]
    paras = []
    closed = False  # после заголовка раздела следующая строка — новый абзац
    for x in lines:
        new = re.match(r'^(\d+\.(\d+\.)*\s|[–—•-]\s)', x)
        if new or not paras or closed:
            paras.append(x)
            closed = bool(re.match(r'^\d+\.\s+[А-ЯЁA-Z]', x)) and len(x) < 120
        else:
            sep = '' if x[0] in '.,;:)' else ' '
            paras[-1] += sep + x
    sections = []
    for p in paras:
        p = p.replace('“', '«').replace('”', '»').replace('"', '»')
        m = re.match(r'^(\d+)\.\s+(.+)$', p)
        if m and not re.match(r'^\d+\.\d', p) and len(p) < 120:
            sections.append({'n': m.group(1), 'h': m.group(2), 'items': []})
        elif sections:
            sections[-1]['items'].append(p)
    return sections


def linkify(x):
    x = esc(x)
    x = re.sub(r'https://expocrimea\.com/?(privacy-policy/)?', lambda m: f'<a href="../politika/index.html">{m.group(0)}</a>' if m.group(1) else f'<a href="../index.html">{m.group(0)}</a>', x)
    x = x.replace('info@expocrimea.com', '<a href="mailto:info@expocrimea.com">info@expocrimea.com</a>')
    return x


def build():
    secs = parse()
    toc = '\n'.join(f'            <a href="#p{s["n"]}"><b>{int(s["n"]):02d}</b>{esc(s["h"])}</a>' for s in secs)
    body = []
    for s in secs:
        items = []
        for it in s['items']:
            m = re.match(r'^(\d+\.\d+(?:\.\d+)*\.)\s+(.*)$', it)
            if m:
                items.append(f'<p><b class="pp__n">{m.group(1)}</b> {linkify(m.group(2))}</p>')
            elif re.match(r'^[–—•-]\s', it):
                items.append(f'<p class="pp__li">{linkify(it[2:])}</p>')
            else:
                items.append(f'<p>{linkify(it)}</p>')
        body.append(f'''        <section class="pp__s" id="p{s['n']}">
          <h2><span>{int(s['n']):02d}</span>{esc(s['h'])}</h2>
          {''.join(items)}
        </section>''')

    head, sprite, header, footer, tail = shared_parts()
    head = re.sub(r'<title>.*?</title>', '<title>Политика конфиденциальности — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Политика обработки персональных данных ООО «ЭКСПОКРЫМ».">', head)
    header = header.replace(' aria-current="page"', '')
    page = f'''{head}</head>
<body class="page-pp">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Политика конфиденциальности</nav>
      <div class="eyebrow">Персональные данные</div>
      <h1 class="hero__title pp__title"><span class="ln" style="--i:0"><span>Политика</span></span><span class="ln" style="--i:1"><span><em>конфиденциальности</em></span></span></h1>
      <p class="hero-n__lead">Как ООО «ЭКСПОКРЫМ» обрабатывает и защищает персональные данные посетителей сайта — в соответствии с Федеральным законом № 152‑ФЗ «О персональных данных».</p>
    </div>
  </section>

  <section class="pp">
    <div class="container pp__grid">
      <aside class="pp__toc">
        <div class="pp__toc-in">
          <small>Содержание</small>
          <nav>
{toc}
          </nav>
          <a class="pp__ask" href="mailto:info@expocrimea.com?subject=%D0%92%D0%BE%D0%BF%D1%80%D0%BE%D1%81%20%D0%BF%D0%BE%20%D0%BF%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%BC%20%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D0%BC">Вопрос по данным: info@expocrimea.com</a>
        </div>
      </aside>
      <div class="pp__body">
{chr(10).join(body)}
      </div>
    </div>
  </section>
</main>

{footer}

{tail}
</body>
</html>
'''
    (ROOT / 'politika').mkdir(exist_ok=True)
    (ROOT / 'politika' / 'index.html').write_text(page, encoding='utf-8')
    return [(s['n'], s['h'], len(s['items'])) for s in secs]


if __name__ == '__main__':
    for x in build():
        print(*x)
