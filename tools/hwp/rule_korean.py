# -*- coding: utf-8 -*-
"""「외국인 유학생 입학 시행세칙」 개정(안) 규정 입안서 및 신·구조문 대조표.

2026-09-29 회차 최종안 hwpx 를 틀로 쓴다.
  section0  1×1 표 한 칸에 규정 입안서 전체가 들어 있다
  section1  2열×3행 대조표
양식의 강조색은 파란색 #0000FF (지난 회차 개정분). 이번 회차 추가 개정분은
빨간색으로 보여야 하므로, 파란 글자모양을 복제해 색만 바꾼 것을 글자모양
목록 끝에 번호가 끊기지 않게 이어 붙인다(한글은 나온 차례대로 번호를 다시
매기므로 중간에 끼우거나 번호를 비우면 어긋난다).
"""
import os, re, subprocess, sys, zipfile
from xml.sax.saxutils import escape

_DESK = os.path.join(os.path.expanduser('~'), 'Desktop', '★국제협력처')
FORM = os.path.join(_DESK, '0. 규정', '규정개정',
    '20260929 외국인유학생입학시행세칙 개정(입학허가 취소 신설)',
    '규정입안서 및 신구조문대조표(외국인 유학생 입학 시행세칙)_최종안.hwpx')

DATE = '2026.00.00.'
START = '2026년 00월 00일'
TITLE0 = '「외국인 유학생 입학 시행세칙」 개정(안) 규정 입안서 및 신·구조문 대조표'
TITLE1 = '「외국인 유학생 입학 시행세칙」 신·구조문 대조표'

#  빨간 글자모양 — (새 번호, 복제할 양식 글자모양)
R_NEW, R_MARK, R_WHY, R_WHAT = 34, 35, 36, 37
REDS = [(R_NEW, 29), (R_MARK, 32), (R_WHY, 33), (R_WHAT, 18)]

#  대조표 칸의 글 폭(HWPUNIT) — 줄 수를 어림해 왼쪽 칸 빈 줄을 맞추는 데 쓴다
CELL_TEXT_W = 34653 - 510 - 510
CHAR_W = 1089                       # 11pt, 자간 -1%

#  ── 제4조의2 조문 (대조표·전문에 같은 글월을 쓴다) ────────────────
ART42 = [
    '제4조의2(한국어 연수 이수의무의 면제 및 연수비 환불)',
    ' ① 제4조제6호 단서에 따라 한국어 연수 이수의무를 면제받으려는 자는 같은 조 '
    '제1호 또는 제4호의 요건을 갖춘 사실을 증명하는 서류를 국제협력처에 제출하여야 한다.',
    ' ② 제1항의 요건을 갖춘 날(이하 “요건충족일”이라 한다)은 한국어능력시험'
    '(TOPIK, TOPIK IBT) 또는 GU-TOPIK의 성적 발표일로 하며, 제4조제4호에 해당하는 '
    '경우에는 어학연수과정 수료일과 GU-TOPIK 성적 발표일 중 늦은 날로 한다.',
    ' ③ 한국어 연수 이수의무의 면제 범위는 다음 각 호와 같다.',
    '  1. 요건충족일이 입학하는 학기의 개강일 이전인 경우: 한국어 연수를 이수하지 아니한다.',
    '  2. 요건충족일이 입학하는 학기의 개강일 후인 경우: 요건충족일의 다음 날부터 '
    '남은 연수시간의 이수를 면제한다.',
    ' ④ 제3항제2호에 따라 이수를 면제받은 자가 연수비를 납부한 경우에는 다음 산식에 '
    '따라 산정한 금액을 환불한다. 이 경우 국제협력처장은 제1항의 서류를 접수한 날부터 '
    '30일 이내에 본인 명의의 계좌로 지급한다.',
    '    환불액 = 납부한 연수비 × 남은 연수시간 ÷ 전체 연수시간',
    ' ⑤ 연수비의 납부 및 환불에 관하여 이 세칙에서 정하지 아니한 사항은 '
    '「한국어 어학연수과정 운영 시행세칙」에서 정하는 바에 따른다.',
]
H6_KEEP = ('  6. 이중언어과정으로 입학하는 경우, 입학 후 1년 이내에 200시간 이상의 '
           '한국어 연수를 이수하여야 한다. ')
H6_NEW = ('다만, 제1호 또는 제4호에 해당하는 자는 그러하지 아니하며, 그 기준일과 '
          '연수비 환불에 관한 사항은 제4조의2에서 정하는 바에 따른다.')

