# -*- coding: utf-8 -*-
"""학⋅처장단회의 자료(국제협력처) — 지난 주 최종본을 그대로 두고 칸 안 글월만 갈아끼운다.

hoe_build.py 의 후속판. 지난 주 최종본에는 손으로 넣은 '표'가 칸 안에 들어 있어
칸의 범위를 문단 번호로 못 박지 않고 글월과 목록 머리로 찾아낸다.
  · 문단 모양(내어쓰기)은 지난 주 파일에 이미 있는 것만 골라 쓴다.
  · 내어쓰기 값 = 그 줄 앞머리('    - 내  용: ')의 실제 너비.
"""
import os, sys, zlib, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olefile
import olewrite as OW
import hwpread as H
import hoe2_content as C

BASE = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의'
SRC = BASE + r'/학처장회의(20261028)-국제협력처(최종).hwp'
DST = BASE + r'/학처장회의(20261104)-국제협력처.hwp'

PP_TEAM = 61      # (1) 국제협력팀
PP_ITEM = 60      #    ① 항목
CS_TEAM = 43
CS_ITEM = 53
CS_CIRCLE = 43    # ①②③ 글자 하나만 다른 글자모양을 쓴다
CS_DETAIL = 54
CIRCLED = ''.join(chr(c) for c in range(0x2460, 0x2474))   # ①~⑳
MARKS = '㉠㉡㉢㉣㉤㉥'

SPACE, ASCII, WIDE = 1200, 924, 2400


def width(s):
    t = 0
    for ch in s:
        t += SPACE if ch == ' ' else (ASCII if ord(ch) < 128 else WIDE)
    return t


# ─── 1. 원본 읽기 ────────────────────────────────────────────────────────
streams, clsid = OW.read_all(SRC)
head = streams['FileHeader']
comp = bool(head[36] & 1)
raw_doc = zlib.decompress(streams['DocInfo'], -15) if comp else streams['DocInfo']
raw_sec = zlib.decompress(streams['BodyText/Section0'], -15) if comp else streams['BodyText/Section0']

# ─── 2. 쓸 수 있는 문단 모양(내어쓰기 → 아이디) 모으기 ────────────────────
indent2pp = {}
n = 0
for tag, lvl, p, ho, po in H.records(raw_doc):
    if tag == 0x19:
        ml, mr, ind = struct.unpack_from('<iii', p, 4)
        if ml == 1000 and -ind not in indent2pp:
            indent2pp[-ind] = n
        n += 1
AVAIL = sorted(indent2pp)


def pp_for(prefix):
    w = width(prefix)
    if w in indent2pp:
        return indent2pp[w], w, True
    near = min(AVAIL, key=lambda v: abs(v - w))
    return indent2pp[near], w, False


# ─── 3. 원본 레코드 훑기 ─────────────────────────────────────────────────
#   표가 들어 있는 칸이 있으므로 '바깥 문단'(level<=2)만 센다.
recs = list(H.records(raw_sec))

outer = []        # 바깥 문단: {i, start, end, text, hdr, cs, seg, lvl}
lh2 = []          # level2 목록 머리: (레코드 시작, 바로 뒤 바깥 문단 번호)
cur = None
for tag, lvl, p, ho, po in recs:
    if lvl <= 2 and cur is not None and cur['end'] is None and ho != cur['start']:
        cur['end'] = ho
    if tag == H.T_PARA_HEADER and lvl <= 2:
        cur = {'i': len(outer), 'start': ho, 'end': None, 'text': '',
               'hdr': p, 'cs': b'', 'seg': b'', 'lvl': lvl}
        outer.append(cur)
    elif tag == H.T_LIST_HEADER and lvl == 2:
        lh2.append((ho, len(outer)))
    elif cur is not None and cur['end'] is None and lvl == cur['lvl'] + 1:
        # 표 안쪽(더 깊은 수준) 레코드는 건너뛴다
        if tag == H.T_PARA_TEXT:
            cur['text'] = ''.join(c for c, _ in H.para_text(p))
        elif tag == H.T_PARA_CHAR_SHAPE:
            cur['cs'] = p
        elif tag == H.T_PARA_LINE_SEG:
            cur['seg'] = p
