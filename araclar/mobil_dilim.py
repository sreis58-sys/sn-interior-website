import sys
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True, device_scale_factor=1)
    pg = ctx.new_page(); pg.goto(url, wait_until="networkidle", timeout=60000)
    H = pg.evaluate("document.body.scrollHeight")
    for y in range(0, H, 400):
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(150)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(800)
    # hide sticky header so it doesn't repeat in clips
    i = 0
    for y in range(844, H, 1700):
        pg.screenshot(path=f"{out}/m_{i}.png", full_page=True, clip={"x":0,"y":y,"width":390,"height":min(1700,H-y)}); i += 1
    print(H, i)
