import type { Cleanup } from './motion';
import { initDraw, initParallax, initReveal } from './reveal';
import { initCursor, initHeader, initIntroAndHero, initMenu } from './chrome';
import { initAccordion, initFilters, initForm, initProcess, initServices } from './interactions';

const perPage = [
  initIntroAndHero,
  initHeader,
  initMenu,
  initReveal,
  initParallax,
  initDraw,
  initServices,
  initProcess,
  initFilters,
  initAccordion,
  initForm,
];

let cleanups: Cleanup[] = [];

document.addEventListener('astro:page-load', () => {
  cleanups = perPage.map((init) => init());
});

document.addEventListener('astro:before-swap', () => {
  cleanups.forEach((c) => c());
  cleanups = [];
});

// ClientRouter <html> özniteliklerini yeni sayfadan kopyalar; JS işaretini geri koy
document.addEventListener('astro:after-swap', () => {
  document.documentElement.classList.add('js');
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.documentElement.classList.toggle(
      'has-cursor',
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    );
  }
});

initCursor();
