# -*- coding: utf-8 -*-
"""분량 축소본 — 뜻은 그대로 두고 줄 수만 줄인 표현.

영문은 국문보다 길어 각 절이 한 쪽을 넘겼다. 본문 글자 크기를 줄이는 것만으로는
원본 14쪽 배치로 돌아오지 않아, 길이가 문제되는 칸만 짧게 고쳐 쓴다.
TR 에 덮어씌워 쓴다(키는 국문 원문 그대로).
"""

SHORT = {
    # ── 4. 제출서류 ──────────────────────────────────────────────────
    '○ 개인정보 수집·이용·제공 동의서': '○ Consent to collection and use of personal information',
    '○ 중국: 호구부 사본 (호구부 2개 이상인 경우 친족관계증명서 공증본)':
        '○ China: copy of the household register (if two or more, a notarized certificate of kinship)',
    '최종학교 졸업 및 성적증명서': 'Graduation certificate and transcript (last school attended)',
    '○ (신입학) 고등학교 졸업(예정)증명서 및 전 학년 성적증명서':
        '○ (Freshman) High school graduation (or expected) certificate and transcripts for all years',
    '○ (편입학) 전문대학 이상 졸업(학위)증명서 및 성적증명서, 4년제 대학 재학자는 수료증명서 포함':
        '○ (Transfer) Graduation (degree) certificate and transcript from a junior college or above; '
        'those enrolled at a 4-year university must add a certificate of completion',
    '○ 아포스티유 또는 재외공관 영사인증 원본, 중국은 학력인증보고서':
        '○ Original apostille or consular authentication; for China, an academic credential '
        'verification report',
    '○ 접수 시 사본 제출, 원본은 합격 후 등록기간까지 제출 가능':
        '○ Copies at application; originals by the end of the registration period after admission',
    '○ 베트남은 고등학교 졸업시험 응시 증명서로 졸업(예정)증명서 대체 가능 (졸업 후 졸업증명서 제출)':
        '○ Vietnam: a certificate of sitting the high school graduation exam may replace the '
        'graduation certificate (submit the certificate after graduation)',
    '○ 본인 또는 부모 명의 은행 잔고증명서 (발급일로부터 30일 이내)':
        '○ Bank balance certificate of the applicant or a parent (issued within 30 days)',
    '○ 재직증명서: 근무처 발행 (자영업자는 사업자등록증 사본으로 갈음)':
        '○ Employment: issued by the employer (self-employed: copy of the business registration '
        'certificate)',
    '○ 수입증명서: 최근 1년간 소득금액 확인 서류': '○ Income: documents verifying income for the past year',
    '○ 입학 지원일로부터 3개월 이내 발급분': '○ Issued within three months before application',
    '○ 지원서, 유학계획서, 자기소개서, 유학경비 부담 서약서':
        '○ Application, study plan, self-introduction, financial affidavit',

    # ── 6. 비자 신청 ─────────────────────────────────────────────────
    '광주대학교 국제협력처': 'GU Office of International Affairs',
    '본국 주재 대한민국 공관': 'Korean mission in the home country',
    '○ 국제협력처 체류자격 변경 설명회 참석': '○ Attend the OIA briefing on change of status',
    '○ 등록금 납부·원본서류 확인 후 본교가 비자 서류 발송':
        '○ The University sends the visa documents after tuition payment and document verification',
    '○ 서류 구비 후 본국 공관에 직접 신청':
        '○ Apply in person at the Korean mission in the home country',
    '○ 체류기간 만료 전·개강 전 신청': '○ Apply before the stay expires and the semester begins',
    '사증(비자) 발급 지연·거부에 따른 불이익은 지원자 본인 부담':
        'Applicants bear any disadvantage from delayed or refused visa issuance.',

    # ── 7. 장학금 ────────────────────────────────────────────────────
    '공인언어능력': 'Language',
    'TOPIK 6급 · 영어트랙 어학성적 기준 충족': 'TOPIK Level 6 · English Track score met',
    '성적우수장학금은 4.5 만점 기준, 학년 구분 없이 직전 학기 성적으로 지급':
        'The Academic Excellence Scholarship is based on a 4.5 scale and awarded on the previous '
        'semester’s grades regardless of year.',
    '어학 성적은 등록금 고지서 발급일 기준 유효기간 이내의 것만 인정':
        'Only language scores valid as of the tuition invoice date are accepted.',
    '선발기준 및 금액은 매 학년도 시행계획과 본교 「장학금 지급에 관한 시행세칙」에 따라 변동 가능':
        'Criteria and amounts may change under each year’s plan and the University’s '
        'Detailed Rules on the Payment of Scholarships.',

    # ── 3. 지원자격 (한 줄 줄이기) ───────────────────────────────────
    '○ 국내외에서 우리나라 초·중등교육에 상응하는 교육과정을 전부 이수한 졸업자 및 졸업예정자':
        '○ Graduates or prospective graduates who completed, in Korea or abroad, the full course of '
        'education equivalent to Korean primary and secondary education',
    '○ 법무부 기준에 따라 영어를 모국어·공용어로 사용하는 국가의 국적자로서 해당 국가에서 '
    '중등·고등교육 이수 시 성적 제출 면제':
        '○ Under Ministry of Justice standards, nationals of countries where English is the native '
        'or official language who completed secondary and higher education there are exempt from '
        'submitting a score',
    '- 1년 이내에 200시간 이상의 한국어 연수를 이수하여야 함. 단, TOPIK 3급 이상 또는 이와 동등한 '
    '자격을 취득한 자는 제외(예체능계열은 2급 이상)':
        '- At least 200 hours of Korean training within one year, except for those who obtain TOPIK '
        'Level 3 or higher or an equivalent qualification (Level 2 for Arts & Physical Education)',

    # ── 5. 모집단위 계열 칸(폭 50pt) — 한 줄에 들어가야 행이 두꺼워지지 않는다 ──
    '자연': 'Natural',
    '인문사회': 'Hum.·Social',
    '예체능': 'Arts & P.E.',
    '공학': 'Engineering',
}
