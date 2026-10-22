# -*- coding: utf-8 -*-
"""학⋅처장단회의 자료(국제협력처) — 지난 주 최종본을 그대로 두고 칸 안 글월만 갈아끼운다.

한글 COM 을 쓰지 않고 HWP(OLE) 를 직접 뜯어고친다.
  · 문단 모양(내어쓰기)은 지난 주 파일에 이미 있는 것만 골라 쓴다.
  · 내어쓰기 값 = 그 줄 앞머리('    - 내  용: ')의 실제 너비.
"""
import os, sys, zlib, struct, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import olefile
import olewrite as OW
import hwpread as H
import hoe_content as C

SRC = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/학처장회의(20261021)-국제협력처(처장님 수정사항 반영본).hwp'
DST = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/학처장회의(20261028)-국제협력처.hwp'

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
recs = []          # (tag, lvl, payload, 레코드 시작, 레코드 끝)
for tag, lvl, p, ho, po in H.records(raw_sec):
    recs.append((tag, lvl, p, ho, po + len(p)))

para_start = []    # 문단별 PARA_HEADER 레코드 시작 위치
list_hdr = []      # (레코드 시작, 문단 수, 다음 문단 번호)
for tag, lvl, p, ho, end in recs:
    if tag == H.T_PARA_HEADER:
        para_start.append(ho)
    elif tag == H.T_LIST_HEADER:
        list_hdr.append((ho, struct.unpack_from('<i', p, 0)[0], len(para_start)))

# 템플릿(머리·줄나눔 정보)은 26번 문단 것을 쓴다
tpl_head = tpl_seg = None
seen = -1
for tag, lvl, p, ho, end in recs:
    if tag == H.T_PARA_HEADER:
        seen += 1
        if seen == 26:
            tpl_head = bytearray(p)
    elif tag == H.T_PARA_LINE_SEG and seen == 26:
        tpl_seg = bytes(p[:36])
assert tpl_head is not None and tpl_seg is not None and len(tpl_head) == 24


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
            label, _, rest = t[2:].partition(':')
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
    return b''.join(out), cnt


done_bytes, done_n = build(C.DONE, '실시')
plan_bytes, plan_n = build(C.PLAN, '계획')

# ─── 5. 갈아끼우기 (뒤 칸부터) ───────────────────────────────────────────
#   실시사항 칸 = 24~92번 문단, 계획사항 칸 = 94~137번 문단
D0, D1 = para_start[24], para_start[93]
P0, P1 = para_start[94], para_start[138]
lh_done = next(h for h, npa, nxt in list_hdr if nxt == 24)
lh_plan = next(h for h, npa, nxt in list_hdr if nxt == 94)

buf = bytearray(raw_sec)
buf[P0:P1] = plan_bytes
buf[D0:D1] = done_bytes


def set_npara(b, hdr_off, n):
    """LIST_HEADER 의 문단 수를 고친다(레코드 머리 4바이트 뒤가 바로 문단 수)."""
    h = struct.unpack_from('<I', b, hdr_off)[0]
    assert (h & 0x3FF) == H.T_LIST_HEADER, '목록 머리 아님'
    sz = (h >> 20) & 0xFFF
    po = hdr_off + 4 + (4 if sz == 0xFFF else 0)
    struct.pack_into('<i', b, po, n)


set_npara(buf, lh_done, done_n)
# 계획 칸 머리는 실시 칸을 갈아끼운 만큼 밀린다
set_npara(buf, lh_plan + (len(done_bytes) - (D1 - D0)), plan_n)

# ─── 5-2. 지난 주 메모(처장님 의견) 떼어내기 ─────────────────────────────
memo_off = None
for tag, lvl, pp_, ho, end in H.records(bytes(buf)):
    if tag == 93 and lvl == 1:
        memo_off = ho
        break
if memo_off is not None:
    removed = len(buf) - memo_off
    del buf[memo_off:]
    warn.append('지난 주 메모 %d바이트 삭제' % removed)

# ─── 6. 일시 고치기 ──────────────────────────────────────────────────────
old = '2026.10.21.(수) 14:00'.encode('utf-16-le')
new = C.MEETING.encode('utf-16-le')
assert len(old) == len(new) and buf.count(old) == 1, '일시 글월 찾기 실패'
buf[:] = buf.replace(old, new)

# ─── 7. 저장 ─────────────────────────────────────────────────────────────
co = zlib.compressobj(9, zlib.DEFLATED, -15)
streams['BodyText/Section0'] = co.compress(bytes(buf)) + co.flush()
OW.write_all(DST, streams, clsid)

log = ['실시 %d문단 / 계획 %d문단' % (done_n, plan_n),
       '새 Section0 %d바이트 (원본 %d)' % (len(buf), len(raw_sec))]
log += ['  ! ' + w for w in warn]
log.append('완료: ' + DST)
sys.stdout.buffer.write(('\n'.join(log) + '\n').encode('utf-8'))
