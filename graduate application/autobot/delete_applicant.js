// 입시원서삭제(gisa1022_s.php3) — 연도/모집구분/이름으로 삭제. ⚠ 복구 불가.
//   node delete_applicant.js "<이름>" [--year=2026] [--sems=3] [--go]
// --go 없으면 드라이런(대상만 확인하고 삭제 버튼 안 누름).
//
// ⚠ 삭제 화면에는 '차수(chasu)' 필터가 없다. (연도 + 모집구분 + 이름)으로만 지운다.
//    같은 이름이 다른 차수에 있으면 그쪽이 지워질 위험이 있으니, 실행 전 명부로 중복을 확인할 것.
const { chromium } = require('playwright-core');

(async () => {
  const who = process.argv[2];
  const args = process.argv.slice(3);
  const go = args.includes('--go');
  const year = (args.find(a => a.startsWith('--year=')) || '--year=2026').split('=')[1];
  const sems = (args.find(a => a.startsWith('--sems=')) || '--sems=3').split('=')[1];
  if (!who) { console.log('사용법: node delete_applicant.js "<이름>" [--go]'); process.exit(1); }

  const browser = await chromium.connectOverCDP('http://localhost:9222');
  let page = null;
  for (const ctx of browser.contexts()) for (const p of ctx.pages()) if (p.url().includes('ipsi_index')) page = p;
  if (!page) { console.log('❌ 입시관리 페이지 없음'); await browser.close(); process.exit(1); }

  const dialogs = [];
  page.on('dialog', async d => { dialogs.push('[' + d.type() + '] ' + d.message()); try { await d.accept(); } catch (e) {} });

  // 삭제 화면 열기
  const left = page.frames().find(f => f.name() === 'left_menu');
  await left.evaluate(() => { const a = [...document.querySelectorAll('a')].find(a => a.textContent.trim() === '입시원서삭제'); if (a) a.click(); });
  await page.waitForTimeout(3000);

  let frame = page.frames().find(f => f.name() === 'right_center' && f.url().includes('gisa1022'));
  if (!frame) { console.log('❌ 삭제 폼 없음'); await browser.close(); process.exit(1); }

  const set = await frame.evaluate(({ y, s, nm }) => {
    const v = (n, val) => { const e = document.getElementsByName(n)[0]; if (e) { e.value = val; return true; } return false; };
    v('year2', y); v('sems2', s); v('name', nm);
    const g = n => { const e = document.getElementsByName(n)[0]; return e ? e.value : '(none)'; };
    return { year2: g('year2'), sems2: g('sems2'), name: g('name'), del: g('del') };
  }, { y: year, s: sems, nm: who });
  console.log(`대상: ${JSON.stringify(set)}`);

  if (!go) { console.log('(드라이런: --go 를 붙이면 실제 삭제)'); await browser.close(); return; }

  await frame.evaluate(() => {
    const b = [...document.querySelectorAll('a,input[type=submit],input[type=button],button')]
      .find(e => /삭제/.test((e.value || '') + (e.textContent || '')));
    if (b) b.click();
  });
  await page.waitForTimeout(3000);

  console.log(dialogs.length ? '📢 ' + dialogs.join(' | ') : '(팝업 없음)');
  await browser.close();
})();
