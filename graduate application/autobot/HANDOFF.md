# 대학원 입시원서 자동입력 (autobot) — 작업 핸드오프

광주대 학사행정시스템(haksa.gwangju.ac.kr) **입시원서입력** 폼에 2026학년도 후기
외국인 대학원 지원자 정보를 Playwright(CDP)로 자동 입력하는 도구.

> ⚠️ **개인정보 주의:** 지원자 실데이터(PDF, 엑셀, `data/*.json`, `node_modules`)는
> `.gitignore`로 저장소에서 제외됨. 이 저장소에는 **재사용 코드와 문서만** 커밋함.
> 원격(GitHub)에 push 시 포털 내부 필드ID/URL이 노출되므로 공개 저장소면 주의.

---

## 1. 집 랩톱 최초 세팅 (한 번만)

1. **Node.js 설치** (winget): `winget install OpenJS.NodeJS.LTS` → 새 터미널
2. 이 폴더에서 의존성 설치: `npm install`  (playwright-core만 필요, 브라우저 다운로드 X)
3. **크롬을 원격디버깅 모드로 실행** (기존 로그인과 충돌 안 나게 별도 프로필):
   ```
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\chrome-debug-profile https://haksa.gwangju.ac.kr/~yslee/ghakjuk/ipsi/ipsi_index.html
   ```
   > 주의: `--user-data-dir`를 반드시 별도 경로로. (기본 프로필은 최신 크롬에서 디버깅 포트 거부)
4. 그 크롬에서 **포털 로그인** (이 프로필은 처음이라 1회 로그인 필요, 이후 유지)
5. 연결 확인: `curl http://localhost:9222/json/version` 또는 브라우저로 접속

## 2. 한 지원자 입력하는 법

1. 그 크롬에서 좌측 **원서관리 → 입시원서입력** 으로 빈 폼을 띄워둔다(스크립트가 자동 리셋도 함).
2. 지원자 데이터 JSON을 `data/` 에 만든다(형식은 §4, 예시는 이미 만든 것 참고).
3. **검토 모드**(저장 안 함)로 먼저:
   ```
   node fill_applicant.js data/파일.json --reset
   ```
   콘솔에 `[OK]/[MISS]` 와 "저장 직전 read-back" 확인.
4. 이상 없으면 **저장**:
   ```
   node fill_applicant.js data/파일.json submit --reset      # ① 신규 등록(INSERT)
   node fill_applicant.js data/파일.json submit --load       # ② 재저장(학력 반영, UPDATE)
   ```
   > ⭐ **반드시 2단계.** 이 시스템은 신규 등록 한 번으로는 **학력(출신학교/성적/학위번호)이
   > 저장되지 않는다.** 수험번호 생성 후 "불러와서 다시 저장(UPDATE)"해야 학력이 들어간다.
5. 검증: `node load_inspect.js "성명"` (편집폼에 로드된 학력 배열 확인),
   `node topik_check.js "성명"` (TOPIK/유효기간 확인).

### fill_applicant.js 인자
- `submit` : "처리" 버튼까지 눌러 저장 (없으면 채우기만/검토)
- `--reset`: 좌측 '입시원서입력' 메뉴 클릭해 **빈 폼으로 초기화 후** 채움 (신규 지원자용)
- `--load` : 이름으로 검색해 **기존 지원자를 수정모드로 불러온 뒤** 채움 (학력 반영/수정용)
- `--chasu=2` : **차수 지정. 신규 등록 시 필수** (안 주면 폼 기본값 3으로 저장된다 → §3 참고)
- 저장 시 alert(확인창)은 자동 수락하고 메시지를 캡처함. `"입력을 완료했습니다"` = 성공.

### 차수를 잘못 넣었을 때 (삭제 후 재등록)
```
node delete_applicant.js "성명" --sems=3 --go     # ⚠ 복구 불가
node fill_applicant.js data/파일.json submit --reset --chasu=2
node fill_applicant.js data/파일.json submit --load  --chasu=2
```
`move_chasu.sh 04 05 …` 로 일괄 처리 가능.
⚠ **삭제 화면(gisa1022)에는 차수 필터가 없다** — (연도 + 모집구분 + 이름)으로만 지운다.
   다른 차수에 동명이인이 있으면 그쪽이 지워질 수 있으니, 삭제 전 `list_chasu.js`로 중복 확인할 것.

