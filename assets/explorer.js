import { verifyBootExample } from './boot-verifier.js';

/* Illustrative architecture with real signature verification of a public sample. */
(() => {
  const scene = document.getElementById('device-scene');
  const art = scene?.querySelector('.device-art');
  const panels = [...document.querySelectorAll('.layer-panel')];
  const links = [...document.querySelectorAll('[data-select]')];
  const buttons = [...document.querySelectorAll('.scene-selector [data-layer]')];
  if (!scene || panels.length !== 4 || links.length !== 4) return;

  const names = {
    hardware: '01 / Physical interfaces',
    firmware: '02 / Firmware & execution',
    security: '03 / Trust & verification',
    evidence: '04 / Traceable evidence',
  };
  const sceneLabel = document.getElementById('scene-label');
  sceneLabel.setAttribute('role', 'status');
  const setLayer = (layer) => {
    if (!Object.hasOwn(names, layer)) return;
    scene.dataset.layer = layer;
    sceneLabel.textContent = names[layer];
    for (const button of buttons)
      button.setAttribute('aria-pressed', String(button.dataset.layer === layer));
    for (const link of links) {
      if (link.dataset.select === layer) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    }
    for (const panel of panels) panel.hidden = panel.id !== 'layer-' + layer;
  };
  const layerFromHash = () => location.hash.replace(/^#layer-/, '');
  setLayer(Object.hasOwn(names, layerFromHash()) ? layerFromHash() : 'firmware');
  buttons.forEach((button) =>
    button.addEventListener('click', () => setLayer(button.dataset.layer)),
  );
  links.forEach((link, index) => {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      setLayer(link.dataset.select);
      history.replaceState(null, '', link.hash);
    });
    link.addEventListener('keydown', (event) => {
      const delta = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
      const next =
        event.key === 'Home'
          ? 0
          : event.key === 'End'
            ? links.length - 1
            : delta
              ? (index + delta + links.length) % links.length
              : -1;
      if (next < 0) return;
      event.preventDefault();
      links[next].focus();
      links[next].click();
    });
  });
  addEventListener('hashchange', () => {
    const layer = layerFromHash();
    if (Object.hasOwn(names, layer)) {
      setLayer(layer);
      document.getElementById('layer-' + layer).scrollIntoView({ block: 'start' });
    }
  });

  const trace = document.getElementById('boot-trace');
  const bootNote = document.getElementById('boot-note');
  const bootButtons = [...document.querySelectorAll('[data-boot]')];
  let verificationSequence = 0;
  const checkPayload = async (button) => {
    const sequence = ++verificationSequence;
    const tampered = button.dataset.boot === 'invalid';
    bootButtons.forEach((other) => other.setAttribute('aria-pressed', String(other === button)));
    trace.setAttribute('aria-busy', 'true');
    bootNote.textContent = 'Checking the sample with your browser’s Web Crypto API…';
    let result;
    try {
      result = await verifyBootExample(tampered);
    } catch {
      result = { supported: false };
    }
    if (sequence !== verificationSequence) return;
    trace.removeAttribute('aria-busy');
    if (!result.supported) {
      trace.hidden = true;
      bootNote.textContent =
        'Signature verification is unavailable in this browser or connection. Inspect the source below; the architecture explorer still works.';
      return;
    }
    trace.hidden = false;
    const invalid = !result.valid;
    const steps = invalid
      ? [
          'Load payload with one altered byte',
          'Verify against the original signature',
          'Signature verification returns false',
          'Reject the modified payload',
        ]
      : [
          'Load the original signed payload',
          'Verify ECDSA P-256 / SHA-256',
          'Signature verification returns true',
          'Authenticity check passed',
        ];
    trace.replaceChildren(
      ...steps.map((text, index) => {
        const item = document.createElement('li');
        const number = document.createElement('span');
        number.textContent = String(index + 1).padStart(2, '0');
        item.append(number, document.createTextNode(text));
        if (index === steps.length - 1) item.className = 'trace-outcome';
        return item;
      }),
    );
    trace.classList.toggle('is-invalid', invalid);
    bootNote.textContent =
      `${result.byteLength} sample bytes · SHA-256 ${result.digest.slice(0, 16)}… ` +
      (invalid
        ? 'One changed byte. The original signature no longer verifies.'
        : 'Verified locally in your browser.') +
      ' A complete boot design also needs trusted keys, version policy and secure recovery.';
  };
  bootButtons.forEach((button) => button.addEventListener('click', () => checkPayload(button)));
  checkPayload(bootButtons[0]);

  /* Pointer response only while interacting; no permanent render loop. */
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(pointer: fine)');
  let frame = 0;
  let pointer = null;
  const reset = () => {
    cancelAnimationFrame(frame);
    frame = 0;
    pointer = null;
    art.style.removeProperty('--device-rx');
    art.style.removeProperty('--device-ry');
  };
  art.addEventListener('pointermove', (event) => {
    if (reduce.matches || !fine.matches) return;
    pointer = { x: event.clientX, y: event.clientY };
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      const bounds = art.getBoundingClientRect();
      art.style.setProperty(
        '--device-rx',
        ((0.5 - (pointer.y - bounds.top) / bounds.height) * 6).toFixed(2) + 'deg',
      );
      art.style.setProperty(
        '--device-ry',
        (((pointer.x - bounds.left) / bounds.width - 0.5) * 8).toFixed(2) + 'deg',
      );
    });
  });
  art.addEventListener('pointerleave', reset);
  reduce.addEventListener('change', reset);
  let inView = true;
  const syncMotion = () => {
    const paused = !inView || document.hidden;
    scene.classList.toggle('is-offscreen', paused);
    if (paused) reset();
  };
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting;
      syncMotion();
    }).observe(scene);
  }
  document.addEventListener('visibilitychange', syncMotion);
  syncMotion();
})();
