with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

lines = bak.splitlines()

for j in range(260, 310):
    print(f"{j+1}: {lines[j]}")
