// 특정 지원자를 (현재 차수로) 불러온 뒤 form_m 전체 필드/값을 덤프 → 저장 키(수험번호) 파악
const { chromium } = require('playwright-core');
(async () => {
  const who = process.argv[2];
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null, frame = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) for (const f of p.frames()) {
    try { if (await f.$('#koNm')) { frame = f; page = p; } } catch (e) {}
  }
  if (!frame) { console.log('폼 없음'); await browser.close(); return; }

  const hdr = () => frame.evaluate(() => {
    const v = n => { const e = document.getElementsByName(n)[0]; return e ? e.value : null; };
    return { year2: v('year2'), sems2: v('sems2'), chasu2_2: v('chasu2_2') };
  });
  console.log('검색 전 차수 헤더:', JSON.stringify(await hdr()));

  if (who) {
    await frame.evaluate(nm => { const n = document.getElementsByName('name')[0]; if (n) n.value = nm; }, who);
    await frame.evaluate(() => { const s = document.querySelector('input[type=submit][name="sub"], input[type=button][name="sub"]'); if (s) s.click(); });
    await page.waitForTimeout(3000);
    frame = null;
    for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
    if (!frame) { console.log('불러오기 후 폼 없음'); await browser.close(); return; }
  }

  const dump = await frame.evaluate(() => {
    const form = document.forms['form_m'] || document.forms[0];
    const out = [];
    for (const e of form.elements) {
      if (!e.name) continue;
      if (/^(schlNm|deptNm|grtnDt|grtnGbCd|scoNo|pectScoCd|degNo|gdhlAcrrGbCd)\[\]$/.test(e.name)) continue; // 학력배열 생략
      out.push({ name: e.name, type: e.type, value: e.value });
    }
    return { action: form.action, method: form.method, fields: out };
  });
  console.log('\naction:', dump.action, '| method:', dump.method);
  console.log('\n=== form_m 필드 (학력배열 제외) ===');
  for (const f of dump.fields) {
    const mark = /no|no$|sesu|ex_no|susi|수험/i.test(f.name) ? ' ★' : '';
    console.log(`  ${f.name.padEnd(22)} [${f.type.padEnd(8)}] = ${JSON.stringify(f.value)}${mark}`);
  }
  await browser.close();
})();
