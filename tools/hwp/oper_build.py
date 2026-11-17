# -*- coding: utf-8 -*-
"""2026학년도 제4차 국제협력운영위원회 회의자료 — 직전 회차(제3차)를 양식으로 삼아 만든다.

표지는 글월만 갈아끼우고, 안건 쪽은 직전 회차 '안건5' 쪽(가장 단순한 쪽)의 바깥표
껍데기를 그대로 쓰고 안쪽 내용만 새로 짠다. 쪽 하나 = 바깥표 하나.
새 서식(paraPr/charPr)은 반드시 목록 '맨 뒤'에 붙인다 — 중간에 끼우면 한글이
번호를 자리 순서로 읽어 뒤 번호가 모두 밀린다(2026-11-17 실측).
"""
import io, os, re, sys, zipfile, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = 'C:/mtgwork/prev.hwpx'
WORK = 'C:/mtgwork/x'
OUT = 'C:/mtgwork/new.hwpx'

# ── 서식 번호 (직전 회차 실측) ──────────────────────────────────────────
CP_AG15B = 31     # '안건1' 15pt 굵게
CP_T15B = 62      # 안건 제목 15pt 굵게
CP_L14B = 63      # 가. 라벨 14pt 굵게
CP_B12 = 69       # 본문 12pt
CP_N10B = 65      # ※ 10pt 굵게 (표 머리에도 쓴다)
CP_TD9 = 74       # 표 안 9pt — 새로 만듦
PP_LABEL = 43     # 여백 0, 내어쓰기 0
PP_DASH = 48      # 내어쓰기 24.41pt ('  - ')
PP_SUB = 51       # 내어쓰기 42pt    ('    ③ ') — 새로 만듦
PP_NOTE = 52      # 내어쓰기 25pt    ('  ※ ' 10pt) — 새로 만듦
PP_CELL = 7       # 표 칸 가운데
BF_HEAD = 14      # 표 머리 칸(음영)
BF_BODY = 3       # 표 본문 칸


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ── 대상자 (입학취소 대상자 명단 .xls) ──────────────────────────────────
ROWS = [
    ('1', '글로벌콘텐츠학부', '20266315', '사보억', '중국', '신입', 3167000),
    ('2', '글로벌콘텐츠학부', '20266316', '주설리', '중국', '신입', 3167000),
    ('3', '뷰티미용학과', '20266733', '레티옥', '베트남', '편입', 0),
    ('4', '컴퓨터공학과', '20266240', '무함마드 모아즈 샤피', '파키스탄', '신입', 1872000),
    ('5', '컴퓨터공학과', '20266255', '아부 후자이파', '파키스탄', '신입', 3744000),
    ('6', '컴퓨터공학과', '20266283', '칸 살만', '파키스탄', '신입', 1872000),
    ('7', '경영학과', '20266284', '턱스볼드', '몽골', '신입', 1583500),
    ('8', '컴퓨터공학과', '20266228', '라나 아만 울라', '파키스탄', '신입', 1872000),
    ('9', '컴퓨터공학과', '20266229', '라흐모노프 자파르베크 우크탐 우글리', '우즈베키스탄', '신입', 2246400),
    ('10', '컴퓨터공학과', '20266254', '샤자입 아흐타르', '파키스탄', '신입', 1872000),
    ('11', '컴퓨터공학과', '20266257', '압바스 알리 샤', '파키스탄', '신입', 1872000),
]
HEAD = ['순번', '학부(과)', '학번', '성명', '국적', '구분', '환불 금액']
WID = [3100, 8500, 5000, 11576, 6800, 3100, 6900]      # 합 44976
TOTAL = sum(r[6] for r in ROWS)
N_REFUND = sum(1 for r in ROWS if r[6])


# ── 문단·표 ───────────────────────────────────────────────────────────
def para(ppr, runs):
    s = '<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">' % ppr
    if not runs:
        s += '<hp:run charPrIDRef="%d"/>' % CP_B12
    for cp, t in runs:
        s += '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, esc(t))
    return s + '</hp:p>'


