import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = [(m.start(), m.group()) for m in re.finditer(r'<section id=["\']tab-[^"\']+["\']', text)]
for pos, m in matches:
    line_no = text[:pos].count('\n') + 1
    print(f'Line {line_no}: {m}')
