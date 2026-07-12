const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  // 인증된 컨텍스트 찾기
  let ctx = browser.contexts()[0];
  const page = await ctx.newPage();
  const url = 'https://haksa.gwangju.ac.kr/~yslee/ghakjuk/ipsi/giam/s_daihak.php3?idx=0';
  await page.goto(url, { waitUntil: 'domcontentloaded' }).catch(e => console.log('goto err', e.message));
  const html = await page.content();
  console.log('URL:', page.url());
  console.log('=== 팝업 HTML (앞 6000자) ===');
  console.log(html.slice(0, 6000));
  await page.close();
  await browser.close();
})();
