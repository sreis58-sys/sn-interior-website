import sys
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width":1440,"height":900})
    pg.goto(url, wait_until="networkidle", timeout=60000)
    H = pg.evaluate("document.body.scrollHeight")
    for y in range(0, H, 600):
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(200)
    pg.wait_for_timeout(1500)
    i = 0
    for y in range(900, H, 1350):
        pg.screenshot(path=f"{out}/d_{i}.png", full_page=True, clip={"x":0,"y":y,"width":1440,"height":min(1350,H-y)}); i += 1
    print(H, i)
