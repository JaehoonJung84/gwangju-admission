# 광주대 입학지원 — 백엔드 프록시 (Cloudflare Worker → Neon)

## 왜 필요한가

Neon Data API는 **모든 요청에 JWT 토큰을 요구**합니다(익명 접근조차 짧은 수명의 JWT 필요).
그래서 공개 페이지에서 "토큰 없이 직접 POST"는 원천적으로 불가능하고, 계속 다음 오류가 납니다:

```
HTTP 400 — missing authentication credentials: required authorization bearer token in JWT format
```

이 프록시는 만료되는 JWT를 쫓는 대신, **Neon 연결 문자열**로 Postgres에 직접 붙어
(Neon의 SQL-over-HTTP) INSERT/SELECT 합니다. 연결 문자열은 **서버(Cloudflare)에만** 두므로
공개 페이지 소스에는 어떤 비밀도 없습니다.

- `POST` → 학생 지원서를 `applications` 테이블에 INSERT (누구나 가능 — 공개 지원 폼)
- `GET`  → 지원자 전체 조회. 단, `x-staff-key` 헤더가 서버의 `STAFF_KEY`와 일치할 때만
- 연결 문자열(`DATABASE_URL`)은 Cloudflare 시크릿으로만 존재 (페이지 소스에 없음)

`worker.js`는 **라이브러리 의존성이 없어서** Cloudflare 대시보드에 붙여넣기만 하면 됩니다
(로컬 Node.js·wrangler 불필요).

---

## 배포 — 브라우저만으로 (권장, Node 불필요)

### 0. Neon 테이블 준비 (최초 1회)
Neon 콘솔 → SQL Editor에서 (이미 만들었다면 건너뜀):

```sql
create table if not exists applications (
  id         bigint generated always as identity primary key,
  payload    jsonb not null,
  created_at timestamptz not null default now()
);
```

### 1. Neon 연결 문자열 복사
Neon 콘솔 → 프로젝트 **Dashboard**(또는 **Connect**) → **Connection string** 복사.
형태 예시:
```
postgresql://neondb_owner:XXXXXX@ep-xxx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```
(비밀번호가 가려져 있으면 "Show password"를 눌러 전체를 복사)

### 2. Cloudflare Worker 생성
1. https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Create Worker**
2. 이름: `gu-admissions-proxy` → **Deploy** (기본 코드로 일단 배포)
3. **Edit code** 클릭 → 편집기의 기존 내용을 전부 지우고 이 폴더의 `worker.js` 내용을
   통째로 붙여넣기 → **Deploy**

### 3. 시크릿/변수 등록
Worker → **Settings** → **Variables and Secrets** 에서 3개 등록:

| 이름 | 종류 | 값 |
|------|------|-----|
| `DATABASE_URL` | **Secret** | 1단계에서 복사한 Neon 연결 문자열 |
| `STAFF_KEY` | **Secret** | 담당자들만 아는 임의의 긴 문자열 (대시보드 조회용) |
| `ALLOW_ORIGIN` | **Text(변수)** | `https://jaehoonjung84.github.io` |

저장 후 다시 **Deploy**(또는 자동 반영) 한 번.

### 4. Worker URL 확인
Worker 개요에 표시된 주소 (예: `https://gu-admissions-proxy.<계정>.workers.dev`) 를 복사.

---

## 페이지에 연결

`Gwangju_Admission_System.html` 상단 설정에 Worker URL을 넣습니다:

```js
const PROXY_ENDPOINT = "https://gu-admissions-proxy.<계정>.workers.dev";
```

커밋/푸시하면 끝. 이후:
- 학생 제출 → 프록시 → Neon `applications` 저장
- 담당자 조회 → `STAFF_KEY` 입력 시 프록시가 전체 목록 반환

`PROXY_ENDPOINT`가 비어 있으면 저장이 동작하지 않습니다(반드시 설정).

---

## 검증 (배포 후)

무토큰 POST가 이제 **201**을 반환해야 합니다:

```bash
curl -i -X POST "https://gu-admissions-proxy.<계정>.workers.dev" \
  -H "Content-Type: application/json" \
  -d '{"payload":{"email":"test@example.com","surname":"TEST"}}'
# → HTTP 201, {"ok":true}
```

담당자 조회(키 필요):

```bash
curl -s "https://gu-admissions-proxy.<계정>.workers.dev" -H "x-staff-key: <STAFF_KEY>"
# → [{"id":..,"created_at":"..","payload":{..}}, ...]
```

Neon에서 직접 확인: `select count(*) from applications;`

---

## CLI로 배포하고 싶다면 (선택, Node.js 필요)

```bash
cd proxy
npx wrangler login
npx wrangler secret put DATABASE_URL   # Neon 연결 문자열
npx wrangler secret put STAFF_KEY      # 담당자 공유 키
npx wrangler deploy
```
`ALLOW_ORIGIN`은 `wrangler.toml`에 있습니다.
