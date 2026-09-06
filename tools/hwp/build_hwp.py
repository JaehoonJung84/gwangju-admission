# -*- coding: utf-8 -*-
"""한글(HWP) 문서 생성기 — 줄바꿈 대신 문단 모양으로 정렬한다.

원칙 (2026-09-06 사용자 요청, 앞으로 만드는 모든 hwp 에 적용):
  · 한 항목은 무조건 한 문단. Enter 로 줄을 나눠 앞단을 맞추지 않는다.
  · 들여쓰기는 글 앞의 공백이 아니라 문단 모양의 왼쪽 여백·내어쓰기가 맡는다.
  · 그래야 나중에 글을 고쳐도 정렬이 저절로 따라오고 서식이 깨지지 않는다.

양식 파일의 DocInfo(글꼴·쪽 설정)와 첫 문단(구역 정의)은 그대로 물려받고,
필요한 글자색·문단모양만 새로 만들어 끼워 넣는다.
"""
import struct, zlib, sys, os
import hwpread as H
import olewrite

TPL = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/교무위원회의(20260812)-국제협력처.hwp'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out.hwp'

from scen_content import BODY

# ── 줄 종류별 서식
#    글자모양: 13 큰제목 / 19 절제목 / 20 블록제목 / 17 본문 / 16 대사
#    문단모양: 아래에서 (왼쪽여백, 내어쓰기) 로 새로 만든다. 단위는 HWPUNIT(1/7200인치),
#              12pt 한글 한 글자 ≈ 1200.
SHAPE = {                    # kind: (왼쪽여백, 내어쓰기, 글자모양)
    't1': (0,    0,     13),
    't2': (0,    0,     19),
    'h':  (600,  0,     20),
    'b':  (2400, 0,     17),
    's':  (3600, 0,     16),
    'li': (3600, -1800, 17),   # 기호(①□×)+한 칸이 왼쪽으로 튀어나오고, 이어지는 줄은 글 시작에 맞춤
    'bl': (0,    0,     17),
}
NEWCOL = {'red': 0x000000FF, 'blue': 0x00C05A1B}   # COLORREF 는 0x00BBGGRR
PAGE_LIMIT = 66900


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


streams, clsid = olewrite.read_all(TPL)
unz = lambda b: zlib.decompress(b, -15)
doc = unz(streams['DocInfo'])
sec = unz(streams['BodyText/Section0'])

recs = list(H.records(doc))
cs_idx = [i for i, r in enumerate(recs) if r[0] == H.T_CHAR_SHAPE]
ps_idx = [i for i, r in enumerate(recs) if r[0] == H.TAG + 9]

# ── 새 글자모양(색만 바꾼 복제본)
col_id, col_recs = {}, []
for name, rgb in NEWCOL.items():
    b = bytearray(recs[cs_idx[17]][2])
    struct.pack_into('<I', b, 52, rgb)
    col_id[name] = len(cs_idx) + len(col_recs)
    col_recs.append(rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(b)))

# ── 새 문단모양(왼쪽 여백·내어쓰기만 바꾼 복제본)
want = sorted({(l, i) for l, i, _ in SHAPE.values()})
ps_id, ps_recs = {}, []
for left, ind in want:
    b = bytearray(recs[ps_idx[23]][2])       # 23번 = 여백 0 · 내어쓰기 0 인 본문 문단모양
    struct.pack_into('<i', b, 4, left)       # 왼쪽 여백
    struct.pack_into('<i', b, 12, ind)       # 내어쓰기(음수)
    ps_id[(left, ind)] = len(ps_idx) + len(ps_recs)
    ps_recs.append(rec(H.TAG + 9, recs[ps_idx[23]][1], bytes(b)))

out = bytearray()
last_cs, last_ps = cs_idx[-1], ps_idx[-1]
for i, (tag, lvl, p, ho, po) in enumerate(recs):
    body = bytearray(p)
    if tag == H.TAG + 1:                                   # ID_MAPPINGS
        n = struct.unpack_from('<i', body, 9 * 4)[0]
        assert n == len(cs_idx), '글자모양 수 어긋남'
        struct.pack_into('<i', body, 9 * 4, n + len(col_recs))
        m = struct.unpack_from('<i', body, 13 * 4)[0]
        assert m == len(ps_idx), '문단모양 수 어긋남'
        struct.pack_into('<i', body, 13 * 4, m + len(ps_recs))
    if tag == H.TAG + 0 and len(body) >= 26:               # 캐럿 위치 초기화
        struct.pack_into('<III', body, 14, 0, 0, 0)
    out += rec(tag, lvl, bytes(body))
    if i == last_cs:
        out += b''.join(col_recs)
    if i == last_ps:
        out += b''.join(ps_recs)
