/* Shared behaviour for inner pages: theme toggle, header state, mobile menu, reveal. */
(() => {
  const root = document.documentElement;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  const syncTheme = () => metaTheme && metaTheme.setAttribute("content", root.dataset.theme === "light" ? "#f6f7fb" : "#05060b");
  syncTheme();

  const themeBtn = document.getElementById("theme");
  if (themeBtn) themeBtn.addEventListener("click", () => {
    const next = root.dataset.theme === "light" ? "dark" : "light";
    const apply = () => { root.dataset.theme = next; syncTheme(); try { localStorage.setItem("nf-theme", next); } catch (e) {} };
    if (document.startViewTransition && !reduce) document.startViewTransition(apply); else apply();
  });

  const top = document.getElementById("top");
  const onScroll = () => top && top.classList.toggle("scrolled", scrollY > 20);
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  const menu = document.getElementById("menu"), nav = document.getElementById("nav");
  if (menu && nav) {
    const setMenu = (open) => { nav.classList.toggle("open", open); menu.setAttribute("aria-expanded", open); menu.setAttribute("aria-label", open ? "Close menu" : "Open menu"); };
    menu.addEventListener("click", () => setMenu(!nav.classList.contains("open")));
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });
    addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
  }

  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }), { threshold: 0.1 });
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
})();
