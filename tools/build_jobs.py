"""Собирает страницу vakansii/index.html.

Вакансии — список JOBS ниже (текст со старой страницы https://expocrimea.com/vakansii/,
латинские буквы-двойники заменены русскими). Шапка и подвал — с главной.
Запуск из корня проекта: python3 -I tools/build_jobs.py, затем typograf по vakansii/index.html.
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, esc, shared_parts  # noqa: E402

PHONE, PHONE_H, MAIL = '+79789009090', '+7 (978) 900-90-90', 'info@expocrimea.com'

JOBS = [{
    'title': 'Специалист по организации выставочных мероприятий',
    'tags': ['Симферополь', 'Полная занятость', '5/2, 09:00–17:00', 'Оклад + премии'],
    'blocks': [
        ('Обязанности', 'i-chat', [
            'Работа с клиентами посредством переговоров',
            'Ведение клиентской базы в CRM (Битрикс24)',
            'Построение партнёрских отношений и работа на выставочных площадях',
        ]),
        ('Требования', 'i-check', [
            'Коммуникабельность и ответственность',
            'Грамотная устная и письменная речь',
            'Приветствуется опыт работы в продажах любого направления',
            'Стрессоустойчивость и умение работать в команде',
        ]),
        ('Условия', 'i-gift', [
            'Оформление согласно ТК РФ',
            'График работы 5/2, с 09:00 до 17:00, суббота и воскресенье — выходные',
            'Официальный оклад и премии',
            'Корпоративное обучение по продуктам, технологиям продаж и работе в программе',
            'Развитая организационная и корпоративная культура, условия для профессионального развития и карьерного роста',
        ]),
    ],
}]

ICONS = '''  <symbol id="i-chat" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></symbol>
'''


def plural(n, f):
    return f[2] if 11 <= n % 100 <= 14 else f[0] if n % 10 == 1 else f[1] if 2 <= n % 10 <= 4 else f[2]


def job_html(j, i):
    tags = ''.join(f'<span>{esc(t)}</span>' for t in j['tags'])
    cols = '\n'.join(f'''          <div class="job__col">
            <div class="job__h"><span class="st__ic"><svg><use href="#{ic}"/></svg></span>{h}</div>
            <ul>{''.join(f'<li>{esc(x)}</li>' for x in items)}</ul>
          </div>''' for h, ic, items in j['blocks'])
    subj = quote('Резюме: ' + j['title'])
    return f'''      <article class="job rv" id="job-{i + 1}">
        <div class="job__top">
          <div>
            <div class="job__n">Вакансия {i + 1:02d}</div>
            <h2 class="job__t">{esc(j['title'])}</h2>
            <div class="job__tags">{tags}</div>
          </div>
          <div class="job__act">
            <a class="btn" href="mailto:{MAIL}?subject={subj}">Отправить резюме</a>
            <a class="btn btn--line" href="tel:{PHONE}">{PHONE_H}</a>
          </div>
        </div>
        <div class="job__cols">
{cols}
        </div>
      </article>'''


def build():
    head, sprite, header, footer, tail = shared_parts()
    sprite = sprite.replace('</svg>', ICONS + '</svg>', 1)
    head = re.sub(r'<title>.*?</title>', '<title>Вакансии — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Вакансии ЭКСПОКРЫМ — организатора выставок и деловых событий в Крыму.">', head)
    header = header.replace(' aria-current="page"', '')
    n = len(JOBS)
    jobs = '\n'.join(job_html(j, i) for i, j in enumerate(JOBS))
    html = f'''{head}</head>
<body class="page-jobs">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span><a href="../o-nas-v2.html">О компании</a><span>/</span>Вакансии</nav>
      <div class="eyebrow">Карьера в ЭКСПОКРЫМ</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Работа</span></span><span class="ln ln--indent" style="--i:1"><span><em>в команде</em></span></span></h1>
      <div class="jobs-h__row">
        <p class="hero-n__lead">Мы с 2010 года проводим выставки и деловые события в Крыму. Присоединяйтесь к команде.</p>
        <a class="jobs-h__cnt" href="#job-1"><b>{n}</b><span>{plural(n, ['открытая вакансия', 'открытые вакансии', 'открытых вакансий'])}</span></a>
      </div>
    </div>
  </section>

  <section class="jl">
    <div class="container">
{jobs}
    </div>
  </section>

  <section class="pcta">
    <div class="container pcta__in">
      <h2 class="h2 rv rv--clip">Как<br><em>откликнуться</em></h2>
      <div class="rv">
        <p>Звоните по номеру {PHONE_H} и отправляйте резюме на {MAIL}.</p>
        <div class="pcta__btns">
          <a class="btn" href="mailto:{MAIL}?subject={quote('Резюме')}">Отправить резюме</a>
          <a class="btn btn--line" href="tel:{PHONE}">{PHONE_H}</a>
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
    (ROOT / 'vakansii').mkdir(exist_ok=True)
    (ROOT / 'vakansii' / 'index.html').write_text(html, encoding='utf-8')


if __name__ == '__main__':
    build()
    print('вакансий:', len(JOBS))
