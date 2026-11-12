with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

lines = bak.splitlines()

# Let's inspect tab-search lines (around 667 to 1082)
tab_search_lines = lines[666:1082]
print(f"tab-search line count: {len(tab_search_lines)}")
print("First 30 lines of tab-search:")
for l in tab_search_lines[:30]:
    print(l)
