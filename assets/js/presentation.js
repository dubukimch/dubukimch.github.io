const slides = [...document.querySelectorAll('.slide')];
const prevButton = document.getElementById('prev-slide');
const nextButton = document.getElementById('next-slide');
const slideCounter = document.getElementById('slide-counter');
const dotNav = document.getElementById('dot-nav');

let currentIndex = 0;

function updateCounter() {
  slideCounter.textContent = `${currentIndex + 1} / ${slides.length}`;
}

function buildDots() {
  slides.forEach((slide, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.setAttribute('aria-label', `${index + 1}번 슬라이드로 이동`);
    button.addEventListener('click', () => goToSlide(index));
    dotNav.appendChild(button);
  });
}

function updateDots() {
  [...dotNav.querySelectorAll('button')].forEach((button, index) => {
    button.classList.toggle('active', index === currentIndex);
  });
}

function setActiveSlide(index) {
  currentIndex = Math.max(0, Math.min(index, slides.length - 1));
  slides.forEach((slide, i) => {
    slide.classList.toggle('is-active', i === currentIndex);
  });
  updateCounter();
  updateDots();
}

function goToSlide(index) {
  setActiveSlide(index);
  slides[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function findClosestSlide() {
  const viewportCenter = window.innerHeight / 2;
  let closestIndex = 0;
  let closestDistance = Number.POSITIVE_INFINITY;

  slides.forEach((slide, index) => {
    const rect = slide.getBoundingClientRect();
    const slideCenter = rect.top + rect.height / 2;
    const distance = Math.abs(slideCenter - viewportCenter);

    if (distance < closestDistance) {
      closestDistance = distance;
      closestIndex = index;
    }
  });

  setActiveSlide(closestIndex);
}

prevButton.addEventListener('click', () => goToSlide(currentIndex - 1));
nextButton.addEventListener('click', () => goToSlide(currentIndex + 1));

window.addEventListener('scroll', () => {
  window.clearTimeout(window.__slideTimer);
  window.__slideTimer = window.setTimeout(findClosestSlide, 80);
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown' || event.key === 'PageDown' || event.key === ' ') {
    event.preventDefault();
    goToSlide(currentIndex + 1);
  }

  if (event.key === 'ArrowLeft' || event.key === 'ArrowUp' || event.key === 'PageUp') {
    event.preventDefault();
    goToSlide(currentIndex - 1);
  }

  if (event.key === 'Home') {
    event.preventDefault();
    goToSlide(0);
  }

  if (event.key === 'End') {
    event.preventDefault();
    goToSlide(slides.length - 1);
  }
});

buildDots();
setActiveSlide(0);
