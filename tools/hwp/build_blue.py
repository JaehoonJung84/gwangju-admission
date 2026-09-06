# -*- coding: utf-8 -*-
"""교무위원회의(20260909)-국제협력처.hwp 만들기.

20260812 교무위원회의 파일을 틀로 삼는다. DocInfo(글자모양·문단모양·글꼴·쪽 설정)와
구역 정의를 담은 첫 문단은 손대지 않고, 본문 문단만 새로 쓴다.
"""
import struct, zlib, sys, os
import hwpread as H
import olewrite
from scen_content import BODY

SRC = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/교무위원회의(20260812)-국제협력처.hwp'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out.hwp'

# 줄 종류별 (문단모양, 글자모양) — 양식 파일에서 그대로 가져온 번호
KIND = {
    't1': (25, 13), 't2': (17, 19), 'h': (23, 20),
    'b':  (23, 17), 's':  (23, 16), 'bl': (23, 17),
}
SIZE = {13: 1800, 16: 1200, 17: 1200, 19: 1400, 20: 1300, 21: 1200, 22: 1200, 26: 1200}
PAGE_LIMIT = 66900


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


# ────────────────────────────── 원본 읽기
streams, clsid = olewrite.read_all(SRC)
head = streams['FileHeader']
assert head[36] & 1, '압축 문서가 아니다'
unz = lambda b: zlib.decompress(b, -15)
doc = unz(streams['DocInfo'])
sec = unz(streams['BodyText/Section0'])

# ────────────────────────────── DocInfo : 빨간 글자모양 추가
recs = list(H.records(doc))
cs_idx = [i for i, r in enumerate(recs) if r[0] == H.T_CHAR_SHAPE]
RED_ID = len(cs_idx)                       # 새 글자모양의 번호 = 기존 개수
BLUE_ID = RED_ID + 1
base = bytearray(recs[cs_idx[17]][2])      # 본문 글자모양 17번을 복제
struct.pack_into('<I', base, 52, 0x000000FF)   # 글자색만 빨강으로 (COLORREF 는 0x00BBGGRR)
red_rec = rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(base))
base2 = bytearray(recs[cs_idx[17]][2])     # 같은 본문 글자모양을 한 번 더 복제
struct.pack_into('<I', base2, 52, 0x00C05A1B)  # 파랑 #1B5AC0
blue_rec = rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(base2))

out = bytearray()
last_cs = cs_idx[-1]
for i, (tag, lvl, p, ho, po) in enumerate(recs):
    body = bytearray(p)
    if tag == H.TAG + 1:                                   # ID_MAPPINGS : 글자모양 수 +1
        n = struct.unpack_from('<i', body, 9 * 4)[0]
        struct.pack_into('<i', body, 9 * 4, n + 2)
        assert n == len(cs_idx), '글자모양 수가 어긋난다 (%d vs %d)' % (n, len(cs_idx))
    if tag == H.TAG + 0 and len(body) >= 26:               # 문서 속성 : 캐럿 위치 초기화
        struct.pack_into('<III', body, 14, 0, 0, 0)
    out += rec(tag, lvl, bytes(body))
    if i == last_cs:
        out += red_rec
        out += blue_rec                                     # 마지막 글자모양 바로 뒤에 끼운다
doc_new = bytes(out)

# ────────────────────────────── Section0 : 첫 문단(구역 정의)만 남기고 새로 쓴다
srecs = list(H.records(sec))
heads = [i for i, r in enumerate(srecs) if r[0] == H.T_PARA_HEADER]
keep_end = srecs[heads[1]][3]              # 두 번째 문단 머리의 시작 위치
prefix = sec[:keep_end]                    # 문단0 통째로 (구역 정의·쪽 설정 포함)

