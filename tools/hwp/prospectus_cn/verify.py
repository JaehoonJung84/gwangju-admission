# -*- coding: utf-8 -*-
"""납품한 중문 PDF를 국문 원본과 맞대어 본다."""
import io
import os
import re

import fitz

BASE = os.path.join(r'C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강', '대학원')
CN = os.path.join(BASE, '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_중문본.pdf')
KO = os.path.join(BASE, '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_초안_10차.pdf')
CSEC = ['1. 招生日程', '2. 选拔方法', '3. 申请资格', '4. 提交材料', '5. 招生专业', '6. 签证申请',
        '7. 奖学金', '8. 宿舍', '9. 其他事项', '10. 注意事项', '11. 主任教授介绍', '12. 校园指南']
KSEC = ['1. 전형일정', '2. 전형방법', '3. 지원자격', '4. 제출서류', '5. 모집단위', '6. 비자 신청',
        '7. 장학금', '8. 기숙사', '9. 기타사항', '10. 유의사항', '11. 주임교수 안내', '12. 캠퍼스 안내']

out = []
cn, ko = fitz.open(CN), fitz.open(KO)
cp = [cn[i].get_text() for i in range(cn.page_count)]
kp = [ko[i].get_text() for i in range(ko.page_count)]
out.append('중문 %d쪽 / 국문 %d쪽  (%.2f MB)' % (cn.page_count, ko.page_count,
                                             os.path.getsize(CN) / 1048576.0))
out.append('')
out.append('%-18s %-6s %-6s %s' % ('절', '국문', '중문', '판정'))
bad = 0
for k, c in zip(KSEC, CSEC):
    a = next((i + 1 for i, t in enumerate(kp) if i != 3 and k.replace(' ', '') in re.sub(r'\s+', '', t)), 0)
    b = next((i + 1 for i, t in enumerate(cp) if i != 3 and c.replace(' ', '') in re.sub(r'\s+', '', t)), 0)
    ok = '같음' if a == b else '다름'
    bad += a != b
    out.append('%-18s %-6d %-6d %s' % (k, a, b, ok))

# 목차에 찍힌 쪽번호가 실제 쪽과 맞는지
toc = re.findall(r'(\d+)\s*$', cp[3], re.M)
out.append('')
out.append('목차에 찍힌 쪽번호: %s' % ' '.join(toc[-12:]))
out.append('실제 절 시작 쪽    : %s' % ' '.join(str(next((i + 1 for i, t in enumerate(cp)
           if i != 3 and c.replace(' ', '') in re.sub(r'\s+', '', t)), 0)) for c in CSEC))
out.append('')
out.append('쪽 밀림 %d건' % bad)
cn.close()
ko.close()
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify.txt'),
        'w', encoding='utf-8').write('\n'.join(out))
print('쪽 밀림 %d건 -> verify.txt' % bad)
