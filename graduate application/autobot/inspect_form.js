const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }
  const out = await frame.evaluate(() => {
    const r = {};
    const fm = document.form_m || document.forms['form_m'] || document.forms[0];
    r.formCount = document.forms.length;
    r.formActions = Array.from(document.forms).map(f => ({ name: f.getAttribute('name'), action: f.getAttribute('action'), fieldCount: f.elements.length }));
    // 각 필드가 어느 폼 소속인지
    const check = id => { const e = document.getElementById(id); if (!e) return '(없음)'; const f = e.form; return f ? (f.getAttribute('action') || f.getAttribute('name') || 'form') : 'NO FORM'; };
    r.membership = { koNm: check('koNm'), ssn1: check('ssn1'), gdhlDeptCd: check('gdhlDeptCd'), colSchlNm: check('colSchlNm'), uniSchlNm: check('uniSchlNm'), colGrtnDt: check('colGrtnDt') };
    // colSchlNm 이 form_m.elements 에 포함되는지 + 테스트값
    const col = document.getElementById('colSchlNm');
    if (col) { Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(col, 'TESTSCHOOL'); }
    // form_m 이 제출할 학력 관련 필드 목록
    r.eduFieldsInForm = [];
    if (fm) {
      for (const el of fm.elements) {
        if (/schlNm|deptNm|grtnDt|scoNo|grtnGbCd|pectScoCd|degNo|AcrrGb/i.test(el.name || '')) {
          r.eduFieldsInForm.push({ name: el.name, id: el.id, type: el.type, disabled: el.disabled, value: (el.value || '').slice(0, 20) });
        }
      }
    }
    r.colSchlNm_inFormElements = fm ? Array.from(fm.elements).includes(col) : 'no form';
    return r;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
