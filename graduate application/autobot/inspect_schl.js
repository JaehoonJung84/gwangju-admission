// 대학명 필드 구조 검증: 학교코드 연동/팝업 여부 확인
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  console.log('--- 열린 탭들 ---');
  const pages = [];
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) { pages.push(p); console.log('  ', p.url()); }
  let page = pages.find(p => p.url().includes('haksa.gwangju.ac.kr'));
  if (!page) { console.log('haksa 탭 없음'); await browser.close(); return; }
  console.log('--- 프레임들 ---');
  let frame = null;
  for (const f of page.frames()) {
    let has = false; try { has = !!(await f.$('#koNm')); } catch (e) {}
    console.log('  ', f.name() || '(no name)', '|', f.url().slice(0, 60), has ? '<= #koNm 있음' : '');
    if (has) frame = f;
  }
  if (!frame) { console.log('❌ #koNm 폼 프레임 없음 - 입시원서입력 신규 폼을 다시 열어주세요'); await browser.close(); return; }

  const info = await frame.evaluate(() => {
    const out = { fields: [], allNamedInputs: [], rowHtml: {} };
    ['colSchlNm', 'uniSchlNm', 'maSchlNm', 'docSchlNm'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) { out.fields.push({ id, exists: false }); return; }
      out.fields.push({
        id, exists: true,
        readonly: el.readOnly, disabled: el.disabled,
        onclick: el.getAttribute('onclick'),
        onfocus: el.getAttribute('onfocus'),
        onkeyup: el.getAttribute('onkeyup'),
        onchange: el.getAttribute('onchange'),
        className: el.className,
        value: el.value,
        outerHTML: el.outerHTML.slice(0, 300)
      });
      // 같은 행(row) HTML 저장 - 숨은 코드필드/버튼 확인용
      const tr = el.closest('tr');
      if (tr) out.rowHtml[id] = tr.outerHTML.slice(0, 1500);
    });
    // 학교/코드 관련 모든 input (hidden 포함)
    document.querySelectorAll('input,select').forEach(el => {
      const n = el.name || '', i = el.id || '';
      if (/sch|schl|univ|code|cd|대학/i.test(n + ' ' + i)) {
        out.allNamedInputs.push({ tag: el.tagName, type: el.type, id: i, name: n, value: (el.value || '').slice(0, 40) });
      }
    });
    return out;
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})();
