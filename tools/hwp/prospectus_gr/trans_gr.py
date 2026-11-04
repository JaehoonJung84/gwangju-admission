# -*- coding: utf-8 -*-
"""2027 전기 대학원 외국인 모집요강 국문 → 영문 대역 사전.

학부판(`C:\\projects\\tools\\hwp\\prospectus_en\\trans.py` + `short.py`)을 바탕으로 하고
대학원에만 있는 글월을 더한다. 학부와 겹치는 학과명은 공식 영문본 표기를 그대로 쓰고,
대학원에만 있는 학과·전공은 새로 지었다(사용자 확인 필요).
주임교수 성명은 관용 성씨 표기 + 국어의 로마자 표기법(이름)으로 옮겼다.
"""
import sys

sys.path.insert(0, r'C:\projects\tools\hwp\prospectus_en')
from trans import TR as _TR                                       # noqa: E402
from short import SHORT as _SHORT                                 # noqa: E402

TR = dict(_TR)
TR.update(_SHORT)

GR = {
    # ── 목차·절 제목 ────────────────────────────────────────────────
    '   주임교수 안내': '   Department Chairs',
    '11. 주임교수 안내': '11. Department Chairs',
    '12. 캠퍼스 안내': '12. Campus Guide',

    # ── 1. 전형일정 ─────────────────────────────────────────────────
    '2026. 11. 16.(월) 10:00': '2026. 11. 16.(Mon) 10:00',

    # ── 2. 전형방법 ─────────────────────────────────────────────────
    '○ 지원자격 충족 여부, 전적 대학(원) 학력·성적, 어학능력, 재정능력 확인':
        '○ Verification of eligibility, academic records from the previous university (or graduate '
        'school), language proficiency and financial capability',
    '○ 전공 수학능력, 어학능력, 연구계획, 학업의지, 유학여건 등 종합 평가':
        '○ Comprehensive assessment of aptitude for the major, language proficiency, research plan, '
        'motivation and study conditions',
    '○ 서류심사 적격자 중 면접심사 70점 이상 득점자를 고득점자 순으로 선발':
        '○ Applicants who pass the document screening and score 70 points or higher in the interview '
        'are selected in order of score',
    '○ 동점자는 전적 대학(원) 성적 환산점수, 동일계 전공자 순으로 선발':
        '○ Ties are broken by the converted grade from the previous institution, then by a major in '
        'the same field',
    '최소 수강인원에 미달하는 모집단위는 선발하지 않을 수 있음':
        'Departments that do not reach the minimum class size may not admit students.',

    # ── 3. 지원자격 ─────────────────────────────────────────────────
    '석사': "Master's",
    '박사': 'Doctoral',
    '○ 국내·외 대학에서 학사학위를 취득한 자 (2027년 2월 학사학위 취득예정자 포함)':
        "○ Holders of a bachelor's degree from a university in Korea or abroad (including those "
        "expecting to receive it in February 2027)",
    '○ 기타 법령에 의하여 위와 동등 이상의 학력이 있다고 인정된 자':
        '○ Others recognized by law as having an equivalent or higher academic background',
    '○ 국내·외 대학에서 석사학위를 취득한 자 (2027년 2월 석사학위 취득예정자 포함)':
        "○ Holders of a master's degree from a university in Korea or abroad (including those "
        "expecting to receive it in February 2027)",
    '○ 동일계열 학과 전공자로서 국내·외 대학원에서 석사과정 2학기 이상 이수한 자':
        "○ Applicants majoring in the same field who have completed at least two semesters of a "
        "master's program at a graduate school in Korea or abroad",
    '○ 동일계열 학과 전공자로서 국내·외 대학원에서 박사과정 2학기 이상 이수한 자':
        '○ Applicants majoring in the same field who have completed at least two semesters of a '
        'doctoral program at a graduate school in Korea or abroad',
    '○ TOPIK 4급 이상 또는 GU-TOPIK 4급 이상 취득':
        '○ TOPIK Level 4 or higher, or GU-TOPIK Level 4 or higher',
    '출신학과에 관계없이 지원이 가능하나, 지원학과에서 정한 선수과목을 이수하여야 함':
        'Applicants may apply regardless of their previous major but must complete the prerequisite '
        'courses set by the department.',
    '상세한 자격 요건은 본교 대학원 학칙 및 관련 규정에 따름':
        'Detailed eligibility requirements follow the graduate school regulations of the University.',

    # ── 4. 제출서류 ─────────────────────────────────────────────────
    '○ 지원서, 학업·연구계획서, 자기소개서':
        '○ Application, study and research plan, self-introduction',
    '○ 개인정보 수집·이용·제공 동의서, 학력조회 동의서':
        '○ Consent to the use of personal information and to academic records verification',
    '○ 중국: 호구부 사본 (2개 이상 소지 시 친족관계증명서 공증본)':
        '○ China: copy of the household register (if two or more, a notarized certificate of kinship)',
    '○ 한부모 가정은 사망증명서·이혼증명서 등 공증본 제출':
        '○ Single-parent families: notarized death or divorce certificate',
    '전적 대학(원)': 'Previous university',
    '졸업(예정)증명서': '(graduate school) diploma',
    '○ (석사 지원) 대학 졸업(예정)증명서':
        "○ (Master's applicants) University graduation (or expected graduation) certificate",
    '○ (박사 지원) 대학 졸업증명서 및 석사 학위(예정)증명서':
        "○ (Doctoral applicants) University graduation certificate and master's degree (or expected) "
        "certificate",
    '○ (편입학) 석사·박사과정 재학(수료·제적)증명서 추가 제출':
        "○ (Transfer) Additional certificate of enrolment, completion or withdrawal from the "
        "master's or doctoral program",
    '○ 중국: 학력인증보고서(CHSI 발급) 별도 제출 필수':
        '○ China: an academic credential verification report (issued by CHSI) is also required',
    '○ 중국 외 국가: 아포스티유 또는 재외공관 영사확인 원본':
        '○ Other countries: original apostille or consular authentication by a Korean mission',
    '○ 접수 시 사본 제출, 원본은 등록기간까지 제출 가능':
        '○ Copies at application; originals by the end of the registration period',
    '전적 대학(원) 성적증명서': 'Transcript from the previous university (graduate school)',
    '○ (석사 지원) 대학 전 학년 성적증명서':
        "○ (Master's applicants) University transcripts for all years",
    '○ (박사 지원) 대학 및 석사과정 성적증명서 각 1부':
        "○ (Doctoral applicants) One transcript each for the university and the master's program",
    '○ 외국대학은 한국어 또는 영어 번역 공증본 제출 필수':
        '○ For foreign universities, a notarized Korean or English translation is required',
    '석사학위 논문 요약본': "Summary of the master's thesis",
    '○ 박사과정 지원자 중 해당자에 한함 (A4 3매 이내)':
        '○ Only for applicable doctoral applicants (within three A4 pages)',
    '○ 국내 체류자: 국내은행 잔고증명서 16,000,000원 이상':
        '○ Applicants in Korea: Korean bank balance certificate of KRW 16,000,000 or more',
    '○ 국외 체류자: 외국은행 6개월 이상 정기예금 잔고증명서':
        '○ Applicants abroad: foreign bank certificate of a time deposit held for six months or more',
    '○ 발급일로부터 30일 이내 발급분': '○ Issued within the last 30 days',
    '○ 재직증명서: 근무처 발행 (자영업자는 사업자등록증 사본)':
        '○ Employment: issued by the employer (self-employed: business registration copy)',
    '○ 원본에 한국어 또는 영어 번역본 첨부':
        '○ A Korean or English translation must accompany the original',
    '공인 어학성적표': 'Official language score report',
    '○ 한국어트랙(자격 소지자): TOPIK 성적증명서 1부':
        '○ Korean Track (qualified applicants): one TOPIK score report',
    '※ 원서접수 시작일 기준으로 유효기간 이내여야 함':
        '※ Must be within its validity period as of the opening date of applications',
    '모든 제출서류는 발급일 기준으로 3개월이 지나지 않아야 하며, 사본 제출 시 원본을 제시하여야 함':
        'All documents must have been issued within the last three months, and originals must be '
        'presented when copies are submitted.',
    '심사에 필요한 경우 본교가 추가 서류를 요구할 수 있음':
        'The University may request additional documents if necessary for the review.',

    # ── 5. 모집단위 ─────────────────────────────────────────────────
    '1. 일반대학원 석사과정': "1. Graduate School — Master's Programs",
    '2. 일반대학원 박사과정': '2. Graduate School — Doctoral Programs',
    '3. 보건상담정책대학원 석사과정':
        "3. Graduate School of Health, Counseling & Policy — Master's Programs",
    '계 열': 'Field',
    '구 분': 'Category',
    '모집단위': 'Department',
    '학위수여 가능전공': 'Majors Available',
    '이중언어': 'Bilingual',
    '과정': 'Program',
    '자연과학': 'Natural Science',
    '단독과정': 'Single Dept.',
    '협동과정': 'Interdisciplinary',

    # 학과 (학부 공식 표기와 겹치는 것은 그대로)
    '물류유통경영학과': 'Logistics & Distribution Management',
    '호텔관광경영학과': 'Hotel & Tourism Management',
    '호텔외식조리학과': 'Hotel & Food Service Culinary Arts',
    '경찰학과': 'Police Science',
    '유아교육학과': 'Early Childhood Education',
    '문예창작학과': 'Creative Writing',
    '정보통신공학과': 'Information & Communication Eng.',
    '건축학과': 'Architecture',
    '미래융합기술공학과': 'Future Convergence Technology Eng.',
    '방재안전공학과': 'Disaster Prevention & Safety Eng.',
    '디자인학과': 'Design',
    '사진학과': 'Photography',
    '문화콘텐츠학과': 'Cultural Contents',
    '의상학과': 'Fashion Design',
    '평생교육학과': 'Lifelong Education',
    '창업학과': 'Entrepreneurship',
    '한국어문화교육콘텐츠학과': 'Korean Language·Culture Education Contents',
    '생명보건학과': 'Life & Health Sciences',
    '간호학과': 'Nursing',
    '경찰·사법·행정학과': 'Police·Judicial·Public Administration',
    '광·정보통신공학과': 'Photonics·Information Communication Eng.',
    '청소년교육·상담학과': 'Youth Education & Counseling',
    '임상상담심리학과': 'Clinical & Counseling Psychology',
    '보건의료관리학과': 'Health Care Management',
    '한국어교육과': 'Korean Language Education',
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
    '문예창작': 'Creative Writing',
    '컴퓨터': 'Computer Engineering',
    '정보통신': 'Information & Communication',
    '토목': 'Civil Engineering',
    '건축공': 'Architectural Engineering',
    '건축': 'Architecture',
    '에너지융합, 기계자동차융합': 'Energy Convergence, Mechanical & Automotive Convergence',
    '방재안전공학': 'Disaster Prevention & Safety Eng.',
    '시각영상, 산업,': 'Visual & Media, Industrial,',
    '주얼리, 인테리어': 'Jewelry, Interior',
    '사진': 'Photography',
    '헤어미용, 피부미용': 'Hair Care, Skin Care,',
    '메이크업, 네일미용': 'Makeup, Nail Art',
    '문화콘텐츠': 'Cultural Contents',
    '식품영양, 커피산업융합': 'Food & Nutrition, Coffee Industry Convergence',
    '의상': 'Fashion',
    '평생교육': 'Lifelong Education',
    '창업학': 'Entrepreneurship',
    '한국어문화교육, 문화교육콘텐츠':
        'Korean Language·Culture Education, Culture Education Contents',
    '식품영양, 작업치료': 'Food & Nutrition, Occupational Therapy',
    '간호': 'Nursing',
    '경찰, 법, 행정': 'Police, Law, Public Administration',
    '광통신, 정보통신': 'Photonics, Information & Communication',
    '교육학': 'Education',
    '임상심리, 상담심리': 'Clinical Psychology, Counseling Psychology',
    '보건의료관리, 의료경영': 'Health Care Mgmt., Medical Management',
    '한국어교육': 'Korean Language Education',
    '창업학, 프랜차이즈': 'Entrepreneurship, Franchising',
    '임상언어치료': 'Clinical Speech-Language Therapy',
    '작업치료': 'Occupational Therapy',
    '스포츠윤리': 'Sports Ethics',

    '수업연한: 석사학위과정 2년(24학점), 박사학위과정 2년(36학점)':
        "Duration: Master's 2 years (24 credits), Doctoral 2 years (36 credits)",
    '수업방법: 학과별 주·야간 전일제 운영':
        'Mode of study: full-time, day or evening classes depending on the department',

    # ── 7. 장학금 ───────────────────────────────────────────────────
    '교내 장학은 대상자에게 유리한 단일 항목을 적용하며, 총 4학기(편입생은 전적학교 인정학기 포함) 동안 적용':
        'Only the single internal scholarship most favourable to the student is applied, for a total '
        'of four semesters (for transfer students, including semesters credited from the previous '
        'institution).',
    '1. 어학능력 장학금': '1. Language Proficiency Scholarship',
    '장학명': 'Scholarship',
    '장학내용': 'Benefit',
    'TOPIK 장학': 'TOPIK Scholarship',
    'TOPIK 4급 이상 소지자': 'TOPIK Level 4 or higher',
    'TOPIK 3급 소지자': 'TOPIK Level 3',
    '이중언어과정 입학자는 TOPIK 성적 취득 시 해당 학기부터 적용':
        'For students admitted to the Bilingual Program, the scholarship applies from the semester '
        'in which the TOPIK score is obtained.',
    '2. 그 밖의 교내·외 장학금': '2. Other Internal and External Scholarships',
    '교내': 'Internal',
    '교외': 'External',
    '호심특별장학': 'Hosim Special Scholarship',
    '대학발전에 기여한 자': 'Those who have contributed to the development of the University',
    '특별추천서에 지정': 'As specified in the special recommendation',
    '호심장학': 'Hosim Scholarship',
    '본교 학사·석사 학위 취득자': "Holders of a bachelor's or master's degree from this University",
    '입학금 면제': 'Admission fee waived',
    '수업료 50%': 'Tuition 50%',
    '매원장학': 'Maewon Scholarship',
    '본교 외 대학 학사·석사 학위 취득자':
        "Holders of a bachelor's or master's degree from another university",
    '수업료 30%': 'Tuition 30%',
    '백인장학': 'Baekin Scholarship',
    '산업체, 공공기관, 교육기관 재직자':
        'Employees of companies, public institutions or educational institutions',
    '특별장학': 'Special Scholarship',
    '계약학과 등': 'Contract-based departments, etc.',
    '수업료 지정': 'Tuition as designated',
    '교직원복지장학': 'Faculty & Staff Welfare Scholarship',
    '본 대학교와 학교법인에 재직하면서': 'Faculty and staff of the University and its foundation',
    '사학연금에 가입 중인 교직원 및 임직원': 'who are enrolled in the private school pension scheme',
    '석사: 수업료 70%': "Master's: tuition 70%",
    '박사: 수업료 50%': 'Doctoral: tuition 50%',
    '대학원동창회장학': 'Graduate Alumni Association Scholarship',
    '지정/봉사자, 기타': 'Designated / volunteers, other',
    '지정/봉사액': 'As designated / for service',
    '산학협동재단장학': 'Industry-Academic Cooperation Foundation Scholarship',
    '기타 교외장학': 'Other external scholarships',

    # ── 8. 기숙사 ───────────────────────────────────────────────────
    '○ 신·편입생은 기숙사 또는 외부 거주 중 선택 가능':
        '○ Entering students may choose between the dormitory and off-campus housing',

    # ── 9. 기타사항 ─────────────────────────────────────────────────
    '2. 학위 취득': '2. Degree Requirements',
    '○ 수업연한: 석사학위과정 2년(24학점), 박사학위과정 2년(36학점)':
        "○ Duration: Master's 2 years (24 credits), Doctoral 2 years (36 credits)",
    '○ 석사학위 취득 방법: 「석사학위논문작성」과 「학위청구논문대체제도」 중 선택':
        "○ Master's degree: choose between writing a thesis and the thesis-substitute coursework "
        "scheme",
    '학위청구논문대체제도': 'Thesis-substitute coursework',
    '(논문작성 대신 논문대체 교과목 수강)': '(courses taken instead of writing a thesis)',
    '일 반 대 학 원': 'Graduate School',
    '9학점 수강': '9 credits',
    '보 건 상 담 정 책 대 학 원': 'Graduate School of Health, Counseling & Policy',
    '6학점 수강': '6 credits',
    '○ 졸업 어학요건: TOPIK 4급 이상 또는 동등한 자격 취득':
        '○ Graduation language requirement: TOPIK Level 4 or higher, or an equivalent qualification',
    '3. 수강신청': '3. Course Registration',
    '○ 상담: 오리엔테이션 이후 소속 학과 주임교수 상담을 거쳐 수강신청':
        '○ Advising: register for courses after consulting the chair of your department following '
        'the orientation',
    '4. 국민건강보험': '4. National Health Insurance',

    # ── 10. 유의사항 (대학원판에서 달라진 항목) ─────────────────────
    '5. 제4호에 따라 입학 허가가 취소된 경우 납부한 등록금은 본교 등록금 반환 기준에 따라 반환':
        '5. Where the admission permit is revoked under item 4, tuition already paid is refunded '
        'under the University\u2019s tuition refund rules.',
    '9. 졸업예정증명서 제출자는 입학 전까지 졸업(학위)증명서를 제출하여야 함':
        '9. Applicants who submit a certificate of expected graduation must submit the graduation '
        '(degree) certificate before enrolment.',
    '11. 등록기간 내 등록금 미납 시 합격 취소하며, 입학 첫 학기는 분할·카드 납부 불가':
        '11. Admission is cancelled if tuition is not paid within the registration period; '
        'instalment and card payment are not available in the first semester.',
    '13. 사증(비자) 발급 거부 또는 체류자격 변경 불허로 입국하지 못한 경우 입학 허가 취소, 등록금은 '
    '본교 규정에 따라 반환':
        '13. Where an applicant cannot enter Korea because a visa is refused or a change of status '
        'is not permitted, the admission permit is revoked and tuition is refunded under the '
        'regulations of the University.',
    '14. 신입생은 입학 후 첫 학기 휴학 불가':
        '14. New students may not take a leave of absence in their first semester.',
    '15. 원서접수 후 TOPIK 급수 상승 시 면접심사 전까지 성적증명서를 제출하여야 장학금 산정에 반영':
        '15. If a TOPIK level rises after the application is submitted, the score report must be '
        'submitted before the interview for it to count towards the scholarship.',
    '16. 번역공증·아포스티유·영사확인 등 인증 절차는 해당 발급기관에 문의':
        '16. For notarized translation, apostille and consular authentication, enquire at the '
        'issuing authority concerned.',
    '17. 수집된 개인정보자료는 입학전형 외 다른 목적으로는 사용하지 않으며, 일정 기간이 지나면 모두 '
    '삭제함 (다만 합격·등록한 자의 개인정보는 본 대학원의 학사업무에 활용)':
        '17. Personal data collected is used only for the admission process and is deleted after a '
        'set period (the data of admitted and enrolled students is used for the academic affairs of '
        'this graduate school).',
    '18. 연락처는 전형 기간 중 연락 가능한 것으로 정확히 기재하여야 하며, 연락처 오류로 인한 안내 '
    '미수신의 불이익은 지원자 본인 부담':
        '18. Contact details must be accurate and reachable throughout the admission period; '
        'applicants bear any disadvantage from not receiving notices because of incorrect details.',
    '19. 본 요강의 국문본과 다국어 번역본의 내용이 서로 다를 경우 국문본을 우선 적용':
        '19. Where the Korean text of these guidelines and a translation differ, the Korean text '
        'prevails.',
    '20. 본 요강에 명시되지 않은 사항은 대학원위원회에서 정한 규정에 따르며, 입학 후의 제반 사항은 '
    '본 대학원 규정에 따름':
        '20. Matters not specified in these guidelines follow the rules set by the Graduate School '
        'Committee; all matters after admission follow the regulations of this graduate school.',
    '21. 문의: 062-670-2855(중국), 2779(베트남), 2569(몽골 및 기타 국가), 2858(영어)':
        '21. Inquiries: 062-670-2855 (Chinese), 2779 (Vietnamese), 2569 (Mongolian and other '
        'countries), 2858 (English)',

    # ── 11. 주임교수 안내 ───────────────────────────────────────────
    '학과': 'Department',
    '주임교수': 'Department Chair',
    '연구실': 'Office',
    '주임교수 및 연락처는 2027학년도 전기 대학원 모집요강 기준이며, 변동될 수 있음':
        'Department chairs and contact numbers are those in the 2027 Spring graduate admission '
        'guidelines and are subject to change.',

    # 성명 — 관용 성씨 표기 + 국어의 로마자 표기법(이름)
    '남아영': 'Nam A-yeong',
    '조유근': 'Cho Yu-geun',
    '김현종': 'Kim Hyeon-jong',
    '김정훈': 'Kim Jeong-hun',
    '김헌철': 'Kim Heon-cheol',
    '정보성': 'Jung Bo-seong',
    '김호현': 'Kim Ho-hyeon',
    '노지윤': 'Noh Ji-yun',
    '안점옥': 'Ahn Jeom-ok',
    '이익훈': 'Lee Ik-hun',
    '김광현': 'Kim Gwang-hyeon',
    '강경오': 'Kang Gyeong-o',
    '양원영': 'Yang Won-yeong',
    '문한솔': 'Moon Han-sol',
    '최재혁': 'Choi Jae-hyeok',
    '송창영': 'Song Chang-yeong',
    '주치수': 'Joo Chi-su',
    '윤태준': 'Yoon Tae-jun',
    '박혜선': 'Park Hye-seon',
    '조대연': 'Cho Dae-yeon',
    '김  승': 'Kim Seung',
    '허승연': 'Heo Seung-yeon',
    '박진영': 'Park Jin-yeong',
    '윤인철': 'Yoon In-cheol',
    '진재섭': 'Jin Jae-seop',
    '백지환': 'Baek Ji-hwan',
    '문덕희': 'Moon Deok-hui',
    '천성권': 'Cheon Seong-gwon',
    '박창규': 'Park Chang-gyu',
    '이응택': 'Lee Eung-taek',
    '박주영': 'Park Ju-yeong',
    '양유정': 'Yang Yu-jeong',
    '손은남': 'Son Eun-nam',
    '허  명': 'Heo Myeong',
    '이지환': 'Lee Ji-hwan',

    # ── 12. 캠퍼스 안내 ─────────────────────────────────────────────
    '주소: (61743) 전남광주통합특별시 남구 효덕로 277 광주대학교 국제협력처(호심관 6층)':
        'Address: Office of International Affairs (Hosim Hall 6F), Gwangju University, '
        '277 Hyodeok-ro, Nam-gu, Jeonnam-Gwangju Integrated Special City 61743, Republic of Korea',
    '국제협력처 홈페이지: https://ie.gwangju.ac.kr':
        'Office of International Affairs: https://ie.gwangju.ac.kr',
    '대학원 교학팀: +82-62-670-2605, 2358, 2122 / https://grad.gwangju.ac.kr':
        'Graduate School Office: +82-62-670-2605, 2358, 2122 / https://grad.gwangju.ac.kr',
}

TR.update(GR)
