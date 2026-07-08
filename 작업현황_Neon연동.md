# 광주대 입학지원 페이지 — Neon DB 연동 작업 현황

> 다른 PC/집에서 이어서 작업하기 위한 진행상황 문서.
> 최종 업데이트: **2026-07-08 저녁** (현재 디버깅 중 — 아래 "지금 막힌 지점" 참고)

- 라이브 페이지: https://jaehoonjung84.github.io/gwangju-admission/Gwangju_Admission_System.html
- 저장소: https://github.com/JaehoonJung84/gwangju-admission
- Neon 프로젝트: `red-sun-47673800` / 브랜치 `production (br-hidden-sky-aoc3g23y)`
- Data API 주소: `https://ep-dry-sea-aoqk565q.apirest.c-2.ap-southeast-1.aws.neon.tech/neondb/rest/v1`

---

## 🎯 목표
전 세계 어디서 지원서를 제출하든 그 정보가 **Neon DB 한 곳에 쌓이도록** 실제 연동을 완성한다.

## 🧩 방식 (확정)
별도 서버(프록시) 없이 **브라우저에서 Neon Data API로 직접 저장**.
- Neon "익명 역할(anonymous)"에 **INSERT(넣기)만 허용, SELECT(읽기)는 금지**.
- 페이지에 비밀 토큰 없음. 노출돼도 아무도 데이터를 못 읽고, 넣기만 가능.
- 담당자 명단 확인 = Neon 콘솔에서 직접 (CSV 내보내기는 맨 아래 참고).
- ✅ 문서로 확인: Neon Data API는 "헤더 없이 요청 → anonymous 역할" 방식이 맞음(공개키 개념 없음).

## ✅ 완료된 것
- **페이지 코드 (커밋 `ad7721f`, push 완료)**:
  - 홈의 "담당자 로그인" 진입 버튼 + JS 제거 → 공개 페이지는 제출 전용.
  - 직원 접속코드 삭제 (`const STAFF=[];`).
  - 제출 코드(`postApplication`)는 토큰 없이 Neon에 직접 POST (그대로 동작).
  - `PROXY_ENDPOINT`/`API_TOKEN` 은 계속 빈 값 유지.
- **실측 확인**:
  - Data API 엔드포인트 살아있음, 주소 정확함(위 주소).
  - **CORS 완전 개방**(`allow-origin: *`, POST/`Prefer` 헤더 허용) → 브라우저 직접 전송 OK.
  - DB에 역할 `anonymous`, `authenticated`, `authenticator` **모두 존재**.
- **Neon 콘솔에서 한 것**:
  - SQL: `applications` 표 생성 + `grant usage/insert ... to anonymous`.
  - Data API → Settings → Advanced → **Anonymous role = `anonymous`** 입력 후 Save("updated successfully" 확인).

## 🐞 지금 막힌 지점 (여기서부터 이어서)
설정은 다 맞는데도, **토큰 없는 테스트 제출이 계속 실패**함:
```
HTTP 400 — "missing authentication credentials: required authorization bearer token in JWT format"
```
이 오류는 PostgREST가 **익명 역할(db-anon-role)이 실행 중인 서버에 적용 안 됨** 상태일 때 내는 문구.
→ 즉 저장은 됐는데 **실행 중인 Data API가 그 설정을 아직 안 읽은** 것으로 추정.
(참고: 지금까지 제출은 전부 거부됐으므로 DB에 테스트 쓰레기 데이터 없음 — 깨끗함.)

## ▶️ 집에서 할 다음 단계 (순서대로)
Claude에게 "작업현황 보고 이어서 하자"라고 한 뒤, 아래를 진행:

**1단계 — 설정 리로드 신호 보내기** (Neon SQL Editor에서 실행):
```sql
notify pgrst, 'reload config';
notify pgrst, 'reload schema';
```
→ Claude에게 "했어" → Claude가 무토큰 POST로 재테스트 (기대: **HTTP 201**).

**2단계 — 1단계로 안 되면, Anonymous role 값 재입력**:
Data API → Settings → Advanced settings → **Anonymous role** 칸을
전부 지우고 `anonymous`를 **직접 타이핑**(연회색 예시가 아니라 검은 글씨) → **Save**.
→ Claude 재테스트.

**3단계 — 그래도 안 되면, 별도 인증 설정 점검**:
Data API 메인 탭에 **Authentication / JWT provider** 설정이 있는지 확인해서
익명 접근을 막고 있진 않은지 Claude와 함께 점검. (필요시 Neon 지원 문서/문의)

**성공(201) 이후**: 라이브 페이지에서 실제 지원서 1건 제출 → Neon에서
`select count(*) from applications;` 로 확인 → 끝.

---

## 📊 담당자 명단 & CSV(엑셀) 내보내기 — Neon 콘솔
Neon 콘솔 → **SQL Editor** → 아래 실행 → 결과창 **다운로드/Export 아이콘**으로 **CSV** 저장:

```sql
select
  id, created_at,
  payload->>'email'          as 이메일,
  payload->>'surname'        as 성,
  payload->>'firstName'      as 이름,
  payload->>'gender'         as 성별,
  payload->>'nationality'    as 국적,
  payload->>'passportNo'     as 여권번호,
  payload->>'passportExpiry' as 여권만료일,
  payload->>'phone'          as 연락처,
  payload->>'admissionType'  as 지원구분,
  payload->>'transferYear'   as 편입학년,
  payload->>'college'        as 단과대학,
  payload->>'department'     as 학부과,
  payload->>'track'          as 트랙,
  payload->>'langTest'       as 어학시험,
  payload->>'langScore'      as 어학점수,
  payload->>'fatherName'     as 부성명,
  payload->>'fatherNat'      as 부국적,
  payload->>'motherName'     as 모성명,
  payload->>'motherNat'      as 모국적,
  payload->>'status'         as 상태,
  payload->>'submittedAt'    as 제출시각
from applications
order by created_at desc;
```
전체 원본: `select id, created_at, payload from applications order by created_at desc;`

---

## 🗂 변경된 파일
- `Gwangju_Admission_System.html` — 제출 전용화 (위 "완료" 참고).
- `proxy/` — 이번 방식에선 미사용(참고용 보관).
- `작업현황_Neon연동.md` — 이 문서.

## 🔒 보안 요약
- 페이지/소스에 토큰·비밀번호 없음. 익명 역할은 INSERT만 → 읽기/수정/삭제 불가.
- 지원자 개인정보 열람은 Neon 콘솔 로그인(관리자 계정)으로만 가능.
