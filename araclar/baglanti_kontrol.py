"""Üretim çıktısındaki (dist/) tüm sayfaları tarar: kırık iç link, eksik anchor, boş href,
bulunamayan görsel/srcset kaynağı, alt özniteliği olmayan görsel, yinelenen id.
Kullanım: python araclar/baglanti_kontrol.py   (proje kökünden, npm run build sonrası)
"""
import os, re, html
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

DIST = "dist"


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.srcs, self.ids, self.imgs_no_alt, self.empty = [], [], [], 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a":
            h = a.get("href")
            if h is None or h.strip() in ("", "#"):
                self.empty += 1
            else:
                self.links.append(h)
        if tag in ("img", "source"):
            if tag == "img" and "alt" not in a:
                self.imgs_no_alt += 1
            for k in ("src", "srcset"):
                if a.get(k):
                    for part in a[k].split(","):
                        self.srcs.append(part.strip().split(" ")[0])
        if tag == "link" and a.get("rel") in ("icon", "preload", "stylesheet") and a.get("href"):
            self.srcs.append(a["href"])
        if tag == "script" and a.get("src"):
            self.srcs.append(a["src"])


def resolve(path):
    path = unquote(path.split("#")[0].split("?")[0])
    if path in ("", "/"):
        return os.path.join(DIST, "index.html")
    p = os.path.join(DIST, path.lstrip("/"))
    for cand in (p, p + ".html", os.path.join(p, "index.html")):
        if os.path.isfile(cand):
            return cand
    return None


pages = {}
for root, _, files in os.walk(DIST):
    for f in files:
        if f.endswith(".html"):
            fp = os.path.join(root, f)
            pr = P()
            pr.feed(open(fp, encoding="utf-8").read())
            pages[os.path.normpath(fp)] = pr

problems = []
for fp, pr in pages.items():
    rel = fp[len(DIST) + 1:]
    dup = {i for i in pr.ids if pr.ids.count(i) > 1}
    if dup:
        problems.append(f"{rel}: yinelenen id {sorted(dup)[:5]}")
    if pr.empty:
        problems.append(f"{rel}: {pr.empty} boş href")
    if pr.imgs_no_alt:
        problems.append(f"{rel}: {pr.imgs_no_alt} görselde alt yok")
    for h in pr.links:
        u = urlparse(h)
        if u.scheme in ("mailto", "tel", "http", "https") and u.netloc not in ("", "sulenuricmimarlik.com.tr"):
            continue
        if u.scheme in ("mailto", "tel"):
            continue
        if h.startswith("#"):
            target = fp
        else:
            target = resolve(u.path)
            if not target:
                problems.append(f"{rel}: kırık link {h}")
                continue
            target = os.path.normpath(target)
        if u.fragment and target in pages and u.fragment not in pages[target].ids:
            problems.append(f"{rel}: anchor yok {h}")
    for s in pr.srcs:
        if s.startswith(("http", "data:")):
            continue
        if not resolve(s):
            problems.append(f"{rel}: kaynak yok {s}")

print(f"{len(pages)} sayfa tarandı, {sum(len(p.links) for p in pages.values())} link, "
      f"{sum(len(p.srcs) for p in pages.values())} kaynak.")
print("\n".join(problems[:60]) if problems else "Sorun yok.")
