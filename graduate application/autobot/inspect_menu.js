const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) page = p; } catch (e) {} }
  if (!page) { console.log('페이지 없음'); await browser.close(); return; }
  for (const f of page.frames()) {
    const nm = f.name();
    if (nm === 'left_menu') {
      const links = await f.evaluate(() => {
        const out = [];
        document.querySelectorAll('a').forEach(a => out.push({ text: a.textContent.trim().slice(0, 20), href: a.getAttribute('href'), onclick: (a.getAttribute('onclick') || '').slice(0, 80), target: a.target }));
        return out;
      });
      console.log('=== left_menu 링크 ===');
      links.forEach(l => { if (l.text) console.log(JSON.stringify(l)); });
    }
  }
  // subm 함수와 신규입력 관련 함수도 확인 (right_center)
  for (const f of page.frames()) {
    if (f.name() === 'right_center') {
      const fns = await f.evaluate(() => {
        const names = ['subm', 'newForm', 'addnew', 'init', 'reset', 'ipwon', 'input_new'];
        const out = {};
        names.forEach(n => { try { out[n] = typeof window[n] === 'function' ? window[n].toString().slice(0, 200) : '(없음)'; } catch (e) { out[n] = 'err'; } });
        return out;
      });
      console.log('\n=== right_center 함수들 ===');
      console.log(JSON.stringify(fns, null, 1));
    }
  }
  await browser.close();
})();
