# 광주대 입학지원 시스템 — 작업 현황 (이어가기용)

> 최종 업데이트: **2026-07-08 밤**. 다음 작업은 **② 담당자 서류 열람 + 판정 워크플로**.

## 🔑 핵심 정보
- **라이브 주소(메인)**: https://gwangju-admission.pages.dev  (Cloudflare Pages)
  - 보조: https://jaehoonjung84.github.io/gwangju-admission/ (GitHub Pages)
- **저장소**: https://github.com/JaehoonJung84/gwangju-admission  (로컬: `C:\projects\gwangju-admission`)
- **메인 파일**: `index.html` (구 `Gwangju_Admission_System.html`은 → `./` 리다이렉트 스텁)
- **프록시(Worker)**: `https://gu-admission-proxy.hubertjung84.workers.dev` (`proxy/worker.js`)
- **Neon**: 프로젝트 `red-sun-47673800` / 브랜치 `production` / `applications` 테이블 (`payload jsonb`)
- **Cloudflare 계정 id**: `3ee489708ec350db06802bd3f5fb4e98`
- **STAFF_KEY**: 담당자 로그인 비밀번호 (Cloudflare Worker 시크릿). 정재훈만 보관.

## 🏗 구조
```
학생/담당자 브라우저  →  Cloudflare Worker(gu-admission-proxy)  →  Neon Postgres
                        (DATABASE_URL 연결문자열 서버 보관)
```
- 제출(POST)은 공개, 조회/삭제/수정(GET/DELETE/PATCH)은 `x-staff-key`(=STAFF_KEY) 필요.
- Worker는 만료 없는 **연결문자열 + SQL-over-HTTP**(`https://{host}/sql`) 방식.

## ✅ 완료된 것
1. Neon DB 연동 (헤더 없는 익명 INSERT는 Neon상 불가 → Worker 프록시로 해결. `POST → 201` 실측).
2. 담당자 로그인(단일 STAFF_KEY, superAdmin 전체열람) + 명단 조회 + 엑셀 내보내기.
3. 새로고침(F5) 로그인/화면 유지 + 폰 하드웨어 뒤로가기 = 직전 화면(모달 먼저 닫힘).
4. 깔끔한 주소 `gwangju-admission.pages.dev` (Pages가 GitHub repo 연결, main push 시 자동 배포).
5. 상세창 레이아웃 깨짐 수정(단일 컬럼) + 초 단위 제출시각(상세/명단/엑셀).
6. 지원서 삭제 = **관리자 비밀번호 재확인 + 소프트 삭제(보관함) + 복원**.

## 🧩 Worker 엔드포인트 (현재 배포됨 — 아래 기능들은 재배포 불필요)
- `POST`  (공개)  — 지원서 INSERT.
- `GET`   (staff) — 기본: 활성 목록(`payload - 'docFiles'`, deleted 제외) / `?id=<appId>`: 단건 전체(docFiles 포함) / `?deleted=1`: 보관함.
- `DELETE`(staff) — `?id=` 소프트 삭제(`deleted`, `deletedAt` 세팅).
- `PATCH` (staff) — `{id, patch}` payload 병합. **복원·판정 저장에 재사용**.

## ⏳ 다음 작업 — ② 담당자 서류 열람 + 판정 워크플로 (전부 `index.html`만 수정, Worker 재배포 불필요)
현재 업로드 파일은 **파일명만 저장**되고 실제 이미지는 브라우저 메모리에만 있어 사라짐(`index.html`의 파일 input `onchange`, 약 line 1074 부근 `current.docs[key]=f.name; FILES[key]=f`).

구현 계획:
1. **파일 저장**: 업로드 시 이미지면 canvas로 다운스케일(예: 최대 1600px, JPEG 0.7) → dataURL을, `current.docFiles[key]=dataURL` 로 보관. 제출 payload에 포함(비이미지/PDF는 용량 상한 두고 그대로 or 경고).
   - Worker 목록 GET은 이미 `payload - 'docFiles'`로 무거운 이미지 제외함(느려지지 않음).
2. **상세창에서 서류 열람**: `openDetail` 시 `GET ?id=<appId>`로 전체 payload(docFiles 포함) 불러와, 각 서류를 썸네일/열기 링크로 표시.
3. **판정 워크플로**:
   - `payload.reviewVerdict` 없으면 상세/명단에 **"⏳ 판정 전(미검토)"** 상태+아이콘.
   - 상세창에 **[적합]/[보완필요]/[부적합]** 버튼 → 선택 시 `PATCH {id, patch:{reviewVerdict, reviewedAt, reviewedBy}}` 저장 → 명단·상세 반영.
   - 기존 규칙엔진(evaluate) 판정은 "참고(자동)"로 남기고, 담당자 수동판정을 공식 값으로.

## 🛠 배포/이어가기 메모
- **페이지 수정**: `git push` 하면 Pages + GitHub Pages 자동 배포. 반영 확인은 `gwangju-admission.pages.dev/?cb=랜덤` 로.
- **Worker(`proxy/worker.js`) 수정 시에만** 수동 배포 필요:
  Cloudflare 대시보드 → Workers & Pages → `gu-admission-proxy` → Edit code → 코드 전체 교체 → Deploy.
  (편집 URL: `https://dash.cloudflare.com/3ee489708ec350db06802bd3f5fb4e98/workers/services/edit/gu-admission-proxy/production`)
- **테스트 더미 정리**(선택): Neon SQL Editor에서
  `delete from applications where payload->>'email' = 'CLAUDE_TEST_DELETE';`

## 📊 담당자 명단 CSV 내보내기 (Neon SQL Editor)
```sql
select id, created_at,
  payload->>'email' as 이메일, payload->>'surname' as 성, payload->>'firstName' as 이름,
  payload->>'nationality' as 국적, payload->>'passportNo' as 여권번호, payload->>'phone' as 연락처,
  payload->>'admissionType' as 지원구분, payload->>'college' as 단과대학, payload->>'department' as 학부과,
  payload->>'track' as 트랙, payload->>'reviewVerdict' as 담당자판정, payload->>'submittedAt' as 제출시각
from applications
where coalesce(payload->>'deleted','') <> 'true'
order by created_at desc;
```

## 🔒 보안 요약
- 공개 페이지에 DB 비밀·토큰 없음. 연결문자열은 Worker 시크릿에만.
- 제출은 INSERT만. 조회/삭제/수정은 STAFF_KEY 필요. 삭제는 소프트(복원 가능).
