const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }
  const out = await frame.evaluate(() => {
    const lab = document.getElementsByName('labEflnYN')[0];
    const r = { labOnchange: lab ? lab.getAttribute('onchange') : '(없음)' };
    // Y로 바꾼 뒤 topik 상태
    lab.value = 'Y'; lab.dispatchEvent(new Event('change', { bubbles: true }));
    const t = document.getElementsByName('topik')[0];
    r.after_Y = { topikDisabled: t.disabled, topikValue: t.value, topikReadonly: t.readOnly };
    // N으로
    lab.value = 'N'; lab.dispatchEvent(new Event('change', { bubbles: true }));
    r.after_N = { topikDisabled: t.disabled, topikValue: t.value };
    // 관련 함수 찾기
    ['chkLab', 'labefln', 'lab_chk', 'fn_lab', 'eflnChk'].forEach(n => { if (typeof window[n] === 'function') r[n] = window[n].toString().slice(0, 300); });
    return r;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
