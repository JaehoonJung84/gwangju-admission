# 국제협력처 자료 허브 (gu-oia)

https://gu-oia.netlify.app · Netlify site_id `1299cf12-f50a-4f12-a9f8-41b42e29464c`

흩어져 있던 국제협력처 웹 자료를 탭 하나로 모아 보는 페이지.
**기존 사이트는 전혀 건드리지 않는다.** 이 허브는 각 사이트를 iframe 으로 불러올 뿐이다.

## 구조

```
public/index.html      셸 + 접속코드 화면 + 탭/카드 UI (주소가 들어있지 않다)
public/logo.png        광주대학교 로고 (gu-calendar 와 동일본)
netlify/functions/links.mjs   접속코드 확인 후에만 링크 모음(JSON)을 내려주는 함수
netlify.toml           publish=public, functions=netlify/functions, noindex 헤더
```

접속코드는 `links.mjs` 의 `CODE` 상수 한 곳에만 있다 (현재 `oia2026`).
정적 HTML 에는 대상 사이트 주소가 하나도 들어있지 않아, 코드를 모르면 링크 모음이 노출되지 않는다.

## 항목 추가·수정

`netlify/functions/links.mjs` 의 `LINKS` 배열만 고치면 탭과 홈 카드가 함께 바뀐다.

| 필드 | 뜻 |
|---|---|
| `key` | URL 해시(`#stats` 등). 즐겨찾기 주소가 되므로 바꾸지 말 것 |
| `tab` | 탭에 찍히는 짧은 이름 |
| `name` / `desc` / `scope` / `icon` | 홈 카드에 쓰이는 표시값 |
| `group` | `staff`(교직원 업무) 또는 `student`(학생 안내) |
| `embed` | `true` 면 화면 안 iframe, `false` 면 새 창 안내 패널 |
| `note` | `embed:false` 일 때 안내 문구 |

## 배포

**`netlify deploy --prod` 를 쓰지 않는다** (무료 플랜 크레딧 소모). 프리뷰 → 승격 2단계:

```bash
cd C:/projects/gu-oia-hub
netlify deploy --dir=public --functions=netlify/functions --no-build --json   # deploy_id 확보
netlify api restoreSiteDeploy --data '{"site_id":"1299cf12-f50a-4f12-a9f8-41b42e29464c","deploy_id":"<DEPLOY_ID>"}'
```

함수가 있는 사이트이므로 **별칭(`--alias`)을 주면 안 된다** — 함수 재업로드를 요구하며 실패한다.

검증:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://gu-oia.netlify.app/                 # 200
curl -s -o /dev/null -w "%{http_code}\n" "https://gu-oia.netlify.app/api/links?code=oia2026"  # 200
curl -s -o /dev/null -w "%{http_code}\n" "https://gu-oia.netlify.app/api/links?code=x"        # 401
```

## 함정 기록

- **새로 만든 Netlify 사이트는 `sso_login:true` 로 생성된다.** 그대로 두면 사이트 전체가 Netlify 팀 로그인 뒤에 갇혀 외부인은 아무것도 못 본다(모든 경로 401 + edge-access 로그인 리다이렉트). 해제:
  ```bash
  netlify api updateSite --data '{"site_id":"<SITE_ID>","body":{"sso_login":false,"sso_login_context":"all"}}'
  ```
- 구글 스프레드시트는 iframe 삽입을 막으므로 `embed:false` 로 두고 새 창으로 연다.
- 허브 접속코드를 통과해도 `oiastats` · `gu-calendar` 는 각자 코드를 다시 묻는다. 그래서 통과 후 상단 「접속코드」 버튼에 같은 코드를 안내한다.
