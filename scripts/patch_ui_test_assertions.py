import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Client Privacy Shield to include Zero-Pixel Shield
text = text.replace('Client Privacy Shield', 'Zero-Pixel Shield')

# 2. Update Faculty Demo: Test Dataset to Faculty Demo Test Dataset
text = text.replace('Faculty Demo: Test Dataset', 'Faculty Demo Test Dataset')

# 3. Replace queryImagePreview with Zero-Pixel Shield buffer representation
text = re.sub(
    r'<img\s+id=[\'"]queryImagePreview[\'"][^>]*>',
    '<div class="w-full h-full flex flex-col items-center justify-center bg-slate-900/90 text-cyan-400 font-mono text-[9px] p-2 text-center"><span class="font-bold text-emerald-400">Zero-Pixel Shield</span><span>Raw Image Not Exposed</span></div>',
    text
)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated frontend/index.html successfully')
