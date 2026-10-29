"""Tam sayfa görsel QA: sayfayı açar, hızlı + yavaş kaydırır, takılı kalan reveal'ları sayar,
tam sayfa görüntüyü okunabilir dilimlere böler.
Kullanım: python tam_sayfa.py <url> <genislik> <cikti_oneki> [--webkit] [--dilim 1800] [--hizli]
  --webkit : Safari motoru + iPhone ayarları (dokunmatik, mobil viewport)
  --hizli  : yavaş kaydırma yok; en alta zıplayıp takılı kalan öğe var mı bakar
"""
import sys
from playwright.sync_api import sync_playwright

url, width, prefix = sys.argv[1], int(sys.argv[2]), sys.argv[3]
webkit = "--webkit" in sys.argv
fast = "--hizli" in sys.argv
tile = int(sys.argv[sys.argv.index("--dilim") + 1]) if "--dilim" in sys.argv else (1800 if width >= 800 else 1500)
mobile = width < 800

with sync_playwright() as p:
    engine = p.webkit if webkit else p.chromium
    b = engine.launch()
    opts = dict(viewport={"width": width, "height": 844 if mobile else 900}, device_scale_factor=1)
    if mobile:
        opts.update(is_mobile=True, has_touch=True)
    if webkit and mobile:
        opts["user_agent"] = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
                              "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
    ctx = b.new_context(**opts)
    ctx.add_init_script("try{sessionStorage.setItem('sn-intro','1')}catch(e){}")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(500)
    H = pg.evaluate("document.documentElement.scrollHeight")
    if fast:
        pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        pg.wait_for_timeout(250)
        pg.evaluate("window.scrollTo(0, 0)")
    else:
        for y in range(0, H, 350):
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(60)
    pg.wait_for_timeout(1500)
    stuck = pg.evaluate("""() => [...document.querySelectorAll('[data-reveal]')].filter(e => !e.classList.contains('is-in') && e.getBoundingClientRect().height > 0)
        .map(e => e.tagName + '.' + String(e.className).slice(0, 40))""")
    hidden_text = pg.evaluate("""() => [...document.querySelectorAll('h1,h2,h3,p,a')].filter(e => {
        const r = e.getBoundingClientRect(); if (!r.width || !r.height) return false;
        const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && parseFloat(cs.opacity) === 0;
      }).length""")
    over = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(600)
    H = pg.evaluate("document.documentElement.scrollHeight")
    n = 0
    for y in range(0, H, tile):
        pg.screenshot(path=f"{prefix}_{n:02d}.png", full_page=True,
                      clip={"x": 0, "y": y, "width": width, "height": min(tile, H - y)})
        n += 1
    print(f"{url} @{width}{' webkit' if webkit else ''}: yükseklik={H} dilim={n} takılı={len(stuck)} "
          f"opak0={hidden_text} taşma={over} hata={errs[:3]} {stuck[:4]}")
    b.close()
