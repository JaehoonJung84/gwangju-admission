# -*- coding: utf-8 -*-
"""(한글)학부 2027학년도 모집요강 → 영문.

키는 원본 PDF 한 칸(cell)의 글월을 공백 하나로 정규화한 것.
긴 칸은 PREFIX(앞머리 일치)로 찾는다. '\n' 은 줄바꿈 고정.
용어는 「2027학년도 1학기 외국인 학부 신·편입 특별전형 모집요강(20261030)_영문본.pdf」를 따른다.
"""

TRANS = {
    # ---------- 머리말·꼬리말 ----------
    '2027학년도 1학기 외국인 학부 신·편입생 특별전형 모집요강':
        '2027 Spring Special Admission for International Freshmen and Transfer Students',
    '카카오플러스친구 @광주대학교입학상담': 'KakaoTalk Plus Friend  @광주대학교입학상담',

    # ---------- 목차 ----------
    'Ⅰ. 전형일정': 'Ⅰ. Admission Schedule',
    'Ⅱ. 전형방법': 'Ⅱ. Admission Procedures',
    'Ⅲ. 지원자격': 'Ⅲ. Eligibility',
    'Ⅳ. 제출서류': 'Ⅳ. Required Documents',
    'Ⅴ. 모집단위': 'Ⅴ. Programs Offered',
    'Ⅵ. 비자 신청': 'Ⅵ. Visa Application',
    'Ⅶ. 장학금': 'Ⅶ. Scholarships',
    'Ⅷ. 기숙사': 'Ⅷ. Dormitory',
    'Ⅸ. 기타사항': 'Ⅸ. Other Information',
    'Ⅹ. 유의사항': 'Ⅹ. Important Notes',
    'ⅩⅠ. 캠퍼스 안내': 'ⅩⅠ. Campus Guide',

    # ---------- 절 제목 ----------
    '전형일정': 'Admission Schedule',
    '전형방법': 'Admission Procedures',
    '지원자격': 'Eligibility',
    '제출서류': 'Required Documents',
    '모집단위': 'Programs Offered',
    '비자 신청': 'Visa Application',
    '장학금': 'Scholarships',
    '기숙사': 'Dormitory',
    '기타사항': 'Other Information',
    '유의사항': 'Important Notes',
    '캠퍼스 안내': 'Campus Guide',
    '1. 전형절차': '1. Admission Process',
    '2. 전형요소': '2. Evaluation',
    '1. 신입학·편입학 모집단위 - 신입학(1학년)':
        '1. Programs Offered - Freshman Admission (1st Year)',
    '2. 신입학·편입학 모집단위 - 편입학(3·4학년)':
        '2. Programs Offered - Transfer Admission (3rd · 4th Year)',
    '1. 신·편입생 장학금': '1. Scholarships for Entering Students',
    '2. 재학생 장학금': '2. Scholarships for Enrolled Students',
    '1. 안내': '1. General Information',
    '2. 기간 및 비용': '2. Period and Fees',
    '3. 입사절차': '3. Move-in Procedure',
    '4. 생활 안내': '4. Living Information',
    '1. 학사 일정': '1. Academic Calendar',
    '2. 수강신청': '2. Course Registration',
    '3. 국민건강보험': '3. National Health Insurance',
    '문의처': 'Contact',

    # ---------- p4 전형일정 ----------
    '구분': 'Category',
    '1차': 'Round 1',
    '2차': 'Round 2',
    '원서접수': 'Application',
    '서류심사': 'Document Screening',
    '면접심사': 'Interview',
    '합격자 발표': 'Announcement of Results',
    '등록금 납부': 'Tuition Payment',
    '표준입학허가서 발급': 'Issuance of Standard Admission Letter',
    '개강': 'Start of Semester',
    '입국 · 개강': 'Arrival · Start of Semester',
    '2026. 11. 11.(수) 10:00 ∼ 12. 4.(금) 17:00':
        '2026. 11. 11.(Wed) 10:00 ∼\n12. 4.(Fri) 17:00',
    '2026. 12. 14.(월) 10:00 ∼ 12. 31.(목) 17:00':
        '2026. 12. 14.(Mon) 10:00 ∼\n12. 31.(Thu) 17:00',
    '2026. 12. 7.(월) ∼ 12. 10.(목)': '2026. 12. 7.(Mon) ∼ 12. 10.(Thu)',
    '2027. 1. 4.(월) ∼ 1. 7.(목)': '2027. 1. 4.(Mon) ∼ 1. 7.(Thu)',
    '2026. 12. 15.(화) ∼ 12. 18.(금)': '2026. 12. 15.(Tue) ∼ 12. 18.(Fri)',
    '2027. 1. 12.(화) ∼ 1. 15.(금)': '2027. 1. 12.(Tue) ∼ 1. 15.(Fri)',
    '2026. 12. 23.(수)': '2026. 12. 23.(Wed)',
    '2027. 1. 21.(목)': '2027. 1. 21.(Thu)',
    '2027. 1. 4.(월) ∼ 1. 8.(금)': '2027. 1. 4.(Mon) ∼ 1. 8.(Fri)',
    '2027. 1. 25.(월) ∼ 1. 29.(금)': '2027. 1. 25.(Mon) ∼ 1. 29.(Fri)',
    '등록금 납부 및 제출서류 확인 후 발급':
        'Issued after tuition payment and verification of submitted documents',
    '2027. 1월 ∼ 2월': '2027. Jan. ∼ Feb.',
    '2027. 2월': '2027. Feb.',
    '2027. 3. 2.(화)': '2027. 3. 2.(Tue)',
    '평가내용': 'Evaluation Content',
    '배점': 'Points',
    '적격 / 부적격': 'Pass / Fail',
    '100점': '100 points',
    '선발기준': 'Selection Criteria',
    '○ 지원자격 충족 여부, 학력·성적, 어학능력, 재정능력 확인 ○ 제출서류 진위 확인':
        '○ Verification of eligibility, academic records, language proficiency and finances\n'
        '○ Verification of the authenticity of submitted documents',
    '○ 어학능력, 수학능력, 학업의지, 진로계획, 유학여건 등 종합 평가':
        '○ Comprehensive assessment of language proficiency, academic ability, motivation, career plan and study conditions',
    '○ 서류심사 적격자 중 면접심사 70점 이상 득점자 선발':
        '○ Applicants who pass the document screening and score 70 or higher in the interview are selected',
    '※ 전형료: 50,000원 (입금계좌: 광주은행 1127-020-252652 광주대학교)':
        '※ Application fee: KRW 50,000 (Gwangju Bank 1127-020-252652, Gwangju University)',

    # ---------- p5 지원자격 ----------
    '내용': 'Requirements',
    '공통': 'Common',
    '신입학': 'Freshman',
    '편입학': 'Transfer',
    '3학년': '3rd Year',
    '4학년': '4th Year',
    '언어능력': 'Language Proficiency',
    '졸업요건': 'Graduation Requirement',
    '한국어트랙': 'Korean Track',
    '영어트랙': 'English Track',
    '한국어트랙 (자격 소지자)': 'Korean Track\n(Qualified Applicants)',
    '한국어트랙 (이중언어과정)': 'Korean Track\n(Bilingual Program)',
    '한국어트랙 및 이중언어과정': 'Korean Track and\nBilingual Program',
    '○ 부모가 모두 외국인인 외국인 ○ 이중 국적자 및 무국적자는 외국인으로 인정하지 않음':
        '○ Foreign nationals whose parents are both foreign nationals\n'
        '○ Dual nationals and stateless persons are not recognized as foreign nationals',
    '○ 국내외에서 우리나라 초·중등교육에 상응하는 교육과정을 전부 이수한 졸업자 및 졸업예정자':
        '○ Graduates or prospective graduates who completed, in Korea or abroad, the full course of education equivalent to Korean primary and secondary education',
    '○ 국내외 4년제 정규대학 2년 이상 수료(예정)자 ○ 국내외 전문대학 졸업(예정)자':
        '○ Applicants who have completed (or will complete) at least two years at a 4-year university in Korea or abroad\n'
        '○ Graduates (or prospective graduates) of a junior college in Korea or abroad',
    '○ 국내외 4년제 정규대학 3년 이상 수료(예정)자 ○ 국내외 전문대학 3년제 학과 졸업(예정)자':
        '○ Applicants who have completed (or will complete) at least three years at a 4-year university in Korea or abroad\n'
        '○ Graduates (or prospective graduates) of a 3-year junior college program in Korea or abroad',
    '○ TOPIK 4급 이상 또는 동등한 자격 취득 (예체능 3급 이상)':
        '○ TOPIK Level 4 or higher, or an equivalent qualification (Level 3 or higher for Arts & P.E.)',
    '○ 별도 어학 졸업요건 없음': '○ No separate language requirement for graduation',

    # ---------- p6 제출서류 ----------
    '순번': 'No.',
    '비고': 'Remarks',
    '입학지원서 (본교 소정양식)': 'Application form\n(University format)',
    '여권 사본 및 여권용 사진 2매': 'Copy of passport and\ntwo passport photos',
    '본인 및 부모 신분증 사본': 'Copies of the applicant’s\nand parents’ ID cards',
    '가족관계 증명서류': 'Proof of family relationship',
    '외국인등록증 사본': 'Copy of Alien\nRegistration Card',
    '최종학교 졸업 및 성적증명서': 'Graduation certificate and\ntranscript (last school)',
    '재정보증 서류': 'Financial guarantee\ndocuments',
    '부모 재직증명서 및 수입증명서': 'Parents’ certificate of\nemployment and proof of\nincome',
    '어학능력 증명서': 'Language proficiency\ncertificate',
    '학력조회 동의서 (본교 양식)': 'Consent to academic records\nverification (University format)',
    '○ 지원서, 유학계획서, 자기소개서, 유학경비 부담 서약서 ○ 개인정보 수집·이용·제공 동의서':
        '○ Application, study plan, self-introduction, financial affidavit\n'
        '○ Consent to collection and use of personal information',
    '○ 여권 유효기간 입학일 기준 6개월 이상':
        '○ Passport valid for at least six months from the date of admission',
    '○ 본국 신분증 또는 시민권': '○ National ID card or certificate of citizenship',
    '○ 국내 체류자에 한함': '○ Only for applicants residing in Korea',
    '○ 제출서류 진위 확인용': '○ Used to verify the authenticity of submitted documents',

    # ---------- p7·p8 모집단위 ----------
    '대학': 'College',
    '학부(과)': 'Department/Division',
    '계열': 'Field',
    '등록금(원)': 'Tuition (KRW)',
    '이중언어과정': 'Bilingual Program',
    '자연': 'Natural',
    '인문사회': 'Hum.·Social',
    '예체능': 'Arts & P.E.',
    '공학': 'Engineering',
    '보건 복지 대학': 'College of\nHealth Welfare',
    '문화 산업 대학': 'College of\nCultural Industry',
    '인문 사회 과학 대학': 'College of\nHumanities &\nSocial Sciences',
    '공과 대학': 'College of\nEngineering',
    'AI 앙트십대학': 'College of\nEntrepreneurship',
    '보건행정학과': 'Health Administration',
    '보건행정학부': 'Health Administration',
    '사회복지학부': 'Social Welfare',
    '식품영양학과': 'Food Science & Nutrition',
    '반려동물보건산업학과': 'Pet Health Industry',
    '스포츠과학부': 'Sports Science',
    '태권도학과': 'Taekwondo',
    '시각영상디자인학과': 'Visual & Media Design',
    '산업디자인학과': 'Industrial Design',
    '인테리어디자인학과': 'Interior Design',
    '패션주얼리디자인학과': 'Fashion & Jewelry Design',
    '패션주얼리디자인학부': 'Fashion & Jewelry Design',
    '뷰티미용학과': 'Beauty Science',
    '사진영상미디어학과': 'Photography, Image & Media',
    '사진영상학과': 'Photography & Image',
    '항공서비스학과': 'Airline Service',
    '호텔조리제과제빵학과': 'Hotel Culinary & Baking Arts',
    '교육상담학과': 'Education & Counseling',
    '청소년상담·평생교육학과': 'Youth Counseling & Lifelong Education',
    '심리학과': 'Psychology',
    '경찰행정학과': 'Police Administration',
    '소방행정학과': 'Fire Administration',
    '문헌정보학과': 'Library & Information Sciences',
    '경영학과': 'Business Administration',
    '회계세무학과': 'Accounting & Tax',
    '무역유통학과': 'Trade & Distribution',
    '건축공학과': 'Architectural Engineering',
    '건축학부': 'Architecture',
    '컴퓨터공학과': 'Computer Engineering',
    '전기공학과': 'Electrical Engineering',
    '토목공학과': 'Civil Engineering',
    '기계자동차공학부': 'Mechanical & Automotive Engineering',
    '글로벌콘텐츠학부': 'Global Contents',

    # ---------- p9 비자·장학금 ----------
    '국내 체류자': 'Applicants in Korea',
    '국외 체류자': 'Applicants Abroad',
    '신청 기관': 'Where to Apply',
    '신청 내용': 'Type of Application',
    '신청 시기': 'When to Apply',
    '절차': 'Procedure',
    '광주대학교 국제협력처': 'GU Office of International Affairs',
    '본국 주재 대한민국 공관': 'Korean mission in the home country',
    '체류자격 변경 (D-2)': 'Change of status of stay (D-2)',
    '유학(D-2) 사증 발급': 'Issuance of a study (D-2) visa',
    '○ 국제협력처 체류자격 변경 설명회 참석 ○ 안내에 따라 신청서류 준비':
        '○ Attend the OIA briefing on change of status\n'
        '○ Prepare the application documents as instructed',
    '○ 등록금 납부·원본서류 확인 후 본교가 비자 서류 발송 ○ 서류 구비 후 본국 공관에 직접 신고':
        '○ The University sends the visa documents after tuition payment and document verification\n'
        '○ Apply in person at the Korean mission in the home country',
    '○ 체류기간 만료 전·개강 전 신청 ○ 변경 절차 완료 시까지 국내 체류':
        '○ Apply before the stay expires and the semester begins\n'
        '○ Remain in Korea until the change procedure is complete',
    '○ 입국 직후 외국인 등록': '○ Complete alien registration immediately after arrival',
    '※ 등록금 납부자에 한하여 표준입학허가서 발급 ※ 사증(비자) 발급 지연·거부에 따른 불이익은 지원자 본인 부담':
        '※ The Standard Admission Letter is issued only to those who have paid tuition\n'
        '※ Applicants bear any disadvantage from delayed or refused visa issuance',
    '트랙': 'Track',
    '어학 성적': 'Language Score',
    '수업료 감면': 'Tuition Reduction',
    '종류': 'Type',
    '기준': 'Criteria',
    '혜택': 'Benefit',
    'TOPIK 3급': 'TOPIK Level 3',
    'TOPIK 4급': 'TOPIK Level 4',
    'TOPIK 5급': 'TOPIK Level 5',
    'TOPIK 6급': 'TOPIK Level 6',
    '공인언어능력 장학금': 'Language Proficiency\nScholarship',
    '성적우수장학금': 'Academic Excellence\nScholarship',
    '수업료 20% 감면': '20% tuition reduction',
    '수업료 30% 감면': '30% tuition reduction',
    '수업료 40% 감면': '40% tuition reduction',
    '수업료 50% 감면': '50% tuition reduction',
    '직전 학기 평점평균 4.00 ∼ 4.29': 'Previous semester GPA 4.00 ∼ 4.29',
    '직전 학기 평점평균 4.30 이상': 'Previous semester GPA 4.30 or higher',
    '300,000원': 'KRW 300,000',
    '500,000원': 'KRW 500,000',
    '※ 입학 학기 1회 지급': '※ Awarded once, in the semester of admission',
    'TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5, TEPS 600(NEW TEPS 330)':
        'TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5, TEPS 600 (NEW TEPS 330)',

    # ---------- p10 기숙사 ----------
    '○ 기간: 2027년 2월말 입국 시 ∼ 2027. 8. 27.(금)':
        '○ Period: from arrival in late February 2027 to 2027. 8. 27.(Fri)',
    '관리비 (180일 기준)': 'Accommodation fee (180 days)',
    '식비 (130일 기준, 1식 4,500원)': 'Meal fee (130 days, KRW 4,500 per meal)',
    '2인실': 'Double room',
    '3인실': 'Triple room',
    '4인실': 'Quad room',
    '1일 1식': '1 meal a day',
    '1일 2식': '2 meals a day',
    '1일 3식': '3 meals a day',
    '1,306,800원': 'KRW 1,306,800',
    '1,119,600원': 'KRW 1,119,600',
    '889,200원': 'KRW 889,200',
    '585,000원': 'KRW 585,000',
    '1,170,000원': 'KRW 1,170,000',
    '1,755,000원': 'KRW 1,755,000',
    '기숙사 선택': 'Choose dormitory',
    '입사 신청': 'Apply',
    '기숙사비 납부': 'Pay fees',
    '호실 발표': 'Room assignment',
    '입사': 'Move in',

    # ---------- p11 기타사항 ----------
    '○ 개강일: 2027. 3. 2.(화) ○ 신·편입생 오리엔테이션: 2027년 2월 말 (세부 일정 개별 안내)':
        '○ First day of class: 2027. 3. 2.(Tue)\n'
        '○ Orientation for entering students: late February 2027 (details announced individually)',

    # ---------- p13 캠퍼스 안내 ----------
    '언어 · 국가': 'Language · Country',
    '전화번호': 'Telephone',
    '중국': 'Chinese',
    '베트남': 'Vietnamese',
    '영어': 'English',
    '몽골 및 기타 국가': 'Mongolian & Other Countries',
}

