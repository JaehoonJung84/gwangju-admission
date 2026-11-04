# -*- coding: utf-8 -*-
"""대학원 영문 표지·머리띠를 만든다.

대학원 표지는 학부 표지와 **작은 제목 줄(y700~1040)만 빼고 픽셀 단위로 동일**하고,
머리띠도 왼쪽 장식이 완전히 같다. 그래서 학부에서 글자를 지워 복원해 둔 배경판
(`prospectus_en/img/cover_bg.png`, `band_bg.png`)을 그대로 다시 쓴다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UIMG = os.path.join(r'C:\projects\tools\hwp\prospectus_en', 'img')
OUT = os.path.join(HERE, 'img')
BD = os.path.join(r'C:\Windows\Fonts', 'malgunbd.ttf')

CENTER = 1231
RULE_X0, RULE_X1 = 680, 1783
SMALL = (181, 236, 255)
WHITE = (255, 255, 255)
BIG_LINES = ['International', 'Freshman & Transfer', 'Admission Guidelines']
SMALL_LINES = ['2027 Spring Semester', 'Gwangju University Graduate School']
APPLY = '2026. 11. 16.(Mon) ~ 12. 31.(Thu)'
BAND_TEXT = '2027 Spring Graduate Admission Guidelines for International Students'


def fit(draw, text, want_w, start=240, floor=40):
    for size in range(start, floor, -2):
        f = ImageFont.truetype(BD, size)
        if draw.textlength(text, font=f) <= want_w:
            return f
    return ImageFont.truetype(BD, floor)


def centered(draw, text, font, cx, y_top, y_bot, fill):
    bb = font.getbbox(text)
    draw.text((cx - (bb[2] - bb[0]) / 2.0 - bb[0],
               (y_top + y_bot) / 2.0 - (bb[3] - bb[1]) / 2.0 - bb[1]),
              text, font=font, fill=fill)


def build_cover():
    bg = Image.open(os.path.join(UIMG, 'cover_bg.png')).convert('RGB')
    d = ImageDraw.Draw(bg)
    d.rectangle([RULE_X0, 604, RULE_X1, 607], fill=(170, 227, 255))
    d.rectangle([RULE_X0, 1130, RULE_X1, 1132], fill=(163, 225, 255))

    f1 = fit(d, SMALL_LINES[0], 1100, start=170)
    centered(d, SMALL_LINES[0], f1, CENTER, 719, 839, SMALL)
    f2 = fit(d, SMALL_LINES[1], 1100, start=170)
    centered(d, SMALL_LINES[1], f2, CENTER, 890, 1031, SMALL)

    size = min(fit(d, t, 1490, start=260).size for t in BIG_LINES)
    gf = ImageFont.truetype(BD, size)
    TOP, BOT = 1362, 1787
    step = (BOT - TOP) / float(len(BIG_LINES))
    for i, t in enumerate(BIG_LINES):
        centered(d, t, gf, CENTER, TOP + step * i, TOP + step * (i + 1), WHITE)

    bf = ImageFont.truetype(BD, 78)
    rows = [('Application', APPLY, 2204, 2277),
            ('Website', 'ie.gwangju.ac.kr', 2336, 2416)]
    label_w = max(d.textlength(r[0], font=bf) for r in rows)
    bb = bf.getbbox('Hg')
    for label, value, y0, y1 in rows:
        y = (y0 + y1) / 2.0 - (bb[3] - bb[1]) / 2.0 - bb[1]
        d.text((579, y), label, font=bf, fill=WHITE)
        bar = 579 + label_w + 46
        d.text((bar, y), '|', font=bf, fill=(170, 210, 245))
        d.text((bar + 52, y), value, font=bf, fill=WHITE)

    bg.save(os.path.join(OUT, 'cover_en.png'))
    bg.resize((760, int(760 * bg.height / bg.width)), Image.LANCZOS).save(
        os.path.join(OUT, 'cover_en_small.png'))
    print('표지 저장 | 큰제목 %dpt | 작은제목 %d %d' % (size, f1.size, f2.size))


def build_band():
    plate = Image.open(os.path.join(UIMG, 'band_bg.png')).convert('RGB')
    d = ImageDraw.Draw(plate)
    f = ImageFont.truetype(BD, 46)
    w = d.textlength(BAND_TEXT, font=f)
    bb = f.getbbox('Hg')
    d.text((2399 - w, (121 - (bb[3] - bb[1])) / 2.0 - bb[1]), BAND_TEXT, font=f, fill=WHITE)
    plate.save(os.path.join(OUT, 'band_en.png'))
    print('배너 저장 | 폭 %d / 시작 x=%d' % (w, 2399 - w))


os.makedirs(OUT, exist_ok=True)
build_band()
build_cover()
