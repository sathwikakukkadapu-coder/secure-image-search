with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

lines = bak.splitlines()

for i, l in enumerate(lines):
    if 'function switchTab' in l:
        print(f"switchTab starts at line {i+1}")
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1}: {lines[j]}")
        break