## 3. 폼 구조 핵심 (역공학 결과)

### ⛔ 차수(chasu) — 제일 위험한 함정. 반드시 먼저 읽을 것
- 화면 상단 **차수**는 필드가 **두 개**다:
  - `sems2` (select) = 모집구분. 전기정시=1 / 전기추가=2 / **후기정시=3** / 후기추가=4
  - `chasu2_2` (text, 폭 30px) = **차수 번호.** 서버가 기본값 **`3`** 으로 렌더한다.
- **우리가 쓰는 건 `sems2=3`(후기정시모집) + `chasu2_2=2`.** 기본값 3을 그대로 두면 안 된다.
  (2026 후기 기준. 차수는 매 학기 담당자에게 확인할 것.)
- `chasu2_2`는 **신규 등록(INSERT) 때만** 차수를 정한다.
  **수정(UPDATE, `--load`)은 차수를 절대 바꾸지 않는다** — 2026-07-13 실증.
  → 잘못된 차수로 넣었으면 **재저장으로는 못 옮긴다. 삭제 후 재등록만이 유일한 방법.**
- 수험번호(`ex_no`)에는 차수가 안 들어간다: `2026|대학원(4=일반,9=보건상담정책)|과정(1=석사,2=박사)|일련번호`.
- 따라서 `fill_applicant.js`는 **항상 `--chasu=2`를 붙여서** 실행할 것.
  (붙이지 않으면 폼 기본값 3으로 들어간다.)

### 그 외
- 폼은 프레임셋. 입력 폼은 **`right_center` 프레임**, `#koNm` 존재로 식별.
- 폼 전체가 단일 `<form name=form_m>` (action=`gisa1020_s.php3`), POST 방식.
- **날짜는 `YYYYMMDD` (구분자 없음!)** 예: `20250612`. datepicker `dateFormat: yymmdd`.
  하이픈(2025-06-12)으로 넣으면 서버가 학력행을 버린다.
- **`ssn2`(주민번호 뒷자리)는 중복 id.** 숨은 `ex_no`와 실제 password칸이 둘 다 id=ssn2.
  → 반드시 `input[name="ssn2"]`(password)로 지정. (`text_by_name` 사용)
- **대학명**은 readonly + `onclick=daihak(idx)` 팝업. 팝업은 `form_m["schlNm[]"][idx].value=name`
  만 세팅 → **학교코드 없음, 자유 텍스트.** 그냥 값 주입해도 무방.
  외국대학은 관례상 `(외국)실제교명` 으로 입력(한국대학은 실교명 그대로).
- **지원학과(`gdhlDeptCd`)·세부전공(`sebujg`)은 AJAX 로딩.** 대학원구분+학위과정 설정 후
  옵션이 뜰 때까지 대기 후 선택(스크립트가 `waitForFunction`으로 처리).
- **TOPIK**: 백엔드는 **`해당없음(9)`을 빈값으로 저장**한다(Y/N 무관). 실제 급수(2~6급)는
  이중언어(Y) 지원자라도 **그대로 저장된다** — 2026-07-13 이계호·장영·홍학개로 확인.
  `subm()`이 topik 비어있으면 막으므로, TOPIK 없는 지원자는 검증통과용으로 `9`를 넣는다.
  → 저장 후 조회하면 9는 공란으로 보이는 게 정상. (이전 문서의 "Y면 무조건 null"은 오기)
- ⚠️ **명부조회(gima1040) 표시 버그**: TOPIK이 빈 행은 목록에서 **바로 윗행 값**을 잘못
  끌어와 표시함(carry-forward). 실제 DB/개별원서는 정상(공란). 전산팀 리포트 수정 사안.

