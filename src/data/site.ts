import type { ImageMetadata } from 'astro';
import konut from '../assets/atmosfer/photo-1618221195710-dd6b41faaea6.jpg';
import ticari from '../assets/projeler/yapi-showroom/09.webp';
import uygulama from '../assets/projeler/yapi-showroom/07.webp';
import mobilya from '../assets/projeler/yapi-showroom/08.webp';

export const site = {
  name: 'Sulenur İç Mimarlık',
  short: 'Sulenur',
  url: 'https://sulenuricmimarlik.com.tr',
  description:
    'Sakarya Serdivan merkezli iç mimarlık stüdyosu. Konut ve ticari mekânlar için tasarım, uygulama ve özel üretim.',
  phone: '+90 544 216 41 54',
  phoneHref: 'tel:+905442164154',
  whatsapp: 'https://wa.me/905442164154',
  email: 'sulenuricmimarlik@gmail.com',
  city: 'Serdivan, Sakarya',
  services: ['Tasarım', 'Uygulama', 'Danışmanlık'],
};

export const nav = [
  { href: '/projelerimiz', label: 'Projeler' },
  { href: '/hizmetlerimiz', label: 'Hizmetler' },
  { href: '/surecimiz', label: 'Süreç' },
  { href: '/hakkimizda', label: 'Hakkımızda' },
  { href: '/blog', label: 'Blog' },
  { href: '/iletisim', label: 'İletişim' },
];

export const legal = [
  { href: '/sss', label: 'S.S.S.' },
  { href: '/gizlilik-politikasi', label: 'Gizlilik Politikası' },
  { href: '/kullanim-kosullari', label: 'Kullanım Koşulları' },
];

export type Service = {
  no: string;
  title: string;
  lead: string;
  text: string;
  items: string[];
  image: ImageMetadata;
  alt: string;
};

export const services: Service[] = [
  {
    no: '01',
    title: 'Konut İç Mekân Tasarımı',
    lead: 'Gündelik yaşama uygun, size özel evler.',
    text: 'Yaşam alanınızın her köşesini özenle tasarlıyoruz. Salondan yatak odasına, mutfaktan banyoya kadar tüm mekânlarınız için bütünsel çözümler sunuyoruz.',
    items: ['Salon ve oturma alanları', 'Yatak odası ve banyolar', 'Mutfak tasarımı', 'Çocuk odaları'],
    image: konut,
    alt: 'Ahşap tavanlı, sıcak ışıklı oturma alanı',
  },
  {
    no: '02',
    title: 'Ticari İç Mekân Tasarımı',
    lead: 'Markanızın kimliğini taşıyan mekânlar.',
    text: 'Markanızın kimliğini yansıtan, çalışan ve müşteri deneyimini iyileştiren ofis, mağaza ve yeme-içme mekânları tasarlıyoruz.',
    items: ['Açık ofis düzenleri', 'Toplantı odaları', 'Marka odaklı mağaza', 'Restoran ve kafe'],
    image: ticari,
    alt: 'Yapı Showroom projesinde çalışma masası ve malzeme duvarı',
  },
  {
    no: '03',
    title: 'Uygulama ve Proje Yönetimi',
    lead: 'Çizimden anahtar teslime tek elden.',
    text: 'Konsept tasarımdan teknik projeye, malzeme tedarikinden tadilata ve montaja kadar tüm süreci tek elden yönetiyoruz. Siz onay verirsiniz; koordinasyon, ustalar ve takvim bizim sorumluluğumuzdadır.',
    items: ['Anahtar teslim uygulama', 'Malzeme tedariki', 'Saha koordinasyonu ve denetim', 'Şeffaf bütçe ve takvim'],
    image: uygulama,
    alt: 'Spot ışıklar altında seramik ve doğal taş numune paneli',
  },
  {
    no: '04',
    title: 'Mobilya ve Özel Üretim',
    lead: 'Mekâna ölçülü, projeye özel.',
    text: 'Projeye özel mobilyaları tasarlıyor, üretim ve montaj sürecini de tek elden yönetiyoruz. Korumak istediğiniz eşyaları da yeni tasarıma uyumlu şekilde planlıyoruz.',
    items: ['Ölçüye özel dolap ve mobilya', 'Mutfak ve banyo dolapları', 'Montaj', 'Üretim garantisi'],
    image: mobilya,
    alt: 'Krem mutfak dolapları ve mermer tezgâh arası',
  },
];

export const process = [
  {
    no: '01',
    title: 'Ücretsiz Keşif',
    meta: 'Ücretsiz · bağlayıcı değil',
    text: 'İlk aşamada yaşam tarzınızı, zevklerinizi ve mekândan beklentilerinizi anlamak için detaylı bir analiz yapıyoruz.',
  },
  {
    no: '02',
    title: 'Fiyatlandırma',
    meta: 'Size özel teklif',
    text: 'Tercihlerinize, mekânın boyutlarına ve bütçenize yönelik bir fiyatlandırma hazırlıyoruz.',
  },
  {
    no: '03',
    title: 'Tasarım',
    meta: 'Konutta ortalama 4–8 hafta',
    text: 'Burası ilham ve duygu aşamasıdır. Sizden alınan brifing doğrultusunda mekânın ruhu belirlenir ve 3D modellerle görünür hale getirilir.',
  },
  {
    no: '04',
    title: 'Uygulama ve Teslimat',
    meta: 'Konutta ortalama 6–12 hafta',
    text: 'İşin en çok emek isteyen, tabiri caizse “toz yutulan” kısmı. Kâğıt üzerindeki çizgilerin betona, ahşaba ve demire dönüştüğü; bütçenin, zamanın ve insan yönetiminin devreye girdiği aşama.',
  },
];

export const principles = [
  'Şeffaf bütçe ve takvim planlaması',
  '3D görselleştirmeler ve örnek malzemeler',
  'Teslim sonrası destek ve garanti',
];

export const messages = [
  { title: 'Mekâna karakter.', text: 'Özgün, işlevsel ve dengeli tasarımlar.' },
  { title: 'Detay fark yaratır.', text: 'Her detay, bütünün anlamını güçlendirir.' },
  { title: 'Zamansız mekânlar.', text: 'Bugünün ihtiyaçları, yarının yaşamı için.' },
];

export const reasons = [
  {
    title: 'Kişiselleştirilmiş yaklaşım',
    text: 'Sizi dinliyor, tarzınızı anlıyor ve yaşam alışkanlıklarınıza en uygun estetik çözümleri sunuyoruz. Her proje kendine özgüdür.',
  },
  {
    title: 'Kalite güvencesi',
    text: 'Kaliteli malzemeler ve titiz işçilik anlayışıyla zamana dayanan mekânlar oluşturuyoruz.',
  },
  {
    title: 'Şeffaf süreç',
    text: 'Her aşamada görseller ve düzenli güncellemelerle iletişimde kalıyoruz. Tasarım kararlarını birlikte alıyor, sürprizleri en aza indiriyoruz.',
  },
];
