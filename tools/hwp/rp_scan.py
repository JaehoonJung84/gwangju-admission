# -*- coding: utf-8 -*-
"""보도자료 양식의 레코드 배치를 본다. 표는 그대로 두고 본문만 갈아 끼우기 위한 사전 조사."""
import struct
import hwpread as H

P = (r'C:\Users\user\Desktop\★국제협력처\0. 보고서'
     r'\20260904 2026-2학기 외국인 유학생 학부(과) 간담회 요청·민원사항 보고.hwp')

doc, secs, comp = H.sections(P)
sec = secs[0]
recs = list(H.records(sec))
print('구역0 %d바이트 · 레코드 %d개' % (len(sec), len(recs)))

pi = -1
for n, (tag, lvl, p, ho, po) in enumerate(recs):
    if tag == H.T_PARA_HEADER:
        pi += 1
        nCh = struct.unpack_from('<I', p, 0)[0]
        cm = struct.unpack_from('<I', p, 4)[0]
        ps, st, ct, nCS, nRT, nLS = struct.unpack_from('<HBBHHH', p, 8)
        cur = {'i': pi, 'n': n, 'off': ho, 'lvl': lvl, 'nCh': nCh & 0x7FFFFFFF,
               'last': bool(nCh & 0x80000000), 'cm': cm, 'ps': ps, 'st': st,
               'nCS': nCS, 'nLS': nLS, 'txt': '', 'cs': []}
        print('P%-3d rec%-4d lvl%-2d ps=%-3d st=%d nCh=%-4d nCS=%d nLS=%-2d cm=0x%X'
              % (pi, n, lvl, ps, st, cur['nCh'], nCS, nLS, cm), end='')
    elif tag == H.T_PARA_TEXT:
        t = ''.join(c for c, _ in H.para_text(p))
        print('  %r' % t.replace('\n', '¶')[:66])
    elif tag == H.T_PARA_CHAR_SHAPE:
        pass
    elif tag == H.T_PARA_HEADER:
        pass
    else:
        nm = {H.T_PARA_LINE_SEG: 'LINESEG', H.T_CTRL_HEADER: 'CTRL',
              H.T_LIST_HEADER: 'LIST', H.T_TABLE: 'TABLE'}.get(tag, 'tag%d' % tag)
        if nm in ('CTRL', 'LIST', 'TABLE'):
            extra = ''
            if nm == 'CTRL' and len(p) >= 4:
                extra = ' id=%r' % p[:4][::-1].decode('latin-1')
            print('\n      └ %s lvl%d%s' % (nm, lvl, extra), end='')
print()