### 주요 필드 id / 코드값
| 항목 | id/name | 값(코드) |
|---|---|---|
| 전형구분 | gdhlEtexScrnGbCd | 외국인특별전형=3, 일반전형=1 |
| 대학원구분 | gdhlGbCd | 일반대학원=4, 사회복지전문대학원=7, 보건상담정책대학원=9 |
| 학위과정 | gdhlDegCosCd | 석사=40, 박사=41 |
| 입학구분 | gdhlEtshGbCd | 신입학=1, 편입학=2 |
| 이중언어 | LAB_EFLN_YN(name=labEflnYN) | Y / N |
| TOPIK | topik | 해당없음=9, 2급=2 … 6급=6 |
| 유효기간 | topik_date (number) | YYYYMMDD |
| 성명한글/영문 | koNm / enNm | |
| 주민번호 | ssn1(앞6, text) / name=ssn2(뒤7, password) | |
| 국적 | ntiCd | 중국=CN … (우즈베키스탄은 옵션명 "우즈베크") |
| 휴대전화 | mobpNo1/2/3 | |
| 주소 | sample6_postcode / sample6_address / sample6_address2 | |
| 학력(4블록 배열) | 접두어 col(전문대)/uni(학사)/ma(석사)/doc(박사) | |
| └ 각 블록 | {pre}SchlNm/DeptNm/GrtnDt/GrtnGbCd/ScoNo/PectScoCd/DegNo | |
| 졸업구분 | grtnGbCd[] | 졸업=1, 수료=2, 예정=3, 제적=4 |
| 만점구분 | pectScoCd[] | 4.5=1, 4.3=2, 4.0=3, 100=4 |

## 4. 데이터 JSON 형식 (예시 골격)
```json
{
  "name_kr": "성명",
  "select_by_value": { "gdhlEtexScrnGbCd":"3","gdhlDegCosCd":"40",
    "gdhlEtshGbCd":"1","LAB_EFLN_YN":"Y","gdhlGbCd":"9" },
  "select_late": { "topik": "9" },
  "dept_substring": "간호",
  "text": { "koNm":"…","enNm":"…","ssn1":"YYMMDD","topik_date":"",
    "mobpNo1":"062","mobpNo2":"670","mobpNo3":"2855",
    "sample6_postcode":"61743","sample6_address":"…","sample6_address2":"…" },
  "text_by_name": { "ssn2": "6999999" },
  "select_by_text": { "ntiCd": "중국" },
  "edu": {
    "col": {"schl":"","dept":"","dt":"YYYYMMDD","gb":"1","sco":"","pect":"4","deg":""},
    "uni": {"schl":"","dept":"","dt":"YYYYMMDD","gb":"1","sco":"","pect":"1","deg":""}
  }
}
```

## 5. 지원자별 데이터 규칙 (담당자 지시)
- **국적**: 엑셀 학생 전원 중국(예외: 개별서류 확인).  **휴대전화**: 전원 `062-670-2855`.
- **주소**: 사무실 주소 (우 61743) 전남광주통합특별시 남구 효덕로 277 광주대학교 /
  상세주소 "호심관 6층 국제협력처".
- **주민번호 뒤 7자리**: 외국인등록번호 있으면 실번호. 없으면 `[코드]999999`
  (1900년대생 남5/여6, 2000년대생 남7/여8) + 앞 6자리는 생년월일 YYMMDD.
- **대학원구분 매핑**(모집요강 기준): 간호학과 석사→보건상담정책대학원, 간호 박사→일반대학원,
  컴퓨터/미래융합/뷰티미용 등 공학·예체능 석사→일반대학원, 법학 석사→보건상담정책대학원,
  법학 박사·호텔관광·평생교육 박사·한국어문화교육콘텐츠 박사→일반대학원. (학과·과정별 상이)
- **이중언어**: 학과명에 "(이중언어과정)" 있으면 Y (중국어 트랙). TOPIK 불필요.
- **성적 만점 주의**: 폼 만점 옵션은 4.5/4.3/4.0/100 뿐. 5점만점 등은 변환 규칙 필요.
  중국 100점제 성적은 담당자가 4.5제로 환산해 엑셀에 기입(대체로 맞으나 오류 사례 있음
  → 성적표 원본 교차확인 권장). **엑셀 성적이 실제 성적표와 다른 경우가 종종 있음.**

## 6. 진행 현황 (2026-07-13 기준)

