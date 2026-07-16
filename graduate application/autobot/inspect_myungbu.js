// 입시지원자명부조회: 연도/모집구분/차수별로 누가 들어있는지 조회 (읽기 전용)
//   node inspect_myungbu.js <chasu>
const { chromium } = require('playwright-core');
(async () => {
  const chasu = process.argv[2] || '3';
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) if (p.url().includes('ipsi_index')) page = p;
  if (!page) { console.log('입시관리 페이지 없음'); await browser.close(); return; }

  const left = page.frames().find(f => f.name() === 'left_menu');
  await left.evaluate(() => { const a = [...document.querySelectorAll('a')].find(a => a.textContent.trim() === '입시지원자명부조회'); if (a) a.click(); });
  await page.waitForTimeout(3500);

  let frame = page.frames().find(f => f.name() === 'right_center');
  const fields = await frame.evaluate(() => Array.from(document.forms[0].elements).filter(e => e.name)
    .map(e => ({ name: e.name, type: e.type, value: e.value })));
  console.log('[조회 폼 필드]', JSON.stringify(fields.map(f => f.name + '=' + f.value)));

  // 차수 입력칸 찾아서 설정 후 조회
  const set = await frame.evaluate((ch) => {
    const names = Array.from(document.forms[0].elements).filter(e => e.name).map(e => e.name);
    const chName = names.find(n => /chasu/i.test(n));
    if (chName) document.getElementsByName(chName)[0].value = ch;
    const btn = document.querySelector('input[type=submit], input[type=button][value*="조회"], input[type=submit][value*="조회"]');
    return { chName, btn: btn ? (btn.value || btn.name) : null };
  }, chasu);
  console.log('[차수 필드]', set.chName, '→', chasu, '| 조회버튼:', set.btn);

  await frame.evaluate(() => {
    const b = Array.from(document.querySelectorAll('input[type=submit],input[type=button],a,button'))
      .find(e => /조회|검색/.test((e.value || '') + (e.textContent || '')));
    if (b) b.click();
  });
  await page.waitForTimeout(4000);

  frame = page.frames().find(f => f.name() === 'right_center');
  const rows = await frame.evaluate(() => Array.from(document.querySelectorAll('table tr'))
    .map(tr => Array.from(tr.cells).map(td => td.innerText.trim().replace(/\s+/g, ' ')).join(' | '))
    .filter(t => t.replace(/[|\s]/g, '')));
  console.log(`\n=== 2026 / 후기정시모집 / 차수 ${chasu} 명부 ===`);
  rows.forEach(r => console.log('  ' + r));
  await browser.close();
})();
