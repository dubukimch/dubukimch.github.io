'use strict';
document.documentElement.classList.add('js');

const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('#nav');
if (navToggle && nav) {
  navToggle.hidden = false;
  const closeNav = () => {
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  };
  navToggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeNav();
      navToggle.focus();
    }
  });
  nav.addEventListener('focusout', event => {
    if (!nav.contains(event.relatedTarget) && event.relatedTarget !== navToggle) closeNav();
  });
}

const tools = document.querySelector('.project-tools');
const search = document.querySelector('#project-search');
const projects = [...document.querySelectorAll('[data-project]')];
if (tools && search && projects.length) {
  tools.hidden = false;
  const count = document.querySelector('#project-count');
  const empty = document.querySelector('.empty-results');
  const filters = [...document.querySelectorAll('[data-filter]')];
  let activeGroup = 'all';
  count.hidden = false;
  const update = () => {
    const terms = search.value.trim().normalize('NFC').toLocaleLowerCase('ko').split(/\s+/).filter(Boolean);
    let visible = 0;
    projects.forEach(project => {
      const matchesGroup = activeGroup === 'all' || project.dataset.group === activeGroup;
      const haystack = project.dataset.search.normalize('NFC');
      const matchesSearch = terms.every(term => haystack.includes(term));
      project.hidden = !(matchesGroup && matchesSearch);
      if (!project.hidden) visible += 1;
    });
    count.textContent = `${visible}개 프로젝트 / 전체 ${projects.length}개`;
    empty.hidden = visible !== 0;
    filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter.dataset.filter === activeGroup)));
  };
  filters.forEach(filter => filter.addEventListener('click', () => {
    activeGroup = filter.dataset.filter;
    update();
  }));
  search.addEventListener('input', update);
  document.querySelector('#reset-filters').addEventListener('click', () => {
    activeGroup = 'all';
    search.value = '';
    update();
    search.focus();
  });
  update();
}

const lightbox = document.querySelector('#lightbox');
if (lightbox && typeof lightbox.showModal === 'function') {
  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('figcaption');
  const position = document.querySelector('#gallery-position');
  const stepButtons = [...lightbox.querySelectorAll('[data-gallery-step]')];
  const shots = [...document.querySelectorAll('[data-lightbox]')];
  let opener;
  let gallery = [];
  let current = 0;
  position.setAttribute('aria-live', 'polite');
  const show = index => {
    current = (index + gallery.length) % gallery.length;
    const shot = gallery[current];
    image.src = shot.dataset.lightbox;
    image.alt = `${shot.dataset.title} 로컬 작업 화면`;
    caption.textContent = shot.dataset.caption;
    position.textContent = `${current + 1} / ${gallery.length} · ${shot.dataset.title}`;
    stepButtons.forEach(button => { button.hidden = gallery.length < 2; });
  };
  shots.forEach(button => button.addEventListener('click', () => {
    opener = button;
    gallery = shots.filter(shot => !shot.closest('[hidden]'));
    show(gallery.indexOf(button));
    lightbox.showModal();
  }));
  stepButtons.forEach(button => button.addEventListener('click', () => show(current + Number(button.dataset.galleryStep))));
  lightbox.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', event => {
    if (event.target === lightbox) {
      const rect = lightbox.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) lightbox.close();
    }
  });
  lightbox.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  lightbox.addEventListener('close', () => opener?.focus());
}

if (['127.0.0.1', 'localhost', '[::1]'].includes(window.location.hostname)) {
  document.querySelectorAll('[data-local-only]').forEach(link => { link.hidden = false; });
}
