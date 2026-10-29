"""Yeni siteyi farklı genişliklerde gezer: tam sayfa ekran görüntüsü, konsol hataları, yatay taşma kontrolü.
Kullanım: python yeni_site_test.py <taban_url> <cikti_klasoru> <yol1,yol2,...> [genislik1,genislik2,...] [--intro]
"""
import sys, os, json
from playwright.sync_api import sync_playwright

base, out, paths = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3].split(",")
widths = [int(w) for w in (sys.argv[4].split(",") if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else ["1440", "390"])]
keep_intro = "--intro" in sys.argv
os.makedirs(out, exist_ok=True)
report = {}

with sync_playwright() as p:
    b = p.chromium.launch()
    for w in widths:
        mobile = w < 800
        ctx = b.new_context(viewport={"width": w, "height": 900 if w >= 800 else 844},
                            device_scale_factor=1, is_mobile=mobile, has_touch=mobile)
        if not keep_intro:
            ctx.add_init_script("try{sessionStorage.setItem('sn-intro','1')}catch(e){}")
        pg = ctx.new_page()
        errors = []
        pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        for path in paths:
            errors.clear()
            pg.goto(base + path, wait_until="networkidle")
            pg.wait_for_timeout(600)
            h = pg.evaluate("document.documentElement.scrollHeight")
            for y in range(0, h, 500):
                pg.evaluate(f"window.scrollTo(0,{y})")
                pg.wait_for_timeout(90)
            pg.wait_for_timeout(1200)
            pg.evaluate("window.scrollTo(0,0)")
            pg.wait_for_timeout(900)
            overflow = pg.evaluate("""() => {
              const W = document.documentElement.clientWidth; const bad = [];
              document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect();
                if (r.right > W + 1 && getComputedStyle(el).position !== 'fixed' && r.width > 0) bad.push(el.tagName + '.' + (el.className.baseVal ?? el.className).toString().slice(0,40) + ' ' + Math.round(r.right)); });
              return { scrollW: document.documentElement.scrollWidth, W, bad: bad.slice(0, 8) };
            }""")
            name = (path.strip("/").replace("/", "_") or "index") + f"_{w}"
            pg.screenshot(path=f"{out}/{name}.png", full_page=True)
            report[name] = {"errors": list(errors), "overflow": overflow}
            print(name, "hata:", len(errors), "taşma:", overflow["scrollW"] > overflow["W"], errors[:3])
        ctx.close()
    b.close()
json.dump(report, open(f"{out}/rapor.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
