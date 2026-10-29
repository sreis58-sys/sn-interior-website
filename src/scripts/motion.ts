/**
 * Hareket sisteminin merkezi. Süre ve easing değerleri global.css'teki
 * --dur-* / --ease* token'larıyla aynıdır; JS yalnızca sınıf ve değişken yazar.
 */

export type Cleanup = () => void;

export const MOTION = {
  introMs: 1500, // açılış perdesinin toplam süresi
  heroAfterIntroMs: 950, // perdeler ayrılırken hero başlar
  parallax: 0.035, // görsel yüksekliğinin en fazla bu oranı kadar kayar
  cursorLerp: 0.24, // imleç yumuşatma (1 = gecikmesiz)
};

const mq = (q: string) => window.matchMedia(q);
export const prefersReduced = () => mq('(prefers-reduced-motion: reduce)').matches;
export const finePointer = () => mq('(hover: hover) and (pointer: fine)').matches;
export const isDesktop = () => mq('(min-width: 1024px)').matches;
export const isTablet = () => mq('(min-width: 768px)').matches;

export const clamp = (v: number, min = 0, max = 1) => Math.min(max, Math.max(min, v));

/**
 * Tek rAF döngüsü: tüm kaydırma bağımlı işler önce okur, sonra yazar.
 * Böylece layout thrashing oluşmaz ve kaydırma olayı başına en fazla bir kare çalışır.
 */
type Job = { read: () => void; write: () => void };
const jobs = new Set<Job>();
let queued = false;
let listening = false;

function frame() {
  queued = false;
  jobs.forEach((j) => j.read());
  jobs.forEach((j) => j.write());
}
export function requestTick() {
  if (!queued) {
    queued = true;
    requestAnimationFrame(frame);
  }
}
function listen() {
  if (listening) return;
  listening = true;
  window.addEventListener('scroll', requestTick, { passive: true });
  window.addEventListener('resize', requestTick, { passive: true });
}

export function onScroll(job: Job): Cleanup {
  listen();
  jobs.add(job);
  requestTick();
  return () => jobs.delete(job);
}