**원본 엑셀**: `…\Desktop\★국제협력처\2. 대학원\2026학년도 후기\지원서류\`
`2026-2학기 중국 유학생 지원자 현황(원서입력-중국)_최종_정재훈 수정_강향옥 수정.xlsx` (Sheet2)

**차수: 2026 / 후기정시모집(sems=3) / 차수 2** ← 이번 학기 우리 차수. (차수 3은 우리가 안 씀)

- ✅ **Sheet2 대학원 지원자 27명 전원 저장 완료** (차수 2, 학력 포함, `verify_all.js` 27/27 일치).
  - 최초에 차수 3(폼 기본값)으로 잘못 넣었다가 삭제 후 차수 2로 재등록함. 차수 3은 현재 0건.
  - 최종 확인: 차수 2 = 40건 (기존 14명 + 이번 26명 + 어제 넣은 정몽정은 원래 차수 2).
- ✅ **바이야노바 나르기자**(박사, 한국어문화교육콘텐츠, 일반대학원) — 별건, 저장 완료.
- ⛔ **범경부**(순번 3, 석사/미래융합기술공학) — 엑셀에서 **취소자**로 이동. 입력 안 함.

### 남은 일
1. **외국인등록번호 임시번호 11명** — 실번호 확보 시 `data/*.json`의 `text_by_name.ssn2`만
   고치고 `node fill_applicant.js data/파일.json submit --load` 로 덮어쓰면 됨.
   상몽적(4)·진세우(6)·유상택(8)·의상(9)·곽우호(10)·적려노이·동간파의(11)·수관상(13)·
   유신로(20)·서욱(23)·진흔신(25)·향원연(27)
2. 향원연(27) 석사 학위번호 `000-8390` — 다른 지원자와 형식이 달라 원본 대조 권장.
3. 명부조회(gima1040) TOPIK carry-forward 표시버그 → 전산팀 수정요청 (미해결).

## 7. 파일 안내
### 파이프라인 (엑셀 → 저장 → 검증)
1. `sheet2rows.ps1` : 엑셀 Sheet2 → 셀 배열 JSON. 엑셀이 열려 있어도 사본을 떠서 읽음.
   `powershell -File sheet2rows.ps1 -Path <xlsx> -Out rows.json`
2. `gen_applicants.js` : rows.json → `data/NN_이름.json` 일괄 생성.
   학과→대학원구분 매핑, 성적/만점 변환, 날짜 정규화, 임시 등록번호 생성, 경고 리포트까지 수행.
   **학과·대학원구분 매핑표(`DEPT`)와 한국대학 목록(`KR_SCHOOLS`)이 이 파일 상단에 있음** — 학과가
   늘면 여기 추가. `KR_SCHOOLS`에 없는 학교는 자동으로 `(외국)` 접두어가 붙는다.
   `node gen_applicants.js rows.json`
3. `batch.sh check` : 전원 검토 모드 1회전 → MISS/경고만 요약. **저장 전 반드시 실행.**
   `batch.sh save [순번…]` : 2단계 저장(INSERT → UPDATE) 일괄 실행.
4. `verify_all.js` : 저장값을 `data/*.json` 원본과 전 항목 대조. 최종 검증용.

### 차수 관리 / 삭제
- `list_chasu.js <차수>` : 해당 차수 지원자 명부 조회 (읽기 전용). **작업 전후로 꼭 확인.**
- `delete_applicant.js "성명" --sems=3 --go` : 입시원서삭제. ⚠ 복구 불가, 차수 필터 없음.
- `move_chasu.sh 04 05 …` : 차수3 삭제 → 차수2 재등록 일괄 처리.

### 그 외
- `fill_applicant.js` : 메인 자동입력 엔진 (단건)
- `readxlsx.ps1` : 엑셀 전체 시트 사람이 읽기용 덤프
- `inspect_*.js`, `topik_check.js`, `load_inspect.js`, `find_country.js` : DOM/저장값 진단 도구
- `data/` (git 제외) : 지원자별 입력 JSON

### 알아둘 것
- 서버는 성적 뒤 0을 절삭해 저장한다(`4.00`→`4`). 값은 동일하니 불일치 아님.
- 엑셀 날짜가 직렬번호(예: `37723`)로 들어있는 셀이 있다. 기준일은 **1899-12-30**.
  (TOPIK 유효기간 AC열이 이 형식) `gen_applicants.js`가 자동 변환한다.
