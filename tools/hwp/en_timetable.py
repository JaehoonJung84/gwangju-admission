# -*- coding: utf-8 -*-
"""영어트랙 시간표 국문 → 영문 변환.

원본 표(칸 색·병합·테두리)를 레코드째 그대로 두고 글월만 영문으로 바꾼다.
글자 수가 바뀌므로 PARA_HEADER 의 nChars 와 글자모양 시작위치를 함께 고친다.
"""
import struct, zlib, os, sys
import hwpread as H
import olewrite

SRC = (r'C:\Users\user\Desktop\★국제협력처\영어트랙\2026-2학기'
       r'\영어트랙 시간표(재학생 2026-2학기)_최종 (1).hwp')
OUT = sys.argv[1] if len(sys.argv) > 1 else '영문시간표.hwp'

# 국문 글월 → 영문 글월. 정확히 일치할 때만 바꾼다.
MAP = {
    ' 1. 영어트랙 2학기 시간표(2026-1학기 입학생)':
        ' 1. English Track Timetable – 2nd Semester (admitted 2026-1)',

    # 표 머리
    '    요일': '    Day',
    '교시': 'Period',
    '시간': 'Time',
    '주간': 'Weekly',
    '시수': 'Hours',
    '월': 'Mon', '화': 'Tue', '수': 'Wed', '목': 'Thu', '금': 'Fri',

    # 교시 이름
    '1교시': 'Period 1', '2교시': 'Period 2', '3교시': 'Period 3', '4교시': 'Period 4',
    '2-1교시': 'Period 2-1', '3-1교시': 'Period 3-1',
    '4-1교시': 'Period 4-1', '4-2교시': 'Period 4-2',
    '4-3교시': 'Period 4-3', '4-4교시': 'Period 4-4',
    '쉬는시간': 'Break', '15분': '15 min',

    # 수업 (과목명 + 강의실)
    '영어로배우는사고와설득의기술':
        'Thinking & Persuasion through English (Hosim Hall 809)',
    'K컬처와글로벌감수성':
        'K-Culture & Global Sensibility (Hosim Hall 806)',
    '이산치구조':
        'Discrete Structures (Computer Eng. Lab 1, Rm 0313)',
    '컴퓨터프로그래밍1':
        'Computer Programming 1 (Computer Eng. Lab 2, Rm 0319)',
    'EnglishGO글로벌영어발표와프로젝트(미란다)':
        'EnglishGO Global Presentation & Project (Prof. Miranda, Hosim Hall 708)',

    # 표 아래 안내
    '※ 영어트랙 재학생': '※ English Track – Current Students',
    '  *경영학과* 16학점': '  *Business Administration* – 16 credits',
    '  *컴퓨터공학과* 17학점': '  *Computer Engineering* – 17 credits',
    '  - 챌린지온옴니버스(온라인영상 / 4115) 2학점(기초교양) Challenge On Omnibus ':
        '  - Challenge On Omnibus (online video / 4115) 2 cr., Basic Liberal Arts',
    '  - 머니플래닝 (온라인영상 / 4029) 2학점(기초교양) Money Planning ':
        '  - Money Planning (online video / 4029) 2 cr., Basic Liberal Arts',
    '  - 컴퓨터프로그래밍1 3학점(일반선택 / 5066) Computer Programming 1 ':
        '  - Computer Programming 1 (5066) 3 cr., General Elective — Computer Eng. Lab 2 (Rm 0319)',
    '  - 컴퓨터프로그래밍1 3학점(전공선택 / 5066) Computer Programming 1 ':
        '  - Computer Programming 1 (5066) 3 cr., Major Elective — Computer Eng. Lab 2 (Rm 0319)',
    '  - 이산치구조 3학점(일반선택 / 4461) Discrete Structures ':
        '  - Discrete Structures (4461) 3 cr., General Elective — Computer Eng. Lab 1 (Rm 0313)',
    '  - 이산치구조 3학점(전공필수 / 4461) Discrete Structures ':
        '  - Discrete Structures (4461) 3 cr., Major Required — Computer Eng. Lab 1 (Rm 0313)',
    '  - K컬처와글로벌감수성  3학점 (교양선택 / 4183) K-Culture and Global Sensibility':
        '  - K-Culture and Global Sensibility (4183) 3 cr., Liberal Arts Elective — Hosim Hall 806',
    '  - 영어로배우는사고와설득의기술 3학점(교양선택 / 4199)':
        '  - Thinking and Persuasion Skills through English (4199) 3 cr., Liberal Arts Elective',
    '    Thinking and Persuasion Skills through English ':
        '    Hosim Hall 809 (Smart Classroom)',
    '  - EnglishGO글로벌영어발표와프로젝트 3학점(교양선택 / 5256) EnglishGO Global Presentation & Project':
        '  - EnglishGO Global Presentation & Project (5256) 3 cr., Liberal Arts Elective — Hosim Hall 708',
}


