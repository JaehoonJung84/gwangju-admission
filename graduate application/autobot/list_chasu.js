// 명부조회(gima1040): 연도/모집구분/차수로 지원자 목록 조회 (읽기 전용)
//   node list_chasu.js <chasu>
const { chromium } = require('playwright-core');
(async () => {
  const chasu = process.argv[2] || '3';
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) if (p.url().includes('ipsi_index')) page = p;
  if (!page) { console.log('입시관리 페이지 없음'); await browser.close(); return; }

  let top = page.frames().find(f => f.name() === 'right_top' && f.url().includes('gima1040'));
  if (!top) {
    const left = page.frames().find(f => f.name() === 'left_menu');
    await left.evaluate(() => { const a = [...document.querySelectorAll('a')].find(a => a.textContent.trim() === '입시지원자명부조회'); if (a) a.click(); });
    await page.waitForTimeout(3500);
    top = page.frames().find(f => f.name() === 'right_top' && f.url().includes('gima1040'));
  }
  if (!top) { console.log('명부조회 폼 없음'); await browser.close(); return; }

  await top.evaluate((ch) => {
    document.getElementsByName('chasu2')[0].value = ch;
    document.forms[0].submit();
  }, chasu);
  await page.waitForTimeout(4500);

  const res = page.frames().find(f => f.name() === 'right_center');
  const rows = await res.evaluate(() => Array.from(document.querySelectorAll('table tr'))
    .map(tr => Array.from(tr.cells).map(td => td.innerText.trim().replace(/\s+/g, ' ')).join(' | '))
    .filter(t => t.replace(/[|\s]/g, '')));
  console.log(`=== 2026 / 후기정시모집 / 차수 ${chasu} — ${Math.max(0, rows.length - 1)}명 ===`);
  rows.forEach(r => console.log('  ' + r));
  await browser.close();
})();