doc_new = bytes(out)

# ── 구역0 : 첫 문단(구역 정의)만 남기고 본문을 새로 쓴다
srecs = list(H.records(sec))
heads = [i for i, r in enumerate(srecs) if r[0] == H.T_PARA_HEADER]
prefix = sec[:srecs[heads[1]][3]]

# 첫 문단 앞머리의 조종문자(구역·단 정의)는 절대 건드리지 않는다.
# 보이는 글자만 공백으로 바꾼다 — 지우면 한글이 '파일이 손상되었습니다'로 거부한다.
_o = bytearray()
for tag, lvl, p, ho, po in H.records(prefix):
    if tag == H.T_PARA_TEXT:
        b = bytearray(p)
        k, n = 0, len(b) // 2
        while k < n:
            c = struct.unpack_from('<H', b, k * 2)[0]
            if c in H.CH_CTRL:
                k += 1
            elif c in H.CH_INLINE or c in H.CH_EXT:
                k += 8
            else:
                struct.pack_into('<H', b, k * 2, 0x20)
                k += 1
        _o += rec(tag, lvl, bytes(b))
    else:
        _o += rec(tag, lvl, p)
prefix = bytes(_o)

child_lvl = next(r[1] for r in srecs if r[0] == H.T_PARA_TEXT)
segs = [r[2] for r in srecs if r[0] == H.T_PARA_LINE_SEG]
SEG_W = struct.unpack_from('<i', segs[1], 28)[0]
p0 = segs[0]
vert = (struct.unpack_from('<i', p0, 4)[0] + struct.unpack_from('<i', p0, 8)[0]
        + struct.unpack_from('<i', p0, 20)[0])

SIZE = {13: 1800, 16: 1200, 17: 1200, 19: 1400, 20: 1300}


def line_seg(v, h):
    sp = h * 3 // 5
    return struct.pack('<I8i', 0, v, h, h, h * 85 // 100, sp, 0, SEG_W, 0x00060000)


body_out = bytearray()
for n, (kind, text, red) in enumerate(BODY):
    left, ind, cs = SHAPE[kind]
    ps = ps_id[(left, ind)]
    if kind == 's':
        cs = col_id['blue']                 # 입으로 말하는 대사
    if red:
        cs = col_id['red']                  # 놓치면 안 되는 경고
    h = SIZE.get(cs, 1200)
    if vert + h > PAGE_LIMIT:
        vert = 0
    last = (n == len(BODY) - 1)
    if kind == 'bl':
        nchars, trec = 1, b''
    else:
        data = (text + '\r').encode('utf-16-le')
        nchars, trec = len(data) // 2, rec(H.T_PARA_TEXT, child_lvl, data)
    hdr = struct.pack('<IIHBBHHHIH', nchars | (0x80000000 if last else 0), 0,
                      ps, 0, 0, 1, 0, 1, 0, 0)
    body_out += rec(H.T_PARA_HEADER, 0, hdr)
    body_out += trec
    body_out += rec(H.T_PARA_CHAR_SHAPE, child_lvl, struct.pack('<II', 0, cs))
    body_out += rec(H.T_PARA_LINE_SEG, child_lvl, line_seg(vert, h))
    vert += h + h * 3 // 5

sec_new = prefix + bytes(body_out)

prv = '\r\n'.join(t for k, t, r in BODY if t)[:1000]
streams['PrvText'] = prv.encode('utf-16-le')
z = lambda b: zlib.compress(b, 9)[2:-4]
streams['DocInfo'] = z(doc_new)
streams['BodyText/Section0'] = z(sec_new)
olewrite.write_all(OUT, streams, clsid)

print('새 글자모양 %s' % col_id)
print('새 문단모양 %s' % {k: v for k, v in ps_id.items()})
print('문단 %d개 (줄바꿈 없이 한 항목 한 문단)' % len(BODY))
print('만든 파일: %s  %d 바이트' % (OUT, os.path.getsize(OUT)))
