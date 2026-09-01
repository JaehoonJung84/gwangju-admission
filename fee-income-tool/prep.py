# -*- coding: utf-8 -*-
"""증빙 캡쳐를 기존 수입처리 파일과 같은 모양으로 자르고, 결의일과 입금일 문구를 만든다.

기존 수입처리 파일의 캡쳐는 계좌정보 박스(예금주·계좌번호·잔액)를 빼고
위(머리말~통장명)와 아래(안내문~거래내역표)를 이어 붙인 형태다. 그 모양을 그대로 맞춘다.

사용 : python prep.py <입금일 YYYY-MM-DD> [--pic 원본.png] [--out 폴더]
출력 : bank_crop.png · date.txt(입금일 문구) · resolve.txt(수입결의일)
"""
import io, os, sys, datetime
from PIL import Image

DOW = '월화수목금토일'
OUTW, OUTH = 958, 346          # 기존 파일의 그림 크기


def resolve_day(d):
    """입금일 → 수입결의일. 금요일은 다음 월요일, 토·일은 다음 화요일."""
    w = d.weekday()                      # 0=월 … 6=일
    if w == 4:                           # 금 → 월(+3)
        return d + datetime.timedelta(days=3), '금요일 입금 → 다음 월요일'
    if w == 5:                           # 토 → 화(+3)
        return d + datetime.timedelta(days=3), '토요일 입금 → 다음 화요일'
    if w == 6:                           # 일 → 화(+2)
        return d + datetime.timedelta(days=2), '일요일 입금 → 다음 화요일'
    return d, '평일 입금 → 당일'


def blank_bands(im, min_px=6):
    """가로로 거의 흰 줄이 이어지는 구간 — 화면의 빈 띠를 찾는다."""
    W, H = im.size
    px = im.load()
    xs = range(0, W, 3)
    bands, start = [], None
    for y in range(H):
        frac = sum(1 for x in xs if min(px[x, y]) > 245) / len(xs)
        if frac > 0.995:
            if start is None:
                start = y
        else:
            if start is not None and y - start >= min_px:
                bands.append((start, y - 1))
            start = None
    if start is not None and H - start >= min_px:
        bands.append((start, H - 1))
    return bands


def crop_like_before(src, dst):
    im = Image.open(src).convert('RGB')
    W, H = im.size
    if H / W < 0.45:                       # 이미 잘려 있는 그림이면 손대지 않는다
        im.resize((OUTW, OUTH), Image.LANCZOS).save(dst, optimize=True)
        return '이미 잘린 캡쳐로 판단해 그대로 사용'
    bands = blank_bands(im)
    # 계좌정보 박스는 화면에서 가장 넓은 빈 띠 사이에 있다.
    # 위쪽 경계 = 통장명 다음 빈 띠, 아래쪽 경계 = 그 다음 큰 빈 띠
    big = sorted(bands, key=lambda b: b[1] - b[0], reverse=True)
    cut = None
    for b in big:
        if 0.25 * H < b[0] < 0.85 * H:      # 화면 가운데쯤의 큰 빈 띠
            cut = b
            break
    if cut is None:
        im.resize((OUTW, OUTH), Image.LANCZOS).save(dst, optimize=True)
        return '자를 구간을 못 찾아 전체를 사용'
    # 박스 위쪽 : cut 바로 앞의 빈 띠
    before = [b for b in bands if b[1] < cut[0]]
    top_end = (before[-1][0] + before[-1][1]) // 2 if before else cut[0]
    bot_start = (cut[0] + cut[1]) // 2
    top = im.crop((0, 0, W, top_end))
    bot = im.crop((0, bot_start, W, H))
    out = Image.new('RGB', (W, top.height + bot.height), 'white')
    out.paste(top, (0, 0))
    out.paste(bot, (0, top.height))
    out.resize((OUTW, OUTH), Image.LANCZOS).save(dst, optimize=True)
    return '계좌정보 박스 y%d~%d 제거' % (top_end, bot_start)


def main():
    day = datetime.date.fromisoformat(sys.argv[1])
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    pic = sys.argv[sys.argv.index('--pic') + 1] if '--pic' in sys.argv else os.path.join(out, 'bank_full.png')
    os.makedirs(out, exist_ok=True)

    text = '※ 입금일: %d. %d. %d.(%s)' % (day.year, day.month, day.day, DOW[day.weekday()])
    io.open(os.path.join(out, 'date.txt'), 'w', encoding='utf-8').write(text)

    rday, why = resolve_day(day)
    io.open(os.path.join(out, 'resolve.txt'), 'w', encoding='utf-8').write(rday.isoformat())
    print('입금일   :', day.isoformat(), '(%s)' % DOW[day.weekday()])
    print('입금일 문구:', text)
    print('수입결의일:', rday.isoformat(), '(%s)' % DOW[rday.weekday()], '—', why)

    if os.path.exists(pic):
        msg = crop_like_before(pic, os.path.join(out, 'bank_crop.png'))
        print('증빙 캡쳐 :', msg, '→ bank_crop.png')
    else:
        print('증빙 캡쳐 : 원본 없음(%s) — 캡쳐 없이 진행' % pic)


if __name__ == '__main__':
    main()
