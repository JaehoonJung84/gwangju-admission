# -*- coding: utf-8 -*-
import zipfile, re, sys
sys.stdout.reconfigure(encoding='utf-8')
SEC = zipfile.ZipFile('p.hwpx').read('Contents/section0.xml').decode('utf-8')

OPEN = re.compile(r'<hp:subList[ >]')
CLOSE = '</hp:subList>'

def match_open(xml, close_pos):
    """close_pos = index of the '</hp:subList>' that we must pair."""
    toks = []
    for m in re.finditer(r'<hp:subList[ >]|</hp:subList>', xml[:close_pos + len(CLOSE)]):
        toks.append((m.start(), m.group(0)))
    depth = 0
    for pos, t in reversed(toks):
        if t == CLOSE:
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return xml.index('>', pos) + 1
    raise SystemExit('unmatched')

def cell(xml, col, row):
    addr = '<hp:cellAddr colAddr="%d" rowAddr="%d"/>' % (col, row)
    hits = [m.start() for m in re.finditer(re.escape(addr), xml)]
    return [(match_open(xml, xml.rindex(CLOSE, 0, h)), xml.rindex(CLOSE, 0, h)) for h in hits]

if __name__ == '__main__':
    for col, row in [(7, 4), (7, 5), (7, 6)]:
        for a, b in cell(SEC, col, row):
            inner = SEC[a:b]
            print('=== c%d r%d  %d..%d len=%d tbl=%d' % (col, row, a, b, b - a, inner.count('<hp:tbl')))
            txt = ' / '.join(re.findall(r'<hp:t>(.*?)</hp:t>', inner, re.S))[:120]
            print('   ', txt.replace('\n', ' '))
