/* Shared navigation and theme. Content is visible without JavaScript. */
(() => {
  const root = document.documentElement;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const themeButton = document.getElementById('theme');
  const syncTheme = () => {
    const light = root.dataset.theme === 'light';
    themeMeta?.setAttribute('content', light ? '#f3f5ed' : '#080c0c');
    themeButton?.setAttribute(
      'aria-label',
      light ? 'Switch to dark theme' : 'Switch to light theme',
    );
  };
  syncTheme();
  themeButton?.addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light';
    const apply = () => {
      root.dataset.theme = next;
      syncTheme();
      try {
        localStorage.setItem('nf-theme', next);
      } catch {
        /* Storage is optional. */
      }
    };
    if (document.startViewTransition && !motion.matches) document.startViewTransition(apply);
    else apply();
  });

  const header = document.getElementById('top');
  const onScroll = () => header?.classList.toggle('scrolled', scrollY > 12);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const menu = document.getElementById('menu');
  const nav = document.getElementById('nav');
  if (!menu || !nav) return;
  const setMenu = (open, restoreFocus = false) => {
    nav.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    if (restoreFocus) menu.focus();
  };
  menu.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) setMenu(false, true);
  });
  document.addEventListener('click', (event) => {
    if (!header.contains(event.target)) setMenu(false);
  });
  matchMedia('(min-width: 901px)').addEventListener('change', (event) => {
    if (event.matches) setMenu(false);
  });
})();
