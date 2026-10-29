"""Yeni sitenin etkileşimlerini uçtan uca dener ve ara ekran görüntüleri alır.
Kullanım: python etkilesim_test.py <taban_url> <cikti_klasoru>
"""
import sys, os
from playwright.sync_api import sync_playwright

base, out = sys.argv[1].rstrip("/"), sys.argv[2]
os.makedirs(out, exist_ok=True)
ok = lambda name, cond: print(("TAMAM " if cond else "HATA  ") + name)
HIDE = "astro-dev-toolbar{display:none!important}"

with sync_playwright() as p:
    b = p.chromium.launch()
    errors = []

    # 1) Açılış: ilk ziyarette görünür, ~1.5 sn sonra kalkar; ikinci sayfada tekrar etmez
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(base + "/", wait_until="commit")
    pg.wait_for_selector(".intro", state="attached")
    pg.wait_for_timeout(500)
    ok("açılış ilk ziyarette görünüyor", pg.evaluate("document.documentElement.classList.contains('intro')"))
    pg.screenshot(path=f"{out}/intro_500ms.png")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{out}/intro_1200ms.png")
    pg.wait_for_timeout(900)
    ok("açılış 1.6 sn içinde kalkıyor", not pg.evaluate("document.documentElement.classList.contains('intro')"))
    ok("hero açıldı", pg.evaluate("document.querySelector('[data-hero]').classList.contains('is-in')"))

    # 2) Proje tıklaması → paylaşılan görsel geçişi → detay
    pg.evaluate("document.querySelector('.works').scrollIntoView()")
    pg.wait_for_timeout(1500)
    pg.click(".works__a")
    pg.wait_for_timeout(350)
    pg.screenshot(path=f"{out}/gecis_350ms.png")
    pg.wait_for_url("**/projelerimiz/yapi-showroom", timeout=5000)
    pg.wait_for_timeout(1500)
    ok("proje detayına geçildi", "Yapı Showroom" in pg.title())
    ok("JS işareti geçişten sonra korunuyor", pg.evaluate("document.documentElement.classList.contains('js')"))
    ok("açılış ikinci sayfada tekrar etmiyor", not pg.evaluate("document.documentElement.classList.contains('intro')"))
    pg.screenshot(path=f"{out}/detay.png")

    # 3) Sonraki proje bağlantısı
    pg.evaluate("document.querySelector('.next').scrollIntoView()")
    pg.wait_for_timeout(900)
    pg.click(".next")
    pg.wait_for_url("**/projelerimiz/yatak-odasi", timeout=5000)
    pg.wait_for_timeout(1200)
    ok("sonraki proje açıldı", "Yatak Odası" in pg.title())

    # 4) Hizmetler hover
    pg.goto(base + "/hizmetlerimiz")
    pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('[data-services]').scrollIntoView()")
    pg.wait_for_timeout(800)
    pg.hover("#hizmet-03 .sx__btn")
    pg.wait_for_timeout(1300)
    active = pg.evaluate("[...document.querySelectorAll('[data-service-img]')].findIndex(e=>e.classList.contains('is-active'))")
    ok("hizmet hover görseli değiştiriyor", active == 2)
    pg.screenshot(path=f"{out}/hizmet_hover.png")

    # 5) Proje filtresi
    pg.goto(base + "/projelerimiz")
    pg.wait_for_timeout(1200)
    pg.click("button[data-filter='Ticari']")
    pg.wait_for_timeout(900)
    visible = pg.evaluate("[...document.querySelectorAll('#proje-listesi .row')].filter(r=>!r.hidden).length")
    ok("Ticari filtresi 1 proje gösteriyor", visible == 1)
    pg.screenshot(path=f"{out}/filtre.png")

    # 6) Blog filtresi
    pg.goto(base + "/blog")
    pg.wait_for_timeout(1000)
    pg.click("#arsiv button[data-filter='Konut']")
    pg.wait_for_timeout(600)
    vis = pg.evaluate("[...document.querySelectorAll('.index-list li')].filter(r=>!r.hidden).length")
    ok(f"blog Konut filtresi ({vis} yazı)", 0 < vis < 67)

    # 7) Akordeon
    pg.goto(base + "/sss")
    pg.wait_for_timeout(1000)
    pg.click("#faq-q-0")
    pg.wait_for_timeout(900)
    ok("S.S.S. açılıyor", pg.evaluate("document.getElementById('faq-0').hasAttribute('data-open') && document.getElementById('faq-0').getBoundingClientRect().height > 20"))
    pg.click("#faq-q-0")
    pg.wait_for_timeout(900)
    ok("S.S.S. kapanıyor", pg.evaluate("document.getElementById('faq-0').getBoundingClientRect().height < 2"))

    # 8) Form doğrulama
    pg.goto(base + "/iletisim")
    pg.wait_for_timeout(1000)
    pg.click("[data-contact-form] button[type=submit]")
    pg.wait_for_timeout(400)
    ok("boş form hata gösteriyor", pg.evaluate("document.getElementById('cf-name').getAttribute('aria-invalid')") == "true")
    ok("ilk hatalı alana odaklanıyor", pg.evaluate("document.activeElement.id") == "cf-name")
    pg.evaluate("document.querySelector('[data-contact-form]').scrollIntoView()")
    pg.screenshot(path=f"{out}/form_hata.png")
    pg.fill("#cf-name", "Test Kişi")
    pg.fill("#cf-email", "test@ornek.com")
    pg.fill("#cf-message", "Salon ve mutfak yenilemesi düşünüyoruz.")
    pg.check("input[name=consent]")
    # uç nokta tanımlı değilse form mailto: ile e-posta uygulamasını açar
    pg.click("[data-contact-form] button[type=submit]")
    pg.wait_for_timeout(500)
    status = pg.inner_text("[data-form-status]")
    ok(f"geçerli form gönderiliyor → '{status[:50]}'", "açıldı" in status or "Teşekkürler" in status)
    ctx.close()

    # 9) Mobil menü
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    ctx.add_init_script("sessionStorage.setItem('sn-intro','1')")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(base + "/")
    pg.add_style_tag(content=HIDE)
    pg.wait_for_timeout(800)
    pg.click("[data-menu-toggle]")
    pg.wait_for_timeout(1300)
    ok("mobil menü açılıyor", pg.evaluate("document.documentElement.classList.contains('menu-open')"))
    ok("menü açıkken içerik inert", pg.evaluate("document.querySelector('main').inert"))
    pg.screenshot(path=f"{out}/mobil_menu.png")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(300)
    ok("Esc menüyü kapatıyor", not pg.evaluate("document.documentElement.classList.contains('menu-open')"))
    pg.click("[data-menu-toggle]")
    pg.wait_for_timeout(900)
    pg.click("#site-menu a[href='/blog']")
    pg.wait_for_url("**/blog", timeout=5000)
    pg.wait_for_timeout(1200)
    ok("menüden gezinme + menü kapanıyor", not pg.evaluate("document.documentElement.classList.contains('menu-open')") and not pg.evaluate("document.querySelector('main').inert"))
    ok("dokunmatikte özel imleç yok", not pg.evaluate("document.documentElement.classList.contains('has-cursor')"))
    ctx.close()

    # 10) Azaltılmış hareket
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(base + "/")
    pg.wait_for_timeout(700)
    pg.add_style_tag(content=HIDE)
    ok("azaltılmış harekette imleç yok", not pg.evaluate("document.documentElement.classList.contains('has-cursor')"))
    pg.evaluate("document.querySelector('.works').scrollIntoView()")
    pg.wait_for_timeout(300)
    ok("azaltılmış harekette içerik hemen görünür", pg.evaluate("getComputedStyle(document.querySelector('.works__a .media__inner')).clipPath") in ("none", ""))
    ctx.close()

    print("sayfa hataları:", errors or "yok")
    b.close()
