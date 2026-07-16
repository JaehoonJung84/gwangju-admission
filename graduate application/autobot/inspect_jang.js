const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0];
  let page = ctx.pages().find(p => p.url().includes('haksa.gwangju.ac.kr')) || ctx.pages()[0];
  await page.goto('https://haksa.gwangju.ac.kr/~bylee/gjuniv/index.php', { waitUntil: 'domcontentloaded', timeout: 20000 }).catch(e=>console.log('goto:',e.message));
  await page.waitForTimeout(3000);
  console.log('URL:', page.url());
  if (page.url().includes('logout') || page.url().includes('portal') || page.url().includes('gsso')) {
    console.log('❌ 로그아웃/포털로 튕김 — ~bylee 접근 불가');
    await b.close(); return;
  }
  for (const f of page.frames()) {
    const info = await f.evaluate(() => ({
      forms: document.forms.length,
      menu: Array.from(document.querySelectorAll('a')).map(a=>({t:a.textContent.trim(), on:a.getAttribute('onclick')||a.getAttribute('href')||''})).filter(x=>x.t).slice(0,60)
    })).catch(()=>null);
    if (info) {
      console.log('\n=== FRAME', JSON.stringify(f.name()||'(top)'), '|', f.url().split('/').pop().slice(0,50), 'forms='+info.forms);
      const jang = info.menu.filter(x=>/장학|입력\(신입\)|장학입력/.test(x.t));
      if (jang.length) jang.forEach(x=>console.log('  ★', x.t, '=>', x.on.slice(0,80)));
    }
  }
  await b.close();
})();
