// 차수(연도/차수) 필드가 어느 프레임/폼에 있고, 저장 폼(form_m)에 포함되는지 조사
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) {
    if (!p.url().includes('ipsi')) continue;
    console.log('PAGE', p.url());
    for (const f of p.frames()) {
      const info = await f.evaluate(() => {
        const out = { forms: [], candidates: [] };
        for (const form of document.forms) {
          out.forms.push({
            name: form.name, action: form.action, method: form.method,
            fields: Array.from(form.elements).map(e => e.name).filter(Boolean).slice(0, 60),
          });
        }
        // 차수 관련 후보: select/input 중 값이 2026 / 3 / 후기 등
        for (const e of document.querySelectorAll('select,input')) {
          const label = (e.name || e.id || '');
          if (!label) continue;
          const isSel = e.tagName === 'SELECT';
          out.candidates.push({
            tag: e.tagName, name: e.name, id: e.id, type: e.type, value: e.value,
            form: e.form ? e.form.name : null,
            text: isSel && e.selectedIndex >= 0 ? e.options[e.selectedIndex].text.trim() : undefined,
            options: isSel ? Array.from(e.options).map(o => o.value + '=' + o.text.trim()).slice(0, 12) : undefined,
          });
        }
        return out;
      }).catch(() => null);
      if (!info) continue;
      const hits = info.candidates.filter(c =>
        /year|yy|chasu|cha|hoi|gbn|term|sesi|sisu|gi|no$/i.test(c.name || '') ||
        ['2026', '3'].includes(String(c.value)) ||
        (c.text && /후기|전기|정시|수시/.test(c.text))
      );
      if (hits.length || info.forms.some(fm => fm.name === 'form_m')) {
        console.log('\n─── FRAME:', f.name() || '(top)', '|', f.url().slice(0, 110));
        console.log('  FORMS:', JSON.stringify(info.forms.map(x => ({ name: x.name, action: (x.action || '').split('/').pop(), n: x.fields.length })), null, 0));
        for (const h of hits) console.log('  ★', JSON.stringify(h));
      }
    }
  }
  await browser.close();
})();
