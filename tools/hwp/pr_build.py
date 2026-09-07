# -*- coding: utf-8 -*-
"""보도자료 초안 — 양식 파일의 표·필드·서식을 하나도 건드리지 않고 글자만 갈아 끼운다.

문단을 새로 만들지 않는다. 기존 문단의 PARA_TEXT 안에서
조종문자(필드 시작·끝)는 그대로 두고 '보이는 글자 덩어리'만 교체한다.
그래서 표 구조, 머리말, 사진 붙임 칸이 원본 그대로 남는다.
"""
import struct, zlib, os, sys
import hwpread as H
import olewrite

TPL = (r'C:\Users\user\Desktop\★국제협력처\보도자료'
       r'\20251107 키르기스스탄 오시국립대 교수단 방문\2024_홍보접수_양식_최종(키르기 교수단 방문).hwp')
OUT = sys.argv[1] if len(sys.argv) > 1 else '보도자료.hwp'

# 문단번호 → [바꿀 글자덩어리들]. 덩어리 개수는 원본과 같아야 한다.
# None 이면 그 덩어리는 그대로 둔다.
EDIT = {
    8:  ['2026. 9. 8.(화)', None],                      # 보도일(필드 안) / ' 부터 보도하여…'는 유지
    18: [None, '광주대, 외국인 신·편입생 152명 학부(과) 교수와 직접 연결'],   # 앞 공백 유지, 제목만
    21: ['- 오리엔테이션에 그치지 않고 11개 학부(과)별 개별 지도까지'],
    24: ['광주대학교(총장 김동진)는 지난 4일 호심관에서 2026학년도 2학기 학부 및 교환학생 과정 '
         '신·편입학 외국인 유학생 152명을 대상으로 오리엔테이션을 실시했다고 밝혔다.'],
    25: ['이번 오리엔테이션에는 경영학과를 비롯한 11개 학부(과)가 참여했으며, 참석 유학생은 '
         '중국어트랙 73명과 한국어트랙 79명이다. 국제협력처는 수강신청과 졸업 등 학사 기본사항과 '
         '국내·교내 생활 전반을 안내했다.'],
    27: ['이번 행사는 안내로 끝나지 않았다. 유학생을 학부(과)별로 나누어 앉힌 뒤 담당 교수와 직접 '
         '인사를 나누게 하고, 곧바로 학부(과)별 개별 오리엔테이션으로 이어갔다. 학부(과) 교수를 '
         '대상으로는 유학생 상담에 쓸 번역기 사용 방법을 따로 안내했다.'],
    29: ['김은실 국제협력처장은 “유학생이 입학 첫 주에 자기 학과 교수의 얼굴을 알고 가는 것이 '
         '학업 적응에 가장 큰 힘이 된다”며 “안내로 끝나는 오리엔테이션이 아니라 학부(과)와 실제로 '
         '연결되는 자리로 설계했다”고 말했다.'],
    30: ['국제협력처는 행사에 이어 학부(과)와의 간담회를 열어 유학생 지도 과정에서 나온 의견을 '
         '수렴했으며, 이를 바탕으로 학기 중 지원 방안을 보완해 나갈 계획이다.'],
}


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


def chunks(units):
    """글자 덩어리와 조종문자 덩어리로 쪼갠다. (종류, 시작, 끝) — 종류 'T'=글자, 'C'=조종"""
    out, k, n = [], 0, len(units)
    while k < n:
        c = units[k]
        if c in H.CH_INLINE or c in H.CH_EXT:
            out.append(('C', k, k + 8)); k += 8
        elif c in H.CH_CTRL:
            out.append(('C', k, k + 1)); k += 1
        else:
            j = k
            while j < n and units[j] > 31:
                j += 1
            out.append(('T', k, j)); k = j
    return out


streams, clsid = olewrite.read_all(TPL)
sec = zlib.decompress(streams['BodyText/Section0'], -15)
recs = list(H.records(sec))

out = bytearray()
pi = -1
pending = None          # (문단번호, 새 글자수, 원래 글자수)
changed = []
for tag, lvl, p, ho, po in recs:
    if tag == H.T_PARA_HEADER:
        pi += 1
        pending = None
        if pi in EDIT:
            pending = pi
            out += b''          # 헤더는 글자 수를 알아야 하므로 뒤에서 다시 쓴다
            hdr_slot = len(out)
            out += rec(tag, lvl, p)      # 일단 원본 그대로, 나중에 덮어쓴다
            hdr_info = (hdr_slot, len(rec(tag, lvl, p)), bytearray(p), lvl, tag)
            continue
        out += rec(tag, lvl, p)
        continue

    if tag == H.T_PARA_TEXT and pending is not None:
        units = [struct.unpack_from('<H', p, k * 2)[0] for k in range(len(p) // 2)]
        segs = chunks(units)
        tsegs = [s for s in segs if s[0] == 'T']
        news = EDIT[pending]
        assert len(news) == len(tsegs), \
            'P%d 글자덩어리 %d개인데 바꿀 값은 %d개' % (pending, len(tsegs), len(news))
        buf, ti = [], 0
        for kind, a, b in segs:
            if kind == 'C':
                buf.extend(units[a:b])
            else:
                nt = news[ti]; ti += 1
                buf.extend(units[a:b] if nt is None else [ord(ch) for ch in nt])
        data = b''.join(struct.pack('<H', u) for u in buf)
        out += rec(tag, lvl, data)
        # 문단 머리의 글자 수를 새 길이로 고친다
        slot, size, hb, hlvl, htag = hdr_info
        old = struct.unpack_from('<I', hb, 0)[0]
        struct.pack_into('<I', hb, 0, (old & 0x80000000) | len(buf))
        out[slot:slot + size] = rec(htag, hlvl, bytes(hb))
        changed.append((pending, len(units), len(buf)))
        pending = None
        continue

    if tag == H.T_PARA_CHAR_SHAPE and changed and changed[-1][0] == pi:
        # 글자모양 구간의 시작 위치가 새 길이를 넘지 않게 정리한다
        ent = [struct.unpack_from('<II', p, k * 8) for k in range(len(p) // 8)]
        newlen = changed[-1][2]
        ent = [(s, i) for s, i in ent if s < newlen] or [(0, ent[0][1])]
        out += rec(tag, lvl, b''.join(struct.pack('<II', s, i) for s, i in ent))
        # 개수가 줄면 문단 머리도 맞춰 준다
        slot, size, hb, hlvl, htag = hdr_info
        struct.pack_into('<H', hb, 12, len(ent))
        out[slot:slot + size] = rec(htag, hlvl, bytes(hb))
        continue

    out += rec(tag, lvl, p)

sec_new = bytes(out)
streams['BodyText/Section0'] = zlib.compress(sec_new, 9)[2:-4]
prv = '광주대, 외국인 신·편입생 152명 학부(과) 교수와 직접 연결'
streams['PrvText'] = prv.encode('utf-16-le')
olewrite.write_all(OUT, streams, clsid)

print('바꾼 문단')
for pnum, a, b in changed:
    print('   P%-3d %3d자 → %3d자' % (pnum, a, b))
print('구역0 %d → %d 바이트' % (len(sec), len(sec_new)))
print('만든 파일: %s  %d 바이트' % (OUT, os.path.getsize(OUT)))