# ── 규정 입안서 (표 한 칸) ─────────────────────────────────────────
PROPOSAL = [
    (21, [(16, '규정 입안서')]),
    (22, [(9, '')]),
    (22, [(9, ' '), (15, '1. 부 서 명 :'), (12, ' 국제협력처 국제협력팀')]),
    (22, [(13, '')]),
    (25, [(9, ' '), (15, '2. 규 정 명 :'), (12, '「외국인 유학생 입학 시행세칙」')]),
    (23, [(13, '')]),
    (30, [(9, ' '), (15, '3. '), (26, '제정(개폐)사유')]),
    (33, [(33, '   1) 한국어능력이 부족한 이중언어과정 입학자에게 한국어연수 이수를 '
                '의무화하고 있으나, (GU)TOPIK 3급 이상 취득자와 같이 일정 수준 이상의 '
                '한국어능력을 갖춘 학생도 입학할 수 있으므로 해당 학생들은 한국어연수 '
                '의무화에 있어 예외를 두고자 함')]),
    (33, [(R_WHY, '   2) 위 예외의 적용 기준일과 연수비 환불 기준이 없어 운영상 '
                   '혼선이 우려되므로 이를 명확히 정하고자 함')]),
    (31, [(R_WHY, '   3)'),
          (33, ' 합격자가 사증(비자) 발급 불허 등의 사유로 입학할 수 없게 된 경우 '
                '입학을 취소할 수 있는 근거가 없어 학적 처리와 등록금 반환에 혼선이 '
                '있으므로, 그 사유와 절차를 명확히 정하고자 함'), (18, ' ')]),
    (20, [(17, '      ')]),
    (24, [(15, ' 4. 주요내용 ')]),
    (32, [(18, '   1) 이중언어과정 한국어 연수 이수 대상을 TOPIK 3급 이상을 취득하지 '
                '못한 자로 한정(제4조 제6호 개정)')]),
    (32, [(R_WHAT, '   2) 면제 기준일·범위 및 환불 방식 신설(제4조의2 신설)')]),
    (32, [(R_WHAT, '   3)'),
          (18, ' 사증(비자) 발급 불허, 제출서류 위조·변조 등의 경우 입학을 취소할 수 '
                '있도록 근거 신설(제12조 신설)')]),
    (32, [(R_WHAT, '   4)'),
          (18, ' 기존 제12조(그 밖의 사항)를 제13조로 조문 번호 조정')]),
    (32, [(R_WHAT, '   5)'), (18, ' 이 세칙은 %s부터 시행한다.' % START)]),
    (32, [(R_WHAT, '   6) 제4조 제6호 및 제4조의2의 개정 규정은 이 세칙 시행 당시 '
                    '재학 중인 자에게도 적용한다.')]),
    (32, [(R_WHAT, '   7)'),
          (18, ' 제12조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.')]),
    (29, [(18, '')]),
    (27, [(20, '규정심의위원장 귀하')]),
    (27, [(20, '')]),
]


def lines(text):
    """칸 폭에 비춘 줄 수 어림 — 한글 한 글자 1, 영문·숫자 0.5로 센다."""
    w = sum(0.5 if ord(c) < 0x1100 else 1.0 for c in text)
    per = CELL_TEXT_W / CHAR_W
    return max(1, int(w / per) + (1 if w % per else 0))


# ── 신·구조문 대조표 ───────────────────────────────────────────────
NEW_TOP = [                                  # 개정(안) — 제4조 ~ 제4조의2
    (35, [(31, '제4조(지원자격)'), (8, ' 《현행과 같음》')]),
    (35, [(8, '  1. ∼ 5. 《현행과 같음》')]),
    (36, [(8, H6_KEEP), (R_NEW, H6_NEW), (R_MARK, ' <개정 %s>' % DATE)]),
    (36, [(8, '')]),
    (35, [(R_NEW, ART42[0]), (R_MARK, ' <신설 %s>' % DATE)]),
] + [(35, [(R_NEW, t)]) for t in ART42[1:]]

NEW_BOT = [                                  # 개정(안) — 제12조 이하
    #  전문은 '입학허가를 취소' 로 쓰고 있어 대조표도 그 글월에 맞춘다
    (35, [(29, '제12조(입학 취소) ① 국제협력처장은 합격자가 다음 각 호의 어느 하나에 '
                '해당하는 경우 입학허가를 취소할 수 있다.')]),
    (40, [(29, '  1. '), (25, '사증 발급 불허, 입국 거부 등의 사유로 입국하지 아니한 경우')]),
    (35, [(29, '  2. 제출서류가 위조·변조되었거나 허위임이 확인된 경우 '),
          (32, '<개정 %s>' % DATE)]),
    (38, [(8, ' ')]),
    (39, [(8, '제6장 《현행과 같음》')]),
    (38, [(8, '')]),
    (35, [(29, '제13조'), (30, '(그 밖의 사항)'),
          (8, ' 이 세칙에 명시되지 아니한 사항은 본교 제 규정, 교육부 유학생 선발 '
               '지침 및 관련 규정에 따라 처리한다.')]),
]

