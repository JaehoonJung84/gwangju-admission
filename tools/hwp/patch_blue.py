# -*- coding: utf-8 -*-
"""build_scen.py 에 파란 글자모양을 하나 더 만들고, 대사(kind 's')에 입힌다.
빨강을 넣던 방식 그대로 — 본문 글자모양을 복제해 색만 바꿔 마지막 글자모양 뒤에 끼운다."""
import io

P = 'build_scen.py'
s = io.open(P, encoding='utf-8').read()

old = """RED_ID = len(cs_idx)                       # 새 글자모양의 번호 = 기존 개수
base = bytearray(recs[cs_idx[17]][2])      # 본문 글자모양 17번을 복제
struct.pack_into('<I', base, 52, 0x000000FF)   # 글자색만 빨강으로
red_rec = rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(base))"""

new = """RED_ID = len(cs_idx)                       # 새 글자모양의 번호 = 기존 개수
BLUE_ID = RED_ID + 1
base = bytearray(recs[cs_idx[17]][2])      # 본문 글자모양 17번을 복제
struct.pack_into('<I', base, 52, 0x000000FF)   # 글자색만 빨강으로 (COLORREF 는 0x00BBGGRR)
red_rec = rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(base))
base2 = bytearray(recs[cs_idx[17]][2])     # 같은 본문 글자모양을 한 번 더 복제
struct.pack_into('<I', base2, 52, 0x00C05A1B)  # 파랑 #1B5AC0
blue_rec = rec(H.T_CHAR_SHAPE, recs[cs_idx[17]][1], bytes(base2))"""
assert old in s
s = s.replace(old, new)

s = s.replace("        struct.pack_into('<i', body, 9 * 4, n + 1)",
              "        struct.pack_into('<i', body, 9 * 4, n + 2)")
s = s.replace("""    if i == last_cs:
        out += red_rec""",
              """    if i == last_cs:
        out += red_rec
        out += blue_rec""")

# 대사 줄은 파란색으로
s = s.replace("""    ps, cs = KIND[kind]
    if red:
        cs = RED_ID""",
              """    ps, cs = KIND[kind]
    if kind == 's':
        cs = BLUE_ID                       # 입으로 말하는 대사만 파랗게
    if red:
        cs = RED_ID""")

s = s.replace("print('빨간 글자모양 번호 %d (글자모양 %d개 → %d개)' % (RED_ID, len(cs_idx), len(cs_idx) + 1))",
              "print('빨강 %d번 · 파랑 %d번 (글자모양 %d개 → %d개)'\n"
              "      % (RED_ID, BLUE_ID, len(cs_idx), len(cs_idx) + 2))")

io.open('build_blue.py', 'w', encoding='utf-8').write(s)
print('build_blue.py 준비 완료')