def cell(txt, cp, col, row, w, h, bf, colspan=1):
    return (
        '<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="%d">'
        '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER"'
        ' linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
        '%s</hp:subList>'
        '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="1"/>'
        '<hp:cellSz width="%d" height="%d"/>'
        '<hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
        % (bf, para(PP_CELL, [(cp, txt)]), col, row, colspan, w, h))


def table():
    H_HEAD, H_BODY = 2270, 1700
    tr = ['<hp:tr>' + ''.join(
        cell(HEAD[i], CP_N10B, i, 0, WID[i], H_HEAD, BF_HEAD) for i in range(len(HEAD))) + '</hp:tr>']
    for n, r in enumerate(ROWS, start=1):
        vals = [r[0], r[1], r[2], r[3], r[4], r[5], ('{:,}'.format(r[6]) if r[6] else '-')]
        tr.append('<hp:tr>' + ''.join(
            cell(vals[i], CP_TD9, i, n, WID[i], H_BODY, BF_BODY) for i in range(len(vals))) + '</hp:tr>')
    n = len(ROWS) + 1
    tr.append('<hp:tr>'
              + cell('계 (11명)', CP_N10B, 0, n, sum(WID[:6]), H_BODY, BF_HEAD, colspan=6)
              + cell('{:,}'.format(TOTAL), CP_N10B, 6, n, WID[6], H_BODY, BF_HEAD)
              + '</hp:tr>')
    h = H_HEAD + H_BODY * (len(ROWS) + 1)
    tbl = ('<hp:tbl id="1177148652" zOrder="18" numberingType="TABLE" textWrap="TOP_AND_BOTTOM"'
           ' textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1"'
           ' rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="3" noAdjust="1">'
           '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
           '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0"'
           ' holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT"'
           ' vertOffset="0" horzOffset="0"/>'
           '<hp:outMargin left="141" right="141" top="141" bottom="141"/>'
           '<hp:inMargin left="510" right="510" top="141" bottom="141"/>%s</hp:tbl>'
           % (len(ROWS) + 2, len(HEAD), sum(WID), h, ''.join(tr)))
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="%d">%s<hp:t/></hp:run></hp:p>' % (PP_LABEL, CP_L14B, tbl))


L = lambda t: para(PP_LABEL, [(CP_L14B, t)])
D = lambda t: para(PP_DASH, [(CP_B12, t)])
S = lambda t: para(PP_SUB, [(CP_B12, t)])
N = lambda t: para(PP_NOTE, [(CP_N10B, t)])
E = lambda: para(PP_LABEL, [])


def body1():
    return ''.join([
        L('가. 추진 배경'),
        D('  - 2026학년도 2학기 학부 외국인 특별전형 합격자 중 11명이 사증(비자) 발급 불허 등의 '
          '사유로 입국하지 못하여 수학할 수 없게 되었음.'),
        D('  - 2026. 11. 11. 개정·시행된 「학칙」 제22조에 취소 사유와 등록금 반환 근거가 '
          '신설되어 이를 심의하고자 함.'),
        E(),
        L('나. 관련 근거'),
        D('  - 「학칙」 제22조(입학허가 및 취소) <개정 2026. 11. 11.>'),
        S('    ③ 다음 각 호의 어느 하나에 해당하는 경우에는 입학 및 졸업 후에라도 교무위원회 '
          '심의를 거쳐 입학허가를 취소할 수 있다.'),
        S('    5. 사증(비자) 발급 불허 등으로 입국하지 못하여 수학할 수 없는 경우'),
        S('    ④ 제3항에 따라 입학허가를 취소하게 되는 경우, 제출한 서류와 등록금을 반환하지 '
          '아니한다. 다만, 제3항제5호에 해당하는 경우에는 등록금을 반환한다.'),
        N('  ※ 「외국인 유학생 입학 시행세칙」 제12조(입학 취소) 신설(안)은 규정 개정 추진 중'),
        E(),
        L('다. 대상자 현황(명단은 붙임 참조)'),
        D('  - 총 11명(신입 10명, 편입 1명) / 재학 6명, 직권휴학 5명(2026. 10. 3.)'),
        D('  - 국적별: 파키스탄 6명, 중국 2명, 몽골·베트남·우즈베키스탄 각 1명'),
        E(),
        L('라. 등록금 반환'),
        D('  - 반환 대상: %d명 / %s원(「학칙」 제22조 제4항 단서, 납부 등록금 전액)'
          % (N_REFUND, '{:,}'.format(TOTAL))),
        D('  - 반환 방법: 취소 통지 후 「등록금 환불신청서」 접수 → 보호자 계좌 입금'),
        E(),
        L('마. 향후 절차'),
        D('  - 국제협력운영위원회 심의 → 교무위원회 심의 → 입학허가 취소 및 학적 정리'),
        D('  - 입학허가 취소 사실 본인 통지 및 관련 부서 통보(교무처·재무처)'),
        E(),
        L('바. 심의 요청사항'),
        D('  - 상기 11명에 대한 「학칙」 제22조 제3항 제5호에 따른 입학허가 취소(안) 및 같은 조 '
          '제4항 단서에 따른 등록금 반환(안)'),
    ])


