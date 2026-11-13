# -*- coding: utf-8 -*-
"""표지·뒤표지의 제목을 영문으로 바꾼다.

학부 앞표지는 글자가 '윤곽선(벡터)'이라 글월이 없다 — 같은 판에 글자가 살아 있는
중문판 1쪽을 가져다 쓴다. 뒤표지는 양쪽 다 윤곽선이라 그 자리의 선그림만 지우고 새로 찍는다.
"""
import fitz, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = {w: os.path.join(HERE, 'fonts', 'NotoSansKR-%d.ttf' % w) for w in (500, 700)}
M = {w: fitz.Font(fontfile=p) for w, p in F.items()}
NAVY = (0.0296, 0.1888, 0.3090)
WHITE = (1, 1, 1)

TITLE = {
    'ug': ('2027 Spring Semester',
           ['Special Admission for International', 'Freshmen and Transfer Students'],
           'Undergraduate'),
    'gr': ('2027 Spring Semester',
           ['Special Admission for International', 'Freshmen and Transfer Students'],
           'Graduate School'),
}


def drop_spans(page, line):
    """글줄 안의 글월만 지운다 — KBLJump(GWANGJU UNIVERSITY)는 그대로 둔다."""
    for sp in line['spans']:
        if 'KBLJump' in sp['font']:
            continue
        oy, sz = sp['origin'][1], sp['size']
        page.add_redact_annot(fitz.Rect(sp['bbox'][0] - 0.5, oy - sz * 0.95,
                                        sp['bbox'][2] + 0.5, oy + sz * 0.30),
                              fill=None, cross_out=False)


def put(page, x, y, text, w, size, color):
    name = 'CV%d' % w
    page.insert_font(fontname=name, fontfile=F[w])
    page.insert_text((x, y), text, fontname=name, fontsize=size, color=color)


def badge(page, x0, ymid, word, size=9.5, pad=7.0, h=17.8):
    tw = M[500].text_length(word, size)
    r = fitz.Rect(x0, ymid - h / 2, x0 + tw + pad * 2, ymid + h / 2)
    page.draw_rect(r, color=None, fill=NAVY, radius=0.28)
    put(page, r.x0 + pad, ymid + size * 0.36, word, 500, size, WHITE)
    return r


def front_ug(doc):
    """학부 앞표지 — 제목이 윤곽선이라 그 자리의 선그림만 지우고 새로 찍는다.
    GWANGJU UNIVERSITY 도 윤곽선이지만 영문이라 그대로 둔다."""
    page = doc[0]
    page.add_redact_annot(fitz.Rect(58, 175, 382, 221), fill=None, cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)
    draw_front(page, 'ug', x=66.5, y1=190.0)


def draw_front(page, tag, x, y1):
    small, big, tag_word = TITLE[tag]
    put(page, x, y1, small, 500, 13.0, NAVY)
    size = 16.0
    while max(M[700].text_length(t, size) for t in big) > 300.0:
        size -= 0.25
    y, ys = y1 + 20.0, []
    for t in big:
        put(page, x, y, t, 700, size, NAVY)
        ys.append(y)
        y += size * 1.22
    bw = M[500].text_length(tag_word, 9.5) + 14.0
    end = x + M[700].text_length(big[-1], size)
    if end + 10.0 + bw <= 386.0:
        badge(page, end + 10.0, (ys[0] + ys[-1]) / 2 - size * 0.30, tag_word)
    else:
        badge(page, x, ys[-1] + size * 0.95, tag_word)


def back(doc, tag, pno):
    page = doc[pno]
    page.add_redact_annot(fitz.Rect(118, 264, 320, 327), fill=None, cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)
    small, big, tag_word = TITLE[tag]
    cx = 218.3
    put(page, cx - M[500].text_length(small, 11.5) / 2, 279.5, small, 500, 11.5, NAVY)
    size = 14.0
    while max(M[700].text_length(t, size) for t in big) > 300.0:
        size -= 0.25
    y = 296.5
    for t in big:
        put(page, cx - M[700].text_length(t, size) / 2, y, t, 700, size, NAVY)
        y += size * 1.22
    w = M[500].text_length(tag_word, 9.5) + 14.0
    badge(page, cx - w / 2, y + 2.0, tag_word)


if __name__ == '__main__':
    tag = sys.argv[1]
    src = 'out_%s_en.pdf' % tag
    doc = fitz.open(src)
    if tag == 'ug':
        front_ug(doc)
        back(doc, 'ug', 15)
    else:
        page = doc[0]
        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                drop_spans(page, l)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_REMOVE)
        page.add_redact_annot(fitz.Rect(310, 190, 372, 221), fill=None, cross_out=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                              text=fitz.PDF_REDACT_TEXT_NONE)
        draw_front(page, 'gr', x=66.5, y1=190.0)
        back(doc, 'gr', 19)
    doc.subset_fonts()
    out = 'final_%s_en.pdf' % tag
    doc.save(out, garbage=4, deflate=True)
    print('saved', out)
