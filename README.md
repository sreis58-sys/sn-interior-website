# Sulenur İç Mimarlık — web sitesi

Astro 7 ile üretilen statik site. Çıktı (`dist/`) her türlü hostinge yüklenebilir.

## Komutlar

```bash
npm install        # bağımlılıklar
npm run dev        # geliştirme sunucusu → http://localhost:4321
npm run build      # tip kontrolü + üretim çıktısı → dist/
npm run preview    # üretim çıktısını yerelde dene
```

## İçerik

| Ne | Nerede |
|---|---|
| Projeler | `src/content/projeler/*.md` — görseller `src/assets/projeler/<proje>/` |
| Blog yazıları | `src/content/blog/*.md` (70 yazı eski siteden aktarıldı) |
| S.S.S. | `src/data/sss.json` |
| İletişim bilgileri, menü, hizmetler, süreç, ilkeler | `src/data/site.ts` |
| Blog yazılarının görsel havuzu | `src/data/blog.ts` |

Yeni proje eklemek için mevcut bir `.md` dosyasını kopyalayıp görsel yollarını ve `order` değerini değiştirmek yeterli.
Proje sayfasındaki fotoğraf dizilimi (tam genişlik → küçük detay → ikili → büyük kırpma) galeri sırasına göre otomatik kurulur.

## İletişim formu

Statik sitede sunucu tarafı yok. `.env` dosyasında `PUBLIC_FORM_ENDPOINT` tanımlanırsa (Formspree, Web3Forms
veya kendi PHP betiğiniz) form JSON olarak oraya gönderilir. Tanımlı değilse ziyaretçinin e-posta uygulaması
doldurulmuş mesajla açılır.

## Yayına alma

- Adresler eski siteyle aynı (`/hakkimizda`, `/projelerimiz/yapi-showroom`, `/blog/...`), Google sıralamaları korunur.
- Apache / LiteSpeed paylaşımlı hostingde `public/.htaccess` uzantısız adresleri `.html` dosyalarına yönlendirir.
- Netlify, Vercel, Cloudflare Pages gibi servislerde ek ayar gerekmez.

## Tasarım sistemi

- Token'lar (renk, tipografi, boşluk, hareket): `src/styles/global.css` başı
- Hareket sabitleri ve tek rAF döngüsü: `src/scripts/motion.ts`
- Tekrar kullanılan parçalar: `Lines` (satır satır başlık), `Media` (maske/paralaks görsel), `Curve` (mercan çizgi),
  `ProjectFigure`, `ServicesExplorer`, `ProcessTrack`, `BlogCard`, `PageIntro`
- `prefers-reduced-motion` açıkken paralaks, imleç, maskeler ve sayfa geçişleri kapanır.

## Testler

```bash
python araclar/yeni_site_test.py http://localhost:4321 <klasör> /,/blog 1440,390   # ekran görüntüsü + hata + taşma
python araclar/etkilesim_test.py http://localhost:4321 <klasör>                    # açılış, geçiş, menü, filtre, form…
python araclar/ios_test.py http://localhost:4321                                   # Safari (WebKit): menü kilidi, geri dönüş, maske geometrisi
python araclar/tam_sayfa.py http://localhost:4321/ 390 <önek> --webkit             # tam sayfa dilimleri + takılı öğe sayımı
python araclar/baglanti_kontrol.py                                                 # dist/: kırık link, anchor, görsel, alt metni
```

Python scriptlerini `-I` olmadan çalıştırın; Git Bash'te URL argümanı için `MSYS_NO_PATHCONV=1` gerekir.

## Kırılım stratejisi

- **≥1280** tam masaüstü kolaj · **1024–1279** aynı kolaj, ayarlı sütunlar
- **768–1023** tablet: ofsetli dikey akış, hizmetlerde görsel solda/metin sağda
- **<768** telefon: tek sütun, paralaks ve dekoratif çizgi yok, kısa hareket profili

Bölüm boşlukları tek ölçekten gelir: `--space-section` (standart) ve `--space-section-l` (editoryal anlar).
