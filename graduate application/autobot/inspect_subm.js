const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('폼 프레임 없음 (입시원서입력 폼을 열어주세요)'); await browser.close(); return; }
  const out = await frame.evaluate(() => {
    const r = {};
    r.subm = window.subm ? window.subm.toString() : '(없음)';
    // 학력 수집 관련 함수 후보
    ['chk_hak', 'hakryuk', 'set_hak', 'fn_hak', 'gohak', 'check_hak', 'hak_chk', 'daihak', 'chk', 'check'].forEach(n => { if (typeof window[n] === 'function') r[n] = window[n].toString().slice(0, 400); });
    // form 이름과 학력행 class(college/university/master/doctor) 표시상태
    const rows = {};
    ['college', 'university', 'master', 'doctor'].forEach(c => { const tr = document.querySelector('tr.' + c); rows[c] = tr ? { display: getComputedStyle(tr).display, visible: tr.offsetParent !== null } : '(없음)'; });
    r.rows = rows;
    return r;
  });
  console.log('=== subm() 전체 ===\n' + out.subm);
  console.log('\n=== 학력 관련 함수 ===');
  Object.keys(out).forEach(k => { if (!['subm', 'rows'].includes(k)) console.log('\n[' + k + ']\n' + out[k]); });
  console.log('\n=== 학력 행 표시상태 ===\n' + JSON.stringify(out.rows, null, 1));
  await browser.close();
})();
