# -*- coding: utf-8 -*-
"""대학원 중문 표지·머리띠를 만든다.

사무처가 낸 학부 중문본의 표지·머리띠와 글자 짜임을 그대로 따르고, 학부만 다른
두 군데(`光州大学 本科` → `研究生院`, 원서접수 시작일)만 대학원에 맞춘다.
바탕판은 국문 표지에서 글자를 지워 복원해 둔 것(prospectus_en/img)을 다시 쓴다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UIMG = os.path.join(r'C:\projects\tools\hwp\prospectus_en', 'img')
OUT = os.path.join(HERE, 'img')
BD = r'C:\Windows\Fonts\msyhbd.ttc'        # Microsoft YaHei Bold
RG = r'C:\Windows\Fonts\msyh.ttc'          # Microsoft YaHei

CENTER = 1231
RULE_X0, RULE_X1 = 680, 1783
SMALL = (181, 236, 255)
WHITE = (255, 255, 255)
SMALL_LINES = ['2027学年度 第1学期', '光州大学 研究生院']
BIG_LINES = ['外国留学生新生·插班生', '特别招生简章']
APPLY = '2026. 11. 16.(周一) ~ 12. 31.(周四)'
SITE = 'ie.gwangju.ac.kr'
BAND_TEXT = '2027学年度第1学期 外国留学生研究生新生·插班生特别招生简章'


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def fit(draw, text, want_w, path=BD, start=240, floor=40):
    for size in range(start, floor, -2):
        f = font(path, size)
        if draw.textlength(text, font=f) <= want_w:
            return f
    return font(path, floor)


def centered(draw, text, f, cx, y_top, y_bot, fill):
    bb = f.getbbox(text)
    draw.text((cx - (bb[2] - bb[0]) / 2.0 - bb[0],
               (y_top + y_bot) / 2.0 - (bb[3] - bb[1]) / 2.0 - bb[1]),
              text, font=f, fill=fill)


def build_cover():
    bg = Image.open(os.path.join(UIMG, 'cover_bg.png')).convert('RGB')
    d = ImageDraw.Draw(bg)
    d.rectangle([RULE_X0, 604, RULE_X1, 607], fill=(170, 227, 255))
    d.rectangle([RULE_X0, 1130, RULE_X1, 1132], fill=(163, 225, 255))

    f1 = fit(d, SMALL_LINES[0], 1100, path=RG, start=170)
    centered(d, SMALL_LINES[0], f1, CENTER, 719, 839, SMALL)
    f2 = fit(d, SMALL_LINES[1], 1100, start=170)
    centered(d, SMALL_LINES[1], f2, CENTER, 890, 1031, SMALL)

    size = min(fit(d, t, 1490, start=260).size for t in BIG_LINES)
    gf = font(BD, size)
    TOP, BOT = 1362, 1787
    step = (BOT - TOP) / float(len(BIG_LINES))
    for i, t in enumerate(BIG_LINES):
        centered(d, t, gf, CENTER, TOP + step * i, TOP + step * (i + 1), WHITE)

    lf, vf = font(BD, 78), font(RG, 78)
    rows = [('报名时间', APPLY, 2204, 2277), ('招生网站', SITE, 2336, 2416)]
    label_w = max(d.textlength(r[0], font=lf) for r in rows)
    bb = lf.getbbox('字Hg')
    for label, value, y0, y1 in rows:
        y = (y0 + y1) / 2.0 - (bb[3] - bb[1]) / 2.0 - bb[1]
        d.text((579, y), label, font=lf, fill=WHITE)
        bar = 579 + label_w + 46
        d.text((bar, y), '|', font=lf, fill=(170, 210, 245))
        d.text((bar + 52, y), value, font=vf, fill=WHITE)

    bg.save(os.path.join(OUT, 'cover_cn.png'))
    bg.resize((760, int(760 * bg.height / bg.width)), Image.LANCZOS).save(
        os.path.join(OUT, 'cover_cn_small.png'))
    print('표지 저장 | 큰제목 %dpt | 작은제목 %d %d' % (size, f1.size, f2.size))


def build_band():
    plate = Image.open(os.path.join(UIMG, 'band_bg.png')).convert('RGB')
    d = ImageDraw.Draw(plate)
    f = font(BD, 46)
    w = d.textlength(BAND_TEXT, font=f)
    bb = f.getbbox('字Hg')
    x = 2399 - w
    d.text((x, (121 - (bb[3] - bb[1])) / 2.0 - bb[1]), BAND_TEXT, font=f, fill=WHITE)
    plate.save(os.path.join(OUT, 'band_cn.png'))
    print('머리띠 저장 | 판 너비 %d | 글자 너비 %d | 시작 x=%d (왼쪽 장식과 거리 %d)'
          % (plate.width, w, x, x))


os.makedirs(OUT, exist_ok=True)
build_band()
build_cover()
