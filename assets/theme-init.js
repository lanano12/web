/* Apply only a recognised saved theme before paint. */
try {
  const theme = localStorage.getItem('nf-theme');
  if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
} catch {
  /* The default theme works without storage. */
}
