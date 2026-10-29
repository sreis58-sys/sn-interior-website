import sys, json
from playwright.sync_api import sync_playwright

url = sys.argv[1]
out = sys.argv[2]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp, mobile in [("desktop", {"width": 1440, "height": 900}, False),
                             ("mobile", {"width": 390, "height": 844}, True)]:
        ctx = b.new_context(viewport=vp, device_scale_factor=1, is_mobile=mobile, has_touch=mobile)
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(2500)
        # scroll to trigger lazy content
        h = pg.evaluate("document.body.scrollHeight")
        for y in range(0, h, 600):
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(150)
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(1000)
        pg.screenshot(path=f"{out}/{name}_fold.png")
        pg.screenshot(path=f"{out}/{name}_full.png", full_page=True)
        if name == "desktop":
            info = pg.evaluate("""() => ({
              title: document.title,
              desc: document.querySelector('meta[name=description]')?.content,
              height: document.body.scrollHeight,
              headings: [...document.querySelectorAll('h1,h2,h3')].map(h=>h.tagName+': '+h.innerText.trim()).slice(0,60),
              links: [...new Set([...document.querySelectorAll('a')].map(a=>a.href))].slice(0,80),
              fonts: [...new Set([...document.querySelectorAll('body *')].slice(0,800).map(e=>getComputedStyle(e).fontFamily))].slice(0,15),
              imgs: document.images.length,
              generator: document.querySelector('meta[name=generator]')?.content,
              text: document.body.innerText.slice(0,6000)
            })""")
            json.dump(info, open(f"{out}/info.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("height", info["height"])
        ctx.close()
    b.close()
