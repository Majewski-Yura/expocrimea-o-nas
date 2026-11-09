"""Собирает страницу kontakty/index.html.

Данные — со старой страницы https://expocrimea.com/contacts/ и подвала старого сайта (соцсети).
Форма «Напишите нам» без сервера: собирает письмо и открывает почтовую программу (mailto).
Запуск из корня проекта: python3 -I tools/build_contacts.py, затем typograf по kontakty/index.html.
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_event import ROOT, shared_parts  # noqa: E402

ADDR = 'Республика Крым, г. Симферополь, ул. Киевская, 41, БЦ «ФАБРИКА», офис 322'
ADDR_Q = 'Симферополь, улица Киевская, 41'
MAIL = 'info@expocrimea.com'
PHONES = [('+79789009090', '+7 (978) 900 90 90', ''), ('+74954450208', '+7 (495) 445-02-08', '')]
SOC = [('Телеграм', 'https://t.me/expocrimea/', 'i-tgf'), ('MAX', 'https://max.ru/id9102171932_biz', 'i-max'), ('ВКонтакте', 'https://vk.com/expocrimea', 'i-vk'), ('Rutube', 'https://rutube.ru/channel/42066549/', 'i-play')]

ICONS = '''  <symbol id="i-pin" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></symbol>
  <symbol id="i-vk" viewBox="0 0 24 24"><path d="M12.8 18.2C6.2 18.2 2.4 13.7 2.2 6h3.3c.1 5.6 2.6 8 4.6 8.5V6h3.1v4.9c1.9-.2 3.9-2.4 4.6-4.9h3.1c-.5 3-2.7 5.2-4.3 6.1 1.6.7 4.1 2.6 5 6.1h-3.4c-.7-2.3-2.6-4.1-5-4.4v4.4z"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M5.5 3h13A3.5 3.5 0 0 1 22 6.5v11a3.5 3.5 0 0 1-3.5 3.5h-13A3.5 3.5 0 0 1 2 17.5v-11A3.5 3.5 0 0 1 5.5 3zM10 8.3v7.4l6.2-3.7z"/></symbol>
  <symbol id="i-tgf" viewBox="0 0 24 24"><path d="M21.9 4.6 18.7 19.7c-.2 1.1-.9 1.3-1.8.8l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1 9.2-8.3c.4-.4-.1-.6-.6-.2L6.1 13.2l-4.9-1.5c-1.1-.3-1.1-1.1.2-1.6l19.1-7.4c.9-.3 1.7.2 1.4 1.9z"/></symbol>
  <symbol id="i-max" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12.2 2C6.5 2 2.3 6.1 2.3 11.6c0 2.6.6 4.6 1.5 6.6.5 1.2.1 2.4-.2 3.4-.2.6.4 1.1 1 .8 1.3-.6 2.6-1.4 3.7-1.2 1.2.5 2.5.8 3.9.8 5.6 0 9.9-4.3 9.9-9.6S17.8 2 12.2 2zm.1 5a4.6 4.6 0 1 1 0 9.2 4.6 4.6 0 0 1 0-9.2z"/></symbol>
  <symbol id="i-route" viewBox="0 0 24 24"><circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/></symbol>
'''


def build():
    head, sprite, header, footer, tail = shared_parts()
    sprite = sprite.replace('</svg>', ICONS + '</svg>', 1)
    head = re.sub(r'<title>.*?</title>', '<title>Контакты — ЭКСПОКРЫМ</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="Контакты ЭКСПОКРЫМ: телефон {PHONES[0][1]}, {MAIL}, {ADDR}.">', head)
    header = header.replace(' aria-current="page"', '').replace('<a href="../kontakty/index.html">Контакты', '<a href="../kontakty/index.html" aria-current="page">Контакты', 1)
    phones = '\n'.join(f'            <a class="ct__big" href="tel:{t}">{h}</a>' + (f'<small>{note}</small>' if note else '') for t, h, note in PHONES)
    soc = '\n'.join(f'          <a class="ct-soc rv" href="{u}" target="_blank" rel="noopener"><span class="st__ic"><svg><use href="#{ic}"/></svg></span><b>{n}</b><span class="ct-soc__go"><svg><use href="#i-arrow"/></svg></span></a>' for n, u, ic in SOC)
    route = 'https://yandex.ru/maps/?rtext=~44.953602%2C34.119784'
    # Киевская, 41 — координаты из Яндекс Карт. Виджет Яндекса без Конструктора карт показывает рекламу, поэтому карта OpenStreetMap
    mapsrc = 'https://www.openstreetmap.org/export/embed.html?bbox=34.1128%2C44.9500%2C34.1268%2C44.9572&layer=mapnik&marker=44.953602%2C34.119784'
    ymap = 'https://yandex.ru/maps/?pt=34.119784,44.953602&z=17&l=map'
    html = f'''{head}</head>
<body class="page-contacts">
{sprite}
<div class="progress" aria-hidden="true"></div>
{header}

<main>
  <section class="hero hero-n">
    <div class="container">
      <nav class="crumbs"><a href="../index.html">Главная</a><span>/</span>Контакты</nav>
      <div class="eyebrow">Контакты</div>
      <h1 class="hero__title"><span class="ln" style="--i:0"><span>Всегда</span></span><span class="ln ln--indent" style="--i:1"><span><em>на связи</em></span></span></h1>
    </div>
  </section>

  <section class="ct">
    <div class="container">
      <div class="ct__grid">
        <div class="ct-card ct-card--phone rv">
          <div class="ct-card__h"><span class="st__ic"><svg><use href="#i-phone"/></svg></span>Телефоны</div>
          <div class="ct-card__b">
{phones}
          </div>
        </div>
        <div class="ct-card rv">
          <div class="ct-card__h"><span class="st__ic"><svg><use href="#i-mail"/></svg></span>Почта</div>
          <div class="ct-card__b">
            <a class="ct__big ct__big--mail" href="mailto:{MAIL}">{MAIL}</a>
            <button class="ct__copy" type="button" data-copy="{MAIL}">Скопировать</button>
          </div>
        </div>
        <div class="ct-card rv">
          <div class="ct-card__h"><span class="st__ic"><svg><use href="#i-clock"/></svg></span>Часы работы</div>
          <div class="ct-card__b">
            <span class="ct__big">Пн–Пт 09:00–17:00</span><small>Сб–Вс выходные</small>
            <span class="ct__now" data-open>&nbsp;</span>
          </div>
        </div>
        <div class="ct-card ct-card--addr rv">
          <div class="ct-card__h"><span class="st__ic"><svg><use href="#i-pin"/></svg></span>Офис</div>
          <div class="ct-card__b">
            <span class="ct__addr">{ADDR}</span>
            <a class="lnk" href="{route}" target="_blank" rel="noopener">Построить маршрут<span><svg><use href="#i-arrow"/></svg></span></a>
          </div>
        </div>
      </div>

      <div class="ct__row2">
        <div class="ct-map rv"><iframe data-src="{mapsrc}" title="Офис ЭКСПОКРЫМ на карте" loading="lazy"></iframe><a class="ct-map__open" href="{ymap}" target="_blank" rel="noopener"><svg><use href="#i-pin"/></svg>Открыть в Яндекс Картах</a></div>
        <form class="ct-form rv" id="form" data-mailto="{MAIL}">
          <h2>Напишите нам</h2>
          <p>Ответим в рабочее время. Письмо откроется в вашей почтовой программе.</p>
          <label><span>Имя</span><input name="name" required autocomplete="name"></label>
          <label><span>Телефон</span><input name="phone" type="tel" required autocomplete="tel"></label>
          <label><span>Сообщение</span><textarea name="msg" rows="4"></textarea></label>
          <label class="ct-form__ok"><input type="checkbox" required> <span>Даю согласие на обработку персональных данных</span></label>
          <button class="btn" type="submit">Отправить</button>
        </form>
      </div>

      <div class="ct__soc">
        <div class="part__label rv">Мы в соцсетях</div>
        <div class="ct-socs">
{soc}
        </div>
      </div>

      <a class="ct-req rv" href="../o-nas-v2.html#contacts"><span>Реквизиты компании и документы</span><span class="ct-soc__go"><svg><use href="#i-arrow"/></svg></span></a>
    </div>
  </section>
</main>

{footer}

{tail}
</body>
</html>
'''
    (ROOT / 'kontakty').mkdir(exist_ok=True)
    (ROOT / 'kontakty' / 'index.html').write_text(html, encoding='utf-8')


if __name__ == '__main__':
    build()
    print('ok')
