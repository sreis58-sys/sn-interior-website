import { clamp, isDesktop, onScroll, prefersReduced, type Cleanup } from './motion';

/**
 * Hizmetler: masaüstünde isim üzerine gelince yan taraftaki görsel değişir.
 * Eski görsel yukarı doğru kapanır, yenisi alttan açılır. Mobilde bu modül pasif kalır;
 * içerik dikey akışta zaten açık.
 */
export function initServices(): Cleanup {
  const root = document.querySelector<HTMLElement>('[data-services]');
  if (!root) return () => {};
  const items = [...root.querySelectorAll<HTMLElement>('[data-service]')];
  const imgs = [...root.querySelectorAll<HTMLElement>('[data-service-img]')];
  let current = 0;
  const timers = new Set<number>();

  const activate = (i: number) => {
    if (i === current || !isDesktop()) return;
    const prev = imgs[current];
    const next = imgs[i];
    items[current].classList.remove('is-active');
    items[i].classList.add('is-active');
    prev.classList.remove('is-active');
    prev.classList.add('is-leaving');
    next.classList.remove('is-leaving');
    next.classList.add('is-active');
    const t = window.setTimeout(
      () => {
        prev.classList.remove('is-leaving');
        timers.delete(t);
      },
      prefersReduced() ? 0 : 1100,
    );
    timers.add(t);
    current = i;
  };

  const handlers = items.map((item, i) => {
    const h = () => activate(i);
    item.addEventListener('pointerenter', h);
    item.addEventListener('focusin', h);
    item.querySelector('button')?.addEventListener('click', h);
    return h;
  });
  return () => {
    items.forEach((item, i) => {
      item.removeEventListener('pointerenter', handlers[i]);
      item.removeEventListener('focusin', handlers[i]);
      item.querySelector('button')?.removeEventListener('click', handlers[i]);
    });
    timers.forEach(clearTimeout);
  };
}

/** Süreç: kaydırdıkça aktif adım ve ince ilerleme çizgisi değişir. Kaydırma serbesttir. */
export function initProcess(): Cleanup {
  const sections = [...document.querySelectorAll<HTMLElement>('[data-process]')];
  if (!sections.length) return () => {};
  const cleanups: Cleanup[] = [];
  for (const section of sections) {
    const steps = [...section.querySelectorAll<HTMLElement>('[data-step]')];
    const track = section.querySelector<HTMLElement>('[data-step-track]');
    let progress = 0;
    let active = -1;
    const stop = onScroll({
      read() {
        const vh = window.innerHeight;
        const r = (track ?? section).getBoundingClientRect();
        progress = clamp((vh * 0.55 - r.top) / r.height);
        // aktif adım: ekranın ortasını geçen son adım
        active = -1;
        steps.forEach((s, i) => {
          if (s.getBoundingClientRect().top < vh * 0.58) active = i;
        });
      },
      write() {
        section.style.setProperty('--progress', progress.toFixed(4));
        steps.forEach((s, i) => {
          s.classList.toggle('is-active', i === active);
          s.classList.toggle('is-past', i < active);
        });
      },
    });
    cleanups.push(stop);
  }
  return () => cleanups.forEach((c) => c());
}

/** Filtreler: kayan mercan gösterge + öğeleri gizle/göster. */
export function initFilters(): Cleanup {
  const groups = [...document.querySelectorAll<HTMLElement>('[data-filters]')];
  const cleanups: Cleanup[] = [];
  for (const group of groups) {
    const target = document.querySelector<HTMLElement>(group.dataset.filters!);
    const buttons = [...group.querySelectorAll<HTMLButtonElement>('button[data-filter]')];
    const status = document.querySelector<HTMLElement>(`${group.dataset.filters} [data-filter-status]`);
    if (!target) continue;

    const moveIndicator = (b: HTMLButtonElement) => {
      group.style.setProperty('--ix', `${b.offsetLeft}px`);
      group.style.setProperty('--iw', `${b.offsetWidth}px`);
    };
    const apply = (b: HTMLButtonElement) => {
      const value = b.dataset.filter!;
      buttons.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      moveIndicator(b);
      let shown = 0;
      target.querySelectorAll<HTMLElement>('[data-category]').forEach((item) => {
        const match = value === 'all' || item.dataset.category === value;
        item.hidden = !match;
        if (match) {
          shown++;
          // filtre değişince kısa bir yeniden belirme
          item.classList.remove('is-filtered-in');
          void item.offsetWidth;
          item.classList.add('is-filtered-in');
        }
      });
      if (status) status.textContent = `${shown} sonuç`;
    };
    const handlers = buttons.map((b) => {
      const h = () => apply(b);
      b.addEventListener('click', h);
      return h;
    });
    const onResize = () => {
      const cur = buttons.find((b) => b.getAttribute('aria-pressed') === 'true');
      if (cur) moveIndicator(cur);
    };
    window.addEventListener('resize', onResize, { passive: true });
    const initial = buttons.find((b) => b.getAttribute('aria-pressed') === 'true') ?? buttons[0];
    if (initial) moveIndicator(initial);
    // fontlar yüklenince ölçüler değişebilir
    document.fonts?.ready.then(onResize);
    cleanups.push(() => {
      buttons.forEach((b, i) => b.removeEventListener('click', handlers[i]));
      window.removeEventListener('resize', onResize);
    });
  }
  return () => cleanups.forEach((c) => c());
}

