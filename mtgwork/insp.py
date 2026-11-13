# -*- coding: utf-8 -*-
import zipfile, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sec = zipfile.ZipFile('p.hwpx').read('Contents/section0.xml').decode('utf-8')

def cell_regions(xml):
    out = []
    for m in re.finditer(r'<hp:cellAddr colAddr="(\d+)" rowAddr="(\d+)"/>', xml):
        end = m.start()
        close = xml.rindex('</hp:subList>', 0, end)
        opn = xml.rindex('<hp:subList ', 0, close)
        opn = xml.index('>', opn) + 1
        out.append((int(m.group(1)), int(m.group(2)), opn, close))
    return out

regs = cell_regions(sec)
for col, row, a, b in regs:
    inner = sec[a:b]
    txt = ' / '.join(re.findall(r'<hp:t>(.*?)</hp:t>', inner, re.S))[:90]
    nest = inner.count('<hp:tbl')
    print('c%-3d r%-3d len=%-7d tbl=%d  %s' % (col, row, b - a, nest, txt.replace('\n', ' ')))
