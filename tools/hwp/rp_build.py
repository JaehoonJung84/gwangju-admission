# -*- coding: utf-8 -*-
"""보고자료 작성 — 기존 보고서를 뼈대로 삼아 제목·일시만 고치고 본문을 새로 쓴다.

머리표(박애인/창의인/전문인 · 제목 · 일시 칸)와 구역 정의는 레코드째 그대로 두고,
본문 문단(L0)만 갈아 끼운다. 들여쓰기는 글 앞 공백이 아니라 문단 모양이 맡는다.
"""
import struct, zlib, os, sys
import hwpread as H
import olewrite
from rp_content import BODY, TITLE, DATE

TPL = (r'C:\Users\user\Desktop\★국제협력처\0. 보고서'
       r'\20260904 2026-2학기 외국인 유학생 학부(과) 간담회 요청·민원사항 보고.hwp')
OUT = sys.argv[1] if len(sys.argv) > 1 else '보고서.hwp'

BODY_FROM = 18                     # 이 문단부터가 본문
TITLE_P, DATE_P = 4, 5             # 머리표 안의 제목·일시 문단
CS_BODY = 47                       # 본문 글자모양(12pt 검정)

# 줄 종류별 (왼쪽여백, 내어쓰기). 첫 줄 위치 = 왼쪽여백 + 내어쓰기
SHAPE = {
    'sec':  (1800, -1800),         # □ 는 0 에서 시작, 넘어가는 줄은 1800
    'item': (3000, -1800),         # ○ 는 1200 에서 시작, 넘어가는 줄은 3000
    'sub':  (4200, -1800),         # - 는 2400 에서 시작, 넘어가는 줄은 4200
    'bl':   (0, 0),
}
PAGE_LIMIT = 66900


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


streams, clsid = olewrite.read_all(TPL)
doc = zlib.decompress(streams['DocInfo'], -15)
sec = zlib.decompress(streams['BodyText/Section0'], -15)

# ── 새 문단모양 만들기 (본문 문단모양 65번을 복제해 여백·내어쓰기만 교체)
drecs = list(H.records(doc))
ps_idx = [i for i, r in enumerate(drecs) if r[0] == H.TAG + 9]
cs_idx = [i for i, r in enumerate(drecs) if r[0] == H.T_CHAR_SHAPE]
want = sorted(set(SHAPE.values()))
ps_id, ps_recs = {}, []
for left, ind in want:
    b = bytearray(drecs[ps_idx[65]][2])
    struct.pack_into('<i', b, 4, left)
    struct.pack_into('<i', b, 12, ind)
    ps_id[(left, ind)] = len(ps_idx) + len(ps_recs)
    ps_recs.append(rec(H.TAG + 9, drecs[ps_idx[65]][1], bytes(b)))
# 빨간 글자모양(확인 필요 항목 표시용)
red = bytearray(drecs[cs_idx[CS_BODY]][2])
struct.pack_into('<I', red, 52, 0x000000FF)
RED_ID = len(cs_idx)
red_rec = rec(H.T_CHAR_SHAPE, drecs[cs_idx[CS_BODY]][1], bytes(red))

out = bytearray()
for i, (tag, lvl, p, ho, po) in enumerate(drecs):
    b = bytearray(p)
    if tag == H.TAG + 1:
        n = struct.unpack_from('<i', b, 9 * 4)[0]
        assert n == len(cs_idx)
        struct.pack_into('<i', b, 9 * 4, n + 1)
        m = struct.unpack_from('<i', b, 13 * 4)[0]
        assert m == len(ps_idx)
        struct.pack_into('<i', b, 13 * 4, m + len(ps_recs))
    if tag == H.TAG + 0 and len(b) >= 26:
        struct.pack_into('<III', b, 14, 0, 0, 0)
    out += rec(tag, lvl, bytes(b))
    if i == cs_idx[-1]:
        out += red_rec
    if i == ps_idx[-1]:
        out += b''.join(ps_recs)
doc_new = bytes(out)

# ── 구역0 : 머리표까지는 그대로(제목·일시 글자만 교체), 본문은 새로 씀
srecs = list(H.records(sec))
heads = [i for i, r in enumerate(srecs) if r[0] == H.T_PARA_HEADER]
cut = srecs[heads[BODY_FROM]][3]                  # 본문 첫 문단이 시작하는 위치

pre = bytearray()
pi = -1
hdr_slot = None
for tag, lvl, p, ho, po in H.records(sec[:cut]):
    if tag == H.T_PARA_HEADER:
        pi += 1
        hdr_slot = (len(pre), len(rec(tag, lvl, p)), bytearray(p), lvl, tag)
        pre += rec(tag, lvl, p)
        continue
    if tag == H.T_PARA_TEXT and pi in (TITLE_P, DATE_P):
        new = (TITLE if pi == TITLE_P else DATE) + '\r'
        data = new.encode('utf-16-le')
        pre += rec(tag, lvl, data)
        slot, size, hb, hlvl, htag = hdr_slot
        old = struct.unpack_from('<I', hb, 0)[0]
        struct.pack_into('<I', hb, 0, (old & 0x80000000) | (len(data) // 2))
        pre[slot:slot + size] = rec(htag, hlvl, bytes(hb))
        continue
    pre += rec(tag, lvl, p)
prefix = bytes(pre)

child_lvl = next(r[1] for r in srecs if r[0] == H.T_PARA_TEXT and r[1] > 0)
segs = [r[2] for r in srecs if r[0] == H.T_PARA_LINE_SEG]
SEG_W = struct.unpack_from('<i', segs[BODY_FROM][0:36], 28)[0] if len(segs) > BODY_FROM else 48188
if SEG_W <= 0:
    SEG_W = 48188


def line_seg(v, h):
    return struct.pack('<I8i', 0, v, h, h, h * 85 // 100, h * 3 // 5, 0, SEG_W, 0x00060000)


body = bytearray()
vert = 0
for n, (kind, text, mark) in enumerate(BODY):
    left, ind = SHAPE[kind]
    ps = ps_id[(left, ind)]
    cs = RED_ID if mark else CS_BODY
    h = 1200
    if vert + h > PAGE_LIMIT:
        vert = 0
    last = (n == len(BODY) - 1)
    if kind == 'bl':
        nch, trec = 1, b''
    else:
        d = (text + '\r').encode('utf-16-le')
        nch, trec = len(d) // 2, rec(H.T_PARA_TEXT, 1, d)
    hdr = struct.pack('<IIHBBHHHIH', nch | (0x80000000 if last else 0), 0,
                      ps, 0, 0, 1, 0, 1, 0, 0)
    body += rec(H.T_PARA_HEADER, 0, hdr)
    body += trec
    body += rec(H.T_PARA_CHAR_SHAPE, 1, struct.pack('<II', 0, cs))
    body += rec(H.T_PARA_LINE_SEG, 1, line_seg(vert, h))
    vert += h + h * 3 // 5

sec_new = prefix + bytes(body)
streams['DocInfo'] = zlib.compress(doc_new, 9)[2:-4]
streams['BodyText/Section0'] = zlib.compress(sec_new, 9)[2:-4]
streams['PrvText'] = (TITLE + '\r\n' + '\r\n'.join(t for k, t, m in BODY if t)[:900]).encode('utf-16-le')
olewrite.write_all(OUT, streams, clsid)

print('새 문단모양 %s · 빨강 글자모양 %d번' % (ps_id, RED_ID))
print('머리표 유지 · 본문 %d문단 새로 씀' % len(BODY))
print('만든 파일: %s  %d 바이트' % (OUT, os.path.getsize(OUT)))