if outer and outer[-1]['end'] is None:
    outer[-1]['end'] = len(raw_sec)


def find_para(text):
    hit = [o for o in outer if o['text'].strip() == text]
    assert len(hit) == 1, '문단 %r 를 %d개 찾음' % (text, len(hit))
    return hit[0]


def cell_of(first_para_i):
    """바깥 문단 first_para_i 로 시작하는 칸의 (목록머리 위치, 시작, 끝)."""
    hit = [h for h, nxt in lh2 if nxt == first_para_i]
    assert len(hit) == 1, '칸 머리 찾기 실패(문단 %d)' % first_para_i
    lh = hit[0]
    start = outer[first_para_i]['start']
    nxt = [h for h, _ in lh2 if h > start]
    end = min(nxt) if nxt else len(raw_sec)
    return lh, start, end


i_done = find_para('실시사항')['i'] + 1
i_plan = find_para('계획사항')['i'] + 1
lh_done, D0, D1 = cell_of(i_done)
lh_plan, P0, P1 = cell_of(i_plan)
assert D1 <= P0, '실시/계획 칸 순서가 뒤집혔다'

# 템플릿(머리·줄나눔 정보)은 '(1) 국제협력팀' 문단 것을 쓴다
tpl = outer[i_done]
tpl_head = bytearray(tpl['hdr'])
tpl_seg = bytes(tpl['seg'][:36])
assert len(tpl_head) == 24 and len(tpl_seg) == 36


def rec(tag, lvl, payload):
    size = len(payload)
    if size < 0xFFF:
        return struct.pack('<I', tag | (lvl << 10) | (size << 20)) + payload
    return struct.pack('<II', tag | (lvl << 10) | (0xFFF << 20), size) + payload


_iid = [0x40000000]


def paragraph(text, pp, runs):
    """문단 하나를 레코드 네 개로 만든다."""
    body = text + '\r'
    head = bytearray(tpl_head)
    struct.pack_into('<I', head, 0, len(body))
    struct.pack_into('<H', head, 8, pp)
    struct.pack_into('<H', head, 12, len(runs))
    struct.pack_into('<H', head, 14, 0)
    struct.pack_into('<H', head, 16, 1)
    _iid[0] += 1
    struct.pack_into('<I', head, 18, _iid[0])
    cs = b''.join(struct.pack('<II', a, b) for a, b in runs)
    seg = bytearray(tpl_seg)
    struct.pack_into('<i', seg, 0, 0)
    return (rec(H.T_PARA_HEADER, 2, bytes(head))
            + rec(H.T_PARA_TEXT, 3, body.encode('utf-16-le'))
            + rec(H.T_PARA_CHAR_SHAPE, 3, cs)
            + rec(H.T_PARA_LINE_SEG, 3, bytes(seg)))


# ─── 4. 글월 → 문단 레코드 ───────────────────────────────────────────────
warn = []


def build(block, where):
    out, cnt, num, last_prefix = [], 0, 0, '    '
    for raw in block.strip().splitlines():
        t = raw.strip()
        if not t:
            continue
        if t.startswith('(') and ')' in t[:4]:
            out.append(paragraph(t, PP_TEAM, [(0, CS_TEAM)]))
            num = 0
        elif t.startswith('@ '):
            num += 1
            mark = CIRCLED[num - 1]
            text = '   %s %s' % (mark, t[2:])
            out.append(paragraph(text, PP_ITEM,
                                 [(0, CS_ITEM), (3, CS_CIRCLE), (4, CS_ITEM)]))
            last_prefix = '    '
        elif t.startswith('- '):
            label, sep, rest = t[2:].partition(':')
            assert sep, '%s 쪽 쌍점 없는 줄: %r' % (where, t)
            rest = rest.strip()
            base = '    - %s: ' % label
            prefix = base + (rest[:2] if rest[:1] in MARKS else '')
            pp, w, exact = pp_for(prefix)
            if not exact:
                warn.append('%s 내어쓰기 %d 없음 → 가까운 값으로: %r' % (where, w, prefix))
            out.append(paragraph(base + rest, pp, [(0, CS_DETAIL)]))
            last_prefix = base
        elif t.startswith('+ '):
            rest = t[2:]
            pad = ' ' * round(width(last_prefix) / SPACE)
            prefix = pad + (rest[:2] if rest[:1] in MARKS else '')
            pp, w, exact = pp_for(prefix)
            if not exact:
                warn.append('%s 내어쓰기 %d 없음 → 가까운 값으로: %r' % (where, w, prefix))
            out.append(paragraph(pad + rest, pp, [(0, CS_DETAIL)]))
        else:
            raise SystemExit('종류를 모르는 줄: ' + t)
        cnt += 1
    # 칸의 마지막 문단에는 '마지막' 표시(글자수 최상위 비트)를 세운다
    tail = bytearray(out[-1])
    struct.pack_into('<I', tail, 4, struct.unpack_from('<I', tail, 4)[0] | 0x80000000)
    out[-1] = bytes(tail)
    return b''.join(out), cnt


