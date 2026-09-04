# -*- coding: utf-8 -*-
"""교무위원회의 양식 파일의 뼈대를 재는 도구. 추측 대신 실제 값을 확인한다."""
import struct, sys, collections
import hwpread as H

path = sys.argv[1]
doc, secs, comp = H.sections(path)
print('압축', comp, '| DocInfo', len(doc), '| 구역 수', len(secs), [len(s) for s in secs])

# ── ID_MAPPINGS 확인
for tag, lvl, p, ho, po in H.records(doc):
    if tag == H.TAG + 1:
        n = len(p) // 4
        vals = struct.unpack_from('<%di' % n, p, 0)
        print('ID_MAPPINGS %d개:' % n, vals)
        break
cnt = collections.Counter(t for t, _, _, _, _ in H.records(doc))
print('DocInfo 태그별 수:', {k: v for k, v in sorted(cnt.items())})

# ── PARA_HEADER 필드 해석이 맞는지 실제 레코드와 대조
print('\n--- 본문 구역0 문단 검증 ---')
sec = secs[0]
recs = list(H.records(sec))
print('레코드 태그 분포:', {k: v for k, v in sorted(collections.Counter(r[0] for r in recs).items())})

cur = None
rows = []
bad = 0
for tag, lvl, p, ho, po in recs:
    if tag == H.T_PARA_HEADER:
        cur = {'hdr': p, 'lvl': lvl, 'text': None, 'cs': None, 'ls': None}
        rows.append(cur)
    elif cur is None:
        continue
    elif tag == H.T_PARA_TEXT:
        cur['text'] = p
    elif tag == H.T_PARA_CHAR_SHAPE:
        cur['cs'] = p
    elif tag == H.T_PARA_LINE_SEG:
        cur['ls'] = p

for i, r in enumerate(rows):
    h = r['hdr']
    nChars, ctrlMask = struct.unpack_from('<II', h, 0)
    paraShape, styleId, colType, nCS, nRT, nLS = struct.unpack_from('<HBBHHH', h, 8)
    tlen = len(r['text']) // 2 if r['text'] is not None else 0
    cs = len(r['cs']) // 8 if r['cs'] is not None else 0
    ls = len(r['ls']) // 36 if r['ls'] is not None else 0
    ok = (nChars == tlen or (r['text'] is None and nChars in (0, 1))) and nCS == cs and nLS == ls
    if not ok:
        bad += 1
        if bad <= 6:
            print(' 불일치 [%d] hdr=%d nChars=%d/글자%d nCS=%d/%d nLS=%d/%d hdrlen=%d'
                  % (i, len(h), nChars, tlen, nCS, cs, nLS, ls, len(h)))
    rows[i]['f'] = (nChars, ctrlMask, paraShape, styleId, colType, nCS, nRT, nLS, len(h))

print('문단 수 %d, 필드 해석 불일치 %d 건' % (len(rows), bad))
print('PARA_HEADER 크기 종류:', sorted({r['f'][8] for r in rows}))
print('paraShapeId 종류:', sorted({r['f'][2] for r in rows}))
print('styleId 종류:', sorted({r['f'][3] for r in rows}))
print('LINE_SEG 항목 크기 확인: 길이 %% 36 ==',
      sorted({len(r['ls']) % 36 for r in rows if r['ls'] is not None}))

# 쓰인 charShapeId 와 그 색
cols = H.char_colors(doc)
used = collections.Counter()
for r in rows:
    if r['cs']:
        for k in range(len(r['cs']) // 8):
            st, cid = struct.unpack_from('<II', r['cs'], k * 8)
            used[cid] += 1
print('\n쓰인 charShapeId:', dict(sorted(used.items())))
for cid in sorted(used):
    print('   id %d 색 %s' % (cid, cols[cid] if cid < len(cols) else '?'))
print('빨간 charShape 이미 있나:',
      [i for i, c in enumerate(cols) if H.is_red(c)])

# 문단별 요약 (앞 12개)
print('\n--- 문단 앞부분 ---')
for i, r in enumerate(rows[:12]):
    txt = ''.join(c for c, _ in H.para_text(r['text'])) if r['text'] is not None else '(없음)'
    print(' [%2d] lvl=%d para=%d style=%d nCS=%d nLS=%d | %r'
          % (i, r['lvl'], r['f'][2], r['f'][3], r['f'][5], r['f'][7], txt[:52]))
print('\n--- 문단 끝부분 ---')
for i, r in list(enumerate(rows))[-6:]:
    txt = ''.join(c for c, _ in H.para_text(r['text'])) if r['text'] is not None else '(없음)'
    print(' [%2d] lvl=%d para=%d style=%d nCS=%d nLS=%d | %r'
          % (i, r['lvl'], r['f'][2], r['f'][3], r['f'][5], r['f'][7], txt[:52]))
