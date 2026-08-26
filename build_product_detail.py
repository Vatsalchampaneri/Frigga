#!/usr/bin/env python3
"""Build optimized self-contained FRIGGA product detail page (Incepta-style PDP)."""
import base64, io, re, os
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
HTML_IN = os.path.join(SRC, "product-detail.html")
HTML_OUT = os.path.join(SRC, "frigga-product-detail.html")
CREAM = (253, 251, 247)

def to_jpeg(path, max_w=800, q=80, bg=CREAM):
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "P"):
        if img.mode == "P": img = img.convert("RGBA")
        bgimg = Image.new("RGB", img.size, bg)
        if img.mode in ("RGBA", "LA"): bgimg.paste(img, mask=img.split()[-1])
        else: bgimg.paste(img)
        img = bgimg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if w > max_w: img = img.resize((max_w, int(h * max_w / w)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"

def to_png(path, max_w=400):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    if w > max_w: img = img.resize((max_w, int(h * max_w / w)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

with open(HTML_IN, encoding="utf-8") as f:
    html = f.read()

pat = re.compile(r'src="(images/[^"]+)"')
js_pat = re.compile(r"'(images/[^']+)'")
refs = sorted(set(pat.findall(html)) | set(js_pat.findall(html)))
print(f"Embedding {len(refs)} images...")
cache = {}
for ref in refs:
    fp = os.path.join(SRC, ref)
    if not os.path.exists(fp):
        print(f"  MISSING: {ref}")
        continue
    fn = os.path.basename(ref)
    if "logo" in fn:                       # logos → keep transparency
        uri = to_png(fp, 500 if "frigga" in fn else 300)
    elif "/thumbs/" in ref:                # gallery thumbs → tiny
        uri = to_jpeg(fp, 160, 72)
    elif "/zodiac/icons/" in ref:          # zodiac selector icons → tiny
        uri = to_jpeg(fp, 96, 72)
    elif "/products/" in ref and "rhino-pendant-" in fn:  # gallery mains → 800px
        uri = to_jpeg(fp, 800, 80)
    else:                                  # related-product cards → 500px
        uri = to_jpeg(fp, 500, 76)
    cache[ref] = uri
    kb = len(uri) * 3 // 4 // 1024
    print(f"  {fn:38s} {kb:5d} KB")

html = pat.sub(lambda m: f'src="{cache.get(m.group(1), m.group(0))}"', html)

# JS gallery array references (single-quoted) — e.g. IMGS=['images/...','images/...']
js_pat = re.compile(r"'(images/[^']+)'")
html = js_pat.sub(lambda m: f"'{cache.get(m.group(1), m.group(1))}'", html)

# favicon
fav = os.path.join(SRC, "images/frigga-logo-dark.png")
if os.path.exists(fav):
    html = html.replace('href="images/frigga-logo-dark.png"', f'href="{to_png(fav, 48)}"')

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)
sz = os.path.getsize(HTML_OUT)
print(f"\nFinal: {sz/1024/1024:.2f} MB -> {HTML_OUT}")
