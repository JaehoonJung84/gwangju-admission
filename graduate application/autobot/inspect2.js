const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) {
    for (const p of ctx.pages()) {
      for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; break; } } catch (e) {} }
      if (frame) break;
    }
    if (frame) break;
  }
  if (!frame) { console.log('❌ #koNm 폼 프레임 없음'); await browser.close(); return; }
  const info = await frame.evaluate(() => {
    const out = {};
    // daihak 함수 소스
    try { out.daihak = window.daihak ? window.daihak.toString() : '(window.daihak 없음)'; } catch (e) { out.daihak = 'err ' + e; }
    // 모든 hidden input
    out.hidden = [];
    document.querySelectorAll('input[type=hidden]').forEach(el => out.hidden.push({ id: el.id, name: el.name, value: (el.value || '').slice(0, 30) }));
    // 폼 정보
    const forms = [];
    document.querySelectorAll('form').forEach(f => forms.push({ name: f.name, action: f.action, method: f.method }));
    out.forms = forms;
    // schlNm 관련: 같은 셀/행에 다른 hidden 있나 재확인 + colSchlNm 뒤 형제요소
    const c = document.getElementById('colSchlNm');
    out.colSchlNm_parentTd = c ? c.closest('td').innerHTML : null;
    return out;
  });
  console.log('=== daihak() 함수 ===');
  console.log(info.daihak);
  console.log('\n=== hidden inputs ===');
  console.log(JSON.stringify(info.hidden, null, 1));
  console.log('\n=== forms ===');
  console.log(JSON.stringify(info.forms, null, 1));
  console.log('\n=== colSchlNm 부모 td ===');
  console.log(info.colSchlNm_parentTd);
  await browser.close();
})();
