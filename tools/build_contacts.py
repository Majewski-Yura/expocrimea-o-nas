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
SOC = [('Телеграм', 'https://t.me/expocrimea/', 'i-tg'), ('ВКонтакте', 'https://vk.com/expocrimea', 'i-vk'), ('Rutube', 'https://rutube.ru/channel/42066549/', 'i-play')]

ICONS = '''  <symbol id="i-pin" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></symbol>
  <symbol id="i-vk" viewBox="0 0 24 24"><path d="M3 7h3.2c.4 3.6 2 5.5 3.3 5.9V7h3v3.4c1.3-.1 2.6-1.7 3.1-3.4h2.9c-.4 2.1-1.9 3.8-3 4.5 1.1.5 2.9 2 3.5 4.5h-3.2c-.5-1.6-1.8-2.8-3.3-3V16h-.4C6.9 16 3.2 13 3 7z"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="4"/><path d="m10 9 5 3-5 3z"/></symbol>
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
    mapsrc = 'https://yandex.ru/map-widget/v1/?ll=34.119784%2C44.953602&z=16&pt=34.119784%2C44.953602%2Cpm2rdl'  # Киевская, 41 — координаты из Яндекс Карт
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
        <div class="ct-map rv"><iframe data-src="{mapsrc}" title="Офис ЭКСПОКРЫМ на карте" loading="lazy" allowfullscreen></iframe></div>
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
