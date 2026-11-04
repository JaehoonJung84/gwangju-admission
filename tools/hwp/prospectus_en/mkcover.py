# -*- coding: utf-8 -*-
"""영문 표지와 머리띠 배너를 만든다.

국문 표지에서 잰 좌표를 그대로 쓴다(괘선 y604·y1130, 글줄 중심 x1231).
배경판(cover_bg.png)은 국·중문 글자를 지워 복원해 둔 것.
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SP = os.path.join(r'C:\Users\user\AppData\Local\Temp\claude\C--projects',
                  'a4f9f4bd-24d4-4ecd-9026-45541c84c019', 'scratchpad', 'en', 'img')
BD = os.path.join(r'C:\Windows\Fonts', 'malgunbd.ttf')

BIG_LINES = ['International', 'Freshman & Transfer', 'Admission Guidelines']
CENTER = 1231
RULE_X0, RULE_X1 = 680, 1783
SMALL = (181, 236, 255)          # RGB
WHITE = (255, 255, 255)


def fit(draw, text, font_path, want_w, start=240, floor=40):
    """want_w 안에 들어가는 가장 큰 크기를 찾는다."""
    for size in range(start, floor, -2):
        f = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=f) <= want_w:
            return f, draw.textlength(text, font=f)
    f = ImageFont.truetype(font_path, floor)
    return f, draw.textlength(text, font=f)


def centered(draw, text, font, cx, y_top, y_bot, fill):
    """글자의 실제 먹는 높이를 기준으로 y_top~y_bot 한가운데에 가운데맞춤으로 쓴다."""
    bb = font.getbbox(text)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    x = cx - w / 2.0 - bb[0]
    y = (y_top + y_bot) / 2.0 - h / 2.0 - bb[1]
    draw.text((x, y), text, font=font, fill=fill)


def build_cover(tag='en'):
    bg = Image.open(os.path.join(SP, 'cover_bg.png')).convert('RGB')
    d = ImageDraw.Draw(bg)

    # 괘선 두 줄 (국문판 자리 그대로)
    d.rectangle([RULE_X0, 604, RULE_X1, 607], fill=(170, 227, 255))
    d.rectangle([RULE_X0, 1130, RULE_X1, 1132], fill=(163, 225, 255))

    # 작은 제목 2줄
    f1, _ = fit(d, '2027 Spring Semester', BD, 1100, start=170)
    centered(d, '2027 Spring Semester', f1, CENTER, 719, 839, SMALL)
    f2, _ = fit(d, 'Gwangju University Undergraduate', BD, 1100, start=170)
    centered(d, 'Gwangju University Undergraduate', f2, CENTER, 890, 1031, SMALL)

    # 큰 제목 — 영문은 길어서 3줄로 나눠야 국문과 비슷한 크기가 나온다
    big = BIG_LINES
    size = min(fit(d, t, BD, 1490, start=260)[0].size for t in big)
    gf = ImageFont.truetype(BD, size)
    TOP, BOT = 1362, 1787
    step = (BOT - TOP) / float(len(big))
    for i, t in enumerate(big):
        centered(d, t, gf, CENTER, TOP + step * i, TOP + step * (i + 1), WHITE)

    # 아래 안내 2줄 (왼쪽맞춤, 국문판 x=579)
    bf = ImageFont.truetype(BD, 78)
    rows = [('Application', '2026. 11. 11.(Wed) ~ 12. 31.(Thu)', 2204, 2277),
            ('Website', 'ie.gwangju.ac.kr', 2336, 2416)]
    label_w = max(d.textlength(r[0], font=bf) for r in rows)
    for label, value, y0, y1 in rows:
        bb = bf.getbbox('Hg')
        y = (y0 + y1) / 2.0 - (bb[3] - bb[1]) / 2.0 - bb[1]
        d.text((579, y), label, font=bf, fill=WHITE)
        bar = 579 + label_w + 46
        d.text((bar, y), '|', font=bf, fill=(170, 210, 245))
        d.text((bar + 52, y), value, font=bf, fill=WHITE)

    out = os.path.join(SP, 'cover_%s.png' % tag)
    bg.save(out)
    small = bg.resize((760, int(760 * bg.height / bg.width)), Image.LANCZOS)
    small.save(os.path.join(SP, 'cover_%s_small.png' % tag))
    print('표지 저장:', out, '| 큰제목 크기', size, '| 작은제목', f1.size, f2.size)


def build_band():
    ko = cv2.imdecode(np.fromfile(os.path.join(SP, 'band_ko.jpeg'), np.uint8), cv2.IMREAD_COLOR)
    a = ko.astype(np.float32)
    X0, X1, Y0, Y1 = 1045, 2440, 26, 108
    top, bot = a[Y0 - 1].copy(), a[Y1 + 1].copy()
    for y in range(Y0, Y1 + 1):
        t = (y - (Y0 - 1)) / float((Y1 + 1) - (Y0 - 1))
        a[y, X0:X1] = top[X0:X1] * (1 - t) + bot[X0:X1] * t
    plate = Image.fromarray(cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(plate)
    s = '2027 Spring Undergraduate Admission Guidelines for International Students'
    f = ImageFont.truetype(BD, 46)
    w = d.textlength(s, font=f)
    bb = f.getbbox('Hg')
    d.text((2399 - w, (121 - (bb[3] - bb[1])) / 2.0 - bb[1]), s, font=f, fill=(255, 255, 255))
    out = os.path.join(SP, 'band_en.png')
    plate.save(out)
    print('배너 저장:', out, '| 폭', int(w))


build_band()
build_cover('en3')
BIG_LINES = ['International Freshman & Transfer', 'Admission Guidelines']
build_cover('en2')