# 긴 칸은 앞머리로 찾는다.
PREFIX = {
    '※ 모든 일정은 한국 시간(KST) 기준':
        '※ All dates and times are based on Korea Standard Time (KST)\n'
        '※ Applications and documents must reach the University by the closing date\n'
        '※ Apostilled or consular-authenticated originals may be submitted by the end of registration\n'
        '※ The interview date and method are announced to each applicant individually\n'
        '※ Dates may change as the process proceeds, and additional recruitment is possible',

    '○ TOPIK(TOPIK IBT 포함) 3급 이상':
        '○ TOPIK Level 3 or higher (TOPIK IBT included), or an equivalent qualification '
        '(Level 2 or higher for Arts & P.E.)\n'
        '   - Equivalent: King Sejong Institute Intermediate 1 or higher, or KIIP Level 3 '
        'or higher (pre-test score of 61 or higher)\n'
        '○ Applicants who completed at least one year of the University’s Korean language '
        'program and obtained GU-TOPIK Level 3 or higher',

    '○ 위 한국어능력 자격을 충족하지 못한 자는':
        '○ Applicants who do not meet the Korean proficiency requirements above '
        'may apply for the Bilingual Program\n'
        '○ After admission, students must complete the Korean language courses '
        'designated by the University\n'
        ' - At least 200 hours of Korean training within one year, except for those who '
        'obtain TOPIK Level 3 or higher or an equivalent qualification '
        '(Level 2 or higher for Arts & P.E.)',

    '○ TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5, TEPS 600(NEW TEPS 330) 또는':
        '○ Holders of TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5, TEPS 600 (NEW TEPS 330), '
        'or an equivalent score on a nationally accredited English proficiency test\n'
        '○ Under Ministry of Justice standards, nationals of countries where English is the '
        'native or official language who completed secondary and higher education there '
        'are exempt from submitting a score',

    '※ 어학 성적은 원서접수 마감일 기준 유효한 것만 인정':
        '※ Only language test scores valid as of the application closing date are accepted\n'
        '※ Detailed eligibility requirements follow the regulations of the University\n'
        '※ English Track: a program with separately designated admission units in which applicants are selected after '
        'verification of their English proficiency, and in which at least 50% of the credits required for graduation '
        'are taught in English',

    '○ 중국: 호구부 사본':
        '○ China: copy of the household register '
        '(if two or more, a notarized certificate of kinship)\n'
        '○ Other countries: certificate of family relationship or birth certificate (in English)',

    '○ (신입학) 고등학교 졸업(예정)증명서':
        '○ (Freshman) High school graduation (or expected) certificate and transcripts for all years\n'
        '○ (Transfer) Graduation (degree) certificate and transcript from a junior college or '
        'above; those enrolled at a 4-year university must add a certificate of completion\n'
        '○ Original apostille or consular authentication; for China, an academic credential '
        'verification report\n'
        '○ Copies at application; originals by the end of the registration period after admission\n'
        '○ Vietnam: a certificate of sitting the high school graduation exam may replace the '
        'graduation certificate (submit the certificate after graduation)',

    '○ 보증금액 16,000,000원 이상':
        '○ Guaranteed amount of KRW 16,000,000 or more\n'
        '○ Bank balance certificate of the applicant or a parent '
        '(issued within 30 days)',

    '○ 재직증명서: 근무처 발행':
        '○ Employment: issued by the employer '
        '(self-employed: copy of the business registration certificate)\n'
        '○ Income: documents verifying income for the past year\n'
        '○ Issued within three months before application',

    '○ 해당자에 한함 (TOPIK 성적증명서 등)':
        '○ Only for applicable applicants (e.g. TOPIK score report)\n'
        '※ Must be within its validity period as of the opening date of the round applied for',

    '※ 한국어·영어 이외의 언어로 작성된 서류는':
        '※ Documents written in a language other than Korean or English must be accompanied by a Korean or English translation\n'
        '※ The University may request additional documents if necessary for the review',

    '※ 이중언어과정은 통번역기 사용 가능':
        '※ Translation devices may be used in the Bilingual Program\n'
        '※ Tuition is based on the 2026 academic year and may change with annual tuition adjustments',

    '※ 성적우수장학금은 4.5 만점 기준':
        '※ The Academic Excellence Scholarship is based on a 4.5 scale and awarded on the previous semester’s grades regardless of year\n'
        '※ Only language scores valid as of the tuition invoice date are accepted\n'
        '※ Criteria and amounts may change under each year’s plan and the University’s Detailed Rules on the Payment of Scholarships',

    '○ 신·편입생은 기숙사 또는 외부 거주 중 선택 가능':
        '○ Entering students may choose between the dormitory and off-campus housing\n'
        '○ A tuberculosis test certificate must be submitted when applying\n'
        '○ Entering students must take at least one meal a day (the fee for at least one meal is compulsory)\n'
        '○ Residents must observe the dormitory rules posted on the dormitory website; violations may result in '
        'penalty points and forced withdrawal',

    '※ 2인실·3인실은 잔여 객실 범위 내에서만':
        '※ Double and triple rooms may be applied for only within the number of rooms available\n'
        '※ The fee for at least one meal a day (KRW 585,000) is compulsory; meals bought on site cost KRW 5,500 each\n'
        '※ The cafeteria is closed on weekends and during national holidays\n'
        '※ The number of meals may be changed only during the meal-change period at the start of the semester; '
        'no change or refund is possible afterwards (dates to be announced)\n'
        '※ The period may change with the academic calendar, and the fees may change accordingly',

    '○ 입사 신청: 기숙사 홈페이지':
        '○ Application: dormitory website → application for entering students (log in with date of birth) '
        '→ complete the form (attach the tuberculosis test certificate)\n'
        '○ Students residing abroad submit the application through the Office of International Affairs\n'
        '○ First-choice room types are assigned first; if unassigned, rooms are allocated in the order of '
        'second, third and fourth choice within the rooms available\n'
        '○ Payment: print the invoice from the website (it is not mailed) and pay at Gwangju Bank or to the virtual account\n'
        '○ Failure to pay within the payment period results in rejection; the room type cannot be changed after payment\n'
        '○ Room assignments and detailed dates are announced on the dormitory website and individually',

    '○ 준비물: 신분증, 침구류':
        '○ What to bring: ID card, bedding, toiletries and personal items\n'
        '○ Prohibited: televisions, electric cooking appliances, flammable materials, pets, gambling devices, knives and the like\n'
        '○ House rules: smoking (including e-cigarettes) is strictly prohibited inside the building; quiet hours after 22:00; '
        'entry and exit closed from 01:00 to 05:00\n'
        '○ Early withdrawal: submit a withdrawal form on the portal system at least three days in advance and obtain '
        'the supervisor’s confirmation\n'
        '○ Refunds: the accommodation fee is settled on a sliding scale under the dormitory rules; the meal fee is '
        'refunded for the remaining days less five days\n'
        '○ Students who withdraw early may not move in again during the same semester or the seasonal session\n'
        '○ Observe the etiquette of communal living (see the dormitory website)\n'
        '○ Use power strips with earth-leakage breakers in the rooms; daisy-chaining outlets is prohibited\n'
        '○ Keep the international students’ kitchen tidy, hygienic and clean after use\n'
        '○ Inquiries: Dormitory Office +82-62-670-2803 / https://dorm.gwangju.ac.kr',

    '○ 상담: 오리엔테이션 이후':
        '○ Advising: register for courses after consulting your department following the orientation\n'
        '○ Method: online through the Gwangju University portal system\n'
        '○ Course registration follows the regulations of the University',

    '○ 가입: 국내에서 외국인등록을 마치면':
        '○ Enrollment: once alien registration is completed in Korea, students are automatically enrolled as local '
        'subscribers of the National Health Insurance\n'
        '○ Premiums: subscribers must pay the premium every month; arrears restrict visa extension and other '
        'residence permits\n'
        '○ Maintenance: international students must keep both National Health Insurance and private insurance '
        'throughout their enrollment',

    '1. 지원자는 두 개 이상의 모집 단위에 중복 지원 불가':
        '1. Applicants may not apply to more than one program',

    '2. 원서의 기재 사항은 모두 정확히 입력하여야 하며':
        '2. All entries on the application must be accurate; applicants bear any disadvantage arising from mistaken, '
        'omitted or incorrect entries or from incomplete documents\n'
        '3. Admission is cancelled if the entries differ from the facts or if a matter materially affecting the admission '
        'decision was not disclosed in advance\n'
        '4. If omission, falsehood or fraud in material respects is found in the documents used for the admission '
        'decision, admission is cancelled whether before or after enrolment; if it emerges, even while enrolled, '
        'that admission was obtained by fraudulent means, the admission permit is revoked\n'
        '5. Tuition already paid is not refunded where the admission permit is revoked under item 4\n'
        '6. Admission scores and evaluation details are not disclosed\n'
        '7. Applications and documents submitted are not returned, whether or not the applicant is admitted; '
        'documents needed for a visa application should be prepared separately\n'
        '8. Applicants who fail to submit the required documents by the deadline are excluded from the interview and '
        'rejected; if this is found after admission, the admission is void\n'
        '9. Applicants who submit a certificate of expected graduation must submit the graduation certificate before '
        'enrolment\n'
        '10. Once the application is complete (application fee paid), it cannot be withdrawn and the fee is not refunded\n'
        '11. Admission is cancelled if tuition is not paid within the registration period\n'
        '12. Applicants who wish to give up their place must notify the Office of International Affairs at least seven '
        'days before the first day of the semester\n'
        '13. An applicant admitted to more than one university may enrol at only one; dual enrolment is prohibited, '
        'so enrolment at any other university must be ended before the first day of the semester (2027. 3. 2.) '
        '(violation results in cancellation of admission)\n'
        '14. Where an applicant cannot enter Korea because a visa is refused or a change of status is not permitted, '
        'the admission permit is revoked and tuition is refunded under the regulations of the University\n'
        '15. Freshmen may not take a leave of absence in their first semester\n'
        '16. If a TOPIK level rises after the application is submitted, the score report must be submitted before the '
        'interview for it to count towards the scholarship\n'
        '17. For notarized translation, apostille and consular authentication, enquire at the issuing authority concerned\n'
        '18. Tuition and scholarships follow the regulations of the University\n'
        '19. Contact details must be accurate and reachable throughout the admission period; applicants bear any '
        'disadvantage from not receiving notices because of incorrect details\n'
        '20. Where the Korean text of these guidelines and a translation differ, the Korean text prevails\n'
        '21. Matters not specified in these guidelines follow the University’s academic regulations and the Detailed '
        'Rules on the Admission of International Students; any other matter is determined by the Office of '
        'International Affairs\n'
        '22. Inquiries: 062-670-2855 (Chinese), 2779 (Vietnamese), 2569 (Mongolian and other countries), 2858 (English)',

    '※ 건물 위치 및 내부 VR 보기':
        '※ Building locations and interior VR tour: https://www.gwangju.ac.kr/page/?site=pvr&mn=871\n'
        '※ Address: Office of International Affairs, Gwangju University, 277 Hyodeok-ro, Nam-gu, '
        'Jeonnam-Gwangju Integrated Special City 61743, Republic of Korea',
}

OVER = {}
