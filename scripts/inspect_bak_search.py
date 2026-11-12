with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

lines = bak.splitlines()

# Search for runContentFreeSearch in lines
for i, l in enumerate(lines):
    if 'function runContentFreeSearch' in l:
        print(f"runContentFreeSearch starts at line {i+1}")
        for j in range(i, min(i+120, len(lines))):
            print(f"{j+1}: {lines[j]}")
        break
