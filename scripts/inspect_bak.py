with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
sections = re.findall(r'<section\s+id=[\'"]([^\'"]+)[\'"]', bak)
print('All tabs in bak:', sections)

# Print lines where each section starts
lines = bak.splitlines()
for idx, line in enumerate(lines):
    for s in sections:
        if f'id="{s}"' in line or f"id='{s}'" in line:
            print(f"Section {s} starts at line {idx+1}")
