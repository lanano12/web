/* Local navigation search. No network calls or query storage. */
(() => {
  const items = [
    {
      title: 'Signed-update engineering study',
      type: 'Engineering study',
      url: '/insights/signed-update-verification/',
      keywords: 'signature rollback device manifest testing threat model case study',
    },
    {
      title: 'Report a security issue privately',
      type: 'Disclosure',
      url: '/security/',
      keywords: 'vulnerability report disclosure security contact',
    },
    {
      title: 'Website privacy',
      type: 'Privacy',
      url: '/privacy/',
      keywords: 'data collection browser local storage',
    },
    {
      title: 'Embedded software engineering',
      type: 'Expertise',
      url: '/services/embedded-software/',
      keywords: 'firmware c c++ cpp hardware integration debugging embedded development testing',
    },
    {
      title: 'Embedded product security',
      type: 'Expertise',
      url: '/services/cyber-security/',
      keywords: 'cyber security threat modelling firmware hardening secure updates fuzzing',
    },
    {
      title: 'CRA engineering readiness',
      type: 'Expertise',
      url: '/services/cra-readiness/',
      keywords: 'cyber resilience act eu regulation compliance sbom documentation evidence',
    },
    {
      title: 'CRA readiness check',
      type: 'Free tool',
      url: '/cra-readiness/',
      keywords: 'checklist self assessment questions gaps reporting readiness',
    },
    {
      title: 'Explore the system',
      type: 'Interactive',
      url: '/engineering/#explorer',
      keywords: 'device architecture hardware firmware security evidence demo boot',
    },
    {
      title: 'How we work',
      type: 'Approach',
      url: '/engineering/#approach',
      keywords: 'process engagement handover ownership',
    },
    {
      title: 'The Cyber Resilience Act: what UK firms need to know',
      type: 'Field note',
      url: '/insights/eu-cyber-resilience-act/',
      keywords: 'cra article timeline reporting enisa regulation',
    },
    {
      title: 'Memory-safety roadmaps: Rust without the rewrite',
      type: 'Field note',
      url: '/insights/memory-safety-roadmaps/',
      keywords: 'rust cpp c++ memory safety modernisation article',
    },
    {
      title: 'All field notes',
      type: 'Writing',
      url: '/insights/',
      keywords: 'insights articles blog notes',
    },
    {
      title: 'Frequently asked questions',
      type: 'Questions',
      url: '/engineering/#faq',
      keywords: 'faq legal existing product engagement ip ownership',
    },
    {
      title: 'Start a conversation',
      type: 'Contact',
      url: '/#contact',
      keywords: 'email contact talk project hire quote enquiry',
    },
  ];
  const dialog = document.querySelector('.kbar');
  if (!dialog || typeof dialog.showModal !== 'function') {
    document.querySelectorAll('[data-kbar]').forEach((button) => (button.hidden = true));
    return;
  }
  const input = dialog.querySelector('input');
  const list = dialog.querySelector('ul');
  let results = [];
  let active = 0;

  const setActive = (index) => {
    active = index;
    [...list.children].forEach((item, i) => {
      if (item.getAttribute('role') === 'option')
        item.setAttribute('aria-selected', String(i === active));
    });
    if (results.length) input.setAttribute('aria-activedescendant', 'kbar-' + active);
    else input.removeAttribute('aria-activedescendant');
  };
  const render = () => {
    const words = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    results = items.filter((item) =>
      words.every((word) => (item.title + ' ' + item.keywords).toLowerCase().includes(word)),
    );
    list.replaceChildren();
    for (const [index, item] of results.entries()) {
      const option = document.createElement('li');
      option.id = 'kbar-' + index;
      option.setAttribute('role', 'option');
      const link = document.createElement('a');
      link.href = item.url;
      link.tabIndex = -1;
      const title = document.createElement('b');
      title.textContent = item.title;
      const type = document.createElement('span');
      type.textContent = item.type;
      link.append(title, type);
      option.append(link);
      list.append(option);
    }
    if (!results.length) {
      const empty = document.createElement('li');
      empty.className = 'kbar-empty';
      empty.textContent = 'No results. Try “firmware”, “security” or “CRA”.';
      empty.setAttribute('role', 'presentation');
      list.append(empty);
    }
    setActive(0);
    list.scrollTop = 0;
  };
  const open = () => {
    if (dialog.open) return;
    input.value = '';
    render();
    dialog.showModal();
    list.scrollTop = 0;
    input.focus();
  };
  input.addEventListener('input', render);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (!results.length) return;
      setActive((active + (event.key === 'ArrowDown' ? 1 : -1) + results.length) % results.length);
      list.children[active].scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (results.length) list.children[active].querySelector('a').click();
    }
  });
  list.addEventListener('click', (event) => {
    if (event.target.closest('a')) dialog.close();
  });
  dialog.querySelector('.kbar-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom
    )
      dialog.close();
  });
  addEventListener('keydown', (event) => {
    const typing =
      /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) ||
      document.activeElement.isContentEditable;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (dialog.open) dialog.close();
      else open();
    } else if (
      event.key === '/' &&
      !typing &&
      !dialog.open &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.altKey
    ) {
      event.preventDefault();
      open();
    }
  });
  document
    .querySelectorAll('[data-kbar]')
    .forEach((button) => button.addEventListener('click', open));
  const mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  document
    .querySelectorAll('.kbar-hint')
    .forEach((hint) => (hint.textContent = mac ? '⌘K' : 'Ctrl K'));
})();
