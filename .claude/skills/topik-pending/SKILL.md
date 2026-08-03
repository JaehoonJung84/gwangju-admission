---
name: topik-pending
description: TOPIK 성적증명서 관리 앱(topik-manager.onrender.com)의 "판독 대기함"에 쌓인 증명서를 판독해 항목을 채워 준다. 사용자가 "판독해줘", "대기함 읽어줘", "TOPIK 대기함 처리해줘" 같은 말을 하면 이 스킬을 쓴다.
---

# TOPIK 판독 대기함 처리

직원들이 앱에 올린 증명서 스캔·사진이 **판독 대기함**에 쌓인다.
서버는 점수·등급을 정확히 읽지 못하므로 **Claude가 직접 읽어서 판독 결과를 채워 준다.**

> ⚠️ **직접 등록(commit)하지 않는다.** Claude는 **판독 결과 저장까지만** 하고,
> 담당자가 대기함 화면에서 증명서와 대조 확인한 뒤 **[등록] 버튼**으로 최종 반영한다
> (2026-08-03 담당자 결정 — 이전의 자동 등록 방식을 대체함).
> 사용자가 명시적으로 "등록까지 해줘"라고 한 경우에만 `tools/pending_commit.py` 를 쓴다.

작업 디렉터리: `C:\projects\topik-manager`
가상환경 파이썬: `./.venv/Scripts/python.exe`

## 순서

### 1. 대기함 내려받기
```
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe tools/pending_fetch.py
```
→ `tools/_pending/p<id>.jpg` 로 증명서 이미지가 저장된다. 없으면 "대기함 비었음"이라고 알리고 끝낸다.

> ⚠️ **판독 직전에 반드시 새로 내려받는다.** 대기함은 삭제·재업로드로 내용이 바뀔 수 있고,
> 과거에 id가 재사용되면서 옛 이미지와 새 판독값이 섞여 보이는 사고가 있었다(2026-08-03).
> 이전 실행의 p*.jpg를 재사용해 판독하지 말 것. (판독 결과 저장 시 서버가 항목 ts를 검증해
> 항목이 바뀌었으면 409로 거부한다 — pending_fill.py가 자동 처리)

### 2. 이미지를 **직접 읽는다** (Read 도구)
각 이미지를 열어 인쇄된 활자만 읽는다. **손글씨는 무시한다.**
양이 많으면(10장 이상) 병렬 에이전트로 나눠 읽되, 필드 규칙·검산을 프롬프트에 그대로 전달한다.

| 필드 | 비고 |
|---|---|
| `name_en` | 성명(Name). 인쇄가 소문자여도 대문자로 |
| `dob` | 생년월일 YYYY-MM-DD |
| `gender` | 남자(Male)→M, 여자(Female)→F |
| `test_type` | `TOPIK II` / `TOPIK I` / `TOPIK II IBT` / `TOPIK I IBT` |
| `test_round` | 회차. `106/2026/05/17` → 106 |
| `test_date`, `valid_until` | YYYY-MM-DD |
| `listening`, `writing`, `reading` | 영역 점수. TOPIK I은 쓰기 없음 → null |
| `total`, `level` | 총점, 등급 |
| `reg_no`, `doc_no` | 수험번호(문자열, 앞자리 0 보존), 문서확인번호 |

**반드시 검산한다: 듣기+쓰기+읽기 = 총점.** 안 맞으면 다시 본다.
숫자가 흐려 확신이 없으면 그 필드는 비우고 사용자에게 알린다. 추측해서 채우지 않는다.

> ⚠️ IBT 성적표는 표의 영역 순서가 **듣기 → 읽기 → 쓰기** 다. 지필과 순서가 다르니 주의.
> IBT 시범시행(TRIAL TEST) 성적표는 정규 시험이 아니므로 **채우지 말고 사용자에게 물어본다.**

### 3. `tools/_pending/results.json` 작성 후 판독 결과 저장
판독 결과를 `tools/_pending/results.json` (id + 위 필드들의 리스트)로 저장하고:
```
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe tools/pending_fill.py
```
→ `POST /api/pending/{id}/hint` 로 저장된다. 대기함 화면에 "AI 판독 완료"로 항목이
채워져 보이고, 학생 후보(candidates)는 서버가 이름·생년월일로 자동 매칭해 보여 준다.

### 4. 결과 보고
판독 저장 몇 건 / 못 읽은 건(어느 필드가 왜) / 이미 등록된 것과 중복으로 보이는 건을
표로 정리해 사용자에게 보여 주고, **대기함에서 확인 후 [등록]을 눌러 달라**고 안내한다.
명단에 없는 학생([등록] 시 신규 생성됨)도 이름을 알려 준다.
대기 항목 삭제는 사용자가 요청할 때만 한다 (운영 데이터라 임의 삭제 금지).

## 환경변수 (기본값이 있어 보통 그냥 실행하면 된다)
- `TOPIK_URL` = https://topik-manager.onrender.com
- `TOPIK_CODE` = 접속 코드
- `TOPIK_EDIT_CODE` = 수정 코드 (판독 저장·등록·삭제에 필요)

## 참고 도구
- `tools/pending_fill.py` — 판독 결과를 힌트로 저장 (기본)
- `tools/pending_commit.py` — 직접 등록 (사용자가 명시 요청할 때만)
- `tools/push_photos.py` — 등록된 증명서 얼굴 사진이 자리표시자로 남았을 때 로컬 크롭을 직접 업로드
