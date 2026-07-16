// 저장된 지원자 값을 data/*.json 원본과 대조 검증
// 사용: node verify_all.js [파일패턴...]   (없으면 data/NN_*.json 전체)
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const DATA = path.join(__dirname, 'data');
const files = (process.argv.length > 2 ? process.argv.slice(2)
  : fs.readdirSync(DATA).filter(f => /^\d\d_.*\.json$/.test(f)).sort().map(f => path.join(DATA, f)));

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages())
    for (const f of p.frames()) { try { if (await f.$('#koNm')) page = p; } catch (e) {} }
  if (!page) { console.log('❌ 폼 없음'); await browser.close(); return; }

  const findFrame = async () => {
    for (const f of page.frames()) { try { if (await f.$('#koNm')) return f; } catch (e) {} }
    return null;
  };

  let okCount = 0; const problems = [];

  for (const file of files) {
    const d = JSON.parse(fs.readFileSync(file, 'utf8'));
    const name = d.name_kr;

    let frame = await findFrame();
    await frame.evaluate(nm => { const n = document.getElementsByName('name')[0]; if (n) n.value = nm; }, name);
    await frame.evaluate(() => { const s = document.querySelector('input[type=submit][name="sub"], input[type=button][name="sub"]'); if (s) s.click(); });
    await page.waitForTimeout(2500);
    frame = await findFrame();
    if (!frame) { problems.push(`${name}: 불러오기 실패`); continue; }

    const got = await frame.evaluate(() => {
      const g = id => { const e = document.getElementById(id); return e ? e.value : null; };
      const byName = n => { const e = document.getElementsByName(n)[0]; return e ? e.value : null; };
      const arr = n => Array.from(document.getElementsByName(n)).map(e => e.value);
      return {
        koNm: g('koNm'), enNm: g('enNm'), ssn1: g('ssn1'),
        ssn2: (document.querySelector('input[name="ssn2"]') || {}).value,
        gdhlGbCd: g('gdhlGbCd'), gdhlDegCosCd: g('gdhlDegCosCd'), gdhlDeptCd: g('gdhlDeptCd'),
        labEflnYN: byName('labEflnYN'), topik: byName('topik'), topik_date: byName('topik_date'),
        ntiCd: g('ntiCd'),
        schlNm: arr('schlNm[]'), grtnDt: arr('grtnDt[]'), scoNo: arr('scoNo[]'),
        pectScoCd: arr('pectScoCd[]'), grtnGbCd: arr('grtnGbCd[]'), degNo: arr('degNo[]'),
      };
    });

    const bad = [];
    const cmp = (label, exp, act) => { if (String(exp) !== String(act)) bad.push(`${label}: 기대="${exp}" 실제="${act}"`); };
    // 성적은 숫자값으로 비교 (서버가 "4.00"을 "4"로 정규화해 저장)
    const cmpNum = (label, exp, act) => {
      if (String(exp) === String(act)) return;
      if (exp !== '' && act !== '' && Number(exp) === Number(act)) return;
      bad.push(`${label}: 기대="${exp}" 실제="${act}"`);
    };

    if (got.koNm !== name) { problems.push(`${name}: 불러온 이름이 "${got.koNm}" — 검색 실패로 판단, 건너뜀`); continue; }
    cmp('enNm', d.text.enNm, got.enNm);
    cmp('ssn1', d.text.ssn1, got.ssn1);
    cmp('ssn2', d.text_by_name.ssn2, got.ssn2);
    cmp('대학원구분', d.select_by_value.gdhlGbCd, got.gdhlGbCd);
    cmp('학위과정', d.select_by_value.gdhlDegCosCd, got.gdhlDegCosCd);
    cmp('이중언어', d.select_by_value.LAB_EFLN_YN, got.labEflnYN);
    // TOPIK 해당없음(9)은 서버가 빈값으로 저장한다 (실제 급수는 그대로 유지됨)
    if (!(d.select_late.topik === '9' && (got.topik || '') === '')) cmp('TOPIK', d.select_late.topik, got.topik);
    cmp('TOPIK유효기간', d.text.topik_date, got.topik_date || '');

    // 학력: col/uni/ma → 배열 인덱스 0/1/2
    const idx = { col: 0, uni: 1, ma: 2, doc: 3 };
    for (const [k, i] of Object.entries(idx)) {
      const e = d.edu[k];
      if (!e) {
        if (got.schlNm[i]) bad.push(`학력[${k}]: 원본엔 없는데 저장값 "${got.schlNm[i]}"`);
        continue;
      }
      cmp(`학력[${k}].학교`, e.schl, got.schlNm[i]);
      cmp(`학력[${k}].졸업일`, e.dt, got.grtnDt[i]);
      cmpNum(`학력[${k}].성적`, e.sco, got.scoNo[i]);
      cmp(`학력[${k}].만점`, e.pect, got.pectScoCd[i]);
      cmp(`학력[${k}].졸업구분`, e.gb, got.grtnGbCd[i]);
      cmp(`학력[${k}].학위번호`, e.deg, got.degNo[i]);
    }

    if (bad.length) { problems.push(`${name}\n      ` + bad.join('\n      ')); console.log(`❌ ${name}`); }
    else { okCount++; console.log(`✅ ${name}`); }
  }

  console.log(`\n═══ 결과: 일치 ${okCount} / ${files.length} ═══`);
  if (problems.length) { console.log('\n[불일치]'); problems.forEach(p => console.log('  • ' + p)); }
  await browser.close();
})();
