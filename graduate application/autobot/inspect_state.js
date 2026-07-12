const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let frame = null, page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) { for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; page = p; } } catch (e) {} } }
  if (!frame) { console.log('폼 프레임 없음'); await browser.close(); return; }
  const info = await frame.evaluate(() => {
    const g = id => { const e = document.getElementById(id); return e ? e.value : '(없음)'; };
    const radios = [];
    document.querySelectorAll('input[type=radio]').forEach(r => radios.push({ id: r.id, name: r.name, checked: r.checked, onclick: r.getAttribute('onclick'), label: (r.parentElement ? r.parentElement.textContent.trim().slice(0, 20) : '') }));
    // 신규/입력 관련 버튼·링크
    const btns = [];
    document.querySelectorAll('a,input[type=button],button').forEach(b => { const t = ((b.value || '') + (b.textContent || '')).trim(); if (/신규|추가|초기화|입력|처리|저장|new/i.test(t) || /new|add|init|clear/i.test(b.id || '')) btns.push({ tag: b.tagName, id: b.id, text: t.slice(0, 15), onclick: (b.getAttribute('onclick') || '').slice(0, 60) }); });
    return {
      url: location.href,
      curVals: { koNm: g('koNm'), ssn1: g('ssn1'), gdhlDeptCd: g('gdhlDeptCd'), gdhlGbCd: g('gdhlGbCd') },
      radios, btns
    };
  });
  console.log('right_center URL:', info.url);
  console.log('\n현재 폼 값(저장 후):', JSON.stringify(info.curVals));
  console.log('\n라디오버튼:', JSON.stringify(info.radios, null, 1));
  console.log('\n관련 버튼/링크:', JSON.stringify(info.btns, null, 1));
  await browser.close();
})();
