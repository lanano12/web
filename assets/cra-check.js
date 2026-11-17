/* Self-reported checklist coverage. No compliance score and no network requests. */
(() => {
  const form = document.getElementById('cra-form');
  const out = document.getElementById('cra-result');
  const err = document.getElementById('cra-error');
  const dataEl = document.getElementById('cra-data');
  if (!form || !out || !dataEl) return;
  const data = JSON.parse(dataEl.textContent);
  const node = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  const link = (text, href, className) => {
    const el = node('a', text, className);
    el.href = href;
    return el;
  };
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    err.textContent = '';
    const names = ['scope', ...data.questions.map((q) => q.id)];
    const missing = names.find((name) => !form.querySelector(`input[name="${name}"]:checked`));
    if (missing) {
      err.textContent = 'Please answer every question to see your summary.';
      form.querySelector(`input[name="${missing}"]`).focus();
      return;
    }
    const value = (name) => form.querySelector(`input[name="${name}"]:checked`).value;
    const scope = value('scope');
    const answers = data.questions.map((question) => ({ ...question, value: value(question.id) }));
    const yes = answers.filter((answer) => answer.value === '2').length;
    const partly = answers.filter((answer) => answer.value === '1').length;
    const no = answers.filter((answer) => answer.value === '0').length;
    const gaps = answers
      .filter((answer) => answer.value !== '2')
      .sort((a, b) => Number(b.live) - Number(a.live) || Number(a.value) - Number(b.value));
    const summary = node('div', null, 'cra-summary');
    summary.append(
      node('p', 'Self-reported checklist', 'eyebrow'),
      node('h2', 'Your next engineering questions'),
    );
    const counts = node('dl', null, 'cra-counts');
    for (const [label, count] of [
      ['In place', yes],
      ['Partly in place', partly],
      ['Not in place', no],
    ]) {
      const item = node('div');
      item.append(node('dt', label), node('dd', String(count)));
      counts.append(item);
    }
    summary.append(
      counts,
      node(
        'p',
        `${yes} of ${answers.length} practices reported in place. These answers have not been independently checked. This checklist does not determine legal scope, conformity or whether a product is secure.`,
      ),
    );
    out.replaceChildren(summary);
    const scopeMessage =
      scope === 'no'
        ? 'You reported no EU supply. This questionnaire does not decide whether your products fall within the CRA. Establish scope before relying on these priorities.'
        : scope === 'unsure'
          ? 'Your scope is unresolved. Confirm which products and activities are covered before treating this as a readiness plan.'
          : 'You reported EU supply. Confirm product scope, classification and applicable obligations with an appropriately qualified adviser.';
    out.append(node('p', scopeMessage, 'cra-scope'));
    if (gaps.length) {
      out.append(node('h3', 'Topics to investigate'));
      const list = node('ol', null, 'gaps');
      for (const gap of gaps) {
        const item = node('li');
        if (gap.live)
          item.append(node('span', 'Reporting priority', 'live-tag'), document.createTextNode(' '));
        item.append(document.createTextNode(gap.advice));
        if (gap.value === '1') item.append(node('span', ' (partly in place)', 'partly'));
        list.append(item);
      }
      out.append(list);
    } else {
      out.append(
        node(
          'p',
          'All listed practices were reported in place. Validate the evidence, test the implementation and identify requirements this short checklist does not cover.',
        ),
      );
    }
    const body = `Hi NexaFusion,\n\nMy checklist reports ${yes} practices in place, ${partly} partly in place and ${no} not in place. This is a self-assessment, not a compliance result.\n\nTopics to investigate:\n${gaps.map((gap, i) => `${i + 1}. ${gap.advice}`).join('\n') || 'Validate evidence for the reported practices.'}\n\nCould we discuss next steps?\n`;
    const actions = node('div', null, 'cta-row');
    actions.append(
      link(
        'Email this summary ↗',
        `mailto:${data.email}?subject=${encodeURIComponent('CRA engineering checklist')}&body=${encodeURIComponent(body)}`,
        'btn',
      ),
      link('How we help', '/services/cra-readiness/', 'btn ghost'),
    );
    out.append(
      actions,
      node(
        'p',
        'Your answers stay in this page. Emailing opens your own mail application with a draft you can review before sending.',
        'note',
      ),
    );
    out.hidden = false;
    out.focus({ preventScroll: true });
    out.scrollIntoView({
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      block: 'start',
    });
  });
  const clear = () => {
    out.hidden = true;
    out.replaceChildren();
    err.textContent = '';
  };
  form.addEventListener('change', clear);
  form.addEventListener('reset', clear);
  form.querySelector('button[type="submit"]').disabled = false;
})();
