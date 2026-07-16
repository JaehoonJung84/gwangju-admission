// 학부 장학입력(신입) 자동화 - ipsr2350
//   node fill_scholarship.js test          → 48명 조회만(저장X), 수험번호/성명 대조 점검
//   node fill_scholarship.js one 3210001 --go → 1명 저장 + 재조회 검증
//   node fill_scholarship.js go             → 48명 저장 + 각 건 재조회 검증
const { chromium } = require('playwright-core');
const fs = require('fs');

const DATA = JSON.parse(fs.readFileSync('C:/Users/user/AppData/Local/Temp/claude/C--projects/bc35f1fa-b7b5-478b-abc9-586980f2ca0c/scratchpad/input_data.json','utf8'))
  .filter(x => typeof x.sch==='number' && x.sch>0)
  .map(x => ({ suhum:String(x.suhum).trim(), name:x.name, amount:Math.round(x.sch) }))
  .sort((a,b)=>a.suhum.localeCompare(b.suhum));

const MENU='https://haksa.gwangju.ac.kr/~bylee/gjuniv/ipsi2026/ipsr2350.php3';
const nrm = s => String(s||'').replace(/\s/g,'');

async function loadForm(page){
  const left = page.frames().find(f=>f.name()==='left');
  await left.evaluate(()=>{const a=[...document.querySelectorAll('a')].find(a=>a.textContent.trim()==='장학입력(신입)'); a&&a.click();});
  await page.waitForTimeout(1400);
  return page.frames().find(f=>f.name()==='right_top');
}
// 조회 후 p_weekook_suup(외국인장학) 필드가 있는 프레임을 반환
async function formFrame(page){
  for (const f of page.frames()){
    const has = await f.evaluate(()=>!!document.getElementsByName('p_weekook_suup')[0] && !!document.getElementsByName('p_suhum_no')[0]).catch(()=>false);
    if (has) return f;
  }
  return null;
}
async function search(page, suhum){
  // 검색 입력칸은 초기 폼(p_search_text)에 있음 - 있는 프레임을 찾아 입력/클릭
  let sf=null;
  for (const f of page.frames()){
    const h=await f.evaluate(()=>!!document.getElementsByName('p_search_text')[0]).catch(()=>false);
    if(h){sf=f;break;}
  }
  if(!sf) return {suhum:'',irum:'',suup:'',frame:null,err:'검색폼없음'};
  await sf.evaluate(s=>{const i=document.getElementsByName('p_search_text')[0]; i.value=s;}, suhum);
  await sf.evaluate(()=>{const b=[...document.querySelectorAll('a,input,img,button')].find(e=>/찾기/.test((e.value||'')+(e.alt||'')+(e.textContent||''))); b&&b.click();});
  await page.waitForTimeout(2400);
  const ff = await formFrame(page);
  if(!ff) return {suhum:'',irum:'',suup:'',frame:null,err:'조회폼없음'};
  const v = await ff.evaluate(()=>({
    suhum:((document.getElementsByName('p_suhum_no')[0]||{}).value||'').trim(),
    irum:((document.getElementsByName('p_irum')[0]||{}).value||'').trim(),
    suup:((document.getElementsByName('p_weekook_suup')[0]||{}).value||'').trim(),
  }));
  v.frameName = ff.name();
  return v;
}

(async () => {
  const mode = process.argv[2]||'test';
  const doSave = mode==='go' || process.argv.includes('--go');
  const onlyId = mode==='one' ? process.argv[3] : null;
  const list = onlyId ? DATA.filter(x=>x.suhum===onlyId) : DATA;

  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = b.contexts()[0];
  let page = ctx.pages().find(p=>p.url().includes('~bylee')) || ctx.pages().find(p=>p.url().includes('haksa'));
  const dialogs=[];
  page.on('dialog', async d=>{ dialogs.push(d.message()); try{await d.accept();}catch(e){} });

  console.log(`모드=${mode} 저장=${doSave} 대상=${list.length}명\n`);
  const results=[];
  for (const st of list){
    let r={...st};
    try{
      await loadForm(page);
      const q = await search(page, st.suhum);
      r.loadedSuhum=q.suhum; r.loadedName=q.irum; r.before=q.suup;
      if(q.suhum!==st.suhum){ r.status='❌수험번호불일치'; results.push(r); console.log(`${st.suhum} ${st.name}: ❌ 조회 수험번호=${q.suhum}`); continue; }
      if(nrm(q.irum)!==nrm(st.name)){ r.status='❌성명불일치'; results.push(r); console.log(`${st.suhum} ${st.name}: ❌ 성명 불일치 (폼:${q.irum})`); continue; }
      if(!doSave){ r.status='✔조회OK'; results.push(r); console.log(`${st.suhum} ${st.name}: ✔ 매칭 (기존수업금="${q.suup}")`); continue; }
      // 저장
      dialogs.length=0;
      let ff = await formFrame(page);
      await ff.evaluate(a=>{const i=document.getElementsByName('p_weekook_suup')[0]; i.value=String(a);}, st.amount);
      await ff.evaluate(()=>{const p=document.getElementsByName('p_proc')[0]; p&&p.click();});
      await page.waitForTimeout(2600);
      r.dialog=dialogs.slice();
      // 재조회 검증
      await loadForm(page);
      const q2 = await search(page, st.suhum);
      r.after=q2.suup;
      const ok = String(parseInt(q2.suup||'0',10))===String(st.amount);
      r.status = ok ? '✅저장확인' : '⚠저장후불일치';
      results.push(r);
      console.log(`${st.suhum} ${st.name}: ${r.status} 입력=${st.amount} 재조회=${q2.suup} ${r.dialog.length?'['+r.dialog.join('|')+']':''}`);
    }catch(e){ r.status='❌예외:'+e.message; results.push(r); console.log(`${st.suhum} ${st.name}: ❌ ${e.message}`); }
  }
  // 요약
  const cnt={}; results.forEach(r=>cnt[r.status]=(cnt[r.status]||0)+1);
  console.log('\n=== 요약 ===', JSON.stringify(cnt));
  fs.writeFileSync('C:/Users/user/AppData/Local/Temp/claude/C--projects/bc35f1fa-b7b5-478b-abc9-586980f2ca0c/scratchpad/jang_result.json', JSON.stringify(results,null,1));
  await b.close();
})();
