# -*- coding: utf-8 -*-
"""디자인 PDF 의 글줄을 '칸(cell)' 단위로 묶는다.

칸 경계는 표의 세로 괘선과 색칠 사각형 모서리에서 뽑는다.
"""
import fitz
import re

# 번호 항목·글머리로 시작하는 줄은 줄 사이가 넓어도 같은 덩어리로 본다.
LISTY = re.compile(r'^(?:[○※•-]|\d{1,2}\.)\s')

PAGE_L, PAGE_R = 51.0, 385.5     # 본문 좌우 여백(실측)


def cuts_for(page):
    out = []
    for g in page.get_drawings():
        r = g['rect']
        if r.width < 2.0 and r.height > 4:          # 세로 괘선
            out.append((round((r.x0 + r.x1) / 2, 2), r.y0, r.y1))
        elif r.width > 4 and r.height > 4:          # 색칠/테두리 사각형
            out.append((round(r.x0, 2), r.y0, r.y1))
            out.append((round(r.x1, 2), r.y0, r.y1))
    return out


def hcuts_for(page):
    """가로 괘선: (y, x0, x1) — 줄 사이에 끼면 다른 칸이다."""
    out = []
    for g in page.get_drawings():
        r = g['rect']
        if r.height < 2.0 and r.width > 8:
            out.append((round((r.y0 + r.y1) / 2, 2), r.x0, r.x1))
        elif r.width > 8 and r.height > 4:
            out.append((round(r.y0, 2), r.x0, r.x1))
            out.append((round(r.y1, 2), r.x0, r.x1))
    return out


def crossed(hcuts, prev, cur):
    """두 글줄 사이를 지나는 가로 괘선이 있는가."""
    y0, y1 = prev['bbox'][3], cur['bbox'][1]
    if y1 <= y0:
        return False
    x0 = max(prev['bbox'][0], cur['bbox'][0])
    x1 = min(prev['bbox'][2], cur['bbox'][2])
    if x1 < x0:
        x0, x1 = min(prev['bbox'][0], cur['bbox'][0]), max(prev['bbox'][2], cur['bbox'][2])
    for y, a, b in hcuts:
        if y0 - 0.3 <= y <= y1 + 0.3 and a <= x1 + 0.5 and b >= x0 - 0.5:
            return True
    return False


def cell_bounds(cuts, bbox):
    x0, y0, x1, y1 = bbox
    ymid = (y0 + y1) / 2
    left, right = PAGE_L, PAGE_R
    for x, a, b in cuts:
        if b < ymid - 0.5 or a > ymid + 0.5:
            continue
        if x <= x0 + 0.6 and x > left:
            left = x
        if x >= x1 - 0.6 and x < right:
            right = x
    return round(left, 2), round(right, 2)


def lines_of(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            spans = [s for s in l['spans'] if s['text'].strip()]
            if not spans:
                continue
            s0 = spans[0]
            out.append(dict(text=''.join(s['text'] for s in l['spans']),
                            bbox=[round(v, 2) for v in l['bbox']],
                            font=s0['font'].split('+')[-1], size=round(s0['size'], 2),
                            color=s0['color'], origin=[round(v, 2) for v in s0['origin']]))
    out.sort(key=lambda d: (round(d['bbox'][1], 1), d['bbox'][0]))
    return out


def cells_of(page):
    cuts = cuts_for(page)
    hcuts = hcuts_for(page)
    lines = lines_of(page)
    for l in lines:
        l['cell'] = cell_bounds(cuts, l['bbox'])

    cells = []
    for l in lines:
        for c in cells:
            if c['cell'] != l['cell'] or abs(c['size'] - l['size']) > 0.01:
                continue
            prev = c['lines'][-1]
            if prev['font'] != l['font']:
                continue
            gap = l['bbox'][1] - prev['bbox'][3]
            lim = l['size'] * (1.25 if LISTY.match(l['text'].lstrip()) else 0.75)
            if -1.0 <= gap <= lim and not crossed(hcuts, prev, l):
                c['lines'].append(l)
                break
        else:
            cells.append(dict(cell=l['cell'], size=l['size'], lines=[l]))
    for c in cells:
        c['text'] = '\n'.join(x['text'] for x in c['lines'])
        c['key'] = ' '.join(' '.join(x['text'].split()) for x in c['lines']).strip()
        c['font'] = c['lines'][0]['font']
        c['color'] = c['lines'][0]['color']
        xs0 = min(x['bbox'][0] for x in c['lines'])
        xs1 = max(x['bbox'][2] for x in c['lines'])
        L, R = c['cell']
        gl, gr = xs0 - L, R - xs1
        bullet = c['text'].lstrip()[:1] in ('○', '※', '-')
        if abs(gl - gr) < 3.0 and gl > 2.0 and not bullet:
            c['align'] = 'C'
        elif len(c['lines']) == 1 and gr < 8.0 and gl > 25.0 and not bullet:
            c['align'] = 'R'
        else:
            c['align'] = 'L'
        c['centered'] = c['align'] == 'C'
        c['bbox'] = [xs0, c['lines'][0]['bbox'][1], xs1, c['lines'][-1]['bbox'][3]]
        c['row'] = row_bounds(hcuts, c['bbox'], c['cell'])
    cells.sort(key=lambda c: (round(c['bbox'][1], 1), c['bbox'][0]))
    # 아래쪽으로 쓸 수 있는 공간 — 가로로 겹치는 다음 칸의 윗머리까지
    H = page.rect.y1
    for i, c in enumerate(cells):
        lim = H - 18.0
        for o in cells:
            if o is c or o['bbox'][1] < c['bbox'][3] - 0.5:
                continue
            if o['bbox'][2] < c['cell'][0] + 1 or o['bbox'][0] > c['cell'][1] - 1:
                continue
            lim = min(lim, o['bbox'][1] - 10.0)
        c['limit'] = round(max(lim, c['bbox'][3]), 2)
    return cells


def row_bounds(hcuts, bbox, cell):
    """칸이 든 표 줄의 위·아래 괘선 y."""
    L, R = cell
    top, bot = bbox[1] - 5.0, bbox[3] + 5.0
    for y, a, b in hcuts:
        if b < L + 1 or a > R - 1:
            continue
        if y <= bbox[1] + 0.8 and y > top:
            top = y
        if y >= bbox[3] - 0.8 and y < bot:
            bot = y
    return round(top, 2), round(bot, 2)
