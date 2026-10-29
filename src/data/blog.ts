import type { ImageMetadata } from 'astro';
import { getCollection, type CollectionEntry } from 'astro:content';

import k1 from '../assets/atmosfer/photo-1618221195710-dd6b41faaea6.jpg';
import k2 from '../assets/atmosfer/photo-1600607687939-ce8a6c25118c.jpg';
import k3 from '../assets/atmosfer/photo-1616486338812-3dadae4b4ace.jpg';
import k4 from '../assets/atmosfer/photo-1598928506311-c55ded91a20c.jpg';
import k5 from '../assets/atmosfer/photo-1588854337221-4cf9fa96059c.jpg';
import k6 from '../assets/atmosfer/photo-1503174971373-b1f69850bded.jpg';
import k7 from '../assets/projeler/yatak-odasi/02.webp';
import k8 from '../assets/projeler/yatak-odasi/03.webp';
import t1 from '../assets/projeler/yapi-showroom/09.webp';
import t2 from '../assets/projeler/yapi-showroom/10.webp';
import t3 from '../assets/projeler/yapi-showroom/01.webp';
import t4 from '../assets/projeler/yapi-showroom/03.webp';
import m1 from '../assets/projeler/yapi-showroom/07.webp';
import m2 from '../assets/projeler/yapi-showroom/05.webp';
import m3 from '../assets/projeler/yapi-showroom/02.webp';
import m4 from '../assets/projeler/yapi-showroom/04.webp';

export type Post = CollectionEntry<'blog'>;

const pools: Record<Post['data']['category'], { src: ImageMetadata; alt: string }[]> = {
  Konut: [
    { src: k1, alt: 'Ahşap tavanlı, sıcak ışıklı oturma alanı' },
    { src: k2, alt: 'Ahşap kaplama duvarlı açık plan yaşam alanı' },
    { src: k3, alt: 'Açık tonlu, sade dekore edilmiş salon' },
    { src: k4, alt: 'Kasetli tavanı ve şömine duvarıyla aydınlık salon' },
    { src: k5, alt: 'Beyaz dolaplı, ada tezgâhlı mutfak' },
    { src: k6, alt: 'Geniş cam cepheli oturma alanı' },
    { src: k7, alt: 'Boydan boya gardırop duvarı ve yatak' },
    { src: k8, alt: 'Vitrin dolabı ve avizeli yatak odası köşesi' },
  ],
  Ticari: [
    { src: t1, alt: 'Malzeme duvarı önünde çalışma masası ve oturma grubu' },
    { src: t2, alt: 'Raf duvarı ve toplantı köşesi' },
    { src: t3, alt: 'Lavabo ve armatür sergisi' },
    { src: t4, alt: 'Mermer adalı açık mutfak sergisi' },
  ],
  'Malzeme & Teknik': [
    { src: m1, alt: 'Seramik ve doğal taş numune paneli' },
    { src: m2, alt: 'Koyu damarlı mermer ada ve aydınlatılmış nişler' },
    { src: m3, alt: 'Taş tezgâhlı ada ve ahşap kapı' },
    { src: m4, alt: 'Damarlı mermer ada ve sıcak ışıklı raflar' },
  ],
};

function hash(s: string) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function postImage(post: Post) {
  const pool = pools[post.data.category];
  return pool[hash(post.id) % pool.length];
}

/** Tarihli yazılar yeniden eskiye, tarihsizler en sonda (başlığa göre). */
export async function getPosts() {
  const posts = await getCollection('blog');
  return posts.sort((a, b) => {
    const da = a.data.date?.getTime() ?? 0;
    const db = b.data.date?.getTime() ?? 0;
    return db - da || a.data.title.localeCompare(b.data.title, 'tr');
  });
}

export const formatDate = (d?: Date) =>
  d ? d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }) : '';

export function readingTime(body = '') {
  const words = body.split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}

export const categories = ['Konut', 'Ticari', 'Malzeme & Teknik'] as const;
