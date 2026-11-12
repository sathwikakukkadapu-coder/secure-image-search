import os

index_html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
with open(index_html_path, "r", encoding="utf-8") as f:
    text = f.read()

target = """      const previewImg = document.getElementById('queryImagePreview');
      if (previewImg) previewImg.src = "";"""

replacement = """      const testSelect = document.getElementById('testDatasetSelect');
      if (testSelect) testSelect.value = "";"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("clearQuery updated successfully.")
else:
    print("Already updated or not found.")
