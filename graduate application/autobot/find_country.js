const { chromium } = require('playwright-core');
(async () => {
  const kw = process.argv[2] || '우즈';
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#ntiCd')) frame = f; } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }
  const opts = await frame.evaluate((kw) => {
    const el = document.getElementById('ntiCd');
    return Array.from(el.options).filter(o => o.text.includes(kw) || (o.value || '').toUpperCase() === 'UZ').map(o => o.text + ' = ' + o.value);
  }, kw);
  console.log('매칭 옵션:', JSON.stringify(opts, null, 1));
  await browser.close();
})();
