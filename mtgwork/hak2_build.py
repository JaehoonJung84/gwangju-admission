# -*- coding: utf-8 -*-
"""학처장회의 자료 — 직전 회차(20261111) HWP 를 양식으로 삼아 본문 칸만 갈아끼운다.

  python hak2_build.py
    1) 직전 회차 HWP → HWPX (COM, 이미 만들어 두면 건너뜀)
    2) section0.xml 의 실시(c7r4)·계획(c7r5)·협의(c7r6) 칸 문단만 교체
       - [MOU 신규 체결 현황] 표와 모집일정 표는 원본 문단째로 물려받는다
    3) HWPX → HWP, PDF (COM)
서식 번호는 직전 회차에서 실측: 부서 61/43, 항목 60(53+43+53),
라벨폭6 63/54, 라벨폭8 66/54, ※ 75/54, 빈 줄 63/54.
"""
import os, re, sys, zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_HWPX = os.path.join(HERE, 'p.hwpx')
import hak2_content as C

CIRCLED = ''.join(chr(c) for c in range(0x2460, 0x2474))   # ①~⑳
LINESEG = re.compile(r'<hp:linesegarray>.*?</hp:linesegarray>', re.S)

# ---------- 칸 찾기 (subList 중첩을 세어 짝을 맞춘다) ----------
CLOSE = '</hp:subList>'

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

def top_paras(inner):
    out, depth, start = [], 0, None
    for m in re.finditer(r'<hp:p[ >]|</hp:p>', inner):
        if m.group(0) != '</hp:p>':
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, m.end()))
    return out

def strip_tail_lineseg(p):
    """문단의 바깥쪽 줄정보만 떼어낸다(한글이 열 때 다시 흘리게)."""
    i = p.rindex('<hp:linesegarray>')
    j = p.index('</hp:linesegarray>', i) + len('</hp:linesegarray>')
    assert p[j:] == '</hp:p>', '바깥 줄정보가 끝에 없다'
    return p[:i] + p[j:]

# ---------- 문단 만들기 ----------
def P(pp, runs):
    body = ''.join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, escape(t))
                   if t else '<hp:run charPrIDRef="%d"/>' % cp for cp, t in runs)
    return ('<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" '
            'columnBreak="0" merged="0">%s</hp:p>' % (pp, body))

def width(s):
    return sum(2 if ord(c) > 0x2000 else 1 for c in s)

def lines_to_paras(block, tables):
    out = []
    for raw in block.strip('\n').splitlines():
        t = raw.rstrip()
        if not t.strip():
            continue
        if t.startswith('@@TBL:'):
            key = t[6:t.index('@@', 6)]
            out.append(tables[key])
        elif t == '|':
            out.append(P(63, [(54, '')]))
        elif re.match(r'^\(\d+\)', t):
            out.append(P(61, [(43, t)]))
        elif t[0] in CIRCLED:
            out.append(P(60, [(53, '   '), (43, t[0]), (53, t[1:])]))
        elif t.startswith('※'):
            out.append(P(75, [(54, '      ' + t)]))
        elif t.startswith('- '):
            m = re.match(r'^- ([^:]{1,8}): ?(.*)$', t)
            pp = 63
            if m:
                w = width(m.group(1))
                pp = 66 if w >= 7 else 63
                assert w in (6, 8), '라벨 폭이 6/8 이 아니다: %r (%d)' % (m.group(1), w)
            out.append(P(pp, [(54, '    ' + t)]))
        else:
            raise SystemExit('종류를 모르는 줄: ' + t)
    return ''.join(out)

def main():
    z = zipfile.ZipFile(SRC_HWPX)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    sec = next(d for i, d in items if i.filename == 'Contents/section0.xml').decode('utf-8')

    # 물려받을 표 문단 두 개를 먼저 떼어 둔다
    a4, b4 = cell_span(sec, 7, 4)
    done_paras = top_paras(sec[a4:b4])
    mou = sec[a4 + done_paras[0][0]: a4 + done_paras[0][1]]
    assert 'MOU 신규 체결 현황' in mou and mou.count('<hp:tbl') == 1, 'MOU 표 문단 아님'
    sched = None
    for s, e in done_paras:
        p = sec[a4 + s: a4 + e]
        if '모집일정' in p and '<hp:tbl' in p:
            sched = p
    assert sched and sched.count('<hp:tbl') == 1, '모집일정 표 문단 못 찾음'
    tables = {'MOU': strip_tail_lineseg(mou), 'SCHED': strip_tail_lineseg(sched)}

    # 뒤에서 앞으로 갈아끼운다(앞을 먼저 바꾸면 뒤 위치가 밀린다)
    for (col, row), block in ((7, 6), C.DISCUSS), ((7, 5), C.PLAN), ((7, 4), C.DONE):
        a, b = cell_span(sec, col, row)
        body = lines_to_paras(block, tables) if block.strip() else P(63, [(54, '')])
        sec = sec[:a] + body + sec[b:]

    assert sec.count('<hp:t>%s</hp:t>' % escape(C.MEETING_OLD)) == 1, '일시 글자 찾기 실패'
    sec = sec.replace('<hp:t>%s</hp:t>' % escape(C.MEETING_OLD),
                      '<hp:t>%s</hp:t>' % escape(C.MEETING_NEW))

    out = os.path.join(HERE, 'out.hwpx')
    with zipfile.ZipFile(out, 'w') as zo:
        for info, data in items:
            if info.filename == 'Contents/section0.xml':
                data = sec.encode('utf-8')
            ct = zipfile.ZIP_STORED if info.filename == 'mimetype' else zipfile.ZIP_DEFLATED
            zo.writestr(info.filename, data, compress_type=ct)
    print('만듦:', out)

if __name__ == '__main__':
    main()