# 문단0 앞머리에는 구역 정의(secd)·단 정의 같은 조종문자가 들어 있다.
# 그걸 지우면 한글이 파일을 손상으로 판단하므로, 조종문자는 그대로 두고
# 눈에 보이는 글자("1. 국제협력처")만 공백으로 바꾼다.
# 글자 수가 그대로라 레코드 크기도 nChars 도 변하지 않는다.
_out = bytearray()
for _tag, _lvl, _p, _ho, _po in H.records(prefix):
    if _tag == H.T_PARA_TEXT:
        _b = bytearray(_p)
        _k = 0
        _n = len(_b) // 2
        while _k < _n:
            _c = struct.unpack_from('<H', _b, _k * 2)[0]
            if _c in H.CH_CTRL:                       # 문단 끝 표시 등 — 그대로 둔다
                _k += 1
            elif _c in H.CH_INLINE or _c in H.CH_EXT:  # 조종문자 8글자 — 건드리지 않는다
                _k += 8
            else:                                      # 보이는 글자만 공백으로
                struct.pack_into('<H', _b, _k * 2, 0x20)
                _k += 1
        _out += rec(_tag, _lvl, bytes(_b))
    else:
        _out += rec(_tag, _lvl, _p)
prefix = bytes(_out)

# 문단0 의 자식 레코드 층(level)을 그대로 빌려 쓴다
child_lvl = next(r[1] for r in srecs if r[0] == H.T_PARA_TEXT)

segs = [r[2] for r in srecs if r[0] == H.T_PARA_LINE_SEG]
p0_seg = segs[0]                                   # 문단0(제목줄)의 줄 정보
SEG_W = struct.unpack_from('<i', segs[1], 28)[0]   # 본문 줄의 가로 폭
assert SEG_W > 0

# 문단0 이 차지한 세로 위치 다음부터 이어 쌓는다
vert = (struct.unpack_from('<i', p0_seg, 4)[0]
        + struct.unpack_from('<i', p0_seg, 8)[0]
        + struct.unpack_from('<i', p0_seg, 20)[0])


def line_seg(v, h):
    sp = h * 3 // 5
    return struct.pack('<I8i', 0, v, h, h, h * 85 // 100, sp, 0, SEG_W, 0x00060000)


body_out = bytearray()
for n, (kind, text, red) in enumerate(BODY):
    ps, cs = KIND[kind]
    if kind == 's':
        cs = BLUE_ID                       # 입으로 말하는 대사만 파랗게
    if red:
        cs = RED_ID
    h = SIZE.get(cs, 1200)
    if vert + h > PAGE_LIMIT:
        vert = 0
    last = (n == len(BODY) - 1)

    if kind == 'bl':                       # 빈 문단 : PARA_TEXT 레코드를 두지 않는다
        nchars, trec = 1, b''
    else:
        data = (text + '\r').encode('utf-16-le')
        nchars, trec = len(data) // 2, rec(H.T_PARA_TEXT, child_lvl, data)

    hdr = struct.pack('<IIHBBHHHIH',
                      nchars | (0x80000000 if last else 0), 0,
                      ps, 0, 0, 1, 0, 1, 0, 0)
    body_out += rec(H.T_PARA_HEADER, 0, hdr)
    body_out += trec
    body_out += rec(H.T_PARA_CHAR_SHAPE, child_lvl, struct.pack('<II', 0, cs))
    body_out += rec(H.T_PARA_LINE_SEG, child_lvl, line_seg(vert, h))
    vert += h + h * 3 // 5

sec_new = prefix + bytes(body_out)

# ────────────────────────────── 미리보기 글월도 새 내용으로
prv = '\r\n'.join(['1. 국제협력처'] + [t for k, t, r in BODY if t])[:1000]
streams['PrvText'] = prv.encode('utf-16-le')

z = lambda b: zlib.compress(b, 9)[2:-4]      # 원시 deflate (zlib 머리·꼬리 제거)
streams['DocInfo'] = z(doc_new)
streams['BodyText/Section0'] = z(sec_new)

olewrite.write_all(OUT, streams, clsid)

print('Section0  원본 %d → 새 %d 바이트' % (len(sec), len(sec_new)))
print('빨강 %d번 · 파랑 %d번 (글자모양 %d개 → %d개)'
      % (RED_ID, BLUE_ID, len(cs_idx), len(cs_idx) + 2))
print('문단 수 1(구역정의) + %d = %d' % (len(BODY), len(BODY) + 1))
print('만든 파일: %s  %d 바이트' % (OUT, os.path.getsize(OUT)))
