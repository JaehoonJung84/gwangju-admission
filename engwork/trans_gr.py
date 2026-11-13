# -*- coding: utf-8 -*-
"""(한글)대학원 2027학년도 모집요강 → 영문.

용어는 「2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_영문본.pdf」를 따른다.
"""

TRANS = {
    # ---------- 머리말·꼬리말 ----------
    '2027학년도 전기 외국인 대학원 신·편입생 특별전형 모집요강':
        '2027 Spring Special Admission for International Graduate Students',
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
    'ⅩⅠ. 주임교수 안내': 'ⅩⅠ. Department Chairs',
    'ⅩⅡ. 캠퍼스 안내': 'ⅩⅡ. Campus Guide',

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
    '주임교수 안내': 'Department Chairs',
    '캠퍼스 안내': 'Campus Guide',
    '1. 전형절차': '1. Admission Process',
    '2. 전형요소': '2. Evaluation',
    '1. 일반대학원 석사과정': '1. Graduate School - Master’s Programs',
    '2. 일반대학원 박사과정': '2. Graduate School - Doctoral Programs',
    '3. 보건상담정책대학원 석사과정':
        '3. Graduate School of Health, Counseling & Policy - Master’s Programs',
    '1. 어학능력 장학금': '1. Language Proficiency Scholarship',
    '2. 그 밖의 교내·외 장학금': '2. Other Internal and External Scholarships',
    '1. 안내': '1. General Information',
    '2. 기간 및 비용': '2. Period and Fees',
    '3. 입사절차': '3. Move-in Procedure',
    '4. 생활 안내': '4. Living Information',
    '1. 학사 일정': '1. Academic Calendar',
    '2. 학위 취득': '2. Degree Requirements',
    '3. 수강신청': '3. Course Registration',
    '4. 국민건강보험': '4. National Health Insurance',
    '문의처': 'Contact',

    # ---------- p4 전형일정·전형방법 ----------
    '구분': 'Category',
    '구 분': 'Category',
    '계 열': 'Field',
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
    '2026. 11. 16.(월) 10:00 ∼ 12. 4.(금) 17:00':
        '2026. 11. 16.(Mon) 10:00 ∼\n12. 4.(Fri) 17:00',
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
    '○ 지원자격 충족 여부, 전적 대학(원) 학력·성적, 어학능력, 재정능력 확인 ○ 제출서류 진위 확인':
        '○ Verification of eligibility, previous academic records, language proficiency and finances\n'
        '○ Verification of the authenticity of submitted documents',
    '○ 전공 수학능력, 어학능력, 연구계획, 학업의지, 유학여건 등 종합 평가':
        '○ Comprehensive assessment of aptitude for the major, language proficiency, research plan, motivation and study conditions',
    '○ 서류심사 적격자 중 면접심사 70점 이상 득점자를 고득점자 순으로 선발 ○ 동점자는 전적 대학(원) 성적 환산점수, 동일계 전공자 순으로 선발':
        '○ Applicants who pass the document screening and score 70 or higher in the interview are selected in order of score\n'
        '○ Ties are broken by the converted grade from the previous institution, then by a major in the same field',
    '※ 최소 수강인원에 미달하는 모집단위는 선발하지 않을 수 있음':
        '※ Departments that do not reach the minimum class size may not admit students',
    '※ 전형료: 50,000원(입금계좌: 광주은행 1127-020-252652 광주대학교)':
        '※ Application fee: KRW 50,000 (Gwangju Bank 1127-020-252652, Gwangju University)',

    # ---------- p5 지원자격 ----------
    '내용': 'Requirements',
    '공통': 'Common',
    '신입학': 'Freshman',
    '편입학': 'Transfer',
    '석사': 'Master’s',
    '박사': 'Doctoral',
    '간호학과': 'Nursing',
    '언어능력': 'Language Proficiency',
    '졸업요건': 'Graduation Requirement',
    '한국어트랙': 'Korean Track',
    '이중언어과정': 'Bilingual Program',
    '한국어트랙 (자격 소지자)': 'Korean Track\n(Qualified Applicants)',
    '한국어트랙 (이중언어과정)': 'Korean Track\n(Bilingual Program)',
    '○ 부모가 모두 외국인인 외국인 ○ 이중 국적자 및 무국적자는 외국인으로 인정하지 않음':
        '○ Foreign nationals whose parents are both foreign nationals\n'
        '○ Dual nationals and stateless persons are not recognized as foreign nationals',
    '○ 국내·외 대학에서 학사학위를 취득한 자 (2027년 2월 학사학위 취득예정자 포함) ○ 기타 법령에 의하여 위와 동등 이상의 학력이 있다고 인정된 자':
        '○ Holders of a bachelor’s degree from a university in Korea or abroad (including those expecting to receive it in February 2027)\n'
        '○ Others recognized by law as having an equivalent or higher academic background',
    '○ 국내·외 대학에서 석사학위를 취득한 자 (2027년 2월 석사학위 취득예정자 포함) ○ 기타 법령에 의하여 위와 동등 이상의 학력이 있다고 인정된 자':
        '○ Holders of a master’s degree from a university in Korea or abroad (including those expecting to receive it in February 2027)\n'
        '○ Others recognized by law as having an equivalent or higher academic background',
    '○ 동일계열 학과 전공자로서 국내·외 대학원에서 석사과정 2학기 이상 이수한 자':
        '○ Applicants majoring in the same field who have completed at least two semesters of a master’s program at a graduate school in Korea or abroad',
    '○ 동일계열 학과 전공자로서 국내·외 대학원에서 박사과정 2학기 이상 이수한 자':
        '○ Applicants majoring in the same field who have completed at least two semesters of a doctoral program at a graduate school in Korea or abroad',
    '○ 간호사 면허(RN) 소지자에 한하여 지원 가능하며, 면접심사에서 학업계획서를 심의함 ○ 박사과정 지원자가 동일계열이 아닌 경우 재학 중 간호학 필수과목 2개(6학점)를 이수하여야 함':
        '○ Only holders of a registered nurse (RN) licence may apply; the study plan is reviewed at the interview\n'
        '○ Doctoral applicants from another field must complete two required nursing courses (6 credits) while enrolled',
    '○ TOPIK 4급 이상 또는 GU-TOPIK 4급 이상 취득':
        '○ TOPIK Level 4 or higher, or GU-TOPIK Level 4 or higher',

    # ---------- p6 제출서류 ----------
    '순번': 'No.',
    '비고': 'Remarks',
    '입학지원서 (본교 소정양식)': 'Application form\n(University format)',
    '여권 사본 및 여권용 사진 2매': 'Copy of passport and\ntwo passport photos',
    '본인 및 부모 신분증 사본': 'Copies of the applicant’s\nand parents’ ID cards',
    '가족관계 증명서류': 'Proof of family relationship',
    '외국인등록증 사본': 'Copy of Alien\nRegistration Card',
    '전적 대학(원) 졸업(예정)증명서': 'Previous university (graduate\nschool) diploma',
    '전적 대학(원) 성적증명서': 'Transcript from the previous\nuniversity (graduate school)',
    '석사학위 논문 요약본': 'Summary of the\nmaster’s thesis',
    '재정보증 서류': 'Financial guarantee\ndocuments',
    '부모 재직증명서 및 수입증명서': 'Parents’ certificate of\nemployment and proof of\nincome',
    '공인 어학성적표': 'Official language\nscore report',
    '○ 지원서, 학업·연구계획서, 자기소개서 ○ 개인정보 수집·이용·제공 동의서, 학력조회 동의서':
        '○ Application, study and research plan, self-introduction\n'
        '○ Consent to the use of personal information and to academic records verification',
    '○ 여권 유효기간 입학일 기준 6개월 이상':
        '○ Passport valid for at least six months from the date of admission',
    '○ 본국 신분증 또는 시민권': '○ National ID card or certificate of citizenship',
    '○ 국내 체류자에 한함': '○ Only for applicants residing in Korea',
    '○ 박사과정 지원자 중 해당자에 한함 (A4 3매 이내)':
        '○ Only for applicable doctoral applicants (within three A4 pages)',
    '○ 한국어트랙(자격 소지자): TOPIK 성적증명서 1부 ※ 원서접수 시작일 기준으로 유효기간 이내여야 함':
        '○ Korean Track (qualified applicants): one TOPIK score report\n'
        '※ Must be within its validity period as of the opening date of applications',

    # ---------- p7·p8·p9 모집단위 ----------
    '대학': 'College',
    '모집단위': 'Department',
    '학과': 'Department',
    '학위수여 가능전공': 'Majors Available',
    '등록금(원)': 'Tuition (KRW)',
    '인문사회': 'Hum.·Social',
    '인문 사회': 'Hum.·Social',
    '공학': 'Engineering',
    '예체능': 'Arts & P.E.',
    '자연과학': 'Natural Science',
    '자연 과학': 'Natural Science',
    '단독과정': 'Single Dept.',
    '협동과정': 'Inter-\ndisciplinary',
    '경영학과': 'Business Administration',
    '회계세무학과': 'Accounting & Tax',
    '물류유통경영학과': 'Logistics & Distribution Management',
    '호텔관광경영학과': 'Hotel & Tourism Management',
    '호텔외식조리학과': 'Hotel & Food Service Culinary Arts',
    '경찰학과': 'Police Science',
    '유아교육학과': 'Early Childhood Education',
    '문헌정보학과': 'Library & Information Sciences',
    '도시재생·부동산학과': 'Urban Regeneration & Real Estate',
    '컴퓨터공학과': 'Computer Engineering',
    '정보통신공학과': 'Information & Communication Eng.',
    '토목공학과': 'Civil Engineering',
    '건축공학과': 'Architectural Engineering',
    '건축학과': 'Architecture',
    '미래융합기술공학과': 'Future Convergence Technology Eng.',
    '방재안전공학과': 'Disaster Prevention & Safety Eng.',
    '디자인학과': 'Design',
    '사진학과': 'Photography',
    '뷰티미용학과': 'Beauty Science',
    '문화콘텐츠학과': 'Cultural Contents',
    '식품영양학과': 'Food Science & Nutrition',
    '의상학과': 'Fashion Design',
    '평생교육학과': 'Lifelong Education',
    '창업학과': 'Entrepreneurship',
    '한국어문화교육콘텐츠학과': 'Korean Language·Culture Education Contents',
    '경찰·사법·행정학과': 'Police·Judicial·Public Administration',
    '광·정보통신공학과': 'Photonics·Info. Communication Eng.',
    '청소년교육·상담학과': 'Youth Education & Counseling',
    '임상상담심리학과': 'Clinical & Counseling Psychology',
    '보건의료관리학과': 'Health Care Management',
    '한국어교육과': 'Korean Language Education',
    '법학과': 'Law',
    '임상언어치료학과': 'Clinical Speech-Language Therapy',
    '작업치료학과': 'Occupational Therapy',
    '스포츠지도학과': 'Sports Coaching',
    '경찰·사법·행정학과 (경찰)': 'Police·Judicial·Public Administration (Police)',
    '경찰·사법·행정학과 (법)': 'Police·Judicial·Public Administration (Law)',
    '광·정보통신공학과 (광통신)': 'Photonics·Info. Communication Eng. (Photonics)',
    '광·정보통신공학과 (정보통신)': 'Photonics·Info. Communication Eng. (ICT)',
    # 학위수여 가능전공
    '경영': 'Business Administration',
    '회계, 세무': 'Accounting, Taxation',
    '물류유통경영': 'Logistics & Distribution Mgmt.',
    '호텔관광경영': 'Hotel & Tourism Mgmt.',
    '호텔외식조리': 'Hotel & Food Service Culinary Arts',
    '경찰': 'Police Science',
    '유아교육': 'Early Childhood Education',
    '문헌정보': 'Library & Information Science',
    '도시재생, 부동산': 'Urban Regeneration, Real Estate',
    '컴퓨터': 'Computer Engineering',
    '정보통신': 'Information & Communication',
    '토목': 'Civil Engineering',
    '건축공': 'Architectural Engineering',
    '건축': 'Architecture',
    '에너지융합, 기계자동차융합': 'Energy Convergence, Mechanical & Automotive Convergence',
    '방재안전공학': 'Disaster Prevention & Safety Eng.',
    '시각영상, 산업, 주얼리, 인테리어': 'Visual & Media, Industrial, Jewelry, Interior',
    '사진': 'Photography',
    '헤어미용, 피부미용 메이크업, 네일미용': 'Hair Care, Skin Care, Makeup, Nail Art',
    '문화콘텐츠': 'Cultural Contents',
    '식품영양, 커피산업융합': 'Food & Nutrition, Coffee Industry Convergence',
    '의상': 'Fashion',
    '평생교육': 'Lifelong Education',
    '창업학': 'Entrepreneurship',
    '한국어문화교육, 문화교육콘텐츠': 'Korean Language·Culture Education, Culture Education Contents',
    '간호': 'Nursing',
    '경찰, 법, 행정': 'Police, Law, Public Administration',
    '광통신, 정보통신': 'Photonics, Information & Communication',
    '교육학': 'Education',
    '임상심리, 상담심리': 'Clinical Psychology, Counseling Psychology',
    '보건의료관리, 의료경영 한국어교육': 'Health Care Mgmt., Medical Management',
    '창업학, 프랜차이즈': 'Entrepreneurship, Franchising',
    '법학': 'Law',
    '임상언어치료': 'Clinical Speech-Language Therapy',
    '작업치료': 'Occupational Therapy',
    '스포츠윤리': 'Sports Ethics',

    # ---------- p9 비자 ----------
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
    '○ 등록금 납부·원본서류 확인 후 본교가 비자 서류 발송 ○ 서류 구비 후 본국 공관에 직접 신':
        '○ The University sends the visa documents after tuition payment and document verification\n'
        '○ Apply in person at the Korean mission in the home country',
    '○ 체류기간 만료 전·개강 전 신청 ○ 변경 절차 완료 시까지 국내 체류':
        '○ Apply before the stay expires and the semester begins\n'
        '○ Remain in Korea until the change procedure is complete',
    '○ 입국 직후 외국인 등록': '○ Complete alien registration immediately after arrival',
    '※ 등록금 납부자에 한하여 표준입학허가서 발급 ※ 사증(비자) 발급 지연·거부에 따른 불이익은 지원자 본인 부담':
        '※ The Standard Admission Letter is issued only to those who have paid tuition\n'
        '※ Applicants bear any disadvantage from delayed or refused visa issuance',

    # ---------- p10 장학금 ----------
    '장학명': 'Scholarship',
    '선발기준': 'Selection Criteria',
    '장학내용': 'Benefit',
    'TOPIK 장학': 'TOPIK Scholarship',
    'TOPIK 4급 이상 소지자': 'TOPIK Level 4 or higher',
    'TOPIK 3급 소지자': 'TOPIK Level 3',
    '수업료 50% 감면': '50% tuition reduction',
    '수업료 40% 감면': '40% tuition reduction',
    '교내': 'Internal',
    '교외': 'External',
    '호심특별장학': 'Hosim Special\nScholarship',
    '호심장학': 'Hosim Scholarship',
    '특별장학': 'Special Scholarship',
    '교직원복지장학': 'Faculty & Staff\nWelfare Scholarship',
    '대학원동창회장학': 'Graduate Alumni\nAssociation Scholarship',
    '산학협동재단장학': 'Industry-Academic\nCooperation Scholarship',
    '기타 교외장학': 'Other external\nscholarships',
    '대학발전에 기여한 자': 'Those who have contributed to the development of the University',
    '본교 학사·석사 학위 취득자': 'Holders of a bachelor’s or master’s degree from this University',
    '계약학과 등': 'Contract-based departments, etc.',
    '본 대학교와 학교법인에 재직하면서 사학연금에 가입 중인 교직원 및 임직원':
        'Faculty and staff of the University and its foundation who are enrolled in the private school pension scheme',
    '지정/봉사자, 기타': 'Designated / volunteers, other',
    '특별추천서에 지정': 'As specified in the special recommendation',
    '입학금 면제 수업료 50%': 'Admission fee waived\nTuition 50%',
    '수업료 지정': 'Tuition as designated',
    '입학금 면제 석사: 수업료 70% 박사: 수업료 50%':
        'Admission fee waived\nMaster’s: tuition 70%\nDoctoral: tuition 50%',
    '지정/봉사액': 'As designated / for service',
    '※ 이중언어과정 입학자는 TOPIK 성적 취득 시 이후 학기부터 적용':
        '※ For students admitted to the Bilingual Program, the scholarship applies from the semester in which the TOPIK score is obtained',
    '※ 어학 성적은 등록금 고지서 발급일 기준 유효기간 이내의 것만 인정':
        '※ Only language scores valid as of the tuition invoice date are accepted',
    '※ 교내 장학은 대상자에게 유리한 단일 항목을 적용하며, 총 4학기(편입생은 전적학교 인정학기 포함) 동안 적용':
        '※ Only the single internal scholarship most favourable to the student is applied, for a total of four semesters '
        '(for transfer students, including semesters credited from the previous institution)',

    # ---------- p11 기숙사 ----------
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

    # ---------- p12 기타사항 ----------
    '○ 개강일: 2027. 3. 2.(화) ○ 신·편입생 오리엔테이션: 2027년 2월 말 (세부 일정 개별 안내)':
        '○ First day of class: 2027. 3. 2.(Tue)\n'
        '○ Orientation for entering students: late February 2027 (details announced individually)',
    '○ 수업연한: 석사학위과정 2년(24학점), 박사학위과정 2년(36학점) ○ 석사학위 취득 방법: 「석사학위논문작성」과 「학위청구논문대체제도」 중 선택':
        '○ Duration: Master’s 2 years (24 credits), Doctoral 2 years (36 credits)\n'
        '○ Master’s degree: choose between writing a thesis and the thesis-substitute coursework scheme',
    '학위청구논문대체제도 (논문작성 대신 논문대체 교과목 수강)':
        'Thesis-substitute coursework (courses taken instead of writing a thesis)',
    '일 반 대 학 원': 'Graduate School',
    '보 건 상 담 정 책 대 학 원': 'Graduate School of Health, Counseling & Policy',
    '9학점 수강': '9 credits',
    '6학점 수강': '6 credits',
    '○ 졸업 어학요건: TOPIK 4급 이상 또는 동등한 자격 취득':
        '○ Graduation language requirement: TOPIK Level 4 or higher, or an equivalent qualification',
    '○ 상담: 오리엔테이션 이후 소속 학과 주임교수 상담을 거쳐 수강신청 ○ 방법: 광주대학교 포털시스템에서 온라인 신청':
        '○ Advising: register for courses after consulting the chair of your department following the orientation\n'
        '○ Method: online through the Gwangju University portal system',

    # ---------- p13 유의사항 ----------
    '1. 지원자는 두 개 이상의 모집단위에 중복 지원 불가':
        '1. Applicants may not apply to more than one program',
    '2. 원서의 기재 사항은 모두 정확히 입력하여야 하며, 입력 착오·누락·오기 및 제출서류 미비로 발생하는 불이익은 지원자 본인 부담':
        '2. All entries on the application must be accurate; applicants bear any disadvantage arising from mistaken, omitted or incorrect entries or from incomplete documents',
    '3. 기재 사항이 사실과 다르거나 입학사정에 중대한 영향을 미칠 사항을 사전에 고지하지 않은 경우 합격 취소':
        '3. Admission is cancelled if the entries differ from the facts or if a matter materially affecting the admission decision was not disclosed in advance',
    '4. 입학사정에 사용된 전형자료에 주요 사항의 누락·허위·부정이 확인될 경우 입학 전후를 불문하고 합격 및 입학 취소, 재학 중이라도 부정한 방법으로 입학한 사실이 드러나면 입학 허가 취소':
        '4. If omission, falsehood or fraud in material respects is found in the documents used for the admission decision, admission is cancelled whether before or after enrolment; if it emerges, even while enrolled, that admission was obtained by fraudulent means, the admission permit is revoked',
    '5. 제4호에 따라 입학 허가가 취소된 경우 납부한 등록금은 본교 등록금 반환 기준에 따라 반환':
        '5. Where the admission permit is revoked under item 4, tuition already paid is refunded under the University’s tuition refund rules',
    '6. 입학성적 및 평가 내용은 공개하지 않음':
        '6. Admission scores and evaluation details are not disclosed',
    '7. 제출한 원서 및 서류는 합격 여부와 관계없이 반환하지 않으므로, 비자 신청 등에 필요한 서류는 별도 준비 필요':
        '7. Applications and documents submitted are not returned, whether or not the applicant is admitted; documents needed for a visa application should be prepared separately',
    '8. 필수 제출서류를 기한 내 제출하지 않을 경우 면접 대상에서 제외하고 불합격 처리하며, 합격 후 확인된 경우 합격(입학) 무효 처리':
        '8. Applicants who fail to submit the required documents by the deadline are excluded from the interview and rejected; if this is found after admission, the admission is void',
    '9. 졸업예정증명서 제출자는 입학 전까지 졸업(학위)증명서를 제출하여야 함':
        '9. Applicants who submit a certificate of expected graduation must submit the graduation (degree) certificate before enrolment',
    '10. 원서접수가 완료(전형료 결제 및 입금)된 후에는 지원을 취소할 수 없으며 전형료는 반환하지 않음':
        '10. Once the application is complete (application fee paid), it cannot be withdrawn and the fee is not refunded',
    '11. 등록기간 내 등록금 미납 시 합격 취소하며, 입학 첫 학기는 분할·카드 납부 불가':
        '11. Admission is cancelled if tuition is not paid within the registration period; instalment and card payment are not available in the first semester',
    '12. 등록을 포기하려는 경우 학기 개시일 7일 전까지 국제협력처에 등록 포기 의사를 통보':
        '12. Applicants who wish to give up their place must notify the Office of International Affairs at least seven days before the first day of the semester',
    '13. 사증(비자) 발급 거부 또는 체류자격 변경 불허로 입국하지 못한 경우 입학 허가 취소, 등록금은 본교 규정에 따라 반환':
        '13. Where an applicant cannot enter Korea because a visa is refused or a change of status is not permitted, the admission permit is revoked and tuition is refunded under the regulations of the University',
    '14. 신입생은 입학 후 첫 학기 휴학 불가':
        '14. New students may not take a leave of absence in their first semester',
    '15. 원서접수 후 TOPIK 급수 상승 시 면접심사 전까지 성적증명서를 제출하여야 장학금 산정에 반영':
        '15. If a TOPIK level rises after the application is submitted, the score report must be submitted before the interview for it to count towards the scholarship',
    '16. 번역공증·아포스티유·영사확인 등 인증 절차는 해당 발급기관에 문의':
        '16. For notarized translation, apostille and consular authentication, enquire at the issuing authority concerned',
    '17. 수집된 개인정보자료는 입학전형 외 다른 목적으로는 사용하지 않으며, 일정 기간이 지나면 모두 삭제함 (다만 합격·등록한 자의 개인정보는 본 대학원의 학사업무에 활용)':
        '17. Personal data collected is used only for the admission process and is deleted after a set period (the data of admitted and enrolled students is used for the academic affairs of this graduate school)',
    '18. 연락처는 전형 기간 중 연락 가능한 것으로 정확히 기재하여야 하며, 연락처 오류로 인한 안내 미수신의 불이익은 지원자 본인 부담':
        '18. Contact details must be accurate and reachable throughout the admission period; applicants bear any disadvantage from not receiving notices because of incorrect details',
    '19. 본 요강의 국문본과 다국어 번역본의 내용이 서로 다를 경우 국문본을 우선 적용':
        '19. Where the Korean text of these guidelines and a translation differ, the Korean text prevails',
    '20. 본 요강에 명시되지 않은 사항은 대학원위원회에서 정한 규정에 따르며, 입학 후의 제반 사항은 본 대학원 규정에 따름':
        '20. Matters not specified in these guidelines follow the rules set by the Graduate School Committee; all matters after admission follow the regulations of this graduate school',
    '21. 문의: 062-670-2855(중국), 2779(베트남), 2569(몽골 및 기타 국가), 2858(영어)':
        '21. Inquiries: 062-670-2855 (Chinese), 2779 (Vietnamese), 2569 (Mongolian and other countries), 2858 (English)',

    # ---------- p14·p15 주임교수 ----------
    '주임교수': 'Department Chair',
    '연구실': 'Office',
    '남아영': 'Nam A-yeong', '조유근': 'Cho Yu-geun', '김현종': 'Kim Hyeon-jong',
    '김정훈': 'Kim Jeong-hun', '김헌철': 'Kim Heon-cheol', '정보성': 'Jung Bo-seong',
    '김호현': 'Kim Ho-hyeon', '노지윤': 'Noh Ji-yun', '김항집': 'Kim Hang-jip',
    '이익훈': 'Lee Ik-hun', '김광현': 'Kim Gwang-hyeon', '강경오': 'Kang Gyeong-o',
    '양원영': 'Yang Won-yeong', '문한솔': 'Moon Han-sol', '최재혁': 'Choi Jae-hyeok',
    '송창영': 'Song Chang-yeong', '주치수': 'Joo Chi-su', '윤태준': 'Yoon Tae-jun',
    '박혜선': 'Park Hye-seon', '조대연': 'Cho Dae-yeon', '김 승': 'Kim Seung',
    '허승연': 'Heo Seung-yeon', '박진영': 'Park Jin-yeong', '윤인철': 'Yoon In-cheol',
    '진재섭': 'Jin Jae-seop', '문덕희': 'Moon Deok-hui', '천성권': 'Cheon Seong-gwon',
    '박창규': 'Park Chang-gyu', '이응택': 'Lee Eung-taek', '박주영': 'Park Ju-yeong',
    '양유정': 'Yang Yu-jeong', '남윤경': 'Nam Yun-gyeong', '손은남': 'Son Eun-nam',
    '허 명': 'Heo Myeong', '이지환': 'Lee Ji-hwan',
    '※ 주임교수 및 연락처는 2027학년도 전기 대학원 모집요강 기준이며, 변동될 수 있음':
        '※ Department chairs and contact numbers are those in the 2027 Spring graduate admission guidelines and are subject to change',

    # ---------- p16 캠퍼스 안내 ----------
    '언어 · 국가': 'Language · Country',
    '전화번호': 'Telephone',
    '중국': 'Chinese',
    '베트남': 'Vietnamese',
    '영어': 'English',
    '몽골 및 기타 국가': 'Mongolian & Other Countries',
    '※ 국제협력처 홈페이지: https://ie.gwangju.ac.kr':
        '※ Office of International Affairs: https://ie.gwangju.ac.kr',
}