CUR_TOP = [                                  # 현행 — 제4조
    (35, [(31, '제4조(지원자격)'), (8, ' 《생 략》')]),
    (35, [(8, '  1. ∼ 5. 《생 략》')]),
    (36, [(8, H6_KEEP)]),
    (36, [(8, '')]),
    (37, [(19, '《신   설》')]),
]
CUR_BOT = [                                  # 현행 — 제12조 이하
    (37, [(19, '《신   설》')]),
    (38, [(8, '')]),
    (38, [(8, '')]),
    (39, [(8, '제6장 《생 략》')]),
    (38, [(8, '')]),
    (35, [(31, '제12조(그 밖의 사항)'),
          (8, ' 이 세칙에 명시되지 아니한 사항은 본교 제 규정, 교육부 유학생 선발 '
               '지침 및 관련 규정에 따라 처리한다.')]),
]

ADD_CUR = [(37, [(19, '《신   설》')]), (37, [(19, '')]),
           (37, [(19, '')]), (37, [(19, '')])]
ADD_NEW = [
    (39, [(27, '부   칙')]),
    (35, [(29, '제1조(시행일) 이 세칙은 %s부터 시행한다.' % START)]),
    (35, [(R_NEW, '제2조(적용례) 제4조제6호 및 제4조의2의 개정규정은 이 세칙 시행 '
                   '당시 재학 중인 자에게도 적용한다.')]),
    (41, [(R_NEW, '제3조(경과조치)'),
          (29, ' 제12조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.')]),
]


def pad_current():
    """제4조의2 가 들어간 만큼 현행 칸에 빈 줄을 넣어 제12조 자리를 맞춘다."""
    right = sum(lines(''.join(t for _, t in runs)) for _, runs in NEW_TOP[2:])
    left = sum(lines(''.join(t for _, t in runs)) for _, runs in CUR_TOP[2:])
    return CUR_TOP + [(37, [(19, '')])] * max(0, right - left) + CUR_BOT


def para(pp, runs):
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


def add_reds(header):
    """파란 글자모양을 복제해 빨간 글자모양을 목록 끝에 이어 붙인다."""
    els = dict((int(re.search(r'id="(\d+)"', e).group(1)), e)
               for e in re.findall(r'<hh:charPr\b.*?</hh:charPr>', header, re.S))
    cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)"', header).group(1))
    assert cnt == len(els) == R_NEW, '글자모양 수가 어긋난다 (%d)' % cnt
    made = ''
    for new_id, src in REDS:
        e = els[src]
        e = re.sub(r'id="\d+"', 'id="%d"' % new_id, e, count=1)
        e = re.sub(r'textColor="#[0-9A-Fa-f]{6}"', 'textColor="#FF0000"', e, count=1)
        made += e
    header = header.replace('<hh:charProperties itemCnt="%d"' % cnt,
                            '<hh:charProperties itemCnt="%d"' % (cnt + len(REDS)), 1)
    tail = '</hh:charProperties>'
    i = header.index(tail)
    return header[:i] + made + header[i:]


def build(out):
    z = zipfile.ZipFile(FORM)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    get = lambda n: next(d for i, d in items if i.filename == n).decode('utf-8')
    hdr = add_reds(get('Contents/header.xml'))
    s0, s1 = get('Contents/section0.xml'), get('Contents/section1.xml')

    s0 = put_cell(put_title(s0, TITLE0), 0, 0, PROPOSAL)
    s1 = put_title(s1, TITLE1)
    s1 = put_cell(s1, 0, 1, pad_current())
    s1 = put_cell(s1, 1, 1, NEW_TOP + [(38, [(8, '')])] + NEW_BOT)
    s1 = put_cell(s1, 0, 2, ADD_CUR)
    s1 = put_cell(s1, 1, 2, ADD_NEW)

    repl = {'Contents/header.xml': hdr.encode('utf-8'),
            'Contents/section0.xml': s0.encode('utf-8'),
            'Contents/section1.xml': s1.encode('utf-8')}
    with zipfile.ZipFile(out, 'w') as zo:
        for info, data in items:
            data = repl.get(info.filename, data)
            zo.writestr(info.filename, data,
                        zipfile.ZIP_STORED if info.filename == 'mimetype'
                        else zipfile.ZIP_DEFLATED)
    print('빨간 글자모양 %s 추가 (글자모양 %d개)' % ([n for n, _ in REDS], R_NEW + len(REDS)))
    print('현행 칸 빈 줄 채움: %d줄' % (len(pad_current()) - len(CUR_TOP) - len(CUR_BOT)))
    print('만든 파일: %s  %d 바이트' % (out, os.path.getsize(out)))
    return out


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    if len(sys.argv) > 2 and sys.argv[2] == 'pdf':
        conv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hwp_conv.py')
        pdf = os.path.splitext(out)[0] + '.pdf'
        r = subprocess.run([sys.executable, conv, out, pdf, 'PDF'],
                           capture_output=True, text=True, timeout=600)
        print(r.stdout.strip() or r.stderr.strip())


if __name__ == '__main__':
    main()