done_bytes, done_n = build(C.DONE, '실시')
plan_bytes, plan_n = build(C.PLAN, '계획')

# ─── 5. 일시 문단 다시 짓기 ──────────────────────────────────────────────
o_date = [o for o in outer if C.OLD_MEETING in o['text']]
assert len(o_date) == 1, '일시 문단 찾기 실패'
o_date = o_date[0]
new_text = o_date['text'].replace(C.OLD_MEETING, C.MEETING).replace('\n', '')
d_head = bytearray(o_date['hdr'])
flag = struct.unpack_from('<I', d_head, 0)[0] & 0x80000000
struct.pack_into('<I', d_head, 0, (len(new_text) + 1) | flag)
struct.pack_into('<H', d_head, 14, 0)
struct.pack_into('<H', d_head, 16, 1)
d_seg = bytearray(o_date['seg'][:36])
struct.pack_into('<i', d_seg, 0, 0)
date_bytes = (rec(H.T_PARA_HEADER, o_date['lvl'], bytes(d_head))
              + rec(H.T_PARA_TEXT, 3, (new_text + '\r').encode('utf-16-le'))
              + rec(H.T_PARA_CHAR_SHAPE, 3, o_date['cs'])
              + rec(H.T_PARA_LINE_SEG, 3, bytes(d_seg)))

# ─── 6. 갈아끼우기 (뒤쪽부터) ────────────────────────────────────────────
buf = bytearray(raw_sec)
buf[P0:P1] = plan_bytes
buf[D0:D1] = done_bytes
buf[o_date['start']:o_date['end']] = date_bytes

d_shift = len(date_bytes) - (o_date['end'] - o_date['start'])
p_shift = d_shift + (len(done_bytes) - (D1 - D0))


def set_npara(b, hdr_off, n):
    """LIST_HEADER 의 문단 수를 고친다(레코드 머리 4바이트 뒤가 바로 문단 수)."""
    h = struct.unpack_from('<I', b, hdr_off)[0]
    assert (h & 0x3FF) == H.T_LIST_HEADER, '목록 머리 아님'
    sz = (h >> 20) & 0xFFF
    po = hdr_off + 4 + (4 if sz == 0xFFF else 0)
    struct.pack_into('<i', b, po, n)


set_npara(buf, lh_done + d_shift, done_n)
set_npara(buf, lh_plan + p_shift, plan_n)

# ─── 7. 저장 ─────────────────────────────────────────────────────────────
co = zlib.compressobj(9, zlib.DEFLATED, -15)
streams['BodyText/Section0'] = co.compress(bytes(buf)) + co.flush()
OW.write_all(DST, streams, clsid)

log = ['실시 %d문단 / 계획 %d문단' % (done_n, plan_n),
       '일시 %s → %s' % (C.OLD_MEETING, C.MEETING),
       '새 Section0 %d바이트 (원본 %d)' % (len(buf), len(raw_sec))]
log += ['  ! ' + w for w in warn]
log.append('완료: ' + DST)
sys.stdout.buffer.write(('\n'.join(log) + '\n').encode('utf-8'))
