with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

lines = bak.splitlines()
print(f"Total lines in bak: {len(lines)}")

# Let's inspect line ranges
import re
sections = [
    'tab-overview',
    'tab-search',
    'tab-evaluation',
    'tab-privacy',
    'tab-security',
    'tab-index',
    'tab-settings'
]

ranges = {}
for i, l in enumerate(lines):
    for s in sections:
        if f'id="{s}"' in l or f"id='{s}'" in l:
            ranges[s] = i

for s in sections:
    print(f"Tab {s}: line {ranges.get(s, -1) + 1}")
