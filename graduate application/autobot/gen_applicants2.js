// 2026 후기 추가모집 2차 명단(★2026학년도 후기 대학원 2차 지원자 현황_정리본.xlsx, 시트 '대학원')
//   → 지원자별 입력 JSON(data2/NN_이름.json) 생성
// 사용: node gen_applicants2.js <rows.json>
//
// 1차(gen_applicants.js)와 다른 점:
//  - 열 배치: [0]순서 [2]구분(석사/박사/석사편입) [3]이름 [4]영문 [5]학과 [6]국적 [7]성별
//              [8]여권 [9]등록번호(YYMMDD-XXXXXXX, 임시번호도 이 형식으로 기재됨)
//              [10~]전문대 [16~]학사 [22~]석사 블록(+0교명 +1평점 +2연제 +3전공 +4졸업일 +5학위번호)
//              [28]토픽 (유효기간 열 없음 → 공란, 추후 보완 예정 — 2026-08-09 담당자 지시)
//  - 생년월일 열 없음 → 등록번호 앞 6자리를 ssn1로 사용
//  - '석사편입' = 학위과정 석사(40) + 입학구분 편입학(2) (2026-08-09 담당자 확인)
//  - 졸업'예정'은 날짜 열에 적혀 있음("2026.8월 예정" 등) → 졸업구분 3, 일자 미상이면 월말로
//  - 학위번호 "8월 제출 예정" → 공란 (졸업일이 예정이 아니면 졸업구분은 졸업 유지)
const fs = require('fs');
const path = require('path');

const rows = JSON.parse(fs.readFileSync(process.argv[2], 'utf8').replace(/^﻿/, ''));
const OUT = path.join(__dirname, 'data2');
fs.mkdirSync(OUT, { recursive: true });

const C = {
  no: 0, gubun: 2, name: 3, en: 4, dept: 5, nati: 6, sex: 7, regNo: 9,
  col: 10, uni: 16, ma: 22, topik: 28,
};

// 학과 → (대학원구분, 폼 옵션 검색 문자열). 모집요강 9차(2026 후기 추가) 대조 완료:
//  - 임상상담심리학과 석사 = 보건상담정책대학원(9), 이중언어 O
//  - 시각영상디자인 = 일반대학원(4) 예체능 '디자인학과'의 시각영상 전공 → 폼 학과는 '디자인'으로 검색
const DEPT = {
  '간호학과':       { ma: '9', doc: '4', find: '간호' },
  '컴퓨터공학과':   { ma: '4', doc: '4', find: '컴퓨터' },
  '법학과':         { ma: '9', doc: '4', find: '법학' },
  '임상상담심리학과': { ma: '9', doc: '4', find: '임상상담' },
  '시각영상디자인': { ma: '4', doc: '4', find: '디자인' },
  '디자인학과':     { ma: '4', doc: '4', find: '디자인' },
  '미래융합기술공학과': { ma: '4', doc: '4', find: '미래융합' },
  '미래융합기술공학':   { ma: '4', doc: '4', find: '미래융합' },
};

const KR_SCHOOLS = new Set([
  '경운대학교', '아주대학교', '전주대학교', '대진대학교', '동신대학교', '초당대학교',
  '광주여자대학교', '대구대학교', '인하대학교', '전남대학교', '계명대학교',
  '디지털서울문화예술대학교', '광주대학교',
]);
// 엑셀 오탈자 교정 (원본 표기 → 정식 교명)
const SCHOOL_FIX = { '디저털서울문화예술대학교': '디지털서울문화예술대학교' };

const PECT = { '4.5': '1', '4.50': '1', '4.3': '2', '4.30': '2', '4.0': '3', '4.00': '3', '4': '3', '100': '4' };
const pad2 = n => String(n).padStart(2, '0');

