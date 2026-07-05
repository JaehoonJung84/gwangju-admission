# 광주대학교 외국인 유학생 입학지원 시스템

광주대학교 외국인 신·편입생 특별전형 온라인 지원 포털 (프로토타입).

## 주요 파일
- **`Gwangju_Admission_System.html`** — 메인 입학지원 시스템 (단일 파일 웹앱)
  - 6개 언어: 한국어 · English · 中文 · Tiếng Việt · Монгол · Oʻzbek
  - 언어 선택 → 지원 정보 입력(프로필) → 서류 제출 → 검토·최종 제출
  - 트랙별 어학요건(한국어/중국어 = TOPIK, 영어 = 공인영어성적), 커스텀 다국어 캘린더
  - 담당자 대시보드 (데모 접속코드: `gu1234`) + 규칙 기반 자동 적격 판정
  - 최종 제출 시 no-reply 확인 메일 자동 구성
- `gwangju-logo.jpg` — 로고
- `Admission Application Form_Gwangju University.docx` — 입학지원서 양식
- `Guidelines_KO/EN/ZH/VI/MN/UZ.pdf` — 언어별 모집요강 (KO·EN 공식본, 그 외 번역본)
- `Gwangju_Admission_Portal.html` — 초기 버전 (참고용)

## 실행
`Gwangju_Admission_System.html` 파일을 웹 브라우저로 열면 됩니다. 별도 서버 불필요.

## 참고 (프로토타입 한계)
- 지원 데이터는 방문자 브라우저(localStorage)에 저장됩니다.
- 확인 메일은 화면에 표시되며, 실제 발송은 백엔드 메일 서버 연동이 필요합니다.
- 자동 적격 판정은 입력값 기반 규칙 엔진입니다. (실서비스에서는 업로드 서류 판독 연동 예정)
