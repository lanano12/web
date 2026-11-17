/* Preserve incoming links after moving the detailed content off the homepage. */
(() => {
  const moved = {
    '#services': '/engineering/#services',
    '#explorer': '/engineering/#explorer',
    '#layer-hardware': '/engineering/#layer-hardware',
    '#layer-firmware': '/engineering/#layer-firmware',
    '#layer-security': '/engineering/#layer-security',
    '#layer-evidence': '/engineering/#layer-evidence',
    '#faq': '/engineering/#faq',
    '#notes': '/insights/',
    '#diagnose': '/cra-readiness/',
  };
  const followMovedLink = () => {
    if (Object.hasOwn(moved, location.hash)) location.replace(moved[location.hash]);
  };
  followMovedLink();
  addEventListener('hashchange', followMovedLink);

  /* The ambient motion stops when it cannot be seen. */
  const hero = document.querySelector('.quiet-hero');
  if (!hero) return;
  let inView = true;
  const syncMotion = () => {
    document.body.classList.toggle('motion-paused', !inView || document.hidden);
  };
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
      syncMotion();
    }).observe(hero);
  }
  document.addEventListener('visibilitychange', syncMotion);
  syncMotion();
})();
