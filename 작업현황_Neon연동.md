# 광주대 입학지원 페이지 — Neon DB 연동 작업 현황

> 최종 업데이트: **2026-07-08 밤** — ✅ **연동 완료 (Cloudflare Worker 프록시 방식)**

- 라이브 페이지: https://gwangju-admission.pages.dev (Cloudflare Pages, 메인) / https://jaehoonjung84.github.io/gwangju-admission/ (GitHub Pages)
- 저장소: https://github.com/JaehoonJung84/gwangju-admission
- Neon 프로젝트: `red-sun-47673800` / 브랜치 `production`
- 프록시(Worker): `https://gu-admission-proxy.hubertjung84.workers.dev`

---

## 🎯 목표
전 세계 어디서 지원서를 제출하든 그 정보가 **Neon DB 한 곳에 쌓이도록** 실제 연동을 완성한다.

## ✅ 최종 방식 (동작 확인됨)
브라우저 → **Cloudflare Worker(심부름꾼)** → **Neon Postgres 직접 INSERT**.
- Worker가 **Neon 연결 문자열**(`DATABASE_URL`)을 서버 시크릿으로 보관 → 공개 페이지 소스에 비밀 없음.
- 학생 제출(POST)은 공개, 담당자 조회(GET)는 `STAFF_KEY`로 보호.
- Worker는 Neon **SQL-over-HTTP**(`https://{host}/sql`)로 직접 호출 → JWT 만료 문제 없음.
- 실측: 무토큰 `POST → HTTP 201 {"ok":true}` 확인. 실제 지원서가 `applications`에 저장됨.

## ❌ 폐기된 이전 방식 (왜 안 됐나)
"Neon 익명 역할에 INSERT 허용 → 브라우저가 헤더 없이 직접 POST" 방식은 **원천적으로 불가능**.
- Neon Data API는 익명 접근조차 **JWT Bearer 토큰을 필수**로 요구(문서 확인).
- 그래서 헤더 없는 POST는 항상 `400 missing authentication credentials ...` 발생.
- Neon 콘솔의 "Enable Data API / Anonymous role" 은 **이제 건드릴 필요 없음**.

## 🧩 구성 요소
- **`proxy/worker.js`** — 의존성 없는 Cloudflare Worker. `POST`=INSERT, `GET`(x-staff-key 게이트)=SELECT, CORS 처리.
- **`proxy/README.md`** — 브라우저만으로(Node 불필요) Cloudflare 대시보드 배포 절차.
- **Cloudflare Worker 시크릿/변수**:
  - `DATABASE_URL` (secret) — Neon 연결 문자열. ✅ 설정됨.
  - `STAFF_KEY` (secret) — 담당자 조회용 공유 키. ⚠️ 아직 미설정/불일치 (GET 401). 담당자 조회 쓸 때 설정.
  - `ALLOW_ORIGIN` (var) — `https://jaehoonjung84.github.io`.
- **`index.html`** — 메인 앱(원래 `Gwangju_Admission_System.html`에서 승격). `const PROXY_ENDPOINT = "https://gu-admission-proxy.hubertjung84.workers.dev";` 설정됨. 옛 파일명은 리다이렉트 스텁으로 유지.

## 🧹 남은 정리 (선택)
1. **테스트 데이터 삭제** — Claude 검증용 더미 2건. Neon SQL Editor에서:
   ```sql
   delete from applications where payload->>'email' = 'CLAUDE_TEST_DELETE';
   ```
2. **담당자 조회 켜려면** — Cloudflare Worker → Settings → Variables and Secrets에서
   `STAFF_KEY`(secret) 등록. (현재 공개 페이지에는 담당자 로그인 UI가 없어, 명단 확인은
   아래 Neon 콘솔 CSV로도 가능.)
3. **최종 확인** — 라이브 페이지에서 실제 지원서 1건 제출 →
   Neon `select count(*) from applications;` 로 증가 확인.

---

## 📊 담당자 명단 & CSV(엑셀) 내보내기 — Neon 콘솔
Neon 콘솔 → **SQL Editor** → 아래 실행 → 결과창 **Export/다운로드**로 **CSV** 저장:

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

## 🔒 보안 요약
- 공개 페이지/소스에 DB 비밀·토큰 없음. 연결 문자열은 Cloudflare Worker 시크릿에만 존재.
- 학생 제출은 INSERT만. 담당자 조회는 `STAFF_KEY` 필요.
- 지원자 개인정보 열람은 Neon 콘솔 로그인 또는 STAFF_KEY 보유자만 가능.