/** S.S.S. akordeonu: yükseklik (grid satırı), opaklık ve gösterge dönüşü CSS'te. */
export function initAccordion(): Cleanup {
  const buttons = [...document.querySelectorAll<HTMLButtonElement>('[data-accordion] button[aria-controls]')];
  const handlers = buttons.map((b) => {
    const h = () => {
      const open = b.getAttribute('aria-expanded') !== 'true';
      b.setAttribute('aria-expanded', String(open));
      document.getElementById(b.getAttribute('aria-controls')!)?.toggleAttribute('data-open', open);
    };
    b.addEventListener('click', h);
    return h;
  });
  return () => buttons.forEach((b, i) => b.removeEventListener('click', handlers[i]));
}

/**
 * İletişim formu. PUBLIC_FORM_ENDPOINT tanımlıysa JSON olarak gönderir;
 * tanımlı değilse ziyaretçinin e-posta uygulamasını doldurulmuş mesajla açar.
 */
export function initForm(): Cleanup {
  const form = document.querySelector<HTMLFormElement>('[data-contact-form]');
  if (!form) return () => {};
  const status = form.querySelector<HTMLElement>('[data-form-status]')!;
  const submit = form.querySelector<HTMLButtonElement>('button[type="submit"]')!;
  const endpoint = form.dataset.endpoint;
  const mail = form.dataset.mail!;

  const showErrors = () => {
    let first: HTMLElement | null = null;
    form.querySelectorAll<HTMLInputElement | HTMLTextAreaElement>('input, textarea').forEach((f) => {
      const field = f.closest('.field');
      const err = field?.querySelector<HTMLElement>('.field__error');
      const invalid = !f.checkValidity();
      f.setAttribute('aria-invalid', String(invalid));
      if (err) err.textContent = invalid ? f.dataset.error || 'Lütfen bu alanı kontrol edin.' : '';
      if (invalid && !first) first = f;
    });
    (first as HTMLElement | null)?.focus();
    return !first;
  };

  const onInput = (e: Event) => {
    const f = e.target as HTMLInputElement;
    if (f.getAttribute('aria-invalid') === 'true' && f.checkValidity()) {
      f.setAttribute('aria-invalid', 'false');
      const err = f.closest('.field')?.querySelector<HTMLElement>('.field__error');
      if (err) err.textContent = '';
    }
  };

  const onSubmit = async (e: SubmitEvent) => {
    e.preventDefault();
    if (!showErrors()) {
      status.textContent = 'Lütfen işaretli alanları kontrol edin.';
      return;
    }
    const data = Object.fromEntries(new FormData(form).entries()) as Record<string, string>;
    if (data.website) return; // bal küpü: botlar bu gizli alanı doldurur

    if (!endpoint) {
      const body = `${data.message}\n\n— ${data.name}\n${data.email}${data.phone ? `\n${data.phone}` : ''}`;
      const subject = `Proje görüşmesi — ${data.name}`;
      window.location.href = `mailto:${mail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      status.textContent = 'E-posta uygulamanız mesajınızla açıldı. Göndermeyi unutmayın.';
      return;
    }

    submit.disabled = true;
    status.textContent = 'Gönderiliyor…';
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(String(res.status));
      form.reset();
      form.classList.add('is-sent');
      status.textContent = 'Teşekkürler. Mesajınız bize ulaştı; en kısa sürede dönüş yapacağız.';
    } catch {
      status.textContent = `Mesaj gönderilemedi. Lütfen ${mail} adresine yazın ya da bizi arayın.`;
    } finally {
      submit.disabled = false;
    }
  };

  form.addEventListener('submit', onSubmit);
  form.addEventListener('input', onInput);
  return () => {
    form.removeEventListener('submit', onSubmit);
    form.removeEventListener('input', onInput);
  };
}
