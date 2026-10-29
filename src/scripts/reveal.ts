import { MOTION, clamp, isDesktop, isTablet, onScroll, prefersReduced, type Cleanup } from './motion';

/** [data-reveal] öğeleri görünür alana girince bir kez açılır. */
export function initReveal(): Cleanup {
  const els = document.querySelectorAll<HTMLElement>('[data-reveal]:not([data-hero] [data-reveal])');
  if (prefersReduced() || !('IntersectionObserver' in window)) {
    els.forEach((el) => el.classList.add('is-in'));
    return () => {};
  }
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        }
      }
    },
    // Üst sınır sonsuz: ekranın üstünde kalan (hızlı kaydırmada atlanan, sayfa ortasında yenilenen)
    // öğeler de "görünür" sayılır; hiçbir şey gizli durumda takılı kalmaz.
    { rootMargin: '100000px 0px -8% 0px', threshold: 0 },
  );
  els.forEach((el) => io.observe(el));
  return () => io.disconnect();
}

/**
 * Hafif paralaks: görsel içeriğe göre biraz daha yavaş akar.
 * Yalnızca ekranda olan öğeler hesaplanır.
 */
export function initParallax(): Cleanup {
  // Telefonlarda paralaks yok (CSS de dönüşümü kapatır)
  if (prefersReduced() || !isTablet()) return () => {};
  const els = [...document.querySelectorAll<HTMLElement>('[data-parallax]')];
  if (!els.length) return () => {};

  const visible = new Set<HTMLElement>();
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) visible.add(e.target as HTMLElement);
      else visible.delete(e.target as HTMLElement);
    }
  });
  els.forEach((el) => io.observe(el));

  const strength = isDesktop() ? MOTION.parallax : MOTION.parallax * 0.5;
  const values = new Map<HTMLElement, number>();
  const stop = onScroll({
    read() {
      const vh = window.innerHeight;
      visible.forEach((el) => {
        const r = el.getBoundingClientRect();
        const p = clamp((r.top + r.height / 2 - vh / 2) / vh, -0.9, 0.9);
        values.set(el, -p * r.height * strength);
      });
    },
    write() {
      values.forEach((v, el) => el.style.setProperty('--py', `${v.toFixed(1)}px`));
      values.clear();
    },
  });
  return () => {
    stop();
    io.disconnect();
  };
}

/** Mercan çizgiler kaydırmayla birlikte çizilir (scroll-jacking yok, yalnızca ilerleme okunur). */
export function initDraw(): Cleanup {
  const svgs = [...document.querySelectorAll<SVGSVGElement>('svg[data-draw="scroll"]')];
  if (!svgs.length) return () => {};
  if (prefersReduced()) {
    svgs.forEach((s) => s.style.setProperty('--draw', '0'));
    return () => {};
  }
  const visible = new Set<SVGSVGElement>();
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) visible.add(e.target as SVGSVGElement);
        else visible.delete(e.target as SVGSVGElement);
      }
    },
    { rootMargin: '10% 0px' },
  );
  svgs.forEach((s) => io.observe(s));
  const values = new Map<SVGSVGElement, number>();
  const stop = onScroll({
    read() {
      const vh = window.innerHeight;
      visible.forEach((s) => {
        const r = s.getBoundingClientRect();
        const p = clamp((vh * 0.92 - r.top) / (r.height * 0.8 + vh * 0.45));
        values.set(s, 1 - p);
      });
    },
    write() {
      values.forEach((v, s) => s.style.setProperty('--draw', v.toFixed(4)));
      values.clear();
    },
  });
  return () => {
    stop();
    io.disconnect();
  };
}
