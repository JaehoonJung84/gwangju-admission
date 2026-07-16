---
name: topik-pending
description: TOPIK 성적증명서 관리 앱(topik-manager.onrender.com)의 "판독 대기함"에 쌓인 증명서를 읽어서 등록한다. 사용자가 "판독해줘", "대기함 읽어줘", "TOPIK 대기함 처리해줘" 같은 말을 하면 이 스킬을 쓴다.
---

# TOPIK 판독 대기함 처리

직원들이 앱에 올린 증명서 스캔·사진이 **판독 대기함**에 쌓인다.
서버는 점수·등급을 정확히 읽지 못하므로(무료 OCR 등급 정확도 57%),
**Claude가 직접 읽어서 등록한다.** 이게 정식 운영 방식이다 (2026-07-13 담당자 결정).

작업 디렉터리: `C:\projects\topik-manager`
가상환경 파이썬: `./.venv/Scripts/python.exe`

## 순서

### 1. 대기함 내려받기
```
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe tools/pending_fetch.py
```
→ `tools/_pending/p<id>.jpg` 로 증명서 이미지가 저장된다. 없으면 "대기함 비었음"이라고 알리고 끝낸다.

### 2. 이미지를 **직접 읽는다** (Read 도구)
각 이미지를 열어 인쇄된 활자만 읽는다. **손글씨는 무시한다.**

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
> IBT 시범시행(TRIAL TEST) 성적표는 정규 시험이 아니므로 **등록하지 말고 사용자에게 물어본다.**

### 3. 학생 찾기
```
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -c "..."   # /api/students 에서 영문명으로 검색
```
- 명단에 있으면 `person_id` 사용
- 없으면 `person_id: null` + `new_name_en` / `new_dob` / `new_gender` 로 새 학생 등록

### 4. `tools/_pending/filled.json` 작성 후 등록
```
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe tools/pending_commit.py
```
같은 사람·같은 시험일·같은 성적이면 서버가 **중복으로 거부**한다(정상 동작).

### 5. 결과 보고
등록 몇 건 / 중복 몇 건 / 실패 몇 건. 새로 만든 학생이 있으면 이름을 알린다.
**중복이라 남은 대기 항목을 지울지 사용자에게 물어본다** (운영 데이터라 임의 삭제 금지).

## 환경변수 (기본값이 있어 보통 그냥 실행하면 된다)
- `TOPIK_URL` = https://topik-manager.onrender.com
- `TOPIK_CODE` = 접속 코드
- `TOPIK_EDIT_CODE` = 수정 코드 (등록·삭제에 필요)