def body2():
    return ''.join([
        L('○ 입학허가 취소 대상자 (11명)'),
        table(),
        N('  ※ 환불 금액은 2026학년도 2학기 납부 등록금 기준이며, 레티옥(20266733)은 반환 대상 '
          '등록금이 없음.'),
        N('  ※ 직권휴학(2026. 10. 3.) 5명: 턱스볼드, 라나 아만 울라, 라흐모노프 자파르베크 '
          '우크탐 우글리, 샤자입 아흐타르, 압바스 알리 샤'),
    ])


# ── 원본 열기 ─────────────────────────────────────────────────────────
shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK, exist_ok=True)
zipfile.ZipFile(SRC).extractall(WORK)
# HWP→HWPX 변환이 표지 로고(jpg)를 'BinData/image1.' 로 내보내고 크기를 0 으로 적어
# 그림이 사라진다 — 이름·형식·크기를 되살린다.
_bd = os.path.join(WORK, 'BinData', 'image1')
if os.path.exists(_bd):
    os.rename(_bd, os.path.join(WORK, 'BinData', 'image1.jpg'))
    for _f in ('Contents/content.hpf', 'META-INF/manifest.xml'):
        _p = os.path.join(WORK, *_f.split('/'))
        if os.path.exists(_p):
            _t = open(_p, encoding='utf-8').read()
            _t = _t.replace('href="BinData/image1." media-type="image/"',
                            'href="BinData/image1.jpg" media-type="image/jpg"')
            _t = _t.replace('BinData/image1.&quot;', 'BinData/image1.jpg&quot;')
            open(_p, 'w', encoding='utf-8').write(_t)
    print('로고 되살림')

sec = os.path.join(WORK, 'Contents', 'section0.xml')
s = open(sec, encoding='utf-8').read()

head = s[:s.index('<hp:p ')]
tops, depth, start = [], 0, None
for m in re.finditer(r'<hp:p\b[^>]*?(/?)>|</hp:p>', s):
    if m.group(0).startswith('</'):
        depth -= 1
        if depth == 0:
            tops.append((start, m.end()))
    else:
        if m.group(1) == '/':
            if depth == 0:
                tops.append((m.start(), m.end()))
            continue
        if depth == 0:
            start = m.start()
        depth += 1
P = [s[a:b] for a, b in tops]
print('바깥 문단', len(P))

TITLE = '2026학년도 2학기 학부 외국인 입학허가 취소 심의'

# ── 표지 ─────────────────────────────────────────────────────────────
cover = P[0].replace('<hp:curSz width="0" height="0"/>', '<hp:curSz width="5669" height="5669"/>')
cover = cover.replace('<hp:t>2026학년도 제3차</hp:t>', '<hp:t>2026학년도 제4차</hp:t>')
cover = cover.replace('<hp:t>○ 일  자 : 2026. 8. 26.(수)</hp:t>',
                      '<hp:t>○ 일  자 : 2026. 11.    .</hp:t>')
i1 = cover.index('<hp:t> 1. 2026학년도 2학기 학부')
a = cover.rindex('<hp:p ', 0, i1)
b = cover.index('</hp:p>', cover.index('책임 수당 심의</hp:t>')) + len('</hp:p>')
cover = cover[:a] + para(38, [(49, ' 1. ' + TITLE + '(11명)')]) + cover[b:]