PREFIX = {
    '1. 지원자는 두 개 이상의 모집단위에 중복 지원 불가':
        '1. Applicants may not apply to more than one program\n'
        '2. All entries on the application must be accurate; applicants bear any disadvantage arising from mistaken, '
        'omitted or incorrect entries or from incomplete documents\n'
        '3. Admission is cancelled if the entries differ from the facts or if a matter materially affecting the admission '
        'decision was not disclosed in advance\n'
        '4. If omission, falsehood or fraud in material respects is found in the documents used for the admission '
        'decision, admission is cancelled whether before or after enrolment; if it emerges, even while enrolled, '
        'that admission was obtained by fraudulent means, the admission permit is revoked\n'
        '5. Where the admission permit is revoked under item 4, tuition already paid is refunded under the University’s '
        'tuition refund rules\n'
        '6. Admission scores and evaluation details are not disclosed\n'
        '7. Applications and documents submitted are not returned, whether or not the applicant is admitted; '
        'documents needed for a visa application should be prepared separately\n'
        '8. Applicants who fail to submit the required documents by the deadline are excluded from the interview and '
        'rejected; if this is found after admission, the admission is void\n'
        '9. Applicants who submit a certificate of expected graduation must submit the graduation (degree) certificate '
        'before enrolment\n'
        '10. Once the application is complete (application fee paid), it cannot be withdrawn and the fee is not refunded\n'
        '11. Admission is cancelled if tuition is not paid within the registration period; instalment and card payment '
        'are not available in the first semester\n'
        '12. Applicants who wish to give up their place must notify the Office of International Affairs at least seven '
        'days before the first day of the semester\n'
        '13. Where an applicant cannot enter Korea because a visa is refused or a change of status is not permitted, '
        'the admission permit is revoked and tuition is refunded under the regulations of the University\n'
        '14. New students may not take a leave of absence in their first semester\n'
        '15. If a TOPIK level rises after the application is submitted, the score report must be submitted before the '
        'interview for it to count towards the scholarship\n'
        '16. For notarized translation, apostille and consular authentication, enquire at the issuing authority concerned\n'
        '17. Personal data collected is used only for the admission process and is deleted after a set period (the data '
        'of admitted and enrolled students is used for the academic affairs of this graduate school)\n'
        '18. Contact details must be accurate and reachable throughout the admission period; applicants bear any '
        'disadvantage from not receiving notices because of incorrect details\n'
        '19. Where the Korean text of these guidelines and a translation differ, the Korean text prevails\n'
        '20. Matters not specified in these guidelines follow the rules set by the Graduate School Committee; '
        'all matters after admission follow the regulations of this graduate school\n'
        '21. Inquiries: 062-670-2855 (Chinese), 2779 (Vietnamese), 2569 (Mongolian and other countries), 2858 (English)',

    '※ 모든 일정은 한국 시간(KST) 기준':
        '※ All dates and times are based on Korea Standard Time (KST)\n'
        '※ Applications and documents must reach the University by the closing date\n'
        '※ Apostilled or consular-authenticated originals may be submitted by the end of registration\n'
        '※ The interview date and method are announced to each applicant individually\n'
        '※ Dates may change as the process proceeds, and additional recruitment is possible',

    '○ TOPIK(TOPIK IBT 포함) 3급 이상':
        '○ TOPIK Level 3 or higher (TOPIK IBT included), or an equivalent qualification (Level 2 or higher for Arts & P.E.)\n'
        ' - Equivalent: King Sejong Institute Intermediate 1 or higher, or KIIP Level 3 or higher (pre-test score of 61 or higher)',

    '○ 위 한국어능력 자격을 충족하지 못한 자는':
        '○ Applicants who do not meet the Korean proficiency requirements above may apply for the Bilingual Program\n'
        '○ After admission, students must complete the Korean language courses designated by the University\n'
        ' - At least 200 hours of Korean training within one year, except for those who obtain TOPIK Level 3 or higher '
        'or an equivalent qualification (Level 2 or higher for Arts & P.E.)',

    '※ 어학 성적은 원서접수 마감일 기준 유효한 것만 인정':
        '※ Only language test scores valid as of the application closing date are accepted\n'
        '※ Applicants may apply regardless of their previous major but must complete the prerequisite courses set by the department\n'
        '※ Detailed eligibility requirements follow the graduate school regulations of the University',

    '○ 중국: 호구부 사본':
        '○ China: copy of the household register (if two or more, a notarized certificate of kinship)\n'
        '○ Single-parent families: notarized death or divorce certificate\n'
        '○ Other countries: certificate of family relationship or birth certificate (in English)',

    '○ (석사 지원) 대학 졸업(예정)증명서':
        '○ (Master’s applicants) University graduation (or expected graduation) certificate\n'
        '○ (Doctoral applicants) University graduation certificate and master’s degree (or expected) certificate\n'
        '○ (Transfer) Additional certificate of enrolment, completion or withdrawal from the master’s or doctoral program\n'
        '○ China: an academic credential verification report (issued by CHSI) is also required\n'
        '○ Other countries: original apostille or consular authentication by a Korean mission\n'
        '○ Copies at application; originals by the end of the registration period',

    '○ (석사 지원) 대학 전 학년 성적증명서':
        '○ (Master’s applicants) University transcripts for all years\n'
        '○ (Doctoral applicants) One transcript each for the university and the master’s program\n'
        '○ For foreign universities, a notarized Korean or English translation is required',

    '○ 국내 체류자: 국내은행 잔고증명서':
        '○ Applicants in Korea: Korean bank balance certificate of KRW 16,000,000 or more\n'
        '○ Applicants abroad: foreign bank certificate of a time deposit held for six months or more\n'
        '○ Issued within the last 30 days',

    '○ 재직증명서: 근무처 발행':
        '○ Employment: issued by the employer (self-employed: business registration copy)\n'
        '○ Income: documents verifying income for the past year\n'
        '○ A Korean or English translation must accompany the original',

    '※ 모든 제출서류는 발급일 기준으로 3개월이':
        '※ All documents must have been issued within the last three months, and originals must be presented when copies are submitted\n'
        '※ Documents written in a language other than Korean or English must be accompanied by a Korean or English translation\n'
        '※ The University may request additional documents if necessary for the review',

    '※ 수업연한: 석사학위과정 2년(24학점)':
        '※ Duration: Master’s 2 years (24 credits), Doctoral 2 years (36 credits)\n'
        '※ Mode of study: full-time, day or evening classes depending on the department\n'
        '※ Tuition is based on the 2026 academic year and may change with annual tuition adjustments',

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

    '○ 가입: 국내에서 외국인등록을 마치면':
        '○ Enrollment: once alien registration is completed in Korea, students are automatically enrolled as local '
        'subscribers of the National Health Insurance\n'
        '○ Premiums: subscribers must pay the premium every month; arrears restrict visa extension and other residence permits\n'
        '○ Maintenance: international students must keep both National Health Insurance and private insurance '
        'throughout their enrollment',

    '※ 건물 위치 및 내부 VR 보기':
        '※ Building locations and interior VR tour: https://www.gwangju.ac.kr/page/?site=pvr&mn=871\n'
        '※ Address: Office of International Affairs (Hosim Hall 6F), Gwangju University, 277 Hyodeok-ro, Nam-gu, '
        'Jeonnam-Gwangju Integrated Special City 61743, Republic of Korea',
}

# '모집단위' 는 절 제목(05 탭)일 때와 표 머리글일 때 뜻이 다르다.
OVER = {
    (7, 2): 'Programs Offered',
    (8, 1): 'Programs Offered',
    # 두 줄이 서로 다른 행의 칸인데 한 칸으로 묶였다 — 줄을 고정해 제자리에 찍는다.
    (9, 23): 'Health Care Mgmt.,\nMedical Mgmt.\nKorean Lang. Edu.',
}
