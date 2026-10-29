"""Bir sayfadan seçilen bölümlerin ekran boyutunda görüntüsünü alır.
Kullanım: python kareler.py <url> <genislik> <cikti_oneki> <secici1|secici2|...> [--intro] [--wait ms]
Seçici yerine 'top' ilk ekranı verir. Her seçici için öğe ekranın üstüne kaydırılır.
"""
import sys
from playwright.sync_api import sync_playwright

url, width, prefix, sels = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4].split("|")
intro = "--intro" in sys.argv
wait = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 2200
mobile = width < 800
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": width, "height": 900 if not mobile else 844}, is_mobile=mobile, has_touch=mobile)
    if not intro:
        ctx.add_init_script("try{sessionStorage.setItem('sn-intro','1')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(url, wait_until="networkidle")
    # dev araç çubuğunu gizle
    pg.add_style_tag(content="astro-dev-toolbar{display:none!important}")
    for i, s in enumerate(sels):
        if s != "top":
            pg.evaluate("(s)=>{const e=document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - 40)}", s)
        pg.wait_for_timeout(wait if i == 0 or s != "top" else 300)
        pg.screenshot(path=f"{prefix}_{i}.png")
    b.close()
