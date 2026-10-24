'use strict';

// Guides remain complete and readable when JavaScript is unavailable.
const manualSearch = document.querySelector('#manual-search');
const manualEntries = [...document.querySelectorAll('[data-manual-search]')];
if (manualSearch && manualEntries.length) {
  document.querySelector('.manual-search-tools').hidden = false;
  const count = document.querySelector('#manual-search-count');
  const empty = document.querySelector('.manual-empty');
  manualSearch.addEventListener('input', () => {
    const terms = manualSearch.value.trim().normalize('NFC').toLocaleLowerCase('ko').split(/\s+/).filter(Boolean);
    let visible = 0;
    manualEntries.forEach(entry => {
      const haystack = entry.dataset.manualSearch.normalize('NFC');
      entry.hidden = !terms.every(term => haystack.includes(term));
      if (!entry.hidden) visible += 1;
    });
    count.textContent = `${visible}개 솔루션 / 전체 ${manualEntries.length}개`;
    empty.hidden = visible !== 0;
  });
}

const manualLinks = [...document.querySelectorAll('.manual-toc a[href^="#"]')];
if (manualLinks.length && 'IntersectionObserver' in window) {
  const sections = manualLinks.map(link => document.getElementById(link.hash.slice(1))).filter(Boolean);
  const markCurrent = id => manualLinks.forEach(link => {
    if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (visible.length) markCurrent(visible[0].target.id);
  }, {rootMargin: '-18% 0px -55% 0px', threshold: 0});
  sections.forEach(section => observer.observe(section));
  manualLinks.forEach(link => link.addEventListener('click', () => markCurrent(link.hash.slice(1))));
}
