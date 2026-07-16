const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0];
  let page = ctx.pages().find(p => p.url().includes('~bylee')) || ctx.pages().find(p=>p.url().includes('haksa'));
  // 장학입력(신입) 메뉴 클릭
  const left = page.frames().find(f => f.name()==='left');
  await left.evaluate(() => { const a=[...document.querySelectorAll('a')].find(a=>a.textContent.trim()==='장학입력(신입)'); if(a) a.click(); });
  await page.waitForTimeout(3000);

  // 수험번호 입력칸/찾기 있는 프레임 찾기
  let ff=null;
  for (const f of page.frames()) {
    const has = await f.evaluate(() => {
      const inps=[...document.querySelectorAll('input')];
      return inps.length>0 && (document.body.innerText.includes('수험번호')||document.body.innerText.includes('찾기')||document.body.innerText.includes('장학'));
    }).catch(()=>false);
    if (has) { ff=f; }
  }
  if(!ff){ console.log('폼 프레임 못찾음'); await b.close(); return; }
  console.log('폼 프레임:', ff.name()||ff.url());

  // 초기 폼 필드 덤프
  const dump = await ff.evaluate(() => {
    const forms=[...document.forms].map(fm=>({name:fm.name, action:(fm.action||'').split('/').pop(), method:fm.method,
      fields:[...fm.elements].filter(e=>e.name||e.id).map(e=>({tag:e.tagName,name:e.name,id:e.id,type:e.type,value:(e.value||'').slice(0,20)}))}));
    const btns=[...document.querySelectorAll('a,input[type=button],input[type=submit],button,img')]
      .map(e=>({txt:((e.value||'')+(e.alt||'')+(e.textContent||'')).trim().slice(0,15),on:(e.getAttribute('onclick')||'').slice(0,60)}))
      .filter(x=>/찾기|저장|검색/.test(x.txt)||/find|save|search|submit/i.test(x.on));
    return {forms,btns};
  });
  console.log('\n[초기 폼]');
  dump.forms.forEach(fm=>{ console.log(` form "${fm.name}" -> ${fm.action}`); fm.fields.forEach(f=>console.log(`   ${f.name||f.id} [${f.type}]`)); });
  console.log('[버튼]'); dump.btns.forEach(x=>console.log('  ·',x.txt,'|',x.on));

  // 테스트: 3210001 넣고 찾기 (저장 안 함)
  console.log('\n=== 3210001 조회 테스트 ===');
  await ff.evaluate(() => {
    const inp=[...document.querySelectorAll('input[type=text]')].find(e=>e.offsetParent!==null);
    if(inp){ inp.value='3210001'; }
  });
  await ff.evaluate(() => {
    const btn=[...document.querySelectorAll('a,input[type=button],input[type=submit],img,button')].find(e=>/찾기|검색/.test((e.value||'')+(e.alt||'')+(e.textContent||'')));
    if(btn) btn.click();
  });
  await page.waitForTimeout(3500);
  // 재탐색 후 전체 폼 덤프 (외국인장학 필드 찾기)
  let gf=null;
  for (const f of page.frames()){ const h=await f.evaluate(()=>document.body&&document.body.innerText.includes('외국인장학')).catch(()=>false); if(h) gf=f; }
  gf=gf||ff;
  const after = await gf.evaluate(() => {
    const out=[];
    for(const fm of document.forms){ for(const e of fm.elements){ if(e.name||e.id) out.push({form:fm.name,name:e.name,id:e.id,type:e.type,value:(e.value||'').slice(0,25)});}}
    // 외국인장학 라벨 주변 텍스트
    const bodytxt=document.body.innerText.split('\n').filter(l=>/외국인장학|수업금|성명|수험번호/.test(l)).slice(0,10);
    return {out,bodytxt, koNm:(document.getElementsByName('name')[0]||{}).value};
  });
  console.log('불러온 폼 필드:');
  after.out.forEach(f=>console.log(`  ${f.name||f.id} [${f.type}] = "${f.value}"`));
  console.log('관련 텍스트:', JSON.stringify(after.bodytxt));
  await b.close();
})();
