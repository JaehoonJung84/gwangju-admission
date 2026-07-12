const { chromium } = require('playwright-core');
(async () => {
  const who = process.argv[2];
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null, frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; page = p; } } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }
  await frame.evaluate((nm) => { const n = document.getElementsByName('name')[0]; if (n) n.value = nm; }, who);
  await frame.evaluate(() => { const s = document.querySelector('input[type=submit][name="sub"],input[type=button][name="sub"]'); if (s) s.click(); });
  await page.waitForTimeout(2500);
  frame = null;
  for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  const d = await frame.evaluate(() => {
    const gv = n => { const e = document.getElementsByName(n)[0]; return e ? e.value : '(없음)'; };
    const topikEl = document.getElementsByName('topik')[0];
    const topikText = topikEl ? topikEl.options[topikEl.selectedIndex].text : '';
    return { koNm: gv('koNm'), labEflnYN: gv('labEflnYN'), topik: gv('topik'), topikText, topik_date: gv('topik_date') };
  });
  console.log(JSON.stringify(d, null, 1));
  await browser.close();
})();
