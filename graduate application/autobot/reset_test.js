const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) page = p; } catch (e) {} }
  if (!page) { for (const ctx of browser.contexts()) for (const p of ctx.pages()) if (p.url().includes('ipsi_index')) page = p; }
  if (!page) { console.log('페이지 없음'); await browser.close(); return; }

  const left = page.frames().find(f => f.name() === 'left_menu');
  console.log('left_menu:', !!left);
  // 입시원서입력 클릭
  await left.evaluate(() => {
    const a = Array.from(document.querySelectorAll('a')).find(a => a.textContent.trim() === '입시원서입력');
    if (a) a.click();
  });
  await page.waitForTimeout(3500);

  // 폼 프레임 재탐색 및 상태 확인
  let frame = null;
  for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('클릭 후 #koNm 폼 없음. 프레임들:'); page.frames().forEach(f => console.log('  ', f.name(), f.url().slice(0, 70))); await browser.close(); return; }
  const st = await frame.evaluate(() => {
    const g = id => { const e = document.getElementById(id); return e ? e.value : '(없음)'; };
    const gName = n => { const e = document.getElementsByName(n)[0]; return e ? e.value : '(없음)'; };
    return { url: location.href, koNm: g('koNm'), ssn1: g('ssn1'), year2: gName('year2'), sems2: gName('sems2'), chasu: gName('chasu2_2'), gdhlGbCd: g('gdhlGbCd') };
  });
  console.log('리셋 후 폼 상태:', JSON.stringify(st, null, 1));
  await browser.close();
})();
