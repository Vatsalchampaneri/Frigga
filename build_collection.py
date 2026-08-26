#!/usr/bin/env python3
import base64, io, os, re
from PIL import Image

SRC = '/home/user/frigga-site'
CREAM = (253,251,247)
cache = {}

def to_data(path, size=400, q=82):
    if path in cache: return cache[path]
    full = os.path.join(SRC, path)
    img = Image.open(full)
    if img.mode in ('RGBA','LA','P'):
        if img.mode=='P': img=img.convert('RGBA')
        bg = Image.new('RGB', img.size, CREAM)
        if img.mode in ('RGBA','LA'): bg.paste(img, mask=img.split()[-1])
        else: bg.paste(img)
        img = bg
    elif img.mode != 'RGB': img=img.convert('RGB')
    w,h=img.size
    c=min(w,h)
    img=img.crop(((w-c)//2,(h-c)//2,(w+c)//2,(h+c)//2))
    img=img.resize((size,size),Image.LANCZOS)
    buf=io.BytesIO(); img.save(buf,'JPEG',quality=q,optimize=True)
    data=f'data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}'
    cache[path]=data
    return data

products = [
    ('new','New','PENDANTS','Rhino & Elephant / Anti-Robbery Pendant','Protection · Anti-Robbery','P3,280',5,34,'images/nobg/na-rhino-pendant.png'),
    ('new','New','AMULETS','Annual Protection Amulet','Protection · Annual Luck','P2,680',5,28,'images/nobg/na-annual-amulet.png'),
    ('new','New','BRACELETS','Dragon Bracelet','Success · Power','P1,680',5,52,'images/nobg/na-dragon-bracelet.png'),
    ('new','New','HOME & DECOR','Gold Dragon Display','Prosperity · Yang Energy','P2,980',4,19,'images/nobg/na-gold-dragon.png'),
    ('new','New','PENDANTS','Destiny Spinner','Manifestation · Focus','P2,880',5,41,'images/nobg/na-destiny-spinner.png'),
    ('new','New','SHAWLS','Astrology 9 Mantra Shawl','Confidence · Fame','P5,280',5,67,'images/nobg/na-astrology-shawl.png'),
    ('new','New','BRACELETS','9 Mantra Charms Bracelet','Protection · Balance','P6,980',5,76,'images/nobg/9-mantra-bracelet.png'),
    ('best','Best Seller','LUCKY BAGS','Lucky Wealth Bag','Abundance · Protection','P4,980',5,127,'images/nobg/lucky-wealth-bag.png'),
]

def stars(n): return '★'*n+'☆'*(5-n)

cards = []
for badge, bt, cat, name, tags, price, rating, reviews, img in products:
    i = to_data(img)
    cards.append(f'''<article class="pcard">
  <div class="pcard-media">
    <span class="pcard-badge {badge}">{bt}</span>
    <button class="pcard-wish" aria-label="Wishlist"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>
    <a href="frigga-product.html" class="pcard-photo"><img src="{i}" alt="{name}" loading="lazy"></a>
  </div>
  <div class="pcard-body">
    <div class="pcard-cat">{cat}</div>
    <a href="frigga-product.html" class="pcard-name">{name}</a>
    <div class="pcard-tags">{tags}</div>
    <div class="pcard-foot">
      <div class="pcard-price">{price}</div>
      <div class="pcard-stars">{stars(rating)} <span>({reviews})</span></div>
    </div>
    <a href="frigga-product.html" class="pcard-btn"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Add to Cart</a>
  </div>
</article>''')

cards_html = '\n'.join(cards)

with open(os.path.join(SRC,'collection.html')) as f: html=f.read()

new_css = '''/* Product grid — seamless square cards */
.product-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding:8px 0 40px}
.pcard{background:transparent;border-radius:0;overflow:visible;transition:var(--t);display:flex;flex-direction:column}
.pcard:hover{transform:translateY(-5px)}
.pcard-media{position:relative;width:100%;aspect-ratio:1;background:var(--cream);border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(11,61,46,.05)}
.pcard:hover .pcard-media{box-shadow:0 12px 32px rgba(11,61,46,.12)}
.pcard-badge{position:absolute;top:12px;left:12px;z-index:5;padding:5px 13px;font-size:9.5px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;border-radius:20px;color:var(--w)}
.pcard-badge.best{background:var(--gold)}.pcard-badge.new{background:var(--gm)}.pcard-badge.limited{background:#8b4513}
.pcard-wish{position:absolute;top:10px;right:10px;z-index:6;width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center;color:var(--tm);opacity:0;transition:var(--t);border:none;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.pcard:hover .pcard-wish{opacity:1}.pcard-wish:hover{color:#e74c3c}.pcard-wish svg{stroke:currentColor;fill:none}
.pcard-photo{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.pcard-photo img{width:85%;height:85%;object-fit:contain;transition:transform .4s ease}
.pcard:hover .pcard-photo img{transform:scale(1.05)}
.pcard-body{padding:14px 4px 8px}
.pcard-cat{font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--goldd);margin-bottom:4px}
.pcard-name{font-family:var(--serif);font-size:17px;font-weight:600;color:var(--td);line-height:1.3;display:block;margin-bottom:4px}
.pcard-tags{font-size:12px;color:var(--goldd);margin-bottom:10px}
.pcard-foot{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.pcard-price{font-size:19px;font-weight:700;color:var(--gd)}
.pcard-stars{color:var(--gold);font-size:13px;letter-spacing:1px}.pcard-stars span{color:var(--tm);font-size:11px;margin-left:4px}
.pcard-btn{display:flex;align-items:center;justify-content:center;gap:6px;padding:11px;background:var(--gd);color:var(--w);font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;border-radius:8px;transition:var(--t)}
.pcard-btn:hover{background:var(--goldd)}.pcard-btn svg{stroke:currentColor;fill:none}
@media(max-width:1024px){.product-grid{grid-template-columns:repeat(3,1fr);gap:18px}}
@media(max-width:768px){.product-grid{grid-template-columns:repeat(2,1fr);gap:14px}.pcard-wish{opacity:1}.pcard-name{font-size:15px}.pcard-price{font-size:17px}.pcard-body{padding:10px 2px 8px}}
@media(max-width:480px){.product-grid{gap:10px}.pcard-cat{font-size:9px}.pcard-name{font-size:13.5px}.pcard-tags{font-size:10.5px;margin-bottom:8px}.pcard-price{font-size:15px}.pcard-stars{font-size:11px}.pcard-btn{padding:9px;font-size:10px}.pcard-badge{font-size:8px;padding:4px 10px;top:8px;left:8px}}'''

pat = r'/\* Product grid.*?\.pcard-btn:hover\{[^}]+\}'
html = re.sub(pat, new_css, html, flags=re.DOTALL)
if 'seamless square cards' not in html:
    html = html.replace('</style>', new_css + '\n</style>')

grid_pat = r'<div class="product-grid"[^>]*>.*?</div>\s*</section>'
m = re.search(grid_pat, html, re.DOTALL)
if m:
    html = html[:m.start()] + f'<div class="product-grid">\n{cards_html}\n  </div>\n</section>' + html[m.end():]

html = re.sub(r'<script>\s*// Product data.*?</script>', '', html, flags=re.DOTALL)

def emb(m):
    p=m.group(1)
    if p.startswith('data:'): return m.group(0)
    return f'src="{to_data(p,300,70)}"'
html = re.sub(r'src="(images/[^"]+)"', emb, html)

out = os.path.join(SRC,'frigga-collection.html')
with open(out,'w') as f: f.write(html)
print(f'Done: {os.path.getsize(out)/1024/1024:.2f} MB | {len(cards)} cards | {len(cache)} images')
