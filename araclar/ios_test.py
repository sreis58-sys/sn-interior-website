"""iOS Safari (WebKit) ve maske geometrisi senaryoları.
Kullanım: python ios_test.py <taban_url>
"""
import sys
from playwright.sync_api import sync_playwright

base = sys.argv[1].rstrip("/")
ok = lambda name, cond, extra="": print(("TAMAM " if cond else "HATA  ") + name + (f"  [{extra}]" if extra else ""))
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")

# Satır maskesi: başlangıç durumunda her satırın gerçek mürekkep alanı maskenin tamamen dışında mı?
# (glif kutusu yerine güvenli tahmin: span'in üst kenarı + aksan payı 0.35em, maskenin alt kenarından aşağıda olmalı)
MASK_JS = """(sel) => [...document.querySelectorAll(sel)].map(line => {
  const span = line.firstElementChild; const m = line.getBoundingClientRect(); const s = span.getBoundingClientRect();
  const fs = parseFloat(getComputedStyle(span).fontSize);
  return { ok: (s.top - 0.35 * fs) >= m.bottom - 0.5, gap: Math.round(s.top - 0.35 * fs - m.bottom) };
})"""

with sync_playwright() as p:
    errs = []
    # --- 1) Maske geometrisi: hero başlamadan ve sayfa başlıkları açılmadan önce
    for engine_name in ("chromium", "webkit"):
        engine = getattr(p, engine_name)
        b = engine.launch()
        for w in (390, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 844 if w < 800 else 900})
            pg = ctx.new_page()
            # JS'yi geciktirip başlangıç durumunu yakala: intro yokken hero iki rAF sonra açılır
            pg.add_init_script("sessionStorage.setItem('sn-intro','1'); window.__raf = window.requestAnimationFrame;"
                               "window.requestAnimationFrame = () => 0;")
            pg.goto(base + "/", wait_until="load")
            pg.wait_for_timeout(400)
            res = pg.evaluate(MASK_JS, "[data-hero] .line")
            ok(f"{engine_name} {w}px hero satırları başlangıçta maskenin dışında", all(r["ok"] for r in res), [r["gap"] for r in res])
            pg.goto(base + "/hakkimizda", wait_until="load")
            pg.wait_for_timeout(200)
            # başlık görünür alanda olduğu için hemen açılır; başlangıç durumunu geçişsiz geri kur ve ölç
            pg.add_style_tag(content="*{transition:none!important}")
            pg.evaluate("document.querySelectorAll(\"[data-reveal='lines']\").forEach(e => e.classList.remove('is-in'))")
            res = pg.evaluate(MASK_JS, "[data-reveal='lines'] .line")
            ok(f"{engine_name} {w}px sayfa başlığı başlangıçta maskenin dışında", all(r["ok"] for r in res), [r["gap"] for r in res][:4])
            ctx.close()
        b.close()

    # --- 2) iPhone WebKit: menü kaydırma kilidi, geri dönüş, yön değişimi
    b = p.webkit.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, user_agent=UA)
    ctx.add_init_script("sessionStorage.setItem('sn-intro','1')")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "/", wait_until="load")
    pg.wait_for_timeout(600)
    pg.evaluate("window.scrollTo(0, 1700)")
    pg.wait_for_timeout(200)
    pg.evaluate("window.scrollTo(0, 1500)")  # yukarı kaydırma gizlenen başlığı geri getirir
    pg.wait_for_timeout(700)
    pg.click("[data-menu-toggle]")
    pg.wait_for_timeout(900)
    ok("menü açıkken gövde sabit", pg.evaluate("getComputedStyle(document.body).position") == "fixed")
    pg.evaluate("window.scrollBy(0, 600)")
    pg.wait_for_timeout(300)
    ok("menü açıkken arka plan kaymıyor", pg.evaluate("window.scrollY") == 0 and pg.evaluate("document.body.style.top") == "-1500px")
    pg.set_viewport_size({"width": 844, "height": 390})  # yan çevirme
    pg.wait_for_timeout(500)
    ok("yatay konumda menü açık ve görünür", pg.evaluate("document.documentElement.classList.contains('menu-open')"))
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(400)
    pg.click("[data-menu-toggle]")
    pg.wait_for_timeout(900)
    y = pg.evaluate("window.scrollY")
    ok("menü kapanınca eski konuma dönülüyor", abs(y - 1500) < 4, y)
    pg.click("[data-menu-toggle]")
    pg.wait_for_timeout(800)
    pg.click("#site-menu a[href='/surecimiz']")
    pg.wait_for_url("**/surecimiz", timeout=6000)
    pg.wait_for_timeout(900)
    ok("menüden gezinme: yeni sayfa en üstte, gövde serbest",
       pg.evaluate("window.scrollY") < 5 and pg.evaluate("document.body.style.position") == "")
    pg.go_back()
    pg.wait_for_url(base + "/", timeout=6000)
    pg.wait_for_timeout(1200)
    stuck = pg.evaluate("[...document.querySelectorAll('[data-reveal]')].filter(e=>!e.classList.contains('is-in') && e.getBoundingClientRect().height>0 && e.getBoundingClientRect().top < innerHeight).length")
    ok("geri dönüşte görünür alanda takılı öğe yok", stuck == 0, stuck)
    # hızlı aşağı/yukarı yön değişimleri
    for yy in (4000, 800, 6500, 200, 9000, 0):
        pg.evaluate(f"window.scrollTo(0,{yy})")
        pg.wait_for_timeout(40)
    pg.wait_for_timeout(1200)
    stuck = pg.evaluate("[...document.querySelectorAll('[data-reveal]')].filter(e=>!e.classList.contains('is-in') && e.getBoundingClientRect().height>0 && e.getBoundingClientRect().bottom < innerHeight).length")
    ok("hızlı yön değişimlerinden sonra yukarıda takılı öğe yok", stuck == 0, stuck)
    ok("telefonda paralaks dönüşümü yok", pg.evaluate("getComputedStyle(document.querySelector('[data-parallax]')).transform") in ("none", ""))
    ok("telefonda dekoratif çizgi gizli", pg.evaluate("getComputedStyle(document.querySelector('.curve')).display") == "none")
    ctx.close()

    # --- 3) Masaüstü → telefon yeniden boyutlandırma
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("sessionStorage.setItem('sn-intro','1')")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "/", wait_until="load")
    pg.wait_for_timeout(500)
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(500)
    ok("yeniden boyutlandırmada taşma yok", not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"))
    ctx.close()
    b.close()
    print("sayfa hataları:", errs or "yok")
