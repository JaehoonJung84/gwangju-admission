// Sheet2 덤프(sheet2rows.ps1 산출) → 지원자별 입력 JSON(data/NN_이름.json) 생성
// 사용: node gen_applicants.js <rows.json>
const fs = require('fs');
const path = require('path');

const rows = JSON.parse(fs.readFileSync(process.argv[2], 'utf8').replace(/^﻿/, ''));
const OUT = path.join(__dirname, 'data');

// 열 인덱스 (강향옥 수정본 Sheet2)
const C = {
  no: 0, gubun: 2, name: 3, en: 4, dept: 5, sex: 6, birth: 7, ssn: 8,
  col: 9, uni: 15, ma: 21,          // 각 학력 블록 시작 (학교명)
  topik: 27, topikDate: 28,
};
// 블록 내 오프셋: +0 학교명, +1 성적, +2 연제, +3 졸업학과, +4 졸업일자, +5 학위번호

// 학과 → (대학원구분 코드, 폼 옵션 검색 문자열)
// 대학원구분: 일반=4, 사회복지전문=7, 보건상담정책=9  (모집요강 기준, HANDOFF §5)
const DEPT = {
  '간호학과':       { ma: '9', doc: '4', find: '간호' },
  '컴퓨터공학과':   { ma: '4', doc: '4', find: '컴퓨터' },
  '법학과':         { ma: '9', doc: '4', find: '법학' },
  '뷰티미용학':     { ma: '4', doc: '4', find: '뷰티' },
  '호텔관광경영학과': { ma: '4', doc: '4', find: '호텔관광' },
  '평생교육학과':   { ma: '4', doc: '4', find: '평생교육' },
  '경영학':         { ma: '4', doc: '4', find: '경영' },   // ⚠ 곽전량: 폼 옵션명 확인 필요
  '미래융합기술공학': { ma: '4', doc: '4', find: '미래융합' },
};

// 한국 소재 대학 (이 목록에 없으면 "(외국)" 접두어를 붙인다)
const KR_SCHOOLS = new Set([
  '경운대학교', '아주대학교', '전주대학교', '대진대학교', '동신대학교', '초당대학교',
  '광주여자대학교', '대구대학교', '인하대학교', '전남대학교', '계명대학교',
]);

const PECT = { '4.5': '1', '4.50': '1', '4.3': '2', '4.30': '2', '4.0': '3', '4.00': '3', '4': '3', '100': '4' };

const pad2 = n => String(n).padStart(2, '0');

// 엑셀 날짜(직렬번호 또는 "2025.6.12" / "2025-06-12") → YYYYMMDD
function toYmd(v) {
  if (!v) return '';
  const s = String(v).trim();
  if (/^\d{5}$/.test(s)) {                        // 엑셀 직렬번호
    const d = new Date(Date.UTC(1899, 11, 30) + Number(s) * 86400000);
    return `${d.getUTCFullYear()}${pad2(d.getUTCMonth() + 1)}${pad2(d.getUTCDate())}`;
  }
  const m = s.match(/^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})$/);
  if (m) return `${m[1]}${pad2(m[2])}${pad2(m[3])}`;
  return null;                                     // 파싱 실패 → 호출부에서 경고
}

// "3.42/4.5" → { sco:'3.42', pect:'1' }
function toScore(v) {
  if (!v) return null;
  const m = String(v).trim().match(/^([\d.]+)\s*\/\s*([\d.]+)$/);
  if (!m) return null;
  const pect = PECT[m[2]];
  if (!pect) return { sco: m[1], pect: null, denom: m[2] };   // 폼에 없는 만점 → 경고
  return { sco: m[1], pect };
}

function school(name) {
  const s = String(name || '').trim();
  if (!s) return '';
  return KR_SCHOOLS.has(s) ? s : `(외국)${s}`;
}

// 학력 블록 하나 파싱
function eduBlock(c, base, warn, label) {
  const schl = (c[base] || '').trim();
  if (!schl) return null;
  const sc = toScore(c[base + 1]);
  const dt = toYmd(c[base + 4]);
  const degRaw = (c[base + 5] || '').trim();
  const yejeong = degRaw.includes('졸업예정');

  if (!sc) warn.push(`${label} 성적 없음/형식오류: "${c[base + 1]}"`);
  else if (!sc.pect) warn.push(`${label} 만점 ${sc.denom} — 폼에 없는 만점(4.5/4.3/4.0/100만 지원)`);
  if (dt === null) warn.push(`${label} 졸업일자 형식오류: "${c[base + 4]}"`);
  if (!dt) warn.push(`${label} 졸업일자 없음`);

  return {
    schl: school(schl),
    dept: (c[base + 3] || '').trim(),
    dt: dt || '',
    gb: yejeong ? '3' : '1',
    sco: sc ? sc.sco : '',
    pect: sc && sc.pect ? sc.pect : '',
    deg: yejeong ? '' : degRaw,
  };
}

