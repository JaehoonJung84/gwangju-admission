// 광주대 입시원서 자동입력 - Playwright(CDP, 기존 로그인 크롬에 연결)
// 사용: node fill_applicant.js <데이터.json> [submit]
//   submit 인자를 주면 "처리"까지 클릭(저장). 없으면 채우기만(검토 모드).
const { chromium } = require('playwright-core');
const fs = require('fs');

(async () => {
  const dataPath = process.argv[2];
  const args = process.argv.slice(3);
  const doSubmit = args.includes('submit');
  const doLoad = args.includes('--load'); // 기존 지원자 검색해 수정모드로 불러온 뒤 채움
  const doReset = args.includes('--reset'); // 신규: 입시원서입력 메뉴 클릭해 빈 폼으로 초기화 후 채움
  if (!dataPath) { console.log('사용법: node fill_applicant.js <데이터.json> [submit] [--load]'); process.exit(1); }
  const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null, frame = null;
  for (const ctx of browser.contexts()) {
    for (const p of ctx.pages()) {
      for (const f of p.frames()) { try { if (await f.$('#koNm')) { frame = f; page = p; break; } } catch (e) {} }
      if (frame) break;
    }
    if (frame) break;
  }
  if (!frame) { console.log('❌ 입력 폼(#koNm)을 못 찾음 (입시원서입력 신규 폼을 여세요)'); await browser.close(); process.exit(1); }
  console.log('페이지:', page.url());

  // 신규 빈 폼 리셋: 좌측 '입시원서입력' 메뉴 클릭
  if (doReset) {
    const left = page.frames().find(f => f.name() === 'left_menu');
    if (left) {
      await left.evaluate(() => { const a = Array.from(document.querySelectorAll('a')).find(a => a.textContent.trim() === '입시원서입력'); if (a) a.click(); });
      await page.waitForTimeout(3500);
      frame = null;
      for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
      if (!frame) { console.log('❌ 리셋 후 폼 없음'); await browser.close(); process.exit(1); }
      const kn = await frame.evaluate(() => (document.getElementById('koNm') || {}).value);
      console.log('폼 리셋 완료 (신규 빈 폼, koNm="' + kn + '")');
    }
  }

  // 기존 지원자 불러오기(수정모드): 이름 검색 → 재탐색
  if (doLoad) {
    await frame.evaluate((nm) => { const n = document.getElementsByName('name')[0]; if (n) n.value = nm; }, data.name_kr);
    await frame.evaluate(() => { const s = document.querySelector('input[type=submit][name="sub"], input[type=button][name="sub"]'); if (s) s.click(); });
    await page.waitForTimeout(3000);
    frame = null;
    for (const f of page.frames()) { try { if (await f.$('#koNm')) frame = f; } catch (e) {} }
    if (!frame) { console.log('❌ 불러오기 후 폼 없음'); await browser.close(); process.exit(1); }
    const loaded = await frame.evaluate(() => ({ koNm: (document.getElementById('koNm') || {}).value, exam: (document.getElementsByName('sesu') || document.getElementsByName('exam_no') || [{}])[0] ? true : false }));
    console.log('불러옴:', loaded.koNm || '(비어있음-검색실패?)');
  }
  console.log('폼 프레임:', frame.name() || frame.url());

  // 1) 기본 셀렉트 설정 + 캐스케이드 드라이버 재발화
  await frame.evaluate((d) => {
    for (const [id, val] of Object.entries(d.select_by_value)) {
      const el = document.getElementById(id);
      if (el) { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }
    }
    ['gdhlGbCd', 'gdhlDegCosCd', 'gdhlEtexScrnGbCd'].forEach(id => { const el = document.getElementById(id); if (el) el.dispatchEvent(new Event('change', { bubbles: true })); });
  }, data);

  // 2) 지원학과 옵션 로딩 대기
  if (data.dept_substring) {
    await frame.waitForFunction((sub) => {
      const el = document.getElementById('gdhlDeptCd');
      return el && Array.from(el.options).some(o => o.text.replace(/\s/g, '').includes(sub));
    }, data.dept_substring, { timeout: 15000 }).catch(() => console.log('⚠ 지원학과 옵션 로딩 타임아웃'));
  }

  // 3) 나머지 필드 채우기
  const result = await frame.evaluate((d) => {
    const log = [];
    const proto = el => { const w = el.ownerDocument.defaultView; return el.tagName === 'SELECT' ? w.HTMLSelectElement.prototype : w.HTMLInputElement.prototype; };
    const setNative = (el, val) => Object.getOwnPropertyDescriptor(proto(el), 'value').set.call(el, val);
    const fire = el => { el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); };
    const text = (id, val) => { const el = document.getElementById(id); if (!el) { log.push('MISS ' + id); return; } setNative(el, val); fire(el); log.push('OK   ' + id + ' = ' + val); };
    const selVal = (id, val) => { const el = document.getElementById(id); if (!el) { log.push('MISS ' + id); return; } el.value = val; fire(el); log.push((el.value === val ? 'OK   ' : '?    ') + id + ' = ' + val); };
    const selText = (id, sub) => { const el = document.getElementById(id); if (!el) { log.push('MISS ' + id); return; } const opts = Array.from(el.options); const o = opts.find(x => x.text.trim() === sub) || opts.find(x => x.text.replace(/\s/g, '') === sub.replace(/\s/g, '')) || opts.find(x => x.text.replace(/\s/g, '').includes(sub)); if (o) { el.value = o.value; fire(el); log.push('OK   ' + id + ' = ' + o.text.trim()); } else log.push('MISS ' + id + ' (' + sub + ')'); };

    if (d.dept_substring) selText('gdhlDeptCd', d.dept_substring);
    for (const [id, val] of Object.entries(d.select_late || {})) selVal(id, val);
    for (const [id, val] of Object.entries(d.text || {})) text(id, val);
    for (const [nm, val] of Object.entries(d.text_by_name || {})) {
      const el = document.querySelector('input[name="' + nm + '"]:not([type=hidden])') || document.querySelector('input[name="' + nm + '"]');
      if (!el) { log.push('MISS name=' + nm); continue; }
      setNative(el, val); fire(el); log.push('OK   [name]' + nm + ' = ' + val);
    }
    for (const [id, sub] of Object.entries(d.select_by_text || {})) selText(id, sub);
    const prefixes = { col: 'col', uni: 'uni', ma: 'ma', doc: 'doc' };
    for (const [k, p] of Object.entries(prefixes)) {
      const e = d.edu && d.edu[k]; if (!e) continue;
      if (e.schl) text(p + 'SchlNm', e.schl);
      if (e.dept) text(p + 'DeptNm', e.dept);
      if (e.dt) text(p + 'GrtnDt', e.dt);
      if (e.gb) selVal(p + 'GrtnGbCd', e.gb);
      if (e.sco) text(p + 'ScoNo', e.sco);
      if (e.pect) selVal(p + 'PectScoCd', e.pect);
      if (e.deg) text(p + 'DegNo', e.deg);
    }
    // 최종 read-back (실제 저장될 핵심 값 확인)
    const rb = {};
    ['gdhlEtexScrnGbCd', 'gdhlGbCd', 'gdhlDegCosCd', 'gdhlDeptCd', 'gdhlEtshGbCd', 'labEflnYN', 'topik', 'topik_date', 'ssn1'].forEach(n => { const e = document.getElementsByName(n)[0]; rb[n] = e ? e.value : '(none)'; });
    rb.ssn2 = (document.querySelector('input[name="ssn2"]') || {}).value;
    return { log, rb };
  }, data);
  console.log('\n=== 입력 결과 (' + (data.name_kr || '') + ') ===');
  console.log(result.log.join('\n'));
  console.log('\n=== 저장 직전 read-back ===');
  console.log(JSON.stringify(result.rb));

  if (doSubmit) {
    const dialogs = [];
    page.on('dialog', async d => { dialogs.push('[' + d.type() + '] ' + d.message()); try { await d.accept(); } catch (e) {} });
    let clicked = false;
    try {
      clicked = await frame.evaluate(() => {
        const all = document.querySelectorAll('a,button,input,img,span,div');
        for (const e of all) {
          const t = ((e.value || '') + (e.alt || '') + (e.textContent || '')).replace(/\s/g, '');
          if (t.indexOf('처리') >= 0 && (e.tagName === 'A' || e.tagName === 'BUTTON' || e.type === 'button' || e.type === 'submit' || e.getAttribute('onclick'))) { e.click(); return true; }
        }
        return false;
      });
    } catch (e) { console.log('(클릭 후 페이지 전환 감지)'); clicked = true; }
    await page.waitForTimeout(3000);
    console.log(clicked ? '\n✅ 처리(저장) 클릭 실행됨.' : '\n⚠ 처리 버튼을 못 찾음 - 화면에서 직접 클릭하세요.');
    if (dialogs.length) console.log('📢 시스템 메시지: ' + dialogs.join('  |  '));
    else console.log('(팝업 메시지 없음 - 화면 상태를 확인하세요)');
  } else {
    console.log('\n(검토 모드: 저장 안 함. 화면 확인 후 "submit" 인자로 재실행하면 저장)');
  }
  await browser.close(); // CDP 연결만 끊김. 크롬은 안 닫힘.
})();
