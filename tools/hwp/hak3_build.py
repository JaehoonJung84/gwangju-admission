# -*- coding: utf-8 -*-
"""학처장회의 자료 — 직전 회차(20261125) HWP 를 양식으로 삼아 본문 칸만 갈아끼운다.

  python hak3_build.py [작업폴더]
    1) <작업폴더>\\p2.hwpx (직전 회차를 COM 으로 HWPX 로 바꿔 둔 것) 를 읽어
    2) section0.xml 의 실시(c7r4)·계획(c7r5)·협의(c7r6) 칸 문단만 교체
    3) <작업폴더>\\out.hwpx 로 내놓는다 (HWP 변환은 hwp_conv.py 로)

서식 번호(20261125 회차 실측):
  부서 paraPr 60 / charPr 43,  항목 60 (52 공백3 + 43 기호 + 52 제목),
  '- 라벨: …' 63/53,  '※ …' 73/53,  빈 줄 60/52.
hak2 와 달리 표를 물려받지 않는다(이번 양식의 실시 칸 표는 지난주 것이라 버린다).
"""
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[1] if len(sys.argv) > 1 else r'C:\projects\mtgwork'
SRC_HWPX = os.path.join(WORK, 'p2.hwpx')
OUT_HWPX = os.path.join(WORK, 'out.hwpx')

sys.path.insert(0, HERE)
import hak3_content as C  # noqa: E402

CIRCLED = ''.join(chr(c) for c in range(0x2460, 0x2474))   # ①~⑳
CLOSE = '</hp:subList>'


# ---------- 칸 찾기 (subList 중첩을 세어 짝을 맞춘다) ----------
def match_open(xml, close_pos):
    toks = [(m.start(), m.group(0)) for m in
            re.finditer(r'<hp:subList[ >]|</hp:subList>', xml[:close_pos + len(CLOSE)])]
    depth = 0
    for pos, t in reversed(toks):
        depth += 1 if t == CLOSE else -1
        if depth == 0 and t != CLOSE:
            return xml.index('>', pos) + 1
    raise SystemExit('subList 짝 맞추기 실패')


def cell_span(xml, col, row):
    addr = '<hp:cellAddr colAddr="%d" rowAddr="%d"/>' % (col, row)
    hits = [m.start() for m in re.finditer(re.escape(addr), xml)]
    assert len(hits) == 1, '칸 %d/%d 가 %d 개' % (col, row, len(hits))
    close = xml.rindex(CLOSE, 0, hits[0])
    return match_open(xml, close), close


# ---------- 문단 만들기 ----------
def P(pp, runs):
    body = ''.join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, escape(t))
                   if t else '<hp:run charPrIDRef="%d"/>' % cp for cp, t in runs)
    return ('<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" '
            'columnBreak="0" merged="0">%s</hp:p>' % (pp, body))


def width(s):
    return sum(2 if ord(c) > 0x2000 else 1 for c in s)


def lines_to_paras(block):
    out = []
    for raw in block.strip('\n').splitlines():
        t = raw.rstrip()
        if not t.strip():
            continue
        if t == '|':
            out.append(P(60, [(52, '')]))
        elif re.match(r'^\(\d+\)', t):
            out.append(P(60, [(43, t)]))
        elif t[0] in CIRCLED:
            out.append(P(60, [(52, '   '), (43, t[0]), (52, t[1:])]))
        elif t.startswith('※'):
            out.append(P(73, [(53, '      ' + t)]))
        elif t.startswith('- '):
            m = re.match(r'^- ([^:]{1,8}): ?(.*)$', t)
            if m:
                w = width(m.group(1))
                assert w in (6, 8), '라벨 폭이 6/8 이 아니다: %r (%d)' % (m.group(1), w)
            out.append(P(63, [(53, '    ' + t)]))
        else:
            raise SystemExit('종류를 모르는 줄: ' + t)
    return ''.join(out)


def main():
    z = zipfile.ZipFile(SRC_HWPX)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    sec = next(d for i, d in items if i.filename == 'Contents/section0.xml').decode('utf-8')

    # 뒤에서 앞으로 갈아끼운다(앞을 먼저 바꾸면 뒤 위치가 밀린다)
    for (col, row), block in (((7, 6), C.DISCUSS), ((7, 5), C.PLAN), ((7, 4), C.DONE)):
        a, b = cell_span(sec, col, row)
        body = lines_to_paras(block) if block.strip() else P(63, [(53, '')])
        sec = sec[:a] + body + sec[b:]

    old = '<hp:t>%s</hp:t>' % escape(C.MEETING_OLD)
    assert sec.count(old) == 1, '일시 글자 찾기 실패'
    sec = sec.replace(old, '<hp:t>%s</hp:t>' % escape(C.MEETING_NEW))

    with zipfile.ZipFile(OUT_HWPX, 'w') as zo:
        for info, data in items:
            if info.filename == 'Contents/section0.xml':
                data = sec.encode('utf-8')
            ct = zipfile.ZIP_STORED if info.filename == 'mimetype' else zipfile.ZIP_DEFLATED
            zo.writestr(info.filename, data, compress_type=ct)
    print('만듦:', OUT_HWPX)


if __name__ == '__main__':
    main()
