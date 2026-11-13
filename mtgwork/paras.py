# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
from insp2 import SEC, cell

def top_paras(inner):
    """top-level <hp:p> ... </hp:p> spans (depth 0)."""
    out, depth, start = [], 0, None
    for m in re.finditer(r'<hp:p[ >]|</hp:p>', inner):
        if m.group(0) != '</hp:p>':
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, m.end()))
    return out

for col, row in [(7, 4), (7, 5)]:
    a, b = cell(SEC, col, row)[0]
    inner = SEC[a:b]
    print('########## c%d r%d  base=%d' % (col, row, a))
    for i, (s, e) in enumerate(top_paras(inner)):
        p = inner[s:e]
        pp = re.search(r'paraPrIDRef="(\d+)"', p).group(1)
        cps = sorted(set(re.findall(r'charPrIDRef="(\d+)"', p)))
        txt = ''.join(re.findall(r'<hp:t>(.*?)</hp:t>', p, re.S))
        tag = 'TBL' if '<hp:tbl' in p else '   '
        print('%3d %s pp=%-3s cp=%-12s abs=%d..%d | %s' % (i, tag, pp, ','.join(cps), a+s, a+e, txt[:95].replace('\n','\n')))
