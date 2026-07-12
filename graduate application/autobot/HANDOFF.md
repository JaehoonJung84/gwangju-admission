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
- 저장 시 alert(확인창)은 자동 수락하고 메시지를 캡처함. `"입력을 완료했습니다"` = 성공.

## 3. 폼 구조 핵심 (역공학 결과)

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
- **TOPIK**: 이중언어(LAB_EFLN_YN=Y) 지원자는 뭘 넣어도 백엔드가 **null 저장**(TOPIK 불필요).
  단 `subm()`이 topik 비어있으면 막으므로 검증통과용으로 `해당없음(9)`을 넣음.
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

## 6. 진행 현황 (2026-07-12 기준)
- ✅ **정몽정**(석사, 간호, 보건상담정책대학원) — 저장 완료(학력 포함).
- ✅ **바이야노바 나르기자**(박사, 한국어문화교육콘텐츠, 일반대학원) — 저장 완료(학력·계명대 학위번호 포함).
- ⏳ Sheet2 나머지 대학원 지원자(약 26명) — 담당자가 외국인등록번호·성적 보완 중. 보완 후 배치.
- 미결: 정우동(호텔관광경영, 한국어과정) TOPIK 급수/유효기간 담당자 추후 입력.
- 미결: 명부 TOPIK carry-forward 표시버그 → 전산팀 수정요청 문구 작성해둠(대화 참조).

## 7. 파일 안내
- `fill_applicant.js` : 메인 자동입력 엔진
- `readxlsx.ps1` : 엑셀(Sheet 전체) 파싱 (`powershell -File readxlsx.ps1 -Path 파일.xlsx`)
- `inspect_*.js`, `topik_check.js`, `load_inspect.js`, `find_country.js` 등 : DOM/저장값 진단·검증 도구
- `data/` (git 제외) : 지원자별 입력 JSON
