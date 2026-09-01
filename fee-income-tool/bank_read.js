/* 광주은행 거래내역조회 화면에서 입금 건을 읽고, 증빙 캡쳐를 저장한다.
 *
 * 전제 : 크롬을 원격디버깅으로 띄우고 그 창에서 은행에 로그인해 거래내역을 조회해 둔다.
 *   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug-profile
 * 비밀번호·인증서는 이 스크립트가 다루지 않는다. 사람이 로그인한 창을 그대로 쓴다.
 *
 * 사용 : node bank_read.js [--out data]
 * 출력 : data/bank_rows.tsv  (입금자명 <TAB> 금액 <TAB> 거래일시)
 *        data/bank_full.png  (전체 화면 캡쳐 — crop_bank.py 가 잘라 쓴다)
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require(path.join(
  'C:', 'projects', 'graduate application', 'autobot', 'node_modules', 'playwright-core'));

const OUT = process.argv.includes('--out')
  ? process.argv[process.argv.indexOf('--out') + 1]
  : path.join(__dirname, 'data');

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const pages = [];
  for (const ctx of browser.contexts()) pages.push(...ctx.pages());

  let page = null;
  for (const p of pages) {
    const t = ((await p.title().catch(() => '')) + ' ' + p.url()).toLowerCase();
    if (t.includes('kjbank') || t.includes('gwangjubank') || t.includes('광주은행')) { page = p; break; }
  }
  if (!page) {
    console.error('광주은행 탭을 찾지 못했습니다. 원격디버깅 크롬에서 거래내역조회 화면을 띄워 주세요.');
    console.error('열린 탭:');
    for (const p of pages) console.error('   ' + (await p.title().catch(() => '')) + '  ' + p.url());
    process.exit(2);
  }
  console.error('대상 탭: ' + (await page.title()) + '  ' + page.url());

  // 거래내역 표 읽기 — 표 구조가 바뀌어도 견디도록 머리글로 열을 찾는다
  const rows = await page.evaluate(() => {
    const tables = [...document.querySelectorAll('table')];
    let best = null, bestScore = 0;
    for (const t of tables) {
      const head = t.innerText.slice(0, 200);
      let s = 0;
      for (const k of ['거래일시', '입금', '통장잔액', '내용1']) if (head.includes(k)) s++;
      if (s > bestScore) { bestScore = s; best = t; }
    }
    if (!best || bestScore < 3) return [];
    const cells = r => [...r.querySelectorAll('th,td')].map(c => c.innerText.trim());
    const all = [...best.querySelectorAll('tr')].map(cells).filter(r => r.length > 3);
    if (!all.length) return [];
    const head = all[0];
    const idx = name => head.findIndex(h => h.replace(/\s/g, '').startsWith(name));
    const iWhen = idx('거래일시'), iName = idx('내용1'), iIn = idx('입금'), iKind = idx('구분');
    return all.slice(1).map(r => ({
      when: iWhen >= 0 ? r[iWhen] : '',
      name: iName >= 0 ? r[iName] : '',
      kind: iKind >= 0 ? r[iKind] : '',
      amount: iIn >= 0 ? r[iIn].replace(/[^0-9]/g, '') : '',
    })).filter(r => r.name && r.amount && (!r.kind || r.kind.includes('입금')));
  });

  fs.mkdirSync(OUT, { recursive: true });
  const tsv = rows.map(r => [r.name, r.amount, r.when].join('\t')).join('\n');
  fs.writeFileSync(path.join(OUT, 'bank_rows.tsv'), tsv + (tsv ? '\n' : ''), 'utf8');
  await page.screenshot({ path: path.join(OUT, 'bank_full.png'), fullPage: false });

  console.error('입금 ' + rows.length + '건');
  for (const r of rows) console.error('   ' + r.when + '  ' + r.name + '  ' + r.amount);
  console.error('저장: ' + path.join(OUT, 'bank_rows.tsv') + ' , bank_full.png');
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
