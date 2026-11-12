with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'<div id="resultsContainer"[^>]*>([\s\S]*?)</div>\s*<!--', html)
if matches:
    print("Inside resultsContainer:")
    print(matches[0][:800])
else:
    print("resultsContainer not matched with regex")
