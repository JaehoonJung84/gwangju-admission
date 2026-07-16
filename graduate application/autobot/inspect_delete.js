// 좌측 메뉴 페이지 열어서 구조 확인 (읽기 전용)
//   node inspect_delete.js "입시원서삭제"
const { chromium } = require('playwright-core');
(async () => {
  const menu = process.argv[2] || '입시원서삭제';
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) if (p.url().includes('ipsi_index')) page = p;
  if (!page) { console.log('입시관리 페이지 없음'); await browser.close(); return; }

  const left = page.frames().find(f => f.name() === 'left_menu');
  const links = await left.evaluate(() => Array.from(document.querySelectorAll('a')).map(a => a.textContent.trim()).filter(Boolean));
  console.log('좌측 메뉴:', links.join(' | '));

  await left.evaluate((m) => {
    const a = Array.from(document.querySelectorAll('a')).find(a => a.textContent.trim() === m);
    if (a) a.click();
  }, menu);
  await page.waitForTimeout(3500);

  for (const f of page.frames()) {
    if (f.name() !== 'right_center') continue;
    const info = await f.evaluate(() => {
      const forms = Array.from(document.forms).map(fm => ({
        name: fm.name, action: fm.action, method: fm.method,
        fields: Array.from(fm.elements).filter(e => e.name).map(e => ({
          name: e.name, type: e.type, value: e.value,
          options: e.tagName === 'SELECT' ? Array.from(e.options).map(o => o.value + '=' + o.text.trim()) : undefined,
        })),
      }));
      const btns = Array.from(document.querySelectorAll('a,input[type=button],input[type=submit],button'))
        .map(e => ((e.value || '') + (e.textContent || '')).trim() + (e.getAttribute('onclick') ? ' onclick=' + e.getAttribute('onclick') : ''))
        .filter(Boolean);
      const rows = Array.from(document.querySelectorAll('table tr')).slice(0, 40)
        .map(tr => Array.from(tr.cells).map(td => td.innerText.trim().replace(/\s+/g, ' ')).join(' | '))
        .filter(t => t.replace(/\|/g, '').trim());
      return { url: location.href, forms, btns, rows };
    }).catch(e => ({ err: String(e) }));
    console.log('\n=== right_center:', info.url);
    console.log('\n[FORMS]');
    for (const fm of info.forms || []) {
      console.log(` form "${fm.name}" → ${(fm.action || '').split('/').pop()} (${fm.method})`);
      for (const fl of fm.fields) console.log(`   - ${fl.name} [${fl.type}] = ${JSON.stringify(fl.value)}${fl.options ? ' opts=' + fl.options.join(',') : ''}`);
    }
    console.log('\n[버튼/링크]');
    (info.btns || []).forEach(b => console.log('  ·', b));
    console.log('\n[표 내용]');
    (info.rows || []).forEach(r => console.log('  ', r));
  }
  await browser.close();
})();
