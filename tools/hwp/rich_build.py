# -*- coding: utf-8 -*-
"""보고자료 생성기 (서식판) — 볼드·밑줄·테두리 상자·표를 쓸 수 있다.

양식(머리표+라이티)이 든 기존 보고서를 뼈대로 삼아 머리표와 구역 정의는
레코드째 그대로 두고 본문만 새로 쓴다.

본문 DSL (rich_content.BODY) — (종류, 내용) 또는 (종류, 내용, 옵션)
  ('sec' , 글)          ○ 절 제목(진하게)
  ('item', 글)          - 항목
  ('note', 글)          ※ 주석(깊은 들여쓰기)
  ('note2', 글)         ※ 주석(얕은 들여쓰기)
  ('bl'  , '')          빈 줄
  ('rows', [[왼쪽, 오른쪽], …])   테두리 없는 2열 — 오른쪽 칸은 오른쪽 정렬
  ('box' , [(종류, 글), …])       테두리 상자로 감싼 묶음

글 자리에 문자열 대신 조각 목록을 주면 조각마다 서식을 준다.
  ['보통 글', ('진하게', 'b'), ('진하고 밑줄', 'bu'), ('빨강', 'r')]
"""
import struct, zlib, os, sys
import hwpread as H
import olewrite
from rich_content import BODY, TITLE, DATE

TPL = (r'C:\Users\user\Desktop\★국제협력처\0. 보고서'
       r'\20260819 2025학년도 후기 외국인 유학생 학위수여식 계획(안).hwp')
OUT = sys.argv[1] if len(sys.argv) > 1 else '보고서.hwp'

# 줄 종류별 (왼쪽여백, 내어쓰기, 정렬 0=양쪽/2=오른쪽, 기본 글자모양)
#   단위는 HWPUNIT(1/7200인치). 12pt 한글 한 글자 ≈ 1200.
SHAPE = {
    'sec':   (1200, -1200, 0, 'bold'),
    'item':  (2400, -1200, 0, 'norm'),
    'note':  (3600, -1200, 0, 'norm'),
    'note2': (2700, -1200, 0, 'norm'),
    'cellL': (2400, -1200, 0, 'norm'),
    'cellR': (0,     0,    2, 'norm'),
    'bl':    (0,     0,    0, 'norm'),
}
CS_NORM = 52          # 12pt 보통
CS_BOLD = 51          # 12pt 진하게
BF_BOX = 24           # 사방 테두리 · 채우기 없음
BF_NONE = 1           # 테두리 없음
LINE_H = 1200
LINE_GAP = LINE_H * 3 // 5
PAGE_LIMIT = 66900
TBL_W = 50982
ANCHOR = '\x0b\u6c20\u7462\x00\x00\x00\x00\x0b'


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


streams, clsid = olewrite.read_all(TPL)
doc = zlib.decompress(streams['DocInfo'], -15)
sec = zlib.decompress(streams['BodyText/Section0'], -15)

srecs = list(H.records(sec))
heads = [i for i, r in enumerate(srecs) if r[0] == H.T_PARA_HEADER]
body_rec = next(i for i in heads[1:] if srecs[i][1] == 0)
PS_SRC = struct.unpack_from('<H', srecs[body_rec][2], 8)[0]

TITLE_P = DATE_P = None
for k, hi in enumerate(heads):
    for j in range(hi, min(hi + 3, len(srecs))):
        if srecs[j][0] == H.T_PARA_TEXT:
            t = srecs[j][2].decode('utf-16-le')
            if '계획(안)' in t and TITLE_P is None:
                TITLE_P = k
            elif t.strip().startswith('일시:') and DATE_P is None:
                DATE_P = k
            break
assert TITLE_P is not None and DATE_P is not None

# ── DocInfo: 글자모양(진하게+밑줄, 빨강)과 문단모양(여백·정렬)을 새로 만든다
drecs = list(H.records(doc))
ps_idx = [i for i, r in enumerate(drecs) if r[0] == H.TAG + 9]
cs_idx = [i for i, r in enumerate(drecs) if r[0] == H.T_CHAR_SHAPE]

cs_new, CS = [], {'norm': CS_NORM, 'n': CS_NORM, 'bold': CS_BOLD, 'b': CS_BOLD}
# 진하게 + 밑줄 : 진하게 글자모양을 복제해 property(오프셋 46) 밑줄 비트를 켠다
b = bytearray(drecs[cs_idx[CS_BOLD]][2])
prop = struct.unpack_from('<I', b, 46)[0]
struct.pack_into('<I', b, 46, (prop & ~0x0000003C) | (1 << 2))   # 밑줄 종류 = 아래쪽, 실선
struct.pack_into('<I', b, 56, 0x00000000)                        # 밑줄 색 = 검정
CS['bu'] = len(cs_idx) + len(cs_new)
cs_new.append(rec(H.T_CHAR_SHAPE, drecs[cs_idx[CS_BOLD]][1], bytes(b)))
# 빨강(확인 필요 표시용)
b = bytearray(drecs[cs_idx[CS_NORM]][2])
struct.pack_into('<I', b, 52, 0x000000FF)
CS['r'] = len(cs_idx) + len(cs_new)
cs_new.append(rec(H.T_CHAR_SHAPE, drecs[cs_idx[CS_NORM]][1], bytes(b)))

