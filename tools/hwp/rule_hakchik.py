# -*- coding: utf-8 -*-
"""「학칙」제22조(입학허가 및 취소) 개정 — 규정입안서 및 신·구조문 대조표.

양식은 2026-09-29 「외국인 유학생 입학 시행세칙」 최종안 hwpx.
문단·글자 모양 번호는 모두 그 양식에서 실측한 것만 쓴다(한글이 새로 만든
글자 모양은 다시 읽을 때 버리므로 기존 것을 재사용해야 한다).
  section0  1×1 표 한 칸에 규정 입안서 전체가 들어 있다
  section1  2열×3행 대조표
  이 양식의 강조색은 파란색 #0000FF 굵게 (c19 c25 c27 c29 c32)
"""
import os, re, subprocess, sys, zipfile
from xml.sax.saxutils import escape

_DESK = os.path.join(os.path.expanduser('~'), 'Desktop', '★국제협력처')
FORM = os.path.join(_DESK, '0. 규정', '규정개정',
    '20260929 외국인유학생입학시행세칙 개정(입학허가 취소 신설)',
    '규정입안서 및 신구조문대조표(외국인 유학생 입학 시행세칙)_최종안.hwpx')

DATE = '2026.00.00.'
START = '2026년 00월 00일'
TITLE0 = '「학칙」 개정(안) 규정 입안서 및 신·구조문 대조표'
TITLE1 = '「학칙」 신·구조문 대조표'

# ── 규정 입안서 (표 한 칸) ─────────────────────────────────────────
PROPOSAL = [
    (21, [(16, '규정 입안서')]),
    (22, []),
    (22, [(9, ' '), (15, '1. 부 서 명 :'), (12, ' 국제협력처 국제협력팀')]),
    (22, []),
    (25, [(9, ' '), (15, '2. 규 정 명 :'), (12, '「학칙」')]),
    (23, []),
    (30, [(9, ' '), (15, '3. '), (26, '제정(개폐)사유')]),
    (33, [(33, '   1) 합격자가 사증(비자) 발급 불허 등의 사유로 입국하지 못하여 수학할 수 '
                '없게 된 경우 입학허가를 취소할 수 있는 근거가 없어 학적 처리에 혼선이 '
                '있으므로, 그 사유를 명확히 정하고자 함')]),
    (31, [(33, '   2) 입학허가를 취소하는 경우 제출 서류와 등록금을 일률적으로 반환하지 '
                '아니하도록 하고 있어, 본인에게 책임이 없는 사유로 취소되는 경우까지 '
                '등록금 반환이 제한되는 문제가 있으므로 예외를 두고자 함')]),
    (20, [(17, '      ')]),
    (24, [(15, ' 4. 주요내용 ')]),
    (32, [(18, '   1) 사증(비자) 발급 불허 등의 사유로 입국하지 못하여 수학할 수 없는 '
                '경우를 입학허가 취소 사유로 신설(제22조제3항제5호 신설)')]),
    (32, [(18, '   2) 제3항제5호에 해당하는 경우에는 등록금을 반환하도록 단서 신설'
                '(제22조제4항 단서 신설)')]),
    (32, [(18, '   3) 이 학칙은 %s부터 시행한다.' % START)]),
    (32, [(18, '   4) 제22조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.')]),
    (29, []),
    (29, []),
    (27, [(20, '규정심의위원장 귀하')]),
]

