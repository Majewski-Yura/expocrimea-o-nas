"""Неразрывные пробелы в тексте HTML: короткие слова к следующему, тире к предыдущему,
последнее слово абзаца к предыдущему. Теги, <script> и <style> не трогает.
Запуск: python3 -I tools/typograf.py page.html"""
import re, sys

NB = ' '
SHORT = r'(?:в|во|на|и|а|но|к|ко|с|со|у|о|об|от|до|по|из|за|не|ни|для|без|при|что|как|или|под|над|про|же|ли|бы|мы|их|все|это|г\.|ул\.)'
BLOCK_END = re.compile(r'</(p|blockquote|figcaption|div|dd|li|h1|h2|h3|h4|span)>')


def fix(t):
    if not t.strip():
        return t
    for _ in range(2):  # дважды — для цепочек вроде «и в»
        t = re.sub(r'(?<![\wА-Яа-яЁё])(' + SHORT + r') (?=\S)', lambda m: m.group(1) + NB, t, flags=re.I)
    t = re.sub(r' (—|–)', NB + r'\1', t)
    t = re.sub(r'(\d) (\d{3})', r'\1' + NB + r'\2', t)
    return t


def main(path):
    s = open(path, encoding='utf-8').read()
    parts = re.split(r'(<script.*?</script>|<style.*?</style>|<[^>]+>)', s, flags=re.S)
    out = []
    for k, part in enumerate(parts):
        if part.startswith('<'):
            out.append(part)
            continue
        t = fix(part)
        nxt = parts[k + 1] if k + 1 < len(parts) else ''
        if BLOCK_END.match(nxt) and len(t.split()) > 3:
            t = re.sub(r' (\S{1,12})(\s*)$', NB + r'\1\2', t)
        out.append(t)
    open(path, 'w', encoding='utf-8').write(''.join(out))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        main(p)