# ── 안건 쪽 (바깥표 껍데기 재사용) ─────────────────────────────────────
TPL = P[7]
_k = TPL.index('<hp:cellAddr colAddr="0" rowAddr="1"/><hp:cellSpan colSpan="2"')
_j = TPL.rindex('</hp:subList>', 0, _k)
_tr2 = TPL.index('<hp:tr>', TPL.index('</hp:tr>'))
_sl = TPL.index('hasNumRef="0">', _tr2) + len('hasNumRef="0">')


def page(tag, title, inner):
    pre = TPL[:_sl]
    # 본문 칸은 가운데 정렬로 되어 있어 글이 적으면 위아래로 벌어진다 → 위 정렬
    i = pre.rindex('vertAlign="CENTER"')
    pre = pre[:i] + 'vertAlign="TOP"' + pre[i + len('vertAlign="CENTER"'):]
    t = pre + inner + TPL[_j:]
    t = t.replace('<hp:t>안건5</hp:t>', '<hp:t>%s</hp:t>' % esc(tag))
    t = t.replace('<hp:t>2026학년도 한국어 어학연수과정 책임 수당 심의</hp:t>',
                  '<hp:t>%s</hp:t>' % esc(title))
    return t


out = (head + cover
       + page('안건1', TITLE, body1())
       + page('붙임', '입학허가 취소 대상자 명단', body2())
       + '</hs:sec>')
out = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', out, flags=re.S)
open(sec, 'w', encoding='utf-8').write(out)
print('section0', len(out))

# ── 서식은 목록 맨 뒤에 붙인다 ────────────────────────────────────────
hp = os.path.join(WORK, 'Contents', 'header.xml')
h = open(hp, encoding='utf-8').read()

ptpl = re.search(r'<hh:paraPr id="48".*?</hh:paraPr>', h, re.S).group(0)
npp = int(re.search(r'<hh:paraProperties itemCnt="(\d+)"', h).group(1))
assert (PP_SUB, PP_NOTE) == (npp, npp + 1), (npp, PP_SUB, PP_NOTE)


def clone_pp(idn, intent):
    t = ptpl.replace('id="48"', 'id="%d"' % idn, 1)
    t = t.replace('<hc:intent value="-2441"', '<hc:intent value="-%d"' % intent, 1)
    return t.replace('<hc:intent value="-4882"', '<hc:intent value="-%d"' % (intent * 2), 1)


h = h.replace('</hh:paraProperties>', clone_pp(PP_SUB, 4200) + clone_pp(PP_NOTE, 2500)
              + '</hh:paraProperties>', 1)
h = h.replace('<hh:paraProperties itemCnt="%d"' % npp,
              '<hh:paraProperties itemCnt="%d"' % (npp + 2), 1)

ctpl = re.search(r'<hh:charPr id="45".*?</hh:charPr>', h, re.S).group(0)
ncp = int(re.search(r'<hh:charProperties itemCnt="(\d+)"', h).group(1))
assert CP_TD9 == ncp, (ncp, CP_TD9)
c = ctpl.replace('id="45"', 'id="%d"' % CP_TD9, 1).replace('height="1100"', 'height="900"', 1)
h = h.replace('</hh:charProperties>', c + '</hh:charProperties>', 1)
h = h.replace('<hh:charProperties itemCnt="%d"' % ncp,
              '<hh:charProperties itemCnt="%d"' % (ncp + 1), 1)
open(hp, 'w', encoding='utf-8').write(h)
print('paraPr', npp, '→', npp + 2, '/ charPr', ncp, '→', ncp + 1)

# ── 다시 묶기 ─────────────────────────────────────────────────────────
if os.path.exists(OUT):
    os.remove(OUT)
names = []
for root, _, files in os.walk(WORK):
    for f in files:
        full = os.path.join(root, f)
        names.append((full, os.path.relpath(full, WORK).replace(os.sep, '/')))
names.sort(key=lambda t: (t[1] != 'mimetype', t[1]))
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for full, rel in names:
        z.write(full, rel, compress_type=zipfile.ZIP_STORED if rel == 'mimetype' else zipfile.ZIP_DEFLATED)
print('만듦', OUT, os.path.getsize(OUT))
