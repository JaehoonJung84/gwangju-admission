# 광주대 입학지원 페이지 — Neon DB 연동 작업 현황

> 이 문서는 다른 PC/집에서 이어서 작업할 수 있도록 진행상황 전체를 정리한 것입니다.
> 최종 업데이트: 2026-07-07

대상 페이지(라이브): https://jaehoonjung84.github.io/gwangju-admission/Gwangju_Admission_System.html
저장소: https://github.com/JaehoonJung84/gwangju-admission

---

## 🎯 목표
전 세계 어디에서 지원서를 제출하든, 그 정보가 **Neon DB 한 곳에 쌓이도록** 실제 연동을 완성한다.

## ✅ 지금까지 완료된 것 (이 커밋 기준)
- **아키텍처 확정**: 별도 서버(프록시) 없이 **Neon Data API로 브라우저에서 직접 저장**.
  - 방식: Neon "익명 역할(anonymous)"에 **INSERT(넣기)만 허용, SELECT(읽기)는 금지**.
  - 효과: 페이지에 비밀 토큰이 **하나도** 안 들어감. 설령 주소가 노출돼도 **아무도 지원자 데이터를 읽을 수 없고**, 제출(넣기)만 된다.
- **확인 완료(실측)**:
  - Neon Data API 엔드포인트 살아있음.
  - **CORS 완전 개방**(`access-control-allow-origin: *`, POST 허용) → GitHub Pages에서 직접 전송 가능.
  - 브라우저가 보내는 `Prefer` 헤더도 프리플라이트 통과 확인.
- **페이지 코드 정리 (제출 전용화)**:
  - 홈 화면의 **"담당자 로그인" 진입 버튼 제거** → 공개 페이지는 지원서 제출 전용.
  - 공개 소스에 노출되던 **직원 접속코드(jjh2026 등) 삭제**.
  - 제출 코드(`postApplication`)는 이미 토큰 없이 Neon에 직접 POST하도록 되어 있어 **그대로 동작**.
  - 담당자 명단 확인은 **Neon 콘솔에서 직접** (아래 CSV 안내 참고).

## ⏳ 남은 일 — **사장님이 Neon 콘솔에서 할 2단계 (약 5분)**
이 2단계만 하면 전 세계 제출이 Neon에 쌓이기 시작합니다.

### 1단계 — 표 만들기 + 익명 INSERT 권한
Neon 콘솔(console.neon.tech) → **SQL Editor** → 붙여넣고 **Run**:

```sql
-- 지원서 저장용 표 (이미 있으면 그대로 둠)
create table if not exists applications (
  id         bigint generated always as identity primary key,
  payload    jsonb       not null,
  created_at timestamptz not null default now()
);

-- 익명(토큰 없는) 요청에 '넣기(INSERT)'만 허용, '읽기(SELECT)'는 주지 않음
grant usage  on schema public to anonymous;
grant insert on table  applications to anonymous;
```

> ⚠️ `role "anonymous" does not exist` 오류가 나면 익명 역할 이름이 다른 것 → Claude에게 그 메시지를 알려주면 맞춰줌.

### 2단계 — Data API에서 익명 역할 켜기
Neon 콘솔 → **Data API** → **Settings** 탭 → **Advanced settings** →
`db_anon_role` 값이 **`anonymous`** 인지 확인(비어 있으면 입력) → **Save**.

### 완료 후 검증
Claude에게 "완료"라고 말하면, **토큰 없는 테스트 제출**을 쏴서 201(정상 저장) 응답을 확인해 줌.
직접 확인하려면 라이브 페이지에서 지원서를 한 건 제출 → Neon SQL Editor에서 `select count(*) from applications;` 로 늘어나는지 확인.

---

## 📊 담당자 명단 확인 & CSV(엑셀) 내보내기 — Neon 콘솔
Neon 콘솔 → **SQL Editor** → 아래 실행 → 결과 위쪽 **다운로드/Export 아이콘**으로 **CSV** 저장(엑셀에서 열림):

```sql
select
  id,
  created_at,
  payload->>'email'         as 이메일,
  payload->>'surname'       as 성,
  payload->>'firstName'     as 이름,
  payload->>'gender'        as 성별,
  payload->>'nationality'   as 국적,
  payload->>'passportNo'    as 여권번호,
  payload->>'passportExpiry' as 여권만료일,
  payload->>'phone'         as 연락처,
  payload->>'admissionType' as 지원구분,
  payload->>'transferYear'  as 편입학년,
  payload->>'college'       as 단과대학,
  payload->>'department'    as 학부과,
  payload->>'track'         as 트랙,
  payload->>'langTest'      as 어학시험,
  payload->>'langScore'     as 어학점수,
  payload->>'fatherName'    as 부성명,
  payload->>'fatherNat'     as 부국적,
  payload->>'motherName'    as 모성명,
  payload->>'motherNat'     as 모국적,
  payload->>'status'        as 상태,
  payload->>'submittedAt'   as 제출시각
from applications
order by created_at desc;
```

전체 원본이 필요하면: `select id, created_at, payload from applications order by created_at desc;`

---

## 🗂 변경된 파일
- `Gwangju_Admission_System.html`
  - 홈 화면 담당자 로그인 버튼 및 JS 배선 제거
  - `const STAFF=[];` (직원 접속코드 삭제)
  - `PROXY_ENDPOINT` / `API_TOKEN` 는 계속 **빈 값** 유지 (익명 직접 저장이므로 채우지 않음)
- `proxy/` 폴더: 이번 방식에선 **사용 안 함**(프록시 없이 진행). 나중에 읽기 기능이 필요해지면 참고용으로 보관.

## 💻 다른 PC에서 이어서 하기
1. `git clone https://github.com/JaehoonJung84/gwangju-admission.git` (또는 기존 폴더에서 `git pull`)
2. 이 파일(`작업현황_Neon연동.md`)이 전체 맥락 — Claude Code를 열고 "작업현황_Neon연동.md 보고 이어서 하자"라고 하면 됨.
3. 남은 것은 위 **Neon 콘솔 2단계** 뿐. 그다음 Claude가 검증 → 필요한 커밋/push 진행.

## 🔒 보안 요약
- 페이지·소스에 토큰/비밀번호 없음.
- 익명 역할은 INSERT만 가능 → 데이터 읽기/수정/삭제 불가.
- 지원자 개인정보 열람은 Neon 콘솔 로그인(사장님 계정)으로만 가능.