def rec(tag, level, payload):
    if len(payload) < 0xFFF:
        return struct.pack('<I', tag | (level << 10) | (len(payload) << 20)) + payload
    return struct.pack('<II', tag | (level << 10) | (0xFFF << 20), len(payload)) + payload


# 조종문자 길이 — 8글자짜리(구역 정의·탭·표 등)와 1글자짜리를 가른다.
WIDE = set([1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23] + [4, 5, 6, 7, 8, 9, 19, 20])


def tokens(s):
    """글월을 (보이는 글, True) / (조종문자 덩어리, False) 조각으로 가른다."""
    out, buf, i = [], '', 0
    while i < len(s):
        c = ord(s[i])
        if c in WIDE and i + 8 <= len(s):
            if buf:
                out.append((buf, True)); buf = ''
            out.append((s[i:i + 8], False)); i += 8
        elif c < 32 and c not in (10,):
            if buf:
                out.append((buf, True)); buf = ''
            out.append((s[i], False)); i += 1
        else:
            buf += s[i]; i += 1
    if buf:
        out.append((buf, True))
    return out


streams, clsid = olewrite.read_all(SRC)
sec = zlib.decompress(streams['BodyText/Section0'], -15)
recs = list(H.records(sec))

out = bytearray()
slot = None                       # 직전 PARA_HEADER 위치
hits, missed = 0, {}
for idx, (tag, lvl, p, ho, po) in enumerate(recs):
    if tag == H.T_PARA_HEADER:
        slot = (len(out), len(rec(tag, lvl, p)), bytearray(p), lvl, tag)
        out += rec(tag, lvl, p)
        continue

    if tag == H.T_PARA_TEXT:
        old = p.decode('utf-16-le')
        tail = '\r' if old.endswith('\r') else ''
        parts, changed = [], False
        for seg, visible in tokens(old[:-1] if tail else old):
            if visible and seg in MAP:
                parts.append(MAP[seg]); changed = True
            else:
                if visible and seg.strip() and any(ord(c) > 0x1100 for c in seg):
                    missed[seg] = missed.get(seg, 0) + 1
                parts.append(seg)
        if not changed:
            out += rec(tag, lvl, p)
            continue
        hits += 1
        data = (''.join(parts) + tail).encode('utf-16-le')
        out += rec(tag, lvl, data)
        s, size, hb, hlvl, htag = slot
        n0 = struct.unpack_from('<I', hb, 0)[0]
        struct.pack_into('<I', hb, 0, (n0 & 0x80000000) | (len(data) // 2))
        out[s:s + size] = rec(htag, hlvl, bytes(hb))
        slot = (s, len(rec(htag, hlvl, bytes(hb))), hb, hlvl, htag)
        # 글자모양 시작위치가 새 길이를 넘지 않도록 다듬는다
        nxt = recs[idx + 1]
        if nxt[0] == H.T_PARA_CHAR_SHAPE and len(nxt[2]) > 8:
            lim = len(data) // 2
            keep, seen = [], set()
            for k in range(len(nxt[2]) // 8):
                pos, cs = struct.unpack_from('<II', nxt[2], k * 8)
                pos = 0 if k == 0 else min(pos, max(lim - 1, 0))
                if pos in seen:
                    continue
                seen.add(pos)
                keep.append((pos, cs))
            recs[idx + 1] = (nxt[0], nxt[1],
                             b''.join(struct.pack('<II', a, b) for a, b in keep),
                             nxt[3], nxt[4])
            # 글자모양 개수는 오프셋 12. (14는 범위태그 개수라 건드리면 한글이 파일을 거부한다)
            struct.pack_into('<H', hb, 12, len(keep))
            out[s:s + len(rec(htag, hlvl, bytes(hb)))] = rec(htag, hlvl, bytes(hb))
        continue

    out += rec(tag, lvl, recs[idx][2])

streams['BodyText/Section0'] = zlib.compress(bytes(out), 9)[2:-4]
streams['PrvText'] = 'English Track Timetable 2026-2'.encode('utf-16-le')
olewrite.write_all(OUT, streams, clsid)

print('바꾼 글월 %d개' % hits)
if missed:
    print('아직 국문으로 남은 글월:')
    for k, v in missed.items():
        print('   %r x%d' % (k[:60], v))
print('만든 파일: %s  %d 바이트' % (OUT, os.path.getsize(OUT)))
