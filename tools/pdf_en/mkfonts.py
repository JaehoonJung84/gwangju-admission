# -*- coding: utf-8 -*-
"""대체 글꼴 만들기 — Noto Sans KR 가변글꼴에서 굵기별 정적 글꼴을 뽑는다.

디자인 PDF 에 박힌 TTMGothic/SDGyeokdong 은 '쓴 글자만 남긴 부분집합'이라
영문 자소가 비어 있다(cmap 은 멀쩡해 보여도 glyf 가 빈 껍데기다). 그래서
중문판이 NotoSansSC 로 바꾼 것과 같은 방식으로 Noto Sans KR 로 바꿔 찍는다.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SRC = r'C:\Windows\Fonts\NotoSansKR-VF.ttf'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

os.makedirs(OUT, exist_ok=True)
for w in (300, 400, 500, 600, 700, 800, 900):
    f = TTFont(SRC)
    instancer.instantiateVariableFont(f, {'wght': w}, inplace=True, updateFontNames=False)
    p = os.path.join(OUT, 'NotoSansKR-%d.ttf' % w)
    f.save(p)
    print(p)
