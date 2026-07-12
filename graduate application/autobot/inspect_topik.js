const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }
  const out = await frame.evaluate(() => {
    const r = {};
    const dumpAll = (sel, label) => { r[label] = Array.from(document.querySelectorAll(sel)).map(e => ({ tag: e.tagName, type: e.type, id: e.id, name: e.name, value: e.value })); };
    dumpAll('[id="topik"]', 'id_topik');
    dumpAll('[name="topik"]', 'name_topik');
    dumpAll('[id="topik_date"]', 'id_topik_date');
    dumpAll('[name="topik_date"]', 'name_topik_date');
    // 현재 로드된 사람
    r.koNm = (document.getElementById('koNm') || {}).value;
    return r;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
