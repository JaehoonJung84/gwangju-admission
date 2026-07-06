# 광주대 입학지원 — 백엔드 프록시 (Neon Data API)

공개 페이지(GitHub Pages)에 Neon 토큰을 두면 지원자 개인정보가 통째로 노출됩니다.
이 프록시가 **Neon 토큰을 서버에만 보관**하고, 담당자 조회(GET)는 **서버 키**로 보호합니다.

- `POST` → 학생 지원서 제출을 Neon으로 전달 (누구나 가능 — 공개 지원 폼)
- `GET` → 지원자 전체 조회. 단, `x-staff-key` 헤더가 서버의 `STAFF_KEY`와 일치할 때만
- Neon 토큰(`NEON_TOKEN`)은 서버 시크릿으로만 존재 (페이지 소스에 없음)

## 배포 (Cloudflare Workers, 무료)

사전 준비: [Cloudflare 계정](https://dash.cloudflare.com/sign-up) (무료), Node.js 설치

```bash
cd proxy
npm install -g wrangler        # 또는 npx 사용
wrangler login                 # 브라우저로 Cloudflare 로그인

# 시크릿 2개 등록 (값 입력 프롬프트가 뜹니다)
wrangler secret put NEON_TOKEN # Neon Data API JWT 토큰 붙여넣기
wrangler secret put STAFF_KEY  # 담당자들이 공유할 임의의 접속 키 (예: 길고 무작위한 문자열)

wrangler deploy                # 배포 → https://gu-admissions-proxy.<계정>.workers.dev 출력됨
```

### 값 설명
- **NEON_TOKEN**: Neon 콘솔 → 프로젝트 → **Data API** 탭에서 발급하는 JWT 토큰.
  (Neon Auth를 쓰는 경우 해당 토큰. 자세한 발급 위치는 Neon 콘솔의 Data API 안내 참조.)
- **STAFF_KEY**: 담당자들만 아는 비밀 문자열. 대시보드에서 처음 한 번 입력하면 세션 동안 저장됩니다.
- **NEON_URL / ALLOW_ORIGIN**: `wrangler.toml`에 있음. 도메인이 바뀌면 여기만 수정.

## 배포 후 연결

배포로 나온 Worker URL을 `Gwangju_Admission_System.html` 상단 설정에 넣으세요:

```js
const PROXY_ENDPOINT = "https://gu-admissions-proxy.<계정>.workers.dev";
```

그리고 커밋/푸시하면 끝. 이후:
- 학생 제출 → 프록시 → Neon 저장
- 담당자 로그인 → 대시보드에서 서버 키 1회 입력 → Neon 데이터 조회 + 엑셀 다운로드

`PROXY_ENDPOINT`가 비어 있으면 기존처럼 브라우저 로컬 저장 데이터로 동작합니다(안내 배너 표시).

## Neon 테이블 준비 (최초 1회)

`applications` 테이블에 `payload jsonb` 컬럼이 있어야 합니다. 없으면 Neon SQL 편집기에서:

```sql
create table if not exists applications (
  id         bigint generated always as identity primary key,
  payload    jsonb not null,
  created_at timestamptz not null default now()
);
```

## 다른 플랫폼

Vercel/Netlify Functions로도 동일 로직 구현 가능합니다. 핵심은 (1) Neon 토큰을 서버 env로,
(2) GET에 STAFF_KEY 검증, (3) CORS 허용 — `worker.js`의 흐름을 그대로 옮기면 됩니다.
