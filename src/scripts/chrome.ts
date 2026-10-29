import { MOTION, finePointer, onScroll, prefersReduced, type Cleanup } from './motion';

const root = document.documentElement;

/** Başlık: üstte saydam; kaydırınca yüzey kazanır, aşağı inerken çekilir, yukarı çıkınca döner. */
export function initHeader(): Cleanup {
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!header) return () => {};
  let last = window.scrollY;
  let y = last;
  return onScroll({
    read() {
      y = window.scrollY;
    },
    write() {
      if (root.classList.contains('menu-open')) return;
      header.classList.toggle('is-scrolled', y > 24);
      const goingDown = y > last + 4;
      const goingUp = y < last - 4;
      if (goingDown && y > 320 && !header.contains(document.activeElement)) header.classList.add('is-hidden');
      else if (goingUp || y < 320) header.classList.remove('is-hidden');
      last = y;
    },
  });
}

/** Tam ekran mobil menü. */
export function initMenu(): Cleanup {
  const btn = document.querySelector<HTMLButtonElement>('[data-menu-toggle]');
  const panel = document.querySelector<HTMLElement>('[data-menu]');
  if (!btn || !panel) return () => {};
  const outside = [...document.querySelectorAll<HTMLElement>('main, footer')];

  // iOS Safari'de overflow:hidden arka plan kaydırmasını her zaman durdurmaz;
  // gövdeyi sabitleyip kapanınca eski kaydırma konumuna dönülür.
  let lockedY = 0;
  const lock = () => {
    lockedY = window.scrollY;
    document.body.style.cssText = `position:fixed;top:-${lockedY}px;left:0;right:0;width:100%`;
  };
  const unlock = (restore: boolean) => {
    if (!document.body.style.position) return;
    document.body.style.cssText = '';
    if (restore) window.scrollTo(0, lockedY);
  };

  const set = (open: boolean, restore = true) => {
    if (open === root.classList.contains('menu-open')) return;
    if (open) lock();
    else unlock(restore);
    root.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.querySelector('[data-menu-label]')!.textContent = open ? 'Kapat' : 'Menü';
    panel.toggleAttribute('inert', !open);
    outside.forEach((el) => el.toggleAttribute('inert', open));
    if (open) panel.querySelector<HTMLElement>('a')?.focus({ preventScroll: true });
  };
  const toggle = () => set(!root.classList.contains('menu-open'));
  const onKey = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && root.classList.contains('menu-open')) {
      set(false);
      btn.focus();
    }
  };
  const onResize = () => {
    if (window.innerWidth >= 1024 && root.classList.contains('menu-open')) set(false);
  };
  // Gezinme başlarken menü açıksa (ya da kapanıyorsa) animasyonsuz kapat. WebKit, açık menü
  // ve sabitlenmiş gövde üzerinden sayfa geçişi görüntüsü alırken sekmeyi çökertiyordu.
  const onNavigate = () => {
    if (!root.classList.contains('menu-open')) return;
    panel.style.transition = 'none';
    (document.activeElement as HTMLElement | null)?.blur();
    set(false, false);
    void panel.offsetHeight;
  };
  btn.addEventListener('click', toggle);
  document.addEventListener('keydown', onKey);
  document.addEventListener('astro:before-preparation', onNavigate);
  window.addEventListener('resize', onResize, { passive: true });
  panel.setAttribute('inert', '');
  return () => {
    btn.removeEventListener('click', toggle);
    document.removeEventListener('keydown', onKey);
    document.removeEventListener('astro:before-preparation', onNavigate);
    window.removeEventListener('resize', onResize);
    // gezinme sırasında: kilidi kaldır ama eski konuma kaydırma (yeni sayfa en üstten açılır)
    unlock(false);
    root.classList.remove('menu-open');
    outside.forEach((el) => el.removeAttribute('inert'));
  };
}

/**
 * Açılış: oturum başına bir kez. Görsel zaman çizelgesi CSS'te (Intro.astro),
 * burada yalnızca bitişi işaretlenir ve hero başlatılır.
 */
let introDone = false;
export function initIntroAndHero(): Cleanup {
  const hero = document.querySelector<HTMLElement>('[data-hero]');
  const timers: number[] = [];
  const startHero = () => hero?.classList.add('is-in');

  if (root.classList.contains('intro') && !introDone) {
    introDone = true;
    try {
      sessionStorage.setItem('sn-intro', '1');
    } catch {}
    timers.push(window.setTimeout(startHero, MOTION.heroAfterIntroMs));
    timers.push(window.setTimeout(() => root.classList.remove('intro'), MOTION.introMs));
  } else {
    root.classList.remove('intro');
    // Sayfa geçişi sırasında yeni sayfanın görünmesiyle birlikte başlasın
    requestAnimationFrame(() => requestAnimationFrame(startHero));
  }
  return () => timers.forEach(clearTimeout);
}

/**
 * Proje görselleri üzerinde dairesel imleç. Yalnızca ince işaretçili cihazlarda;
 * dokunmatik ve azaltılmış harekette hiç başlamaz. Sayfalar arasında kalıcıdır.
 */
export function initCursor() {
  const el = document.querySelector<HTMLElement>('[data-cursor-el]');
  if (!el || !finePointer() || prefersReduced()) return;
  root.classList.add('has-cursor');
  const label = el.querySelector<HTMLElement>('[data-cursor-label]')!;
  let tx = 0,
    ty = 0,
    x = 0,
    y = 0,
    raf = 0,
    active = false;

  const loop = () => {
    x += (tx - x) * MOTION.cursorLerp;
    y += (ty - y) * MOTION.cursorLerp;
    el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.1 ? requestAnimationFrame(loop) : 0;
  };
  document.addEventListener(
    'pointermove',
    (e) => {
      tx = e.clientX;
      ty = e.clientY;
      if (!active) {
        x = tx;
        y = ty;
      }
      if (!raf) raf = requestAnimationFrame(loop);
    },
    { passive: true },
  );
  document.addEventListener('pointerover', (e) => {
    const t = (e.target as Element).closest<HTMLElement>('[data-cursor]');
    if (t) {
      label.textContent = t.dataset.cursor || 'Projeyi gör';
      active = true;
      el.classList.add('is-active');
    }
  });
  document.addEventListener('pointerout', (e) => {
    const from = (e.target as Element).closest('[data-cursor]');
    const to = (e.relatedTarget as Element | null)?.closest?.('[data-cursor]');
    if (from && from !== to) {
      active = false;
      el.classList.remove('is-active');
    }
  });
  document.addEventListener('astro:before-swap', () => {
    active = false;
    el.classList.remove('is-active');
  });
}
