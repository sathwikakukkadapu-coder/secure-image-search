import re

with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    cur = f.read()

bak_sections = re.findall(r'<section\s+id=[\'\"]([^\'\"]+)[\'\"]', bak)
cur_sections = re.findall(r'<section\s+id=[\'\"]([^\'\"]+)[\'\"]', cur)

print('Sections in BAK:', bak_sections)
print('Sections in CUR:', cur_sections)

bak_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', bak))
cur_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', cur))

missing_funcs = bak_funcs - cur_funcs
print('Missing functions count:', len(missing_funcs))
print('Missing functions:', sorted(list(missing_funcs)))

# Check all element IDs that might be missing
bak_ids = set(re.findall(r'id=[\'\"]([^\'\"]+)[\'\"]', bak))
cur_ids = set(re.findall(r'id=[\'\"]([^\'\"]+)[\'\"]', cur))
missing_ids = bak_ids - cur_ids
print('Missing IDs count:', len(missing_ids))
print('Missing IDs:', sorted(list(missing_ids))[:40])