want = sorted({(v[0], v[1], v[2]) for v in SHAPE.values()})
ps_id, ps_new = {}, []
src_ps = drecs[ps_idx[PS_SRC]]
for left, ind, align in want:
    b = bytearray(src_ps[2])
    v = struct.unpack_from('<I', b, 0)[0]
    struct.pack_into('<I', b, 0, (v & ~0x0000001C) | (align << 2))
    struct.pack_into('<i', b, 4, left)
    struct.pack_into('<i', b, 12, ind)
    ps_id[(left, ind, align)] = len(ps_idx) + len(ps_new)
    ps_new.append(rec(H.TAG + 9, src_ps[1], bytes(b)))

out = bytearray()
for i, (tag, lvl, p, ho, po) in enumerate(drecs):
    b = bytearray(p)
    if tag == H.TAG + 1:                       # ID_MAPPINGS
        n = struct.unpack_from('<i', b, 9 * 4)[0]
        assert n == len(cs_idx)
        struct.pack_into('<i', b, 9 * 4, n + len(cs_new))
        m = struct.unpack_from('<i', b, 13 * 4)[0]
        assert m == len(ps_idx)
        struct.pack_into('<i', b, 13 * 4, m + len(ps_new))
    if tag == H.TAG + 0 and len(b) >= 26:
        struct.pack_into('<III', b, 14, 0, 0, 0)
    out += rec(tag, lvl, bytes(b))
    if i == cs_idx[-1]:
        out += b''.join(cs_new)
    if i == ps_idx[-1]:
        out += b''.join(ps_new)
doc_new = bytes(out)

