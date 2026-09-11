# -*- coding: utf-8 -*-
"""보고자료 작성 — 본문에 '표'를 넣을 수 있는 생성기.

같은 양식(머리표+라이티)에 본문 표가 들어 있는 보고서를 뼈대로 삼아,
머리표와 구역 정의는 레코드째 그대로 두고 본문만 새로 쓴다.
표는 뼈대 문서의 표 레코드 구성을 그대로 따라 만든다.

본문 DSL (tbl_content.BODY):
  ('sec' , '□ ...')      절 제목
  ('item', '○ ...')      1단계
  ('sub' , '- ...')      2단계
  ('bl'  , '')           빈 줄
  ('table', {'w': [열너비비율...], 'rows': [[셀,...], ...]})   첫 행이 머리행
세 번째 값이 True 면 빨간 글씨.
"""
import struct, zlib, os, sys
import hwpread as H
import olewrite
from bm_content import BODY, TITLE, DATE

TPL = (r'C:\Users\user\Desktop\★국제협력처\0. 보고서'
       r'\20260819 2025학년도 후기 외국인 유학생 학위수여식 계획(안).hwp')
OUT = sys.argv[1] if len(sys.argv) > 1 else '보고서.hwp'

SHAPE = {                      # (왼쪽여백, 내어쓰기)
    'sec':  (1800, -1800),
    'item': (3000, -1800),
    'sub':  (4200, -1800),
    'bl':   (0, 0),
}
PAGE_LIMIT = 66900
TBL_W = 50982                  # 본문 폭(뼈대 문서의 표 폭과 같게)
CELL_H = 1948                  # 셀 한 줄 높이
BF_HEAD, BF_BODY = 23, 24      # 머리행 / 본문행 테두리·배경
CS_HEAD, CS_CELL = 46, 47      # 머리행 / 본문행 글자모양
PS_CELL = 52                   # 셀 문단모양(가운데)

# 표를 붙들어 두는 문단에 들어가는 조종문자: 0x0B + 'tbl '(뒤집힘) + 0*4 + 0x0B
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

# ── 본문 첫 문단 = 머리표 다음의 L0 문단
body_rec = next(i for i in heads[1:] if srecs[i][1] == 0)
BODY_FROM = heads.index(body_rec)
PS_SRC = struct.unpack_from('<H', srecs[body_rec][2], 8)[0]


def _cs_of(rec_i):
    return next(struct.unpack_from('<I', srecs[j][2], 4)[0]
                for j in range(rec_i, len(srecs)) if srecs[j][0] == H.T_PARA_CHAR_SHAPE)


# 뼈대의 절 제목(○로 시작)은 진하게, 그 아래 항목은 보통 글자모양을 쓴다.
CS_SEC = _cs_of(body_rec)
CS_BODY = CS_SEC
for hi in heads:
    if srecs[hi][1] != 0 or hi <= body_rec:
        continue
    t = next((srecs[j][2].decode('utf-16-le') for j in range(hi, min(hi + 3, len(srecs)))
              if srecs[j][0] == H.T_PARA_TEXT), '')
    if t.strip().startswith('-'):
        CS_BODY = _cs_of(hi)
        break
assert CS_BODY != CS_SEC, '본문(보통) 글자모양을 뼈대에서 못 찾음'

# ── 머리표 안 제목·일시 문단 번호 찾기
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
assert TITLE_P is not None and DATE_P is not None, '제목·일시 문단을 못 찾음'

# ── DocInfo: 여백 지정한 문단모양을 새로 만들고 빨간 글자모양을 더한다
drecs = list(H.records(doc))
ps_idx = [i for i, r in enumerate(drecs) if r[0] == H.TAG + 9]
cs_idx = [i for i, r in enumerate(drecs) if r[0] == H.T_CHAR_SHAPE]
want = sorted(set(SHAPE.values()))
ps_id, ps_recs = {}, []
src_ps = drecs[ps_idx[PS_SRC]]
for left, ind in want:
    b = bytearray(src_ps[2])
    struct.pack_into('<i', b, 4, left)
    struct.pack_into('<i', b, 12, ind)
    ps_id[(left, ind)] = len(ps_idx) + len(ps_recs)
    ps_recs.append(rec(H.TAG + 9, src_ps[1], bytes(b)))
red = bytearray(drecs[cs_idx[CS_BODY]][2])
struct.pack_into('<I', red, 52, 0x000000FF)
RED_ID = len(cs_idx)
red_rec = rec(H.T_CHAR_SHAPE, drecs[cs_idx[CS_BODY]][1], bytes(red))

out = bytearray()
for i, (tag, lvl, p, ho, po) in enumerate(drecs):
    b = bytearray(p)
    if tag == H.TAG + 1:                       # ID_MAPPINGS
        n = struct.unpack_from('<i', b, 9 * 4)[0]
        assert n == len(cs_idx)
        struct.pack_into('<i', b, 9 * 4, n + 1)
        m = struct.unpack_from('<i', b, 13 * 4)[0]
        assert m == len(ps_idx)
        struct.pack_into('<i', b, 13 * 4, m + len(ps_recs))
    if tag == H.TAG + 0 and len(b) >= 26:      # 캐럿 위치 초기화
        struct.pack_into('<III', b, 14, 0, 0, 0)
    out += rec(tag, lvl, bytes(b))
    if i == cs_idx[-1]:
        out += red_rec
    if i == ps_idx[-1]:
        out += b''.join(ps_recs)
doc_new = bytes(out)

# ── 구역0 앞부분(머리표)은 그대로 두고 제목·일시 글자만 교체
pre = bytearray()
pi = -1
hdr_slot = None
cut = srecs[body_rec][3]
for tag, lvl, p, ho, po in H.records(sec[:cut]):
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

