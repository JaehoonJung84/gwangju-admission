# -*- coding: utf-8 -*-
"""디자인 PDF 의 글월만 영문으로 갈아끼운다 — 판·그림·괘선은 그대로 둔다.

  python render.py ug        (ug_ko.pdf  + trans_ug.py  -> out_ug_en.pdf)
  python render.py gr        (grad_ko.pdf + trans_gr.py -> out_gr_en.pdf)
"""
import fitz, sys, io, re, importlib, os
import layout

HAN = re.compile(r'[가-힣]')
PREFIX = []

# 원본 글꼴 → 대체 글꼴(Noto Sans KR 굵기별). 원본 글꼴은 자소가 빠진 부분집합이라
# 영문을 찍을 수 없어 같은 계열의 고딕으로 바꾼다(중문판이 NotoSansSC 로 바꾼 것과 같은 방식).
FONTMAP = {
    'TTMGothicL': 300, 'TTMGothicR': 400, 'TTMGothicM': 500,
    'TTMGothicSB': 600, 'TTMGothicB': 700,
    'SDGdGothic': 700, 'SDGyeokdongG206Hv': 800, 'SDGyeokdongG205Bd': 700,
    'Freesentation-6SemiBold': 600, 'Freesentation-8ExtraBold': 800,
    'KBLJump_EB_ExtendedTTF': 800,
}
FONTFILE = {w: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'fonts', 'NotoSansKR-%d.ttf' % w) for w in set(FONTMAP.values())}
MEASURE = {w: fitz.Font(fontfile=p) for w, p in FONTFILE.items()}
BULLET = re.compile(r'^(\s*(?:[○•\-–※]|\d{1,2}\.)\s+)')
# Noto Sans KR 에 없는 글자는 모양이 같은 것으로 바꾼다(∼ U+223C 가 없다).
SUBST = {'∼': '~', '–': '-', '⋅': '·'}


def fix(t):
    for a, b in SUBST.items():
        t = t.replace(a, b)
    return t


def rgb(color):
    return ((color >> 16) & 255) / 255.0, ((color >> 8) & 255) / 255.0, (color & 255) / 255.0


def wrap(text, font, size, width, hang=True):
    """forced '\\n' 를 지키며 width 안에서 낱말 단위로 접는다."""
    out = []
    for seg in text.split('\n'):
        seg = seg.rstrip()
        if not seg:
            out.append('')
            continue
        m = BULLET.match(seg)
        indent = ' ' * len(m.group(1)) if (m and hang) else ''
        words, cur = seg.split(' '), ''
        for w in words:
            cand = (cur + ' ' + w) if cur else w
            pre = indent if out and cur == '' and False else ''
            if font.text_length(cand, size) <= width or not cur:
                cur = cand
            else:
                out.append(cur)
                cur = indent + w
        out.append(cur)
    return out


def layout_lines(c, en, in_table):
    """줄 수·글자크기를 정한다. 표 안이면 줄 높이까지 보고 줄인다."""
    L, R = c['cell']
    first = c['lines'][0]
    w = FONTMAP.get(c['font'], 400)
    font = MEASURE[w]
    n0 = len(c['lines'])
    PAD = 3.0
    if c['align'] == 'C':
        avail = (R - L) - 2 * PAD
        left = None
    elif c['align'] == 'R':
        avail = max(c['bbox'][2] - L - PAD, 20.0)
        left = c['bbox'][2]
    else:
        left = first['bbox'][0]
        avail = max(R - PAD - left, 20.0)
    size = c['size']
    rowh = max(c['row'][1] - c['row'][0], c['bbox'][3] - c['bbox'][1] + 4.0)
    if not in_table:
        rowh = max(c['limit'] - c['bbox'][1], c['bbox'][3] - c['bbox'][1] + 2.0)

    def wide(lines, s):
        return max((font.text_length(t, s) for t in lines if t), default=0) > avail + 0.2

    def fits_row(s, n):
        return (n - 1) * s * 1.15 + s + 0.8 <= rowh

    cand = []
    s = size
    while True:
        lines = wrap(en, font, s, avail)
        cand.append((s, lines))
        if not wide(lines, s):
            if len(lines) <= n0:
                return s, lines, left, avail, w
            if s <= size * 0.88 + 0.001 and fits_row(s, len(lines)):
                return s, lines, left, avail, w
            if s == size and fits_row(s, len(lines)):
                return s, lines, left, avail, w
        if s <= size * 0.70 + 0.001:
            break
        s = round(s - 0.25, 2)
    good = [(s, l) for s, l in cand if not wide(l, s)]
    pool = good or cand
    nmin = min(len(l) for _, l in pool)
    for s, lines in pool:
        if len(lines) == nmin:
            return s, lines, left, avail, w
    return pool[-1][0], pool[-1][1], left, avail, w


