// chasu2_2 가 sems2 의 미러인지, 독립 필드인지 소스에서 확인 (읽기 전용)
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) {
    try { if (await f.$('#koNm')) frame = f; } catch (e) {}
  }
  if (!frame) { console.log('입력 폼 없음 — 좌측 입시원서입력을 여세요'); await browser.close(); return; }

  const r = await frame.evaluate(() => {
    const html = document.documentElement.outerHTML;
    const out = { lines: [], scripts: [] };
    // chasu / sems 가 언급된 HTML 라인
    html.split('\n').forEach((l, i) => {
      if (/chasu|sems2/i.test(l)) out.lines.push((i + 1) + ': ' + l.trim().slice(0, 240));
    });
    // 관련 함수 정의
    for (const s of document.querySelectorAll('script')) {
      const t = s.textContent || '';
      if (/chasu|sems2/i.test(t)) {
        t.split('\n').forEach(l => { if (/chasu|sems2|function/i.test(l)) out.scripts.push(l.trim().slice(0, 200)); });
      }
    }
    const el = document.getElementsByName('chasu2_2')[0];
    const sems = document.getElementsByName('sems2')[0];
    return {
      ...out,
      chasu: el ? { value: el.value, readOnly: el.readOnly, onchange: el.getAttribute('onchange'), outer: el.outerHTML } : null,
      semsOnchange: sems ? sems.getAttribute('onchange') : null,
      semsOuter: sems ? sems.outerHTML.slice(0, 300) : null,
    };
  });
  console.log('=== chasu2_2 요소 ===');
  console.log(JSON.stringify(r.chasu, null, 1));
  console.log('\n=== sems2 onchange ===', r.semsOnchange);
  console.log(r.semsOuter);
  console.log('\n=== HTML 내 chasu/sems2 언급 ===');
  r.lines.slice(0, 30).forEach(l => console.log('  ' + l));
  console.log('\n=== script 내 언급 ===');
  [...new Set(r.scripts)].slice(0, 40).forEach(l => console.log('  ' + l));
  await browser.close();
})();
