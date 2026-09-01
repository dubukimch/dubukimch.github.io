const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('#nav');

navToggle?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', String(open));
});

nav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    nav.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
  });
});

const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.08 });
  reveals.forEach((element) => revealObserver.observe(element));
} else {
  reveals.forEach((element) => element.classList.add('visible'));
}

const sections = [...document.querySelectorAll('main section[id]')];
const sectionLinks = [...document.querySelectorAll('#nav a[href^="#"]')];
if ('IntersectionObserver' in window) {
  const navObserver = new IntersectionObserver((entries) => {
    const current = entries.find((entry) => entry.isIntersecting);
    if (!current) return;
    sectionLinks.forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${current.target.id}`);
    });
  }, { rootMargin: '-30% 0px -60% 0px' });
  sections.forEach((section) => navObserver.observe(section));
}

const lightbox = document.querySelector('#lightbox');
const lightboxImage = lightbox?.querySelector('img');
const lightboxCaption = lightbox?.querySelector('figcaption');
const lightboxClose = lightbox?.querySelector('.lightbox-close');

document.querySelectorAll('[data-lightbox]').forEach((button) => {
  button.addEventListener('click', () => {
    if (!lightbox || !lightboxImage || !lightboxCaption) return;
    lightboxImage.src = button.dataset.lightbox;
    lightboxImage.alt = button.dataset.caption || '프로젝트 상세 화면';
    lightboxCaption.textContent = button.dataset.caption || '';
    lightbox.showModal();
  });
});

lightboxClose?.addEventListener('click', () => lightbox.close());
lightbox?.addEventListener('click', (event) => {
  if (event.target === lightbox) lightbox.close();
});
