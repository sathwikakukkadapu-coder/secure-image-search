with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

# Find script tag
script_start = bak.rfind('<script>')
print(f"Script starts around character {script_start}, length: {len(bak) - script_start}")
print("Last 1000 chars of script:")
print(bak[-1000:])
