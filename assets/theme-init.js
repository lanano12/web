/* Apply saved theme before paint to avoid a flash. */
try { var t = localStorage.getItem("nf-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
