const { chromium } = require('playwright-core');
(async () => {
  const who = process.argv[2] || '';
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null, frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; page = p; } } catch (e) {} }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }

  // datepicker 형식 먼저 확인
  const dfmt = await frame.evaluate(() => {
    try { return (window.jQuery && jQuery('#colGrtnDt').datepicker) ? jQuery('#colGrtnDt').datepicker('option', 'dateFormat') : '(jq/datepicker 확인불가)'; } catch (e) { return 'err ' + e.message; }
  });
  console.log('datepicker dateFormat:', dfmt);

  // 검색: 학번/이름에 이름 넣고 검색
  await frame.evaluate((nm) => { const n = document.getElementsByName('name')[0]; if (n) n.value = nm; }, who);
  const clicked = await frame.evaluate(() => {
    const subs = Array.from(document.querySelectorAll('input[type=submit][name="sub"], input[type=button][name="sub"]'));
    if (subs.length) { subs[0].click(); return subs.length; }
    return 0;
  });
  console.log('검색버튼 클릭:', clicked);
  await page.waitForTimeout(3000);

  // 재탐색 후 학력 값 덤프
  frame = null;
  for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
  if (!frame) { console.log('검색 후 폼 없음'); await browser.close(); return; }
  const dump = await frame.evaluate(() => {
    const g = id => { const e = document.getElementById(id); return e ? e.value : null; };
    const arr = name => Array.from(document.getElementsByName(name)).map(e => e.value);
    return {
      koNm: g('koNm'), gdhlGbCd: g('gdhlGbCd'), gdhlDeptCd: g('gdhlDeptCd'),
      schlNm: arr('schlNm[]'), deptNm: arr('deptNm[]'), grtnDt: arr('grtnDt[]'),
      grtnGbCd: arr('grtnGbCd[]'), scoNo: arr('scoNo[]'), pectScoCd: arr('pectScoCd[]'),
      degNo: arr('degNo[]'), gdhlAcrrGbCd: arr('gdhlAcrrGbCd[]')
    };
  });
  console.log('\n=== 불러온 지원자 학력 ===');
  console.log(JSON.stringify(dump, null, 1));
  await browser.close();
})();