# ── 머리표는 그대로 두고 제목·일시 글자만 교체
pre = bytearray()
pi = -1
hdr_slot = None
for tag, lvl, p, ho, po in H.records(sec[:srecs[body_rec][3]]):
    if tag == H.T_PARA_HEADER:
        pi += 1
        hdr_slot = (len(pre), len(rec(tag, lvl, p)), bytearray(p), lvl, tag)
        pre += rec(tag, lvl, p)
        continue
    if tag == H.T_PARA_TEXT and pi in (TITLE_P, DATE_P):
        data = ((TITLE if pi == TITLE_P else DATE) + '\r').encode('utf-16-le')
        pre += rec(tag, lvl, data)
        slot, size, hb, hlvl, htag = hdr_slot
        old = struct.unpack_from('<I', hb, 0)[0]
        struct.pack_into('<I', hb, 0, (old & 0x80000000) | (len(data) // 2))
        pre[slot:slot + size] = rec(htag, hlvl, bytes(hb))
        continue
    pre += rec(tag, lvl, p)
prefix = bytes(pre)

SEG_W = struct.unpack_from('<i', srecs[body_rec + 3][2], 28)[0] or 48188


def line_seg(v, h, w):
    return struct.pack('<I8i', 0, v, h, h, h * 85 // 100, h * 3 // 5, 0, w, 0x00060000)


def runs_of(content, base):
    """글 조각 목록 → (전체 글, [(시작위치, 글자모양), …])"""
    if isinstance(content, str):
        content = [content]
    text, marks, pos = '', [], 0
    for piece in content:
        s, style = (piece, base) if isinstance(piece, str) else (piece[0], piece[1])
        cs = CS[style] if style in CS else CS[base]
        if not marks or marks[-1][1] != cs:
            marks.append((pos, cs))
        text += s
        pos += len(s)
    return text, marks


def para(kind, content, lvl=0, vert=0, w=SEG_W, last=False):
    left, ind, align, base = SHAPE[kind]
    ps = ps_id[(left, ind, align)]
    if content is None:
        hdr = struct.pack('<IIHBBHHHIH', 1 | (0x80000000 if last else 0), 0,
                          ps, 0, 0, 1, 0, 1, 0, 0)
        return (rec(H.T_PARA_HEADER, lvl, hdr)
                + rec(H.T_PARA_CHAR_SHAPE, lvl + 1, struct.pack('<II', 0, CS[base]))
                + rec(H.T_PARA_LINE_SEG, lvl + 1, line_seg(vert, LINE_H, w)))
    text, marks = runs_of(content, base)
    d = (text + '\r').encode('utf-16-le')
    hdr = struct.pack('<IIHBBHHHIH', (len(d) // 2) | (0x80000000 if last else 0), 0,
                      ps, 0, 0, len(marks), 0, 1, 0, 0)
    pcs = b''.join(struct.pack('<II', p, c) for p, c in marks)
    return (rec(H.T_PARA_HEADER, lvl, hdr)
            + rec(H.T_PARA_TEXT, lvl + 1, d)
            + rec(H.T_PARA_CHAR_SHAPE, lvl + 1, pcs)
            + rec(H.T_PARA_LINE_SEG, lvl + 1, line_seg(vert, LINE_H, w)))


def wrapped(text, w):
    """글이 폭 w 안에서 몇 줄이 될지 어림한다(한글 1200, 그 밖 600)."""
    if not isinstance(text, str):
        text = ''.join(p if isinstance(p, str) else p[0] for p in text)
    used = sum(1200 if ord(c) > 0x2000 else 600 for c in text)
    return max(1, -(-used // max(w, 1)))


def table(cellspec, vert, last, widths, heights, bfill):
    """표 한 벌. cellspec[r][c] = [(종류, 글), …] (셀 안 문단들)."""
    nr, nc = len(cellspec), len(widths)
    height = sum(heights)
    d = (ANCHOR + '\r').encode('utf-16-le')
    hdr = struct.pack('<IIHBBHHHIH', (len(d) // 2) | (0x80000000 if last else 0),
                      0x00000800, ps_id[(0, 0, 0)], 0, 0, 1, 0, 1, 0, 0)
    o = bytearray()
    o += rec(H.T_PARA_HEADER, 0, hdr)
    o += rec(H.T_PARA_TEXT, 1, d)
    o += rec(H.T_PARA_CHAR_SHAPE, 1, struct.pack('<II', 0, CS_NORM))
    o += rec(H.T_PARA_LINE_SEG, 1, line_seg(vert, LINE_H, 0))

    ctrl = bytearray(bytes.fromhex(
        '206c627410032a08000000000000000026c70000d4160000'
        '040000008c008c008c008c0069f48745000000000000'))
    struct.pack_into('<II', ctrl, 16, sum(widths), height)
    o += rec(H.T_CTRL_HEADER, 1, bytes(ctrl))

    t = bytearray()
    t += struct.pack('<IHHH', 0x04000006, nr, nc, 0)
    t += struct.pack('<4h', 510, 510, 141, 141)
    t += b''.join(struct.pack('<H', nc) for _ in range(nr))
    t += struct.pack('<HH', 21, 0)
    o += rec(H.T_TABLE, 2, bytes(t))

    for r in range(nr):
        for c in range(nc):
            paras = cellspec[r][c] or [('bl', None)]
            lh = bytearray()
            lh += struct.pack('<Ii', len(paras), 0x05000020)
            lh += struct.pack('<HHHH', c, r, 1, 1)
            lh += struct.pack('<II', widths[c], heights[r])
            lh += struct.pack('<4h', 510, 510, 141, 141)
            lh += struct.pack('<H', bfill)
            lh += struct.pack('<I', widths[c])
            lh += b'\x00' * 9
            o += rec(H.T_LIST_HEADER, 2, bytes(lh))
            v = 0
            for k, (kind, txt) in enumerate(paras):
                o += para(kind, txt, lvl=2, vert=v, w=widths[c] - 1020,
                          last=(k == len(paras) - 1))
                v += LINE_H + LINE_GAP
    return bytes(o), height


body = bytearray()
vert = 0
for n, entry in enumerate(BODY):
    kind, val = entry[0], entry[1]
    last = (n == len(BODY) - 1)
    if kind == 'rows':
        wl = TBL_W * 78 // 100
        widths = [wl, TBL_W - wl]
        heights = [LINE_H + 748 for _ in val]
        spec = [[[('cellL', row[0])], [('cellR', row[1])]] for row in val]
        blk, hgt = table(spec, vert, last, widths, heights, BF_NONE)
        body += blk
        vert += hgt + 200
    elif kind == 'box':
        inner = TBL_W - 1020
        nlines = sum(wrapped(t, inner) for _, t in val)
        h = nlines * (LINE_H + LINE_GAP) + 600
        blk, hgt = table([[val]], vert, last, [TBL_W], [h], BF_BOX)
        body += blk
        vert += hgt + 200
    else:
        if vert + LINE_H > PAGE_LIMIT:
            vert = 0
        body += para(kind, None if kind == 'bl' else val, lvl=0, vert=vert, last=last)
        vert += (LINE_H + LINE_GAP) * wrapped(val, SEG_W)
    if vert > PAGE_LIMIT:
        vert = 0

sec_new = prefix + bytes(body)
streams['DocInfo'] = zlib.compress(doc_new, 9)[2:-4]
streams['BodyText/Section0'] = zlib.compress(sec_new, 9)[2:-4]
flat = []
for e in BODY:
    if e[0] in ('rows', 'box'):
        continue
    flat.append(e[1] if isinstance(e[1], str) else runs_of(e[1], 'norm')[0])
streams['PrvText'] = (TITLE + '\r\n' + '\r\n'.join(flat))[:900].encode('utf-16-le')
olewrite.write_all(OUT, streams, clsid)

print('글자모양 추가 %s · 문단모양 %s' % ({k: v for k, v in CS.items()}, ps_id))
print('본문 %d항목 · 파일 %s  %d 바이트' % (len(BODY), OUT, os.path.getsize(OUT)))
