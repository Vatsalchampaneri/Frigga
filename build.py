#!/usr/bin/env python3
"""Build optimized self-contained FRIGGA homepage."""
import base64, io, re, os
from PIL import Image

SRC = "/home/user/frigga-site"
HTML_IN = os.path.join(SRC, "index.html")
HTML_OUT = os.path.join(SRC, "frigga-homepage.html")
CREAM = (253, 251, 247)

def to_jpeg(path, max_w=700, q=78, bg=CREAM):
    img = Image.open(path)
    if img.mode in ("RGBA","LA","P"):
        if img.mode == "P": img = img.convert("RGBA")
        bgimg = Image.new("RGB", img.size, bg)
        if img.mode in ("RGBA","LA"): bgimg.paste(img, mask=img.split()[-1])
        else: bgimg.paste(img)
        img = bgimg
    elif img.mode != "RGB": img = img.convert("RGB")
    w,h = img.size
    if w > max_w: img = img.resize((max_w, int(h*max_w/w)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"

def to_png(path, max_w=400):
    img = Image.open(path).convert("RGBA")
    w,h = img.size
    if w > max_w: img = img.resize((max_w, int(h*max_w/w)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "PNG", optimize=True)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

with open(HTML_IN, encoding="utf-8") as f: html = f.read()

pat = re.compile(r'src="(images/[^"]+)"')
refs = sorted(set(pat.findall(html)))
print(f"Embedding {len(refs)} images...")
cache = {}
for ref in refs:
    fp = os.path.join(SRC, ref)
    if not os.path.exists(fp): print(f"  MISSING: {ref}"); continue
    fn = os.path.basename(ref)
    if "/icons/" in ref or "/zodiac/" in ref or "frigga-logo" in fn or "destara-logo" in fn or "marites-logo" in fn:
        uri = to_png(fp, 500 if "frigga" in fn else 300)
    elif "hero-bags" in fn:
        uri = to_jpeg(fp, 1400, 82, (240,233,220))
    elif "/nobg/" in ref:
        uri = to_jpeg(fp, 500, 76, CREAM)
    elif fn.startswith("zodiac-"):
        uri = to_jpeg(fp, 400, 75)
    elif fn.startswith("blog-"):
        uri = to_jpeg(fp, 600, 78)
    else:
        uri = to_jpeg(fp, 600, 78)
    cache[ref] = uri
    kb = len(uri)*3//4//1024
    print(f"  {fn:38s} {kb:5d} KB")

html = pat.sub(lambda m: f'src="{cache.get(m.group(1), m.group(0))}"', html)

# Handle CSS background-image url references
bg_pat = re.compile(r"url\('(images/[^']+)'\)")
for m in bg_pat.finditer(html):
    ref = m.group(1)
    fp = os.path.join(SRC, ref)
    if os.path.exists(fp):
        uri = to_jpeg(fp, 1400, 82, (240,233,220))
        html = html.replace(f"url('{ref}')", f"url({uri})")

fav = os.path.join(SRC, "images/flower-logo.png")
if os.path.exists(fav): html = html.replace('href="images/flower-logo.png"', f'href="{to_png(fav, 32)}"')

with open(HTML_OUT, "w", encoding="utf-8") as f: f.write(html)
sz = os.path.getsize(HTML_OUT)
print(f"\nFinal: {sz/1024/1024:.2f} MB -> {HTML_OUT}")