SEG_W = struct.unpack_from('<i', srecs[body_rec + 3][2], 28)[0]
if SEG_W <= 0:
    SEG_W = 48188


def line_seg(v, h, w):
    return struct.pack('<I8i', 0, v, h, h, h * 85 // 100, h * 3 // 5, 0, w, 0x00060000)


def para(text, ps, cs, lvl=0, vert=0, h=1200, w=SEG_W, last=False):
    """문단 한 벌(헤더 + 글월 + 글자모양 + 줄정보)."""
    if text is None:
        nch, trec = 1, b''
    else:
        d = (text + '\r').encode('utf-16-le')
        nch, trec = len(d) // 2, rec(H.T_PARA_TEXT, lvl + 1, d)
    hdr = struct.pack('<IIHBBHHHIH', nch | (0x80000000 if last else 0), 0,
                      ps, 0, 0, 1, 0, 1, 0, 0)
    return (rec(H.T_PARA_HEADER, lvl, hdr) + trec
            + rec(H.T_PARA_CHAR_SHAPE, lvl + 1, struct.pack('<II', 0, cs))
            + rec(H.T_PARA_LINE_SEG, lvl + 1, line_seg(vert, h, w)))


def table(spec, vert, last):
    """표 한 벌. spec = {'w': 열너비비율, 'rows': [[셀,…], …]} — 첫 행이 머리행."""
    rows, ratio = spec['rows'], spec['w']
    nr, nc = len(rows), len(ratio)
    tot = sum(ratio)
    widths = [TBL_W * r // tot for r in ratio]
    widths[-1] += TBL_W - sum(widths)
    height = CELL_H * nr

    d = (ANCHOR + '\r').encode('utf-16-le')
    hdr = struct.pack('<IIHBBHHHIH', (len(d) // 2) | (0x80000000 if last else 0),
                      0x00000800, ps_id[SHAPE['item']], 0, 0, 1, 0, 1, 0, 0)
    o = bytearray()
    o += rec(H.T_PARA_HEADER, 0, hdr)
    o += rec(H.T_PARA_TEXT, 1, d)
    o += rec(H.T_PARA_CHAR_SHAPE, 1, struct.pack('<II', 0, CS_BODY))
    o += rec(H.T_PARA_LINE_SEG, 1, line_seg(vert, 1200, 0))

    ctrl = bytearray(bytes.fromhex(
        '206c627410032a08000000000000000026c70000d4160000'
        '040000008c008c008c008c0069f48745000000000000'))
    struct.pack_into('<II', ctrl, 16, TBL_W, height)
    o += rec(H.T_CTRL_HEADER, 1, bytes(ctrl))

    t = bytearray()
    t += struct.pack('<IHHH', 0x04000006, nr, nc, 0)
    t += struct.pack('<4h', 510, 510, 141, 141)
    t += b''.join(struct.pack('<H', nc) for _ in range(nr))
    t += struct.pack('<HH', 21, 0)
    o += rec(H.T_TABLE, 2, bytes(t))

    for r, row in enumerate(rows):
        head = (r == 0)
        for c in range(nc):
            txt = str(row[c]) if c < len(row) and row[c] not in (None, '') else None
            lh = bytearray()
            lh += struct.pack('<Ii', 1, 0x05000020)
            lh += struct.pack('<HHHH', c, r, 1, 1)
            lh += struct.pack('<II', widths[c], CELL_H)
            lh += struct.pack('<4h', 510, 510, 141, 141)
            lh += struct.pack('<H', BF_HEAD if head else BF_BODY)
            lh += struct.pack('<I', widths[c])
            lh += b'\x00' * 9
            o += rec(H.T_LIST_HEADER, 2, bytes(lh))
            o += para(txt, PS_CELL, CS_HEAD if head else CS_CELL,
                      lvl=2, vert=0, h=1100, w=widths[c] - 1020, last=True)
    return bytes(o), height


body = bytearray()
vert = 0
for n, entry in enumerate(BODY):
    kind, val = entry[0], entry[1]
    mark = entry[2] if len(entry) > 2 else False
    last = (n == len(BODY) - 1)
    if kind == 'table':
        blk, hgt = table(val, vert, last)
        body += blk
        vert += hgt + 300
        if vert > PAGE_LIMIT:
            vert = 0
    else:
        left, ind = SHAPE[kind]
        h = 1200
        if vert + h > PAGE_LIMIT:
            vert = 0
        cs = CS_SEC if kind == 'sec' else CS_BODY
        body += para(None if kind == 'bl' else val, ps_id[(left, ind)],
                     RED_ID if mark else cs, lvl=0, vert=vert, h=h, last=last)
        vert += h + h * 3 // 5

sec_new = prefix + bytes(body)
streams['DocInfo'] = zlib.compress(doc_new, 9)[2:-4]
streams['BodyText/Section0'] = zlib.compress(sec_new, 9)[2:-4]
prv = TITLE + '\r\n' + '\r\n'.join(e[1] for e in BODY if e[0] != 'table' and e[1])
streams['PrvText'] = prv[:900].encode('utf-16-le')
olewrite.write_all(OUT, streams, clsid)

ntbl = sum(1 for e in BODY if e[0] == 'table')
print('뼈대 본문시작문단 %d · 제목 %d · 일시 %d · 본문글자모양 %d · 문단모양원본 %d'
      % (BODY_FROM, TITLE_P, DATE_P, CS_BODY, PS_SRC))
print('새 문단모양 %s · 빨강 글자모양 %d번' % (ps_id, RED_ID))
print('본문 %d항목(표 %d개) · 파일 %s  %d 바이트'
      % (len(BODY), ntbl, OUT, os.path.getsize(OUT)))