// 외국인등록번호 뒤 7자리. 없으면 임시번호 [코드]999999
//   1900년대생 남5/여6, 2000년대생 남7/여8   (HANDOFF §5)
function ssn2(regNo, birthYmd, sex, warn) {
  const s = String(regNo || '').trim();
  const m = s.match(/-\s*(\d{7})$/);
  if (m) return { v: m[1], temp: false };
  if (s) warn.push(`외국인등록번호 형식 이상: "${s}" → 임시번호 사용`);
  const y2000 = Number(birthYmd.slice(0, 4)) >= 2000;
  const male = sex === '남';
  const code = y2000 ? (male ? '7' : '8') : (male ? '5' : '6');
  return { v: `${code}999999`, temp: true };
}

// ── 본문 ─────────────────────────────────────────────────────────────
const out = [];
let cancelled = false;

for (const row of rows) {
  const c = row.c;
  if (String(c[0]).trim() === '취소자') { cancelled = true; continue; }   // 이 아래는 취소자
  if (cancelled) { out.push({ skip: `취소자: ${c[C.name]}` }); continue; }

  const no = String(c[C.no]).trim();
  if (!/^\d+$/.test(no)) continue;                    // 헤더 행 등
  const gubun = String(c[C.gubun]).trim();            // 석사 / 박사
  if (gubun !== '석사' && gubun !== '박사') continue;

  const warn = [];
  const nameKr = String(c[C.name]).trim();
  const deptRaw = String(c[C.dept]).trim();
  const isBilingual = deptRaw.includes('이중언어');
  const deptBase = deptRaw.replace(/\(.*?\)/g, '').trim();
  const dmap = DEPT[deptBase];
  if (!dmap) { warn.push(`학과 매핑 없음: "${deptBase}"`); }

  const birth = toYmd(c[C.birth]);
  if (!birth) warn.push(`생년월일 형식오류: "${c[C.birth]}"`);
  const sex = String(c[C.sex]).trim();
  const s2 = ssn2(c[C.ssn], birth || '', sex, warn);
  if (s2.temp) warn.push(`외국인등록번호 미기재 → 임시번호 ${s2.v}`);

  // TOPIK: 급수 있으면 그대로, 없으면 해당없음(9)
  const tRaw = String(c[C.topik] || '');
  const tm = tRaw.match(/(\d)\s*급/);
  const topik = tm ? tm[1] : '9';
  let topikDate = '';
  if (tm) {
    topikDate = toYmd(c[C.topikDate]) || '';
    if (!topikDate) warn.push(`TOPIK ${tm[1]}급인데 유효기간 없음`);
  }

  const edu = {};
  const col = eduBlock(c, C.col, warn, '전문대');
  const uni = eduBlock(c, C.uni, warn, '학사');
  const ma = eduBlock(c, C.ma, warn, '석사');
  if (col) edu.col = col;
  if (uni) edu.uni = uni;
  if (ma) edu.ma = ma;
  if (!uni) warn.push('학사(4년제) 학력 없음');
  if (gubun === '박사' && !ma) warn.push('박사 지원인데 석사 학력 없음');

  const data = {
    name_kr: nameKr,
    select_by_value: {
      gdhlEtexScrnGbCd: '3',                                   // 외국인특별전형
      gdhlDegCosCd: gubun === '석사' ? '40' : '41',
      gdhlEtshGbCd: '1',                                       // 신입학
      LAB_EFLN_YN: isBilingual ? 'Y' : 'N',
      gdhlGbCd: dmap ? (gubun === '석사' ? dmap.ma : dmap.doc) : '',
    },
    select_late: { topik },
    dept_substring: dmap ? dmap.find : '',
    text: {
      koNm: nameKr,
      enNm: String(c[C.en]).trim().replace(/\s+/g, ' '),
      ssn1: (birth || '').slice(2),
      topik_date: topikDate,
      mobpNo1: '062', mobpNo2: '670', mobpNo3: '2855',
      sample6_postcode: '61743',
      sample6_address: '전남광주통합특별시 남구 효덕로 277 광주대학교',
      sample6_address2: '호심관 6층 국제협력처',
    },
    text_by_name: { ssn2: s2.v },
    select_by_text: { ntiCd: '중국' },
    edu,
  };

  const file = path.join(OUT, `${String(no).padStart(2, '0')}_${nameKr.replace(/[·\s]/g, '')}.json`);
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
  out.push({ no, name: nameKr, gubun, dept: deptBase, lab: isBilingual ? 'Y' : 'N', topik, topikDate, ssn2: s2.v, file: path.basename(file), warn });
}

// ── 리포트 ───────────────────────────────────────────────────────────
console.log('생성:', out.filter(o => o.file).length, '건\n');
for (const o of out) {
  if (o.skip) { console.log(`   -  ${o.skip} (건너뜀)`); continue; }
  console.log(`${String(o.no).padStart(2)} ${o.name} (${o.gubun}/${o.dept}) 이중언어=${o.lab} TOPIK=${o.topik}${o.topikDate ? '/' + o.topikDate : ''} ssn2=${o.ssn2}`);
  for (const w of o.warn) console.log(`      ⚠ ${w}`);
}
