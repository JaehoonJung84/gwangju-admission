# -*- coding: utf-8 -*-
"""2027-1 학부 외국인 모집요강 국문 → 영문 대역 사전.

학과·대학 영문명은 기존 공식 영문본
`★광주대학교_외국인 신편입 특별전형 모집요강(영문)_260520.pdf` 의 표기를 따랐다.
새로 생긴 교육상담학과만 대응 표기가 없어 새로 지었다(사용자 확인 필요).
"""

TR = {
    # ── 목차 ─────────────────────────────────────────────────────────
    'C O N T E N T S': 'C O N T E N T S',
    '   전형일정': '   Admission Schedule',
    '   전형방법': '   Admission Procedures',
    '   지원자격': '   Eligibility',
    '   제출서류': '   Required Documents',
    '   모집단위': '   Programs Offered',
    '   비자 신청': '   Visa Application',
    '   장학금': '   Scholarships',
    '   기숙사': '   Dormitory',
    '   기타사항': '   Other Information',
    '   유의사항': '   Important Notes',
    '   캠퍼스 안내': '   Campus Guide',

    # ── 1. 전형일정 ──────────────────────────────────────────────────
    '1. 전형일정': '1. Admission Schedule',
    '구분': 'Category',
    '1차': 'Round 1',
    '2차': 'Round 2',
    '원서접수': 'Application',
    '2026. 11. 11.(수) 10:00': '2026. 11. 11.(Wed) 10:00',
    '∼ 12. 4.(금) 17:00': '∼ 12. 4.(Fri) 17:00',
    '2026. 12. 14.(월) 10:00': '2026. 12. 14.(Mon) 10:00',
    '∼ 12. 31.(목) 17:00': '∼ 12. 31.(Thu) 17:00',
    '서류심사': 'Document Screening',
    '2026. 12. 7.(월) ∼ 12. 10.(목)': '2026. 12. 7.(Mon) ∼ 12. 10.(Thu)',
    '2027. 1. 4.(월) ∼ 1. 7.(목)': '2027. 1. 4.(Mon) ∼ 1. 7.(Thu)',
    '면접심사': 'Interview',
    '2026. 12. 15.(화) ∼ 12. 18.(금)': '2026. 12. 15.(Tue) ∼ 12. 18.(Fri)',
    '2027. 1. 12.(화) ∼ 1. 15.(금)': '2027. 1. 12.(Tue) ∼ 1. 15.(Fri)',
    '합격자 발표': 'Announcement of Results',
    '2026. 12. 23.(수)': '2026. 12. 23.(Wed)',
    '2027. 1. 21.(목)': '2027. 1. 21.(Thu)',
    '등록금 납부': 'Tuition Payment',
    '2027. 1. 4.(월) ∼ 1. 8.(금)': '2027. 1. 4.(Mon) ∼ 1. 8.(Fri)',
    '2027. 1. 25.(월) ∼ 1. 29.(금)': '2027. 1. 25.(Mon) ∼ 1. 29.(Fri)',
    '표준입학허가서 발급': 'Issuance of Standard Admission Letter',
    '등록금 납부 및 제출서류 확인 후 발급':
        'Issued after tuition payment and verification of submitted documents',
    '비자 신청': 'Visa Application',
    '2027. 1월 ∼ 2월': '2027. Jan. ∼ Feb.',
    '개강': 'Start of Semester',
    '2027. 3. 2.(화)': '2027. 3. 2.(Tue)',
    '※ ': '※ ',
    '모든 일정은 한국 시간(KST) 기준':
        'All dates and times are based on Korea Standard Time (KST).',
    '원서 및 제출서류는 접수 마감일까지 본교에 도착한 것에 한하여 접수':
        'Applications and documents are accepted only if they reach the University by the closing date.',
    '아포스티유·영사확인 원본 서류는 합격 후 등록기간까지 제출 가능':
        'Original apostilled or consular-authenticated documents may be submitted by the end of '
        'the registration period after admission.',
    '면접 일시 및 방법은 지원자에게 개별 안내':
        'The date and method of the interview are announced to each applicant individually.',
    '세부일정은 전형 진행 상황에 따라 변동 및 추가모집 가능':
        'Detailed dates may change depending on the progress of the admission process, and '
        'additional recruitment may be conducted.',

    # ── 2. 전형방법 ──────────────────────────────────────────────────
    '2. 전형방법': '2. Admission Procedures',
    '1. 전형절차': '1. Admission Process',
    '⇨': '⇨',
    '입국 · 개강': 'Arrival · Start of Semester',
    '2. 전형요소': '2. Evaluation',
    '평가내용': 'Evaluation Content',
    '배점': 'Points',
    '○ 지원자격 충족 여부, 학력·성적, 어학능력, 재정능력 확인':
        '○ Verification of eligibility, academic records, language proficiency and financial capability',
    '○ 제출서류 진위 확인': '○ Verification of the authenticity of submitted documents',
    '적격 / 부적격': 'Pass / Fail',
    '○ 어학능력, 수학능력, 학업의지, 진로계획, 유학여건 등 종합 평가':
        '○ Comprehensive assessment of language proficiency, academic ability, motivation, '
        'career plan and study conditions',
    '100점': '100 points',
    '선발기준': 'Selection Criteria',
    '○ 서류심사 적격자 중 면접심사 70점 이상 득점자 선발':
        '○ Applicants who pass the document screening and score 70 points or higher in the '
        'interview are selected',
    '※ 전형료: 50,000원': '※ Application fee: KRW 50,000',

    # ── 3. 지원자격 ──────────────────────────────────────────────────
    '3. 지원자격': '3. Eligibility',
    '내용': 'Requirements',
    '공통': 'Common',
    '○ 부모가 모두 외국인인 외국인':
        '○ Foreign nationals whose parents are both foreign nationals',
    '○ 이중 국적자 및 무국적자는 외국인으로 인정하지 않음':
        '○ Dual nationals and stateless persons are not recognized as foreign nationals',
    '신입학': 'Freshman',
    '○ 국내외에서 우리나라 초·중등교육에 상응하는 교육과정을 전부 이수한 졸업자 및 졸업예정자':
        '○ Graduates or prospective graduates who have completed, in Korea or abroad, the entire '
        'course of education equivalent to Korean primary and secondary education',
    '편입학': 'Transfer',
    '3학년': '3rd Year',
    '○ 국내외 4년제 정규대학 2년 이상 수료(예정)자':
        '○ Applicants who have completed (or will complete) at least two years at a 4-year '
        'university in Korea or abroad',
    '○ 국내외 전문대학 졸업(예정)자':
        '○ Graduates (or prospective graduates) of a junior college in Korea or abroad',
    '4학년': '4th Year',
    '○ 국내외 4년제 정규대학 3년 이상 수료(예정)자':
        '○ Applicants who have completed (or will complete) at least three years at a 4-year '
        'university in Korea or abroad',
    '○ 국내외 전문대학 3년제 학과 졸업(예정)자':
        '○ Graduates (or prospective graduates) of a 3-year junior college program in Korea or abroad',
    '언어능력': 'Language Proficiency',
    '한국어트랙': 'Korean Track',
    '(자격 소지자)': '(Qualified Applicants)',
    '○ TOPIK(TOPIK IBT 포함) 3급 이상 또는 동등 자격 취득자 (예체능 2급 이상)':
        '○ TOPIK Level 3 or higher (TOPIK IBT included), or an equivalent qualification '
        '(Level 2 or higher for Arts & Physical Education)',
    '- 동등 자격: 세종학당 중급1 이상 수료, 사회통합프로그램 3단계 이상 이수(사전평가 61점 이상)':
        '- Equivalent qualifications: completion of King Sejong Institute Intermediate 1 or higher, '
        'or completion of KIIP Level 3 or higher (pre-test score of 61 or higher)',
    '○ 본교 한국어 어학연수과정 1년 이상 수료 후 GU-TOPIK 3급 이상 취득자':
        '○ Applicants who have completed at least one year of the University’s Korean language '
        'program and obtained GU-TOPIK Level 3 or higher',
    '(이중언어과정)': '(Bilingual Program)',
    '○ 위 한국어능력 자격을 충족하지 못한 자는 이중언어과정으로 지원 가능':
        '○ Applicants who do not meet the Korean proficiency requirements above may apply for the '
        'Bilingual Program',
    '○ 입학 후 본교가 지정하는 한국어 교육과정을 의무적으로 이수하여야 함':
        '○ After admission, students must complete the Korean language courses designated by the '
        'University',
    '- 1년 이내에 200시간 이상의 한국어 연수를 이수하여야 함. 단, TOPIK 3급 이상 또는 이와 동등한 '
    '자격을 취득한 자는 제외(예체능계열은 2급 이상)':
        '- At least 200 hours of Korean language training must be completed within one year, except '
        'for those who obtain TOPIK Level 3 or higher or an equivalent qualification '
        '(Level 2 or higher for Arts & Physical Education)',
    '영어트랙': 'English Track',
    '○ TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5, TEPS 600(NEW TEPS 330) 또는 이에 상응하는 '
    '국가공인 영어능력평가 성적 소지자':
        '○ Holders of TOEFL PBT 530 · CBT 210 · iBT 80, IELTS 5.5, TEPS 600 (NEW TEPS 330), or an '
        'equivalent score on a nationally accredited English proficiency test',
    '○ 법무부 기준에 따라 영어를 모국어·공용어로 사용하는 국가의 국적자로서 해당 국가에서 '
    '중등·고등교육 이수 시 성적 제출 면제':
        '○ Under the standards of the Ministry of Justice, nationals of countries where English is '
        'the native or official language who completed secondary and higher education in those '
        'countries are exempt from submitting a score',
    '졸업요건': 'Graduation Requirement',
    '○ TOPIK 4급 이상 또는 동등한 자격 취득 (예체능 3급 이상)':
        '○ TOPIK Level 4 or higher, or an equivalent qualification '
        '(Level 3 or higher for Arts & Physical Education)',
    '○ 별도 어학 졸업요건 없음': '○ No separate language requirement for graduation',
    '어학 성적은 원서접수 마감일 기준 유효한 것만 인정':
        'Only language test scores valid as of the application closing date are accepted.',
    '상세한 자격 요건은 본교 규정에 따름':
        'Detailed eligibility requirements follow the regulations of the University.',
    '영어트랙: 모집단위를 별도로 설정하고 입학 시 「영어능력」을 검증하여 선발하는 과정으로, 졸업을 '
    '위하여 이수하여야 하는 학점의 50% 이상이 영어로 진행되는 학사 단위를 의미':
        'English Track: a program with separately designated admission units in which applicants are '
        'selected after verification of their English proficiency, and in which at least 50% of the '
        'credits required for graduation are taught in English.',

    # ── 4. 제출서류 ──────────────────────────────────────────────────
    '4. 제출서류': '4. Required Documents',
    '순번': 'No.',
    '제출서류': 'Document',
    '비고': 'Remarks',
    '입학지원서 (본교 소정양식)': 'Application form (University format)',
    '○ 지원서, 유학계획서, 자기소개서, 유학경비 부담 서약서':
        '○ Application, study plan, self-introduction and financial affidavit',
    '○ 개인정보 수집·이용·제공 동의서':
        '○ Consent to the collection, use and provision of personal information',
    '여권 사본 및 여권용 사진 2매': 'Copy of passport and two passport photos',
    '○ 여권 유효기간 입학일 기준 6개월 이상':
        '○ Passport valid for at least six months from the date of admission',
    '본인 및 부모 신분증 사본': 'Copies of the applicant’s and parents’ ID cards',
    '○ 본국 신분증 또는 시민권': '○ National ID card or certificate of citizenship',
    '가족관계 증명서류': 'Proof of family relationship',
    '○ 중국: 호구부 사본 (호구부 2개 이상인 경우 친족관계증명서 공증본)':
        '○ China: copy of the household register (if there are two or more registers, a notarized '
        'certificate of kinship)',
    '○ 그 밖의 국가: 가족관계증명서 또는 출생증명서(영문)':
        '○ Other countries: certificate of family relationship or birth certificate (in English)',
    '외국인등록증 사본': 'Copy of Alien Registration Card',
    '○ 국내 체류자에 한함': '○ Only for applicants residing in Korea',
    '최종학교 졸업 및 성적증명서':
        'Graduation certificate and transcript from the last school attended',
    '○ (신입학) 고등학교 졸업(예정)증명서 및 전 학년 성적증명서':
        '○ (Freshman) High school graduation (or expected graduation) certificate and transcripts '
        'for all years',
    '○ (편입학) 전문대학 이상 졸업(학위)증명서 및 성적증명서, 4년제 대학 재학자는 수료증명서 포함':
        '○ (Transfer) Graduation (degree) certificate and transcript from a junior college or above; '
        'students enrolled at a 4-year university must also submit a certificate of completion',
    '○ 아포스티유 또는 재외공관 영사인증 원본, 중국은 학력인증보고서':
        '○ Original apostille or consular authentication by a Korean diplomatic mission; for China, '
        'an academic credential verification report',
    '○ 접수 시 사본 제출, 원본은 합격 후 등록기간까지 제출 가능':
        '○ Copies at the time of application; originals may be submitted by the end of the '
        'registration period after admission',
    '○ 베트남은 고등학교 졸업시험 응시 증명서로 졸업(예정)증명서 대체 가능 (졸업 후 졸업증명서 제출)':
        '○ For Vietnam, a certificate of sitting the high school graduation examination may replace '
        'the graduation certificate (the graduation certificate must be submitted after graduation)',
    '재정보증 서류': 'Financial guarantee documents',
    '○ 보증금액 16,000,000원 이상': '○ Guaranteed amount of KRW 16,000,000 or more',
    '○ 본인 또는 부모 명의 은행 잔고증명서 (발급일로부터 30일 이내)':
        '○ Bank balance certificate in the name of the applicant or a parent (issued within the '
        'last 30 days)',
    '부모 재직증명서 및 수입증명서':
        'Parents’ certificate of employment and proof of income',
    '○ 재직증명서: 근무처 발행 (자영업자는 사업자등록증 사본으로 갈음)':
        '○ Certificate of employment: issued by the employer (for the self-employed, a copy of the '
        'business registration certificate)',
    '○ 수입증명서: 최근 1년간 소득금액 확인 서류':
        '○ Proof of income: documents verifying income for the past year',
    '○ 입학 지원일로부터 3개월 이내 발급분':
        '○ Issued within three months before the date of application',
    '어학능력 증명서': 'Language proficiency certificate',
    '○ 해당자에 한함 (TOPIK 성적증명서 등)':
        '○ Only for applicable applicants (e.g. TOPIK score report)',
    '※ 지원하는 차수의 원서접수 시작일 기준으로 유효기간 이내여야 함':
        '※ Must be within its validity period as of the opening date of the round applied for',
    '학력조회 동의서 (본교 양식)': 'Consent to academic records verification (University format)',
    '○ 제출서류 진위 확인용': '○ Used to verify the authenticity of submitted documents',
    '한국어·영어 이외의 언어로 작성된 서류는 한국어 또는 영어 번역본 첨부':
        'Documents written in a language other than Korean or English must be accompanied by a '
        'Korean or English translation.',
    '심사에 필요한 경우 본교가 추가 서류 요구 가능':
        'The University may request additional documents if necessary for the review.',

    # ── 5. 모집단위 ──────────────────────────────────────────────────
    '5. 모집단위': '5. Programs Offered',
    '1. 신입학 (1학년)': '1. Freshman Admission (1st Year)',
    '2. 편입학 (3·4학년)': '2. Transfer Admission (3rd · 4th Year)',
    '대학': 'College',
    '학부(과)': 'Department/Division',
    '계열': 'Field',
    '등록금(원)': 'Tuition (KRW)',
    '이중언어과정': 'Bilingual Program',
    '○': '○',
    # 계열
    '자연': 'Natural Science',
    '인문사회': 'Humanities & Social',
    '예체능': 'Arts & Phys. Edu.',
    '공학': 'Engineering',
    # 단과대학
    '보건복지대학': 'College of Health Welfare',
    '문화산업대학': 'College of Cultural Industry',
    '인문사회과학대학': 'College of Humanities & Social Sciences',
    '공과대학': 'College of Engineering',
    'AI앙트십대학': 'College of Entrepreneurship',
    # 학부(과)
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
    '기계자동차공학과': 'Mechanical & Automotive Engineering',
    '기계자동차공학부': 'Mechanical & Automotive Engineering',
    '글로벌콘텐츠학부': 'Global Contents',
    '이중언어과정은 통번역기 사용 가능':
        'Translation devices may be used in the Bilingual Program.',
    '등록금은 2026학년도 기준이며, 매 학년도 등록금 조정에 따라 변동 가능':
        'Tuition is based on the 2026 academic year and may change with annual tuition adjustments.',

    # ── 6. 비자 신청 ─────────────────────────────────────────────────
    '6. 비자 신청': '6. Visa Application',
    '국내 체류자': 'Applicants in Korea',
    '국외 체류자': 'Applicants Abroad',
    '신청 기관': 'Where to Apply',
    '광주대학교 국제협력처': 'Office of International Affairs, Gwangju University',
    '본국 주재 대한민국 공관': 'Korean embassy or consulate in the home country',
    '신청 내용': 'Type of Application',
    '체류자격 변경 (D-2)': 'Change of status of stay (D-2)',
    '유학(D-2) 사증 발급': 'Issuance of a study (D-2) visa',
    '신청 시기': 'When to Apply',
    '2027. 2월': '2027. Feb.',
    '절차': 'Procedure',
    '○ 국제협력처 체류자격 변경 설명회 참석':
        '○ Attend the briefing on change of status held by the Office of International Affairs',
    '○ 안내에 따라 신청서류 준비': '○ Prepare the application documents as instructed',
    '○ 등록금 납부·원본서류 확인 후 본교가 비자 서류 발송':
        '○ The University sends the visa documents after tuition payment and verification of the '
        'original documents',
    '○ 서류 구비 후 본국 공관에 직접 신청':
        '○ Apply in person at the Korean mission in the home country with the documents',
    '유의사항': 'Notes',
    '○ 체류기간 만료 전·개강 전 신청':
        '○ Apply before the period of stay expires and before the semester begins',
    '○ 변경 절차 완료 시까지 국내 체류': '○ Remain in Korea until the change procedure is complete',
    '○ 입국 직후 외국인 등록': '○ Complete alien registration immediately after arrival',
    '등록금 납부자에 한하여 표준입학허가서 발급':
        'The Standard Admission Letter is issued only to those who have paid tuition.',
    '사증(비자) 발급 지연·거부에 따른 불이익은 지원자 본인 부담':
        'Applicants bear any disadvantage arising from delay in or refusal of visa issuance.',

    # ── 7. 장학금 ────────────────────────────────────────────────────
    '7. 장학금': '7. Scholarships',
    '1. 신·편입생 장학금': '1. Scholarships for Entering Students',
    '트랙': 'Track',
    '어학 성적': 'Language Score',
    '수업료 감면': 'Tuition Reduction',
    '및': 'and',
    'TOPIK 3급': 'TOPIK Level 3',
    'TOPIK 4급': 'TOPIK Level 4',
    'TOPIK 5급': 'TOPIK Level 5',
    'TOPIK 6급': 'TOPIK Level 6',
    '40%': '40%',
    '100%': '100%',
    '50%': '50%',
    'TOEFL PBT 530·CBT 210·iBT 80, IELTS 5.5,': 'TOEFL PBT 530 · CBT 210 · iBT 80, IELTS 5.5,',
    'TEPS 600(NEW TEPS 330)': 'TEPS 600 (NEW TEPS 330)',
    '입학 학기 1회 지급': 'Awarded once, in the semester of admission.',
    '2. 재학생 장학금': '2. Scholarships for Enrolled Students',
    '종류': 'Type',
    '기준': 'Criteria',
    '혜택': 'Benefit',
    '공인언어능력': 'Accredited Language',
    '장학금': 'Proficiency Scholarship',
    '수업료 20% 감면': '20% tuition reduction',
    '수업료 30% 감면': '30% tuition reduction',
    '수업료 40% 감면': '40% tuition reduction',
    'TOPIK 6급 · 영어트랙 어학성적 기준 충족':
        'TOPIK Level 6 · meets the English Track score requirement',
    '수업료 50% 감면': '50% tuition reduction',
    '성적우수장학금': 'Academic Excellence Scholarship',
    '직전 학기 평점평균 4.00 ∼ 4.29': 'Previous semester GPA 4.00 ∼ 4.29',
    '300,000원': 'KRW 300,000',
    '직전 학기 평점평균 4.30 이상': 'Previous semester GPA 4.30 or higher',
    '500,000원': 'KRW 500,000',
    '성적우수장학금은 4.5 만점 기준, 학년 구분 없이 직전 학기 성적으로 지급':
        'The Academic Excellence Scholarship is based on a 4.5 scale and is awarded on the previous '
        'semester’s grades regardless of year level.',
    '어학 성적은 등록금 고지서 발급일 기준 유효기간 이내의 것만 인정':
        'Only language scores within their validity period as of the date the tuition invoice is '
        'issued are accepted.',
    '선발기준 및 금액은 매 학년도 시행계획과 본교 「장학금 지급에 관한 시행세칙」에 따라 변동 가능':
        'Selection criteria and amounts may change according to each year’s implementation plan '
        'and the University’s Detailed Rules on the Payment of Scholarships.',

    # ── 8. 기숙사 ────────────────────────────────────────────────────
    '8. 기숙사': '8. Dormitory',
    '1. 안내': '1. General Information',
    '○ 신입생은 기숙사 또는 외부 거주 중 선택 가능':
        '○ Entering students may choose between the dormitory and off-campus housing',
    '○ 입사 신청 시 「결핵검사확인서」 제출':
        '○ A tuberculosis test certificate must be submitted when applying',
    '○ 신·편입생은 1일 1식 이상 의무식 (최소 1식 식비 반드시 납부)':
        '○ Entering students must take at least one meal a day (the fee for at least one meal is '
        'compulsory)',
    '○ 입사자는 사생수칙(기숙사 홈페이지 게시)을 준수하여야 하며, 위반 시 벌점 부과 및 강제퇴사 가능':
        '○ Residents must observe the dormitory rules posted on the dormitory website; violations '
        'may result in penalty points and forced withdrawal',
    '2. 기간 및 비용': '2. Period and Fees',
    '○ 기간: 2027년 2월말 입국 시 ∼ 2027. 8. 27.(금)':
        '○ Period: from arrival in late February 2027 to 2027. 8. 27.(Fri)',
    '관리비 (180일 기준)': 'Accommodation fee (180 days)',
    '식비 (130일 기준, 1식 4,500원)': 'Meal fee (130 days, KRW 4,500 per meal)',
    '2인실': 'Double room',
    '1,306,800원': 'KRW 1,306,800',
    '1일 1식': '1 meal a day',
    '585,000원': 'KRW 585,000',
    '3인실': 'Triple room',
    '1,119,600원': 'KRW 1,119,600',
    '1일 2식': '2 meals a day',
    '1,170,000원': 'KRW 1,170,000',
    '4인실': 'Quad room',
    '889,200원': 'KRW 889,200',
    '1일 3식': '3 meals a day',
    '1,755,000원': 'KRW 1,755,000',
    '2인실·3인실은 잔여 객실 범위 내에서만 신청 가능하며, 초과 시 신청 불가':
        'Double and triple rooms may be applied for only within the number of rooms available.',
    '최소 1일 1식 식비(585,000원) 의무 납부, 식당 현장 구매 시 1식 5,500원':
        'The fee for at least one meal a day (KRW 585,000) is compulsory; meals bought on site at '
        'the cafeteria cost KRW 5,500 each.',
    '식당은 주말 및 명절 연휴 미운영':
        'The cafeteria is closed on weekends and during national holidays.',
    '식수 변경은 개강 초 식수변경기간에만 가능하며, 이후 변경·환불 불가 (일정 추후 공지)':
        'The number of meals may be changed only during the meal-change period at the start of the '
        'semester; no change or refund is possible afterwards (dates to be announced).',
    '기간은 학사일정에 따라 변경 가능하며, 이에 따라 관리비·식비도 변동 가능':
        'The period may change with the academic calendar, and the accommodation and meal fees may '
        'change accordingly.',
    '3. 입사절차': '3. Move-in Procedure',
    '기숙사 선택': 'Choose dormitory',
    '입사 신청': 'Apply',
    '기숙사비 납부': 'Pay fees',
    '호실 발표': 'Room assignment',
    '입사': 'Move in',
    '○ 입사 신청: 기숙사 홈페이지 → 신·편입생 입사신청(생년월일 로그인) → 신청서 작성(결핵검사확인서 첨부)':
        '○ Application: dormitory website → application for entering students (log in with date of '
        'birth) → complete the form (attach the tuberculosis test certificate)',
    '○ 국외 체류 유학생은 국제협력처를 통하여 입사신청서를 작성·제출':
        '○ Students residing abroad submit the application through the Office of International Affairs',
    '○ 1지망 인실 우선 배정, 미배정 시 잔여 객실에 한하여 2·3·4지망 순으로 배정':
        '○ First-choice room types are assigned first; if unassigned, rooms are allocated in the '
        'order of second, third and fourth choice within the rooms available',
    '○ 기숙사비 납부: 홈페이지에서 고지서 출력(우편 미발송) 후 광주은행 또는 가상계좌 입금':
        '○ Payment: print the invoice from the website (it is not mailed) and pay at Gwangju Bank or '
        'to the virtual account',
    '○ 납부기간 내 미납 시 불합격 처리, 납부 후 인실 변경 불가':
        '○ Failure to pay within the payment period results in rejection; the room type cannot be '
        'changed after payment',
    '○ 호실 발표 및 세부 일정은 기숙사 홈페이지 공지 및 합격자 개별 안내':
        '○ Room assignments and detailed dates are announced on the dormitory website and '
        'individually to successful applicants',
    '4. 생활 안내': '4. Living Information',
    '○ 준비물: 신분증, 침구류, 세면도구, 개인 생활용품':
        '○ What to bring: ID card, bedding, toiletries and personal items',
    '○ 반입 금지: TV, 전열 취사도구, 인화성 물질, 애완동물, 도박성 오락기구, 과도 등':
        '○ Prohibited: televisions, electric cooking appliances, flammable materials, pets, gambling '
        'devices, knives and the like',
    '○ 생활수칙: 건물 내 흡연(전자담배 포함) 엄금, 22시 이후 정숙, 01:00 ∼ 05:00 출입 전면 폐쇄':
        '○ House rules: smoking (including e-cigarettes) is strictly prohibited inside the building; '
        'quiet hours after 22:00; entry and exit closed from 01:00 to 05:00',
    '○ 중도퇴사: 퇴사 3일 전까지 포털시스템에서 퇴사신청서 작성 후 사감 확인':
        '○ Early withdrawal: submit a withdrawal form on the portal system at least three days in '
        'advance and obtain the supervisor’s confirmation',
    '○ 환불: 관리비는 기숙사 규정에 따라 차등 정산, 식비는 잔여일수 중 5일을 제외한 일수 기준 환불':
        '○ Refunds: the accommodation fee is settled on a sliding scale under the dormitory rules; '
        'the meal fee is refunded for the remaining days less five days',
    '○ 중도퇴사자는 해당 학기 및 계절학기 재입사 불가':
        '○ Students who withdraw early may not move in again during the same semester or the '
        'seasonal session',
    '○ 공동생활 에티켓 준수 (생활관 홈페이지 참조)':
        '○ Observe the etiquette of communal living (see the dormitory website)',
    '○ 객실 내 누전차단기 멀티콘센트 사용, 문어발식 콘센트 연결 금지':
        '○ Use power strips with earth-leakage breakers in the rooms; daisy-chaining outlets is '
        'prohibited',
    '○ 유학생 조리실 사용 후 정리정돈 및 위생·청결 유지':
        '○ Keep the international students’ kitchen tidy, hygienic and clean after use',
    '○ 문의: 기숙사 행정실 062-670-2803 / https://dorm.gwangju.ac.kr':
        '○ Inquiries: Dormitory Office +82-62-670-2803 / https://dorm.gwangju.ac.kr',

    # ── 9. 기타사항 ──────────────────────────────────────────────────
    '9. 기타사항': '9. Other Information',
    '1. 학사 일정': '1. Academic Calendar',
    '○ 개강일: 2027. 3. 2.(화)': '○ First day of class: 2027. 3. 2.(Tue)',
    '○ 신·편입생 오리엔테이션: 2027년 2월 말 (세부 일정 개별 안내)':
        '○ Orientation for entering students: late February 2027 (details announced individually)',
    '2. 수강신청': '2. Course Registration',
    '○ 상담: 오리엔테이션 이후 소속 학부(과) 상담을 거쳐 수강신청':
        '○ Advising: register for courses after consulting your department following the orientation',
    '○ 방법: 광주대학교 포털시스템에서 온라인 신청':
        '○ Method: online through the Gwangju University portal system',
    '○ 수강신청에 관련한 내용은 본교 학칙에 따름':
        '○ Course registration follows the regulations of the University',
    '3. 국민건강보험': '3. National Health Insurance',
    '○ 가입: 국내에서 외국인등록을 마치면 국민건강보험 지역가입자로 자동 가입':
        '○ Enrollment: once alien registration is completed in Korea, students are automatically '
        'enrolled as local subscribers of the National Health Insurance',
    '○ 보험료: 가입자는 매월 보험료를 납부하여야 하며, 체납 시 비자 연장 등 각종 체류허가가 제한됨':
        '○ Premiums: subscribers must pay the premium every month; arrears restrict visa extension '
        'and other residence permits',
    '○ 자격 유지: 유학생은 재학 기간 동안 국민건강보험과 민간보험 자격을 모두 유지하여야 함':
        '○ Maintenance: international students must keep both National Health Insurance and private '
        'insurance throughout their enrollment',

    # ── 10. 유의사항 ─────────────────────────────────────────────────
    '10. 유의사항': '10. Important Notes',
    '1. 지원자는 두 개 이상의 모집단위에 중복 지원 불가':
        '1. Applicants may not apply to more than one program.',
    '2. 원서의 기재 사항은 모두 정확히 입력하여야 하며, 입력 착오·누락·오기 및 제출서류 미비로 '
    '발생하는 불이익은 지원자 본인 부담':
        '2. All entries on the application must be accurate; applicants bear any disadvantage '
        'arising from mistaken, omitted or incorrect entries or from incomplete documents.',
    '3. 기재 사항이 사실과 다르거나 입학사정에 중대한 영향을 미칠 사항을 사전에 고지하지 않은 경우 '
    '합격 취소':
        '3. Admission is cancelled if the entries differ from the facts or if a matter materially '
        'affecting the admission decision was not disclosed in advance.',
    '4. 입학사정에 사용된 전형자료에 주요 사항의 누락·허위·부정이 확인될 경우 입학 전후를 불문하고 '
    '합격 및 입학 취소, 재학 중이라도 부정한 방법으로 입학한 사실이 드러나면 입학 허가 취소':
        '4. If omission, falsehood or fraud in material respects is found in the documents used for '
        'the admission decision, admission is cancelled whether before or after enrolment; if it '
        'emerges, even while enrolled, that admission was obtained by fraudulent means, the '
        'admission permit is revoked.',
    '5. 제4호에 따라 입학 허가가 취소된 경우 납부한 등록금은 반환하지 않음':
        '5. Tuition already paid is not refunded where the admission permit is revoked under item 4.',
    '6. 입학성적 및 평가 내용은 공개하지 않음':
        '6. Admission scores and evaluation details are not disclosed.',
    '7. 제출한 원서 및 서류는 합격 여부와 관계없이 반환하지 않으므로, 비자 신청 등에 필요한 서류는 '
    '별도 준비 필요':
        '7. Applications and documents submitted are not returned, whether or not the applicant is '
        'admitted; documents needed for a visa application should be prepared separately.',
    '8. 필수 제출서류를 기한 내 제출하지 않을 경우 면접 대상에서 제외하고 불합격 처리하며, 합격 후 '
    '확인된 경우 합격(입학) 무효 처리':
        '8. Applicants who fail to submit the required documents by the deadline are excluded from '
        'the interview and rejected; if this is found after admission, the admission is void.',
    '9. 졸업예정증명서 제출자는 입학 전까지 졸업증명서를 제출하여야 함':
        '9. Applicants who submit a certificate of expected graduation must submit the graduation '
        'certificate before enrolment.',
    '10. 원서접수가 완료(전형료 결제 및 입금)된 후에는 지원을 취소할 수 없으며 전형료는 반환하지 않음':
        '10. Once the application is complete (application fee paid), it cannot be withdrawn and the '
        'fee is not refunded.',
    '11. 등록기간 내 등록금 미납 시 합격 취소':
        '11. Admission is cancelled if tuition is not paid within the registration period.',
    '12. 등록을 포기하려는 경우 학기 개시일 7일 전까지 국제협력처에 등록 포기 의사를 통보':
        '12. Applicants who wish to give up their place must notify the Office of International '
        'Affairs at least seven days before the first day of the semester.',
    '13. 복수 대학 합격 시 1개 대학에만 등록하여야 하며, 이중학적은 금지되므로 학기 개시일'
    '(2027. 3. 2.) 이전에 타 대학 학적을 정리하여야 함 (위반 시 입학 취소)':
        '13. An applicant admitted to more than one university may enrol at only one; dual '
        'enrolment is prohibited, so enrolment at any other university must be ended before the '
        'first day of the semester (2027. 3. 2.). Violation results in cancellation of admission.',
    '14. 사증(비자) 발급 거부 또는 체류자격 변경 불허로 입국하지 못한 경우 입학 허가 취소, 등록금은 '
    '본교 규정에 따라 반환':
        '14. Where an applicant cannot enter Korea because a visa is refused or a change of status '
        'is not permitted, the admission permit is revoked and tuition is refunded under the '
        'regulations of the University.',
    '15. 신입생은 입학 후 첫 학기 휴학 불가':
        '15. Freshmen may not take a leave of absence in their first semester.',
    '16. 원서접수 후 TOPIK 급수 상승 시 면접심사 전까지 성적증명서를 제출하여야 장학금 산정에 반영':
        '16. If a TOPIK level rises after the application is submitted, the score report must be '
        'submitted before the interview for it to count towards the scholarship.',
    '17. 번역공증·아포스티유·영사확인 등 인증 절차는 해당 발급기관에 문의':
        '17. For notarized translation, apostille and consular authentication, enquire at the '
        'issuing authority concerned.',
    '18. 등록금 및 장학금은 본교 규정에 따름':
        '18. Tuition and scholarships follow the regulations of the University.',
    '19. 연락처는 전형 기간 중 연락 가능한 것으로 정확히 기재하여야 하며, 연락처 오류로 인한 안내 '
    '미수신의 불이익은 지원자 본인 부담':
        '19. Contact details must be accurate and reachable throughout the admission period; '
        'applicants bear any disadvantage from not receiving notices because of incorrect details.',
    '20. 본 요강의 국문본과 다국어 번역본의 내용이 서로 다를 경우 국문본을 우선 적용':
        '20. Where the Korean text of these guidelines and a translation differ, the Korean text '
        'prevails.',
    '21. 본 요강에 명시되지 않은 사항은 본교 학사 관련 규정 및 「외국인 유학생 입학 시행세칙」에 '
    '따르며, 그 밖의 사항은 국제협력처가 정함':
        '21. Matters not specified in these guidelines follow the University’s academic '
        'regulations and the Detailed Rules on the Admission of International Students; any other '
        'matter is determined by the Office of International Affairs.',
    '22. 문의: 062-670-2855(중국), 2779(베트남), 2569(몽골 및 기타 국가), 2858(영어)':
        '22. Inquiries: 062-670-2855 (Chinese), 2779 (Vietnamese), 2569 (Mongolian and other '
        'countries), 2858 (English)',

    # ── 11. 캠퍼스 안내 ──────────────────────────────────────────────
    '11. 캠퍼스 안내': '11. Campus Guide',
    '건물 위치 및 내부 VR 보기: https://www.gwangju.ac.kr/page/?site=pvr&mn=871':
        'Building locations and interior VR tour: https://www.gwangju.ac.kr/page/?site=pvr&mn=871',
    '주소: (61743) 전남광주통합특별시 남구 효덕로 277 광주대학교 국제협력처':
        'Address: Office of International Affairs, Gwangju University, 277 Hyodeok-ro, Nam-gu, '
        'Jeonnam-Gwangju Integrated Special City 61743, Republic of Korea',
    '문의처': 'Contact',
    '언어 · 국가': 'Language · Country',
    '전화번호': 'Telephone',
    '중국': 'Chinese',
    '베트남': 'Vietnamese',
    '영어': 'English',
    '몽골 및 기타 국가': 'Mongolian & Other Countries',
}
