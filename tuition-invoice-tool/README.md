# 등록금·장학금 산출 / 고지서 생성 도구 (내부 업무용)

광주대학교 국제협력처 외국인 유학생 **등록금·장학금 자동 산출** 및 **학생별 등록금 고지서 PDF 일괄 생성** PowerShell 도구입니다.

> ⚠️ **개인정보 미포함**: 이 공개 저장소에는 **로직(스크립트)과 공개성 기준자료만** 포함되어 있습니다.
> 학생 명단·장학 데이터 엑셀, 생성된 고지서 PDF(실명 포함), 직인 이미지, 내부 규정(시행세칙) 등은 **의도적으로 제외**했습니다.
> 실제 실행에는 담당자 로컬 PC의 원본 데이터 파일이 필요합니다.

## 구성
```
tuition-invoice-tool/
├─ scripts/
│  ├─ 등록금계산.ps1     # 장학 규정 기반 등록금·장학금 자동 산출 → *_자동계산.xlsx
│  ├─ 고지서생성.ps1     # (재학생) 자동계산 결과 → 학생별 등록금 고지서 PDF 일괄 생성
│  ├─ 인보이스생성.ps1    # (신·편입) 완성본 엑셀 → 학생별 TUITION INVOICE PDF (한/영 병기, 가상계좌)
│  ├─ 합격통지서생성.ps1  # (신·편입) 완성본 엑셀 → 학생별 OFFER LETTER PDF (한/영 병기)
│  └─ 배치생성.ps1       # 학생 1명당 2p PDF(OFFER LETTER+TUITION INVOICE)를 신입/편입 × 국가폴더로 일괄 생성
├─ 로고_국영문_full.png       # 대학 로고(초록, 완전한 프레임) — 문서 상단, base64 자동 삽입
├─ 국제협력처장직인.png       # 국제협력처장 직인(붉은 인장) — 서명란 (gitignore 제외, 로컬 전용)
└─ reference/
   ├─ 모집요강.pdf                                      # 2026 후기 외국인 신·편입 특별전형(공개)
   ├─ 외국인 유학생 입학서류 체크리스트 및 적합 기준.hwpx  # 자격/서류/판정 기준
   ├─ 심사기준_정리.md                                  # 위 기준을 개발용으로 정리
   └─ application_10.docx                              # 입학지원서 양식(백지)
```

## 사용 (담당자 로컬 PC)
```powershell
# ① 등록금·장학금 자동 산출  (입력 엑셀 → *_자동계산.xlsx)
powershell -ExecutionPolicy Bypass -File "scripts\등록금계산.ps1" -InputFile "<장학반영 원본.xlsx>"

# ② 학생별 등록금 고지서 PDF 생성  (자동계산.xlsx → PDF 폴더)
#    로고/직인은 지정 안 하면 scripts\ 상위 폴더의 기본 이미지를 자동 사용
powershell -ExecutionPolicy Bypass -File "scripts\고지서생성.ps1" -InputFile "<자동계산.xlsx>" -OutDir "<출력폴더>"

# ③ (신·편입) OFFER LETTER / TUITION INVOICE 개별 생성  (-Limit N 으로 샘플 확인 권장)
powershell -ExecutionPolicy Bypass -File "scripts\합격통지서생성.ps1" -OutDir "<출력폴더>"
powershell -ExecutionPolicy Bypass -File "scripts\인보이스생성.ps1" -OutDir "<출력폴더>"

# ④ 배치: 학생 1명당 2페이지 PDF(OFFER LETTER+TUITION INVOICE)를 폴더 구조로 일괄 생성
#    저장: <OutRoot>\{신입학|편입학}\{1. 베트남|2. 중국|3. 몽골 및 기타국가}\한글명_영문명.pdf
#    가상계좌: 포털 엑셀에서 수험번호(7자리)-계좌(###-###-######) 패턴 매칭
powershell -ExecutionPolicy Bypass -File "scripts\배치생성.ps1" -MainFile "<완성본.xlsx>" -AcctFile "<포털.xlsx>" -OutRoot "<출력루트>"
```
> 로고·직인 이미지는 `-LogoImage`/`-SealImage`로 바꿀 수 있고, 미지정 시 `로고_국영문_full.png`·`국제협력처장직인.png`를 자동 사용합니다.
> 스크립트 상단 `param()`의 기본 경로와 `등록금계산.ps1`의 [설정] 상수(계열 등록금·TOPIK 감면율 등)는 학기/환경에 맞게 수정해 사용하세요.
> 신·편입 완성본 엑셀은 `수험번호·한글명·영문명·국가명·학부(과)·구분(신입/편입)·트랙` 열을 사용합니다(현재 열 위치: 4·5·6·9·10·2·3).
> ⚠️ 한글(스크립트·README)이 깨지지 않도록 `.ps1`은 **UTF-8 BOM**으로 저장할 것 (PowerShell 5.1 cp949 오독 방지).

## 산출 규정 요약
- 등록금(A): 인문사회 3,077,000원 / 공학·예체능·보건 3,744,000원
- 토픽장학금(B): 직전학기 12학점↑ & 평점 2.5↑ 충족 시 — 3급 40% / 4급 55% / 5급 60% / 6급 65%
- 성적장학금(C): 평점 4.0↑ 300,000원
- 실납부액 = A − (B+C+D)