function toYmd(v) {
  if (!v) return '';
  let s = String(v).trim();
  if (/^\d{5}(\.\d+)?$/.test(s)) {
    const d = new Date(Date.UTC(1899, 11, 30) + Math.round(Number(s)) * 86400000);
    return `${d.getUTCFullYear()}${pad2(d.getUTCMonth() + 1)}${pad2(d.getUTCDate())}`;
  }
  s = s.replace(/[.\-/]+/g, '-').replace(/-$/, '');      // "2026-02.-11" 같은 이중 구분자 정리
  const m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (m) return `${m[1]}${pad2(m[2])}${pad2(m[3])}`;
  return null;
}

// 날짜 칸의 '예정' 처리: "2026.8.14 예정"→(3, 20260814) / "2026.8월 예정"→(3, 20260831+경고)
function parseDate(v, warn, label) {
  const s = String(v || '').trim();
  if (!s) { warn.push(`${label} 졸업일자 없음`); return { dt: '', gb: null }; }
  if (s.includes('예정')) {
    let m = s.match(/(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})/);
    if (m) return { dt: `${m[1]}${pad2(m[2])}${pad2(m[3])}`, gb: '3' };
    m = s.match(/(\d{4})[.\-/](\d{1,2})월?/);
    if (m) {
      warn.push(`${label} "${s}" — 일자 미상, 해당 월 말일(${m[1]}${pad2(m[2])}31?)로 추정 기입 → 확인 필요`);
      const last = new Date(Date.UTC(Number(m[1]), Number(m[2]), 0)).getUTCDate();
      return { dt: `${m[1]}${pad2(m[2])}${pad2(last)}`, gb: '3' };
    }
    warn.push(`${label} 졸업일자 파싱 불가: "${s}"`);
    return { dt: '', gb: '3' };
  }
  const dt = toYmd(s);
  if (dt === null) { warn.push(`${label} 졸업일자 형식오류: "${s}"`); return { dt: '', gb: null }; }
  return { dt, gb: null };
}

function toScore(v) {
  if (!v) return null;
  const m = String(v).trim().match(/^([\d.]+)\s*\/\s*([\d.]+)$/);
  if (!m) return null;
  const pect = PECT[m[2]];
  if (!pect) return { sco: m[1], pect: null, denom: m[2] };
  return { sco: m[1], pect };
}

function school(name) {
  let s = String(name || '').trim();
  if (!s) return '';
  s = SCHOOL_FIX[s] || s;
  return KR_SCHOOLS.has(s) ? s : `(외국)${s}`;
}

function eduBlock(c, base, warn, label, forceGb) {
  const schl = (c[base] || '').trim();
  if (!schl) return null;
  const sc = toScore(c[base + 1]);
  const { dt, gb } = parseDate(c[base + 4], warn, label);
  let degRaw = (c[base + 5] || '').trim();
  if (degRaw.includes('예정')) {                     // "8월 제출 예정", "졸업예정" 등
    warn.push(`${label} 학위번호 "${degRaw}" → 공란 처리`);
    degRaw = '';
  }
  if (!sc) warn.push(`${label} 성적 없음/형식오류: "${c[base + 1]}"`);
  else if (!sc.pect) warn.push(`${label} 만점 ${sc.denom} — 폼에 없는 만점(4.5/4.3/4.0/100만 지원)`);

  return {
    schl: school(schl),
    dept: (c[base + 3] || '').trim(),
    dt,
    gb: forceGb || gb || '1',
    sco: sc ? sc.sco : '',
    pect: sc && sc.pect ? sc.pect : '',
    deg: degRaw,
  };
}

