/**
 * Regression checks and screenshots for the static site.
 * Requires Playwright and its Chromium browser in the development environment.
 *   node tools/browser-check.cjs
 * Or use an existing installation:
 *   PLAYWRIGHT_MODULE=/path/to/playwright node tools/browser-check.cjs
 * Regenerate og.png and app icons from tools/share.html and favicon.svg:
 *   node tools/browser-check.cjs --render-assets
 * Preview images go to the OS temp directory, or NEXAFUSION_PREVIEW_DIR.
 * The localhost server and browser are closed when the command finishes.
 */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const output =
  process.env.NEXAFUSION_PREVIEW_DIR ||
  path.join(require('node:os').tmpdir(), 'nexafusion-preview');
fs.mkdirSync(output, { recursive: true });
const server = http.createServer((req, res) => {
  let p = path.join(root, decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (!p.startsWith(root + '/') || p.includes('/.')) {
    res.writeHead(403).end();
    return;
  }
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p)) {
    res.writeHead(404).end();
    return;
  }
  res.setHeader(
    'Content-Type',
    {
      '.html': 'text/html',
      '.js': 'text/javascript',
      '.css': 'text/css',
      '.svg': 'image/svg+xml',
      '.woff2': 'font/woff2',
      '.json': 'application/json',
      '.png': 'image/png',
    }[path.extname(p)] || 'application/octet-stream',
  );
  res.end(fs.readFileSync(p));
});
(async () => {
  await new Promise((ok, no) => {
    server.once('error', no);
    server.listen(0, '127.0.0.1', ok);
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  try {
    if (process.argv.includes('--render-assets')) {
      const imagePage = await browser.newPage({
        viewport: { width: 1200, height: 630 },
        deviceScaleFactor: 1,
        reducedMotion: 'reduce',
      });
      await imagePage.goto(base + '/tools/share.html');
      await imagePage.evaluate(() => document.fonts.ready);
      await imagePage.waitForFunction(
        () => !!document.querySelector('object').contentDocument?.querySelector('svg'),
      );
      await imagePage.screenshot({ path: path.join(root, 'og.png') });
      const svg = fs.readFileSync(path.join(root, 'favicon.svg'), 'utf8');
      for (const [size, name] of [
        [180, 'apple-touch-icon.png'],
        [192, 'icon-192.png'],
        [512, 'icon-512.png'],
      ]) {
        await imagePage.setViewportSize({ width: size, height: size });
        await imagePage.setContent(
          '<style>html,body{margin:0;width:100%;height:100%;background:#080c0c}svg{display:block;width:100%;height:100%}</style>' +
            svg,
        );
        await imagePage.screenshot({ path: path.join(root, name) });
      }
      console.log('Rendered share image and app icons from their sources');
      return;
    }
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1080 },
      reducedMotion: 'reduce',
    });
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(m.text());
    });
    await page.goto(base);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(output, 'nexafusion-desktop.png') });
    await page.screenshot({ path: path.join(output, 'nexafusion-full.png'), fullPage: true });
    for (const route of [
      '/',
      '/services/embedded-software/',
      '/services/cyber-security/',
      '/services/cra-readiness/',
      '/cra-readiness/',
      '/insights/',
      '/insights/eu-cyber-resilience-act/',
      '/insights/memory-safety-roadmaps/',
    ]) {
      await page.goto(base + route);
      await page.evaluate(() => document.fonts.ready);
      for (const width of [1440, 1024, 900, 820, 768, 640, 390, 320]) {
        await page.setViewportSize({ width, height: 900 });
        const overflow = await page.evaluate(() => ({
          page: innerWidth,
          content: document.documentElement.scrollWidth,
          actions: document.querySelector('.top-actions').getBoundingClientRect().right,
        }));
        assert.ok(
          overflow.content <= width + 1,
          `${route} page overflow at ${width}: ${JSON.stringify(overflow)}`,
        );
        assert.ok(overflow.actions <= width, `${route} header overflow at ${width}`);
      }
    }
    console.log('PASS: eight routes across eight viewport widths, no page or header overflow');
    await page.goto(base + '/');
    await page.setViewportSize({ width: 1440, height: 1000 });
    for (const layer of ['hardware', 'security', 'evidence', 'firmware']) {
      await page.locator(`.scene-selector [data-layer=${layer}]`).click();
      assert.equal(await page.locator(`#layer-${layer}`).isVisible(), true);
      assert.equal(await page.locator('.layer-panel:visible').count(), 1);
      assert.equal(
        await page.locator('.scene-selector [aria-pressed=true]').getAttribute('data-layer'),
        layer,
      );
    }
    await page.locator('[data-boot=invalid]').click();
    await page.waitForFunction(() =>
      document.getElementById('boot-trace').textContent.includes('Reject the modified payload'),
    );
    assert.match(await page.locator('#boot-note').innerText(), /no longer verifies/);
    await page.locator('[data-boot=valid]').click();
    await page.waitForFunction(() =>
      document.getElementById('boot-trace').textContent.includes('Authenticity check passed'),
    );
    assert.match(await page.locator('#boot-note').innerText(), /Verified locally/);
    await page.locator('.layer-tabs a[data-select=hardware]').click();
    await page.keyboard.press('ArrowRight');
    assert.equal(
      await page.locator('.layer-tabs [aria-current=true]').getAttribute('data-select'),
      'firmware',
    );
    await page.goto(base + '/#layer-security');
    assert.equal(await page.locator('#layer-security').isVisible(), true);
    console.log(
      'PASS: all architecture layers, actual ECDSA verification and tampering rejection, keyboard navigation and deep links',
    );
    await page.locator('[data-kbar]').click();
    await page.locator('.kbar input').fill('firmware');
    assert.ok((await page.locator('.kbar [role=option]').count()) >= 1);
    await page.keyboard.press('Enter');
    await page.waitForURL('**/services/embedded-software/');
    await page.locator('[data-kbar]').click();
    await page.locator('.kbar-list').evaluate((el) => (el.scrollTop = el.scrollHeight));
    await page.keyboard.press('Escape');
    await page.locator('[data-kbar]').click();
    assert.equal(await page.locator('.kbar-list').evaluate((el) => el.scrollTop), 0);
    await page.locator('.kbar-close').click();
    assert.equal(await page.locator('.kbar').isVisible(), false);
    await page.locator('[data-kbar]').click();
    await page.locator('.kbar input').fill('zzzzzz');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    assert.match(await page.locator('.kbar-list').innerText(), /No results/);
    await page.keyboard.press('Escape');
    console.log('PASS: search navigation, empty results, close button and scroll reset');
    await page.goto(base + '/cra-readiness/');
    await page.locator('button[type=submit]').click();
    assert.equal(await page.evaluate(() => document.activeElement.name), 'scope');
    await page.locator('input[name=scope][value=yes]').check();
    for (const input of await page.locator('fieldset:not(.scope) input[value="2"]').all())
      await input.check();
    await page.locator('button[type=submit]').click();
    assert.equal(await page.locator('.score-ring span').innerText(), '100%');
    await page.locator('input[name=report][value="0"]').check();
    assert.equal(await page.locator('#cra-result').isHidden(), true);
    assert.equal(await page.locator('#cra-result a').count(), 0);
    await page.locator('button[type=submit]').click();
    assert.equal(await page.locator('.score-ring span').innerText(), '91%');
    assert.match(
      decodeURIComponent(await page.locator('#cra-result a[href^="mailto:"]').getAttribute('href')),
      /91%/,
    );
    await page.locator('button[type=reset]').click();
    assert.equal(await page.locator('#cra-result').isHidden(), true);
    assert.equal(await page.locator('input:checked').count(), 0);
    console.log('PASS: CRA validation, scoring, stale result invalidation, email and reset');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(base + '/');
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(output, 'nexafusion-mobile.png') });
    await page.screenshot({
      path: path.join(output, 'nexafusion-mobile-full.png'),
      fullPage: true,
    });
    await page.locator('#menu').click();
    assert.equal(await page.locator('#nav').isVisible(), true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#nav').isVisible(), false);
    await page.locator('#theme').click();
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.goto(base + '/services/embedded-software/');
    assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
    await page.screenshot({ path: path.join(output, 'nexafusion-inner-mobile.png') });
    await page.goto(base + '/');
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: path.join(output, 'nexafusion-light.png') });
    const nojs = await browser.newPage({
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    await nojs.goto(base + '/');
    assert.equal(await nojs.locator('.layer-panel:visible').count(), 4);
    assert.equal(await nojs.locator('#contact').isVisible(), true);
    assert.equal(
      await nojs
        .locator('.service-card')
        .first()
        .evaluate((el) => getComputedStyle(el).opacity),
      '1',
    );
    console.log('PASS: mobile menu, saved theme and no-JavaScript content');
    assert.deepEqual(errors, []);
    console.log('PASS: no browser errors');
    const fallback = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await fallback.addInitScript(() =>
      Object.defineProperty(window.crypto, 'subtle', { value: undefined }),
    );
    await fallback.goto(base + '/');
    await fallback.locator('#explorer').scrollIntoViewIfNeeded();
    await fallback.waitForFunction(() =>
      document.getElementById('boot-note').textContent.includes('unavailable'),
    );
    assert.equal(await fallback.locator('.layer-panel:visible').count(), 1);
    console.log('PASS: graceful fallback without Web Crypto');
    await nojs.goto(base + '/cra-readiness/');
    assert.equal(await nojs.locator('button[type=submit]').isDisabled(), true);
    console.log('PASS: no-JavaScript form cannot transmit answers');
    await page.goto(base + '/services/ai-compilers/');
    await page.waitForURL('**/#services');
    await page.goto(base + '/insights/inference-cost-compilers/');
    await page.waitForURL('**/insights/');
    await page.goto(base + '/404.html');
    assert.equal(await page.getByRole('link', { name: 'Back to NexaFusion' }).isVisible(), true);
    console.log('PASS: retired routes and 404 recovery');
    console.log('Preview images: ' + output);
  } finally {
    await browser.close();
    server.close();
  }
})().catch((e) => {
  console.error(e);
  server.close();
  process.exitCode = 1;
});
