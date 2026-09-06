# gu-calendar (라이브 사본 — 전체 소스 아님)

`index.html` 은 https://gu-calendar.netlify.app/ 에 **현재 올라가 있는 화면 파일 그대로**다.
(라이브에서 내려받아 → Netlify 가 서빙할 때 끼워 넣는 안내 주석·HUD 스크립트만 걷어내고 → 고친 것.
걷어낸 뒤 sha1 이 배포본 `/index.html` 과 정확히 일치함을 확인했다.)

## 주의 — 이 폴더로 `netlify deploy` 하지 말 것

여기엔 **서버 함수(`/api/events`)와 그림 파일이 없다.** 이 폴더째 배포하면 일정 API 가 사라진다.
사무실 PC 에 있는 원본 소스가 진짜다. 원본을 고칠 때 이 파일 내용을 반영할 것.

## 소스 없이 화면만 고쳐 올리는 법 (검증됨 2026-09-06)

1. `netlify deploy --dir=<index.html 하나만 든 폴더> --no-build --json --site dcde0049-80ae-4181-a88a-807069ecaee8`
   → 새 index.html 의 내용만 Netlify 저장소에 올린다(프리뷰, 무료).
2. `netlify api listSiteFiles` 로 기존 14개 파일의 sha1 을 받아 그대로 쓰고, `/index.html` sha1 만 새 값으로 바꾼다.
   함수는 `{"functions":{"events":"<published_deploy.available_functions[0].d>"}}` 로 다이제스트만 넘기면 라우트(`/api/events`)까지 그대로 딸려온다.
   (`functions_config` 를 같이 넣으면 422 — 넣지 말 것.)
3. `netlify api createSiteDeploy --data '{"site_id":"…","body":{"files":{…},"functions":{…},"draft":true}}'`
   → `required: []` 이면 올릴 게 없다는 뜻이고 곧 `state:ready` 가 된다.
4. 프리뷰 주소로 `/`, `/api/events`(401 code_required 가 정상), `/logo.png` 확인.
5. `netlify api restoreSiteDeploy --data '{"site_id":"…","deploy_id":"…"}'` → 프로덕션 승격(크레딧 미소모).

- site_id : `dcde0049-80ae-4181-a88a-807069ecaee8`
- 되돌리기 : 이전 배포 `6a9a893c672d40b752330ab1` 을 같은 방법으로 restore
