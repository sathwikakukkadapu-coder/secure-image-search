import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

sections = re.findall(r'id=["\']([^"\']+)["\']', text)
key_ids = [s for s in sections if any(k in s.lower() for k in ['tab', 'panel', 'view', 'nav', 'search', 'result', 'drop', 'metric', 'chart', 'modal', 'vault', 'user'])]
print(f"Total element IDs: {len(sections)}")
print(f"Key semantic IDs: {len(key_ids)}")
print("\nSample Key IDs:")
for i in key_ids[:50]:
    print(f" - {i}")
