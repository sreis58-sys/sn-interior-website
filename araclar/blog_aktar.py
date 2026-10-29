"""Eski sitedeki blog yazılarını, S.S.S.'yi ve blog kategorilerini yeni sitenin içerik dosyalarına aktarır.
Kullanım: python blog_aktar.py   (proje kökünden)
Çıktı: src/content/blog/*.md, src/data/sss.json
"""
import json, re, html, os, urllib.request
from playwright.sync_api import sync_playwright

B = "https://sulenuricmimarlik.com.tr"
AYLAR = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, "Temmuz": 7,
         "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")


def inline_md(s):
    s = re.sub(r"<(strong|b)>(.*?)</\1>", r"**\2**", s, flags=re.S)
    s = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", s, flags=re.S)
    s = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "  \n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"[ \t\r\n]+", " ", s)).strip()


def to_md(body):
    out = []
    for m in re.finditer(r"<(h2|h3|h4|p|ul|ol|blockquote)[^>]*>(.*?)</\1>", body, flags=re.S):
        tag, inner = m.group(1), m.group(2)
        if tag in ("ul", "ol"):
            items = re.findall(r"<li[^>]*>(.*?)</li>", inner, flags=re.S)
            out.append("\n".join(("- " if tag == "ul" else f"{i}. ") + inline_md(x) for i, x in enumerate(items, 1)))
        elif tag == "blockquote":
            out.append("> " + inline_md(inner))
        elif tag.startswith("h"):
            out.append("#" * int(tag[1]) + " " + inline_md(inner))
        else:
            t = inline_md(inner)
            if t:
                out.append(t)
    return "\n\n".join(out)


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --- kategoriler: Livewire filtrelerine tıklayarak hangi yazının hangi kategoride olduğunu bul
cats = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(B + "/blog", wait_until="networkidle")
    for idx, name in [(1, "Tasarım İpuçları"), (2, "Trendler")]:
        pg.click(f'[wire\\:click="setCategory({idx})"]')
        pg.wait_for_timeout(2500)
        for h in pg.eval_on_selector_all('a[href*="/blog/"]', "els => els.map(e => e.href)"):
            cats.setdefault(h.split("/blog/")[1].split("?")[0].split("#")[0], name)
    b.close()

# --- yazılar
pages = json.load(open("eski-site/icerik/sayfalar-tam.json", encoding="utf-8"))
urls = [u for u in pages if "/blog/" in u]
os.makedirs("src/content/blog", exist_ok=True)
for u in urls:
    slug = u.rsplit("/", 1)[1]
    s = fetch(u)
    title = html.unescape(re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(desc.group(1)).strip() if desc else ""
    dm = re.search(r"(\d{1,2}) (\w+) (\d{4}) •", s)
    date = f"{dm.group(3)}-{AYLAR[dm.group(2)]:02d}-{int(dm.group(1)):02d}" if dm else "2026-06-01"
    body = re.search(r'<div class="article-content[^"]*">(.*?)</div>\s*</section>', s, re.S).group(1)
    md = to_md(body)
    fm = ["---", f"title: {yaml_str(title)}", f"description: {yaml_str(desc)}", f"date: {date}"]
    if slug in cats:
        fm.append(f"category: {yaml_str(cats[slug])}")
    fm.append("---")
    open(f"src/content/blog/{slug}.md", "w", encoding="utf-8").write("\n".join(fm) + "\n\n" + md + "\n")
    print(date, cats.get(slug, "-"), slug, len(md))

# --- S.S.S.
s = fetch(B + "/sss")
qa = re.findall(r"<button[^>]*>\s*<span[^>]*>(.*?)</span>.*?</button>\s*<div[^>]*>(.*?)</div>\s*</div>", s, re.S)
faq = [{"q": inline_md(q), "a": inline_md(a)} for q, a in qa]
os.makedirs("src/data", exist_ok=True)
json.dump(faq, open("src/data/sss.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(faq), "soru")
