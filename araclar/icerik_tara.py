"""Eski sitedeki tüm iç sayfaları gezer; metin, başlık ve görsel adreslerini JSON'a yazar.
Kullanım: python -I icerik_tara.py <kok_url> <cikti.json>
"""
import sys, json
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

root, out = sys.argv[1].rstrip("/"), sys.argv[2]
host = urlparse(root).netloc
seen, queue, pages = set(), [root + "/"], {}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    while queue and len(seen) < int(sys.argv[3] if len(sys.argv) > 3 else 80):
        url = queue.pop(0).split("#")[0]
        if url in seen:
            continue
        seen.add(url)
        try:
            pg.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            pages[url] = {"error": str(e)}
            continue
        h = pg.evaluate("document.body.scrollHeight")
        for y in range(0, h, 700):
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(120)
        pg.wait_for_timeout(600)
        info = pg.evaluate("""() => ({
          title: document.title,
          desc: document.querySelector('meta[name=description]')?.content || null,
          headings: [...document.querySelectorAll('h1,h2,h3,h4')].map(h => h.tagName + ': ' + h.innerText.trim()),
          main: (document.querySelector('main') || document.body).innerText,
          imgs: [...new Set([...document.images].map(i => i.currentSrc || i.src).filter(Boolean))],
          bgs: [...new Set([...document.querySelectorAll('*')].map(e => getComputedStyle(e).backgroundImage).filter(s => s && s.startsWith('url(')))],
          links: [...new Set([...document.querySelectorAll('a[href]')].map(a => a.href))]
        })""")
        pages[url] = info
        for l in info["links"]:
            u = urlparse(l)
            if u.netloc == host and not l.startswith("mailto") and not l.startswith("tel"):
                clean = l.split("#")[0].split("?")[0]
                if clean not in seen and clean not in queue:
                    queue.append(clean)
    b.close()

json.dump(pages, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(pages), "sayfa")
for u in pages:
    print(u)
