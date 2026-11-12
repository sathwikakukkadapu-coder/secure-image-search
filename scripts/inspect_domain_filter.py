with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'let\s+currentDomainFilter\s*=[^;]+;', html)
print(matches)

matches2 = re.findall(r'function onDomainFilterChange[\s\S]*?^  }', html, re.MULTILINE)
if matches2:
    print(matches2[0])
