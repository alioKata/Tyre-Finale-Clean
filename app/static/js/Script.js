// app/static/js/Script.js
document.addEventListener('DOMContentLoaded', () => {
  let lastScroll = 0;
  const downContainer = document.querySelector('.down-container');
  const carouselSection = document.querySelector('.carousel-section');

  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    downContainer.classList.toggle('hidden', currentScroll > 10);

    // if user scrolls up into the carousel, show the first slide
    if (
      currentScroll < lastScroll &&
      currentScroll > carouselSection.offsetTop - 50 &&
      currentScroll < carouselSection.offsetTop + carouselSection.offsetHeight
    ) {
      navigateToBox(0);
    }
    lastScroll = currentScroll;
  });

  let currentIndex = 0;
  const boxes = document.querySelectorAll('.carousel-box');
  const dots  = document.querySelectorAll('.step-dot');

  function navigateToBox(idx) {
    boxes[currentIndex].classList.remove('active');
    currentIndex = idx;
    boxes[currentIndex].classList.add('active');
    updateNavigation();
  }

  function updateNavigation() {
    dots.forEach((d, i) => d.classList.toggle('active', i === currentIndex));
    document.querySelector('.prev').style.visibility = currentIndex === 0 ? 'hidden' : 'visible';
    document.querySelector('.next').style.visibility = currentIndex === boxes.length - 1 ? 'hidden' : 'visible';
  }

  document.querySelector('.next').addEventListener('click', () => {
    if (currentIndex < boxes.length - 1) navigateToBox(currentIndex + 1);
  });
  document.querySelector('.prev').addEventListener('click', () => {
    if (currentIndex > 0) navigateToBox(currentIndex - 1);
  });
  dots.forEach((dot, i) => dot.addEventListener('click', () => navigateToBox(i)));

  document.querySelector('.down-button').addEventListener('click', () => {
    window.scrollTo({ top: carouselSection.offsetTop, behavior: 'smooth' });
  });

  // hover effects
  document.querySelectorAll('.main-btn').forEach(btn => {
    const parent = btn.closest('.welcome-box') || btn.closest('.carousel-box');
    btn.addEventListener('mouseenter', () => {
      parent.style.backgroundColor = '#1877f2';
      parent.style.color = 'white';
      btn.style.borderColor = 'white';
      btn.style.color = 'white';
      parent.querySelectorAll('a.login-link').forEach(a => a.style.color = 'white');
    });
    btn.addEventListener('mouseleave', () => {
      parent.style.backgroundColor = '';
      parent.style.color = '';
      btn.style.borderColor = '#1877f2';
      btn.style.color = '#1877f2';
      parent.querySelectorAll('a.login-link').forEach(a => a.style.color = '#1877f2');
    });
  });

  updateNavigation();
});
