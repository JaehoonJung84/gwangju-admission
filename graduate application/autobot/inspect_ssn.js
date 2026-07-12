const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) { for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; } } catch (e) {} } }
  const info = await frame.evaluate(() => {
    const out = { byName_ssn1: [], byName_ssn2: [], byName_exno: [], byId_ssn2: [], allSsn: [] };
    document.querySelectorAll('input[name="ssn1"]').forEach(e => out.byName_ssn1.push({ type: e.type, id: e.id, value: e.value }));
    document.querySelectorAll('input[name="ssn2"]').forEach(e => out.byName_ssn2.push({ type: e.type, id: e.id, value: e.value }));
    document.querySelectorAll('input[name="ex_no"]').forEach(e => out.byName_exno.push({ type: e.type, id: e.id, value: e.value }));
    // id=ssn2 를 가진 모든 요소(중복 id 확인)
    document.querySelectorAll('[id="ssn2"]').forEach(e => out.byId_ssn2.push({ tag: e.tagName, type: e.type, name: e.name, value: e.value }));
    document.querySelectorAll('[id="ssn1"]').forEach(e => out.allSsn.push({ which: 'id=ssn1', tag: e.tagName, type: e.type, name: e.name, value: e.value }));
    return out;
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})();
