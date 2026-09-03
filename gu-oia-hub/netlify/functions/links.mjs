// 국제협력처 허브 — 접속코드 확인 후에만 링크 모음을 내려준다.
// 정적 파일에는 아래 주소들이 들어있지 않다.

const CODE = 'oia2026';

const LINKS = [
  {
    key: 'stats',
    tab: '유학생 현황',
    name: '외국인 유학생 현황',
    url: 'https://oiastats.netlify.app/',
    desc: '학위과정 재학생 통계 현황판. 학과별·국적별·트랙별 인원을 바로 조회한다.',
    scope: '교직원 전용',
    group: 'staff',
    icon: '📊',
    embed: true
  },
  {
    key: 'cal',
    tab: '일정',
    name: '국제협력처 일정',
    url: 'https://gu-calendar.netlify.app/',
    desc: '부서 공유 달력. 입시·비자·등록장학·학사·교류·행사·보고 8종 분류, 「한눈에」 학년도 전체 보기.',
    scope: '구성원 · 접속코드 필요',
    group: 'staff',
    icon: '🗓️',
    embed: true
  },
  {
    key: 'attend',
    tab: '출결관리',
    name: '어학연수과정 관리프로그램',
    url: 'https://gwangju-attendance-check.vercel.app/',
    desc: '연수생 출결 확인·관리. 명단 시트와 함께 쓴다.',
    scope: '구성원 · 접속코드 필요',
    group: 'staff',
    icon: '✅',
    embed: true
  },
  {
    key: 'sheet',
    tab: '명단 시트',
    name: '어학연수 명단 구글시트',
    url: 'https://docs.google.com/spreadsheets/d/1Uu7y9Feud6EgMDKfH83Nysx86N46Cl6d0aHipoO0q2U/edit?gid=0#gid=0',
    desc: '출결관리 프로그램이 사용하는 연수생 명단 원본.',
    scope: '구글 로그인 필요',
    group: 'staff',
    icon: '📄',
    embed: false,
    note: '구글 문서는 보안 설정상 이 화면 안에 끼워 넣을 수 없어 새 창으로 엽니다.'
  },
  {
    key: 'ot',
    tab: '학위 OT',
    name: '학위과정 OT 자료',
    url: 'https://gu-ot.netlify.app/',
    desc: '신·편입생 오리엔테이션 안내 (12개 언어). 대학원 안내는 사이트 안 /grad 페이지.',
    scope: '학생 대상 · 공개',
    group: 'student',
    icon: '🎓',
    embed: true
  },
  {
    key: 'klc',
    tab: '연수 OT',
    name: '한국어 어학연수과정 OT 자료',
    url: 'https://gu-klc.netlify.app/',
    desc: '어학연수과정 신입 연수생 오리엔테이션 안내.',
    scope: '학생 대상 · 공개',
    group: 'student',
    icon: '🇰🇷',
    embed: true
  },
  {
    key: 'name',
    tab: '이름찾기',
    name: '유학생 한글이름 찾기',
    url: 'https://gu-findname.netlify.app/',
    desc: '학생이 본인 확인 후 자신의 한글 이름 표기를 조회한다.',
    scope: '학생 대상 · 본인 확인',
    group: 'student',
    icon: '🔎',
    embed: true
  }
];

export default async (req) => {
  const code = (new URL(req.url).searchParams.get('code') || '').trim().toLowerCase();
  const head = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };
  if (code !== CODE) {
    return new Response(JSON.stringify({ ok: false }), { status: 401, headers: head });
  }
  return new Response(JSON.stringify({ ok: true, code: CODE, links: LINKS }), { headers: head });
};

export const config = { path: '/api/links' };