def draw_cell(page, c, en):
    L, R = c['cell']
    in_table = (L > layout.PAGE_L + 0.5) or (R < layout.PAGE_R - 0.5)
    size, lines, left, avail, w = layout_lines(c, en, in_table)
    n0, n = len(c['lines']), len(lines)
    col = rgb(c['color'])
    fname = 'N%d' % w
    page.insert_font(fontname=fname, fontfile=FONTFILE[w])
    font = MEASURE[w]

    if n == n0 and abs(size - c['size']) < 0.001:
        ys = [l['origin'][1] for l in c['lines']]
    else:
        if n0 >= 2:
            lead = (c['lines'][-1]['origin'][1] - c['lines'][0]['origin'][1]) / (n0 - 1)
        else:
            lead = size * 1.38
        if in_table:
            rtop, rbot = c['row']
            if n > 1:
                lead = min(lead, max((rbot - rtop - size - 0.8) / (n - 1), size * 1.02))
            mid = (rtop + rbot) / 2 if (rbot - rtop) > size else (c['bbox'][1] + c['bbox'][3]) / 2
            y0 = mid + size * 0.36 - lead * (n - 1) / 2
        else:
            y0 = c['lines'][0]['origin'][1]
        ys = [y0 + lead * i for i in range(n)]

    for y, t in zip(ys, lines):
        if not t:
            continue
        if c['align'] == 'C':
            x = (L + R) / 2 - font.text_length(t, size) / 2
        elif c['align'] == 'R':
            x = left - font.text_length(t, size)
        else:
            x = left
        page.insert_text((x, y), t, fontname=fname, fontsize=size, color=col)
    return n, n0, size


def run(tag):
    src = {'ug': 'ug_ko.pdf', 'gr': 'grad_ko.pdf'}[tag]
    tr = importlib.import_module('trans_' + tag)
    TRANS, OVER = tr.TRANS, getattr(tr, 'OVER', {})
    global PREFIX
    PREFIX = sorted(getattr(tr, 'PREFIX', {}).items(), key=lambda kv: -len(kv[0]))
    doc = fitz.open(src)
    report = []
    for pi, page in enumerate(doc):
        cells = layout.cells_of(page)
        todo = []
        for ci, c in enumerate(cells):
            en = OVER.get((pi + 1, ci))
            if en is None:
                en = TRANS.get(c['key'])
            if en is None:
                for pre, v in PREFIX:
                    if c['key'].startswith(pre):
                        en = v
                        break
            if en is None:
                if HAN.search(c['key']):
                    report.append('MISS p%d.%02d %s' % (pi + 1, ci, c['key'][:70]))
                continue
            en = fix(en)
            if en == c['key']:
                continue
            miss = {ch for ch in en if ch not in '\n '
                    and not MEASURE[FONTMAP.get(c['font'], 400)].has_glyph(ord(ch))}
            if miss:
                report.append('GLYPH p%d.%02d %s' % (pi + 1, ci, ' '.join(sorted(miss))))
            todo.append((c, en))
        for c, en in todo:
            for l in c['lines']:
                r = fitz.Rect(l['bbox'][0] - 0.6, l['bbox'][1] - 0.6,
                              l['bbox'][2] + 0.6, l['bbox'][3] + 0.6)
                page.add_redact_annot(r, fill=None, cross_out=False)
        if todo:
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_REMOVE)
        for ci, (c, en) in enumerate(todo):
            n, n0, size = draw_cell(page, c, en)
            if n != n0 or abs(size - c['size']) > 0.01:
                report.append('FIT  p%d lines %d->%d size %.2f->%.2f | %s' %
                              (pi + 1, n0, n, c['size'], size, en[:60].replace('\n', '/')))
    doc.subset_fonts()
    out = 'out_%s_en.pdf' % tag
    doc.save(out, garbage=4, deflate=True)
    with io.open('report_%s.txt' % tag, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print('saved', out, 'issues', len(report))


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'ug')
