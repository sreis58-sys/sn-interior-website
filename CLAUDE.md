# Şulenur İç Mimarlık — web sitesi yenileme

Kroki uygulamasıyla hiçbir ilgisi yok; o projeye dokunma, ondan bahsetme.

## Durum (2026-10-15)
- Eski site: https://sulenuricmimarlik.com.tr/ — Hakan Tahta yapmış. Admin paneli var (adresi ve kapsamı henüz bilinmiyor). Kaynak koda erişim belirsiz.
- Yeni marka kimliği: `marka/marka-kimligi.png`
- Eski sitenin ekran görüntüleri: `eski-site/ekran-goruntuleri/` (d_* masaüstü, m_* mobil dilimler)
- İnceleme notları: `eski-site/inceleme.md`
- Ekran görüntüsü scriptleri: `araclar/` — Python: `C:\Users\msali\AppData\Local\Programs\Python\Python312\python.exe` (Playwright kurulu, `-I` ile çalıştırma)

## RAFA KALDIRILDI (2026-10-15)
Kullanıcı projeyi şimdilik durdurdu. Son durum: site hazır, build temiz, testler geçiyor; bir Netlify önizlemesi
(rainbow-biscotti-fe1786.netlify.app) yüklendi ama son QA turundaki `dist` oraya yüklenmedi. Kullanıcı memnun kalmadı;
dönünce önce neyin olmadığını sor. Bekleyenler: gerçek logo, kendi fotoğraflar, Instagram, ticari iddiaların teyidi,
yasal metinlerin hukuk kontrolü, form uç noktası.

## Yeni site (2026-10-15'te kuruldu)
- Astro 7 statik site, kökte (`src/`, `public/`). Ayrıntılar `README.md`'de. Eski kaynak kod yok; içerik canlı siteden tarandı (`araclar/icerik_tara.py`, `araclar/blog_aktar.py`, ham veri `eski-site/icerik/`).
- Fontlar: başlık Newsreader (Canela yerine, açık lisans), metin Satoshi (yerel `public/fonts/`).
- Ultramarin olarak panoya yakın `#2443D6` kullanıldı; #2E64FE dijitalde fazla parlak.
- Logo henüz tipografik geçici monogram (`src/components/Monogram.astro`) — vektör logo gelince değiştir.
- "15+ yıl / 50+ ekip / 5+ ödül / ödüllü ekip" iddiaları doğrulanmadığı için sitede yok.
- Yasal metinler (gizlilik/KVKK, kullanım koşulları) taslak — hukukçu kontrolü gerekli.
- Python scriptleri `-I` OLMADAN çalıştır (Playwright kullanıcı site-packages'ta). Git Bash'te URL argümanı için `MSYS_NO_PATHCONV=1`.

## Yeni kimlik
- Renkler: Koyu Gri #2B2B2B, Taş #D7C9B2, Kemik #F4EFEA, Açık Gri #E5E5E5, Ultramarin #2E64FE (panodaki renk daha koyu görünüyor — netleştir), Mercan #E7664F
- Fontlar: Canela (başlık, ücretli — web lisansı gerekir), Satoshi (metin, ücretsiz)
- Grafik dil: logodan türeyen ince çizgi, mimari kemer formları, doğal ışık/gölge, keskin köşeler, taş/ahşap dokular
- Mesajlar: "Mekân insanla tamamlanır", "Mekâna karakter", "Detay fark yaratır", "Zamansız mekanlar"
- Pano yapay zekâyla üretilmiş görünüyor; logo varyantlarında yazım hataları var → temiz vektör logo lazım. İsim: "Şulenur" mu "Sulenur" mu netleştir.

## Bekleyen sorular
- Admin panel adresi ve neler yönetiliyor (proje, blog, galeri, metin)?
- Kaynak kod Hakan Tahta'dan alınabilir mi?
- Kendi proje fotoğrafları/render'ları var mı?
- Sitedeki "15+ yıl, 50+ ekip, 5+ ödül" bilgileri doğru mu?
