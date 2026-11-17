/* EU CRA readiness check — runs entirely in the browser; nothing is sent or stored. */
(() => {
  const form = document.getElementById('cra-form');
  const out = document.getElementById('cra-result');
  const err = document.getElementById('cra-error');
  const dataEl = document.getElementById('cra-data');
  if (!form || !out || !dataEl) return;
  const data = JSON.parse(dataEl.textContent);
  const esc = (s) =>
    String(s).replace(
      /[&<>"]/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c],
    );

  const band = (pct) =>
    pct >= 90
      ? [
          'Strong position',
          'You have most of the foundations. Focus on evidence and keeping it current.',
        ]
      : pct >= 70
        ? [
            'Well on the way',
            'Good foundations, with a few gaps worth closing before December 2027.',
          ]
        : pct >= 40
          ? [
              'Partly ready',
              'Important pieces are missing. Start with the duties that already apply.',
            ]
          : [
              'Early stage',
              'There is real work to do — but a focused plan gets you a long way quickly.',
            ];

  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    err.textContent = '';
    const names = ['scope', ...data.questions.map((q) => q.id)];
    const missing = names.find((n) => !form.querySelector(`input[name="${n}"]:checked`));
    if (missing) {
      err.textContent = 'Please answer every question to see your results.';
      form.querySelector(`input[name="${missing}"]`).focus();
      return;
    }
    const val = (n) => form.querySelector(`input[name="${n}"]:checked`).value;
    const scope = val('scope');
    let got = 0;
    const max = data.questions.length * 2;
    const gaps = [];
    for (const q of data.questions) {
      const v = Number(val(q.id));
      got += v;
      if (v < 2) gaps.push({ ...q, partly: v === 1 });
    }
    gaps.sort((a, b) => b.live - a.live || a.partly - b.partly);
    const pct = Math.round((got / max) * 100);
    const [title, summary] = band(pct);

    const scopeNote =
      scope === 'no'
        ? `<p class="cra-scope">You said you don’t supply the EU market, so the CRA may not apply to you today — but these practices are increasingly expected by customers everywhere, and the UK is moving in a similar direction.</p>`
        : scope === 'unsure'
          ? `<p class="cra-scope">You’re not sure whether you’re in scope. That’s the first thing to settle: if you supply software or connected products to EU customers commercially, assume yes until checked.</p>`
          : '';

    const gapHtml = gaps.length
      ? `<h3>Your priorities</h3><ol class="gaps">${gaps
          .map(
            (g) =>
              `<li>${g.live ? '<span class="live-tag">Reporting priority</span> ' : ''}${esc(g.advice)}${g.partly ? ' <span class="partly">(partly in place)</span>' : ''}</li>`,
          )
          .join('')}</ol>`
      : `<p>No gaps reported — impressive. The next step is making sure the evidence would stand up to scrutiny.</p>`;

    const subject = `CRA readiness check — ${pct}%`;
    const bodyText = `Hi NexaFusion,\n\nI took your CRA readiness check and scored ${pct}% (${title}).\n\nTop gaps:\n${
      gaps
        .slice(0, 5)
        .map((g, i) => `${i + 1}. ${g.advice}`)
        .join('\n') || 'None reported'
    }\n\nCould we talk about next steps?\n`;
    const mailto = `mailto:${data.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(bodyText)}`;

    out.innerHTML = `
      <div class="cra-score" style="--pct:${pct}">
        <div class="score-ring" role="img" aria-label="Readiness score ${pct} percent"><span>${pct}%</span></div>
        <div><p class="eyebrow">Your indicative result</p><h2>${esc(title)}</h2><p>${esc(summary)}</p></div>
      </div>
      ${scopeNote}
      ${gapHtml}
      <div class="cta-row"><a class="btn" href="${mailto}">Send these results to us <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a><a class="btn ghost" href="/services/cra-readiness/">How we help</a></div>
      <p class="note">Indicative only and not legal advice. Your answers never leave this page unless you choose to email them.</p>`;
    out.hidden = false;
    out.focus({ preventScroll: true });
    out.scrollIntoView({
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start',
    });
  });

  const clearResult = () => {
    out.hidden = true;
    out.replaceChildren();
    err.textContent = '';
  };
  form.addEventListener('change', clearResult);
  form.addEventListener('reset', clearResult);
  form.querySelector('button[type="submit"]').disabled = false;
})();