// ── 본문 ─────────────────────────────────────────────────────────────
const out = [];
for (const row of rows) {
  const c = row.c;
  const no = String(c[C.no]).trim();
  if (!/^\d+$/.test(no)) continue;
  const gubunRaw = String(c[C.gubun]).trim();        // 석사 / 박사 / 석사편입
  if (!/^(석사|박사)/.test(gubunRaw)) continue;
  const isDoc = gubunRaw.startsWith('박사');
  const isTransfer = gubunRaw.includes('편입');

  const warn = [];
  const nameKr = String(c[C.name]).trim();
  const deptRaw = String(c[C.dept]).trim();
  const isBilingual = deptRaw.includes('이중언어');
  const deptBase = deptRaw.replace(/\(.*?\)/g, '').trim();
  const dmap = DEPT[deptBase];
  if (!dmap) warn.push(`학과 매핑 없음: "${deptBase}"`);

  // 등록번호 "YYMMDD-XXXXXXX" → ssn1/ssn2
  const reg = String(c[C.regNo] || '').trim();
  const rm = reg.match(/^(\d{6})\s*-\s*(\d{7})$/);
  if (!rm) warn.push(`등록번호 형식 이상: "${reg}"`);
  const s1 = rm ? rm[1] : '';
  const s2 = rm ? rm[2] : '';
  if (/9{6}$/.test(s2)) warn.push(`임시 등록번호(${s2}) — 실번호 확보 시 --load 재저장`);

  const tRaw = String(c[C.topik] || '');
  const tm = tRaw.match(/(\d)\s*급/);
  const topik = tm ? tm[1] : '9';
  if (tm) warn.push(`TOPIK ${tm[1]}급 — 유효기간 공란(추후 보완 예정, 2026-08-09 지시)`);

  const edu = {};
  const col = eduBlock(c, C.col, warn, '전문대');
  const uni = eduBlock(c, C.uni, warn, '학사');
  // 이모디(석사편입): 석사 재학 이력 있으나 졸업일자 기재 → 담당자 지시대로 '졸업(1)'
  const ma = eduBlock(c, C.ma, warn, '석사');
  if (col) edu.col = col;
  if (uni) edu.uni = uni;
  if (ma) edu.ma = ma;
  if (!uni) warn.push('학사(4년제) 학력 없음');
  if (isDoc && !ma) warn.push('박사 지원인데 석사 학력 없음');

  const data = {
    name_kr: nameKr,
    select_by_value: {
      gdhlEtexScrnGbCd: '3',
      gdhlDegCosCd: isDoc ? '41' : '40',
      gdhlEtshGbCd: isTransfer ? '2' : '1',
      LAB_EFLN_YN: isBilingual ? 'Y' : 'N',
      gdhlGbCd: dmap ? (isDoc ? dmap.doc : dmap.ma) : '',
    },
    select_late: { topik },
    dept_substring: dmap ? dmap.find : '',
    text: {
      koNm: nameKr,
      enNm: String(c[C.en]).trim().replace(/\s+/g, ' '),
      ssn1: s1,
      topik_date: '',
      mobpNo1: '062', mobpNo2: '670', mobpNo3: '2855',
      sample6_postcode: '61743',
      sample6_address: '전남광주통합특별시 남구 효덕로 277 광주대학교',
      sample6_address2: '호심관 6층 국제협력처',
    },
    text_by_name: { ssn2: s2 },
    select_by_text: { ntiCd: String(c[C.nati] || '중국').trim() },
    edu,
  };

  const file = path.join(OUT, `${String(no).padStart(2, '0')}_${nameKr.replace(/[·\s]/g, '')}.json`);
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
  out.push({ no, name: nameKr, gubun: gubunRaw, dept: deptBase, lab: isBilingual ? 'Y' : 'N',
             topik, ssn: `${s1}-${s2}`, file: path.basename(file), warn });
}

console.log('생성:', out.length, '건 → data2/\n');
for (const o of out) {
  console.log(`${String(o.no).padStart(2)} ${o.name} (${o.gubun}/${o.dept}) 이중언어=${o.lab} TOPIK=${o.topik} 등록번호=${o.ssn}`);
  for (const w of o.warn) console.log(`      ⚠ ${w}`);
}