# ── 신·구조문 대조표 ───────────────────────────────────────────────
# 현행(왼쪽)
CUR = [
    (35, [(31, '제22조(입학허가 및 취소)'), (8, ' ① ∼ ② 《생 략》')]),
    (35, [(8, ' ③ 다음 각 호의 1에 해당하는 경우에는 입학 및 졸업 후에라도 교무위원회 '
               '심의를 거쳐 입학허가를 취소할 수 있다. 다만, 제1호 내지 제3호에 해당하는 '
               '경우 입학허가를 취소하여야 한다.')]),
    (35, [(8, '  1. ∼ 4. 《생 략》')]),
    (37, [(19, '《신   설》')]),
    (35, []),
    (35, [(8, ' ④ 제3항에 따라 입학허가를 취소하게 되는 경우, 제출한 서류와 등록금을 '
               '반환하지 아니한다.')]),
    (35, []),
]
# 개정(안)(오른쪽) — 바뀐 글월만 파란 굵은 글씨(c29), 개정 표시는 c32
NEW = [
    (35, [(31, '제22조(입학허가 및 취소)'), (8, ' ① ∼ ② 《현행과 같음》')]),
    (35, [(8, ' ③ 《현행과 같음》')]),
    (35, []),
    (35, []),
    (35, [(8, '  1. ∼ 4. 《현행과 같음》')]),
    (40, [(29, '  5. 사증(비자) 발급 불허 등의 사유로 입국하지 못하여 수학할 수 없는 경우 '),
          (32, '<신설 %s>' % DATE)]),
    (35, [(8, ' ④ 제3항에 따라 입학허가를 취소하게 되는 경우, 제출한 서류와 등록금을 '
               '반환하지 아니한다. '),
          (29, '다만, 제3항제5호에 해당하는 경우에는 등록금을 반환한다. '),
          (32, '<개정 %s>' % DATE)]),
]
ADD_CUR = [(37, [(19, '《신   설》')]),
           (37, []), (37, []), (37, [])]
ADD_NEW = [
    (39, [(27, '부   칙')]),
    (35, [(29, '제1조(시행일) 이 학칙은 %s부터 시행한다.' % START)]),
    (41, [(29, '제2조(적용례) 제22조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.')]),
]


def para(pp, runs):
    """runs = [(글자모양번호, 글월)] — 빈 목록이면 빈 줄(c8)."""
    if not runs:
        body = '<hp:run charPrIDRef="8"><hp:t/></hp:run>'
    else:
        body = ''.join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, escape(t))
                       for cp, t in runs)
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" '
            'merged="0">%s</hp:p>' % (pp, body))


def cell_bounds(xml, col, row):
    addr = '<hp:cellAddr colAddr="%d" rowAddr="%d"/>' % (col, row)
    end = xml.index(addr)
    close = xml.rindex('</hp:subList>', 0, end)
    opn = xml.index('>', xml.rindex('<hp:subList ', 0, close)) + 1
    return opn, close


def put_cell(xml, col, row, paras):
    a, b = cell_bounds(xml, col, row)
    return xml[:a] + ''.join(para(pp, runs) for pp, runs in paras) + xml[b:]


def put_title(xml, new):
    m = re.search(r'<hp:t>[^<]*신·구조문 대조표</hp:t>', xml)
    return xml[:m.start()] + '<hp:t>%s</hp:t>' % escape(new) + xml[m.end():]


def build(out):
    z = zipfile.ZipFile(FORM)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    get = lambda n: next(d for i, d in items if i.filename == n).decode('utf-8')
    s0, s1 = get('Contents/section0.xml'), get('Contents/section1.xml')

    s0 = put_cell(put_title(s0, TITLE0), 0, 0, PROPOSAL)
    s1 = put_title(s1, TITLE1)
    s1 = put_cell(s1, 0, 1, CUR)
    s1 = put_cell(s1, 1, 1, NEW)
    s1 = put_cell(s1, 0, 2, ADD_CUR)
    s1 = put_cell(s1, 1, 2, ADD_NEW)

    with zipfile.ZipFile(out, 'w') as zo:
        for info, data in items:
            if info.filename == 'Contents/section0.xml':
                data = s0.encode('utf-8')
            elif info.filename == 'Contents/section1.xml':
                data = s1.encode('utf-8')
            zo.writestr(info.filename, data,
                        zipfile.ZIP_STORED if info.filename == 'mimetype'
                        else zipfile.ZIP_DEFLATED)
    return out


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print('생성:', out)
    if len(sys.argv) > 2 and sys.argv[2] == 'pdf':
        conv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hwp_conv.py')
        pdf = os.path.splitext(out)[0] + '.pdf'
        r = subprocess.run([sys.executable, conv, out, pdf, 'PDF'],
                           capture_output=True, text=True, timeout=600)
        print(r.stdout.strip() or r.stderr.strip())


if __name__ == '__main__':
    main()
