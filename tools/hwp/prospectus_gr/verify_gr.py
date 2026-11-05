# -*- coding: utf-8 -*-
"""납품한 대학원 영문 PDF를 국문 원본과 맞대어 본다."""
import io
import os
import re

import fitz

BASE = os.path.join(r'C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강', '대학원')
EN = os.path.join(BASE, '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_영문본.pdf')
KO = os.path.join(BASE, '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_초안_10차.pdf')
ESEC = ['1. Admission Schedule', '2. Admission Procedures', '3. Eligibility',
        '4. Required Documents', '5. Programs Offered', '6. Visa Application',
        '7. Scholarships', '8. Dormitory', '9. Other Information',
        '10. Important Notes', '11. Department Chairs', '12. Campus Guide']
KSEC = ['1. 전형일정', '2. 전형방법', '3. 지원자격', '4. 제출서류', '5. 모집단위', '6. 비자 신청',
        '7. 장학금', '8. 기숙사', '9. 기타사항', '10. 유의사항', '11. 주임교수 안내', '12. 캠퍼스 안내']

en, ko = fitz.open(EN), fitz.open(KO)
ep = [en[i].get_text() for i in range(en.page_count)]
kp = [ko[i].get_text() for i in range(ko.page_count)]
out = ['영문 %d쪽 / 국문 %d쪽  (%.2f MB)' % (en.page_count, ko.page_count,
                                        os.path.getsize(EN) / 1048576.0), '']
out.append('%-18s %-6s %-6s %s' % ('절', '국문', '영문', '판정'))
bad = 0
for k, e in zip(KSEC, ESEC):
    a = next((i + 1 for i, t in enumerate(kp) if i != 3 and k.replace(' ', '') in re.sub(r'\s+', '', t)), 0)
    b = next((i + 1 for i, t in enumerate(ep) if i != 3 and e.replace(' ', '') in re.sub(r'\s+', '', t)), 0)
    bad += a != b
    out.append('%-18s %-6d %-6d %s' % (k, a, b, '같음' if a == b else '다름'))
han = sum(1 for t in ep for line in t.splitlines() if re.search('[\uac00-\ud7a3]', line))
out += ['', '남은 한글 줄 %d개' % han, '쪽 밀림 %d건' % bad]
en.close()
ko.close()
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify.txt'),
        'w', encoding='utf-8').write(os.linesep.join(out))
print('쪽 밀림 %d건, 한글 %d줄 -> verify.txt' % (bad, han))
