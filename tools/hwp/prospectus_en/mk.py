# -*- coding: utf-8 -*-
"""영문 모집요강 HWPX를 만들고 PDF로 변환한다.

  python mk.py [본문배율]      예: python mk.py 0.80

국문 원본은 쪽나눔 12개로 14쪽 구성이 고정돼 있다. 영문은 글월이 길어 그대로 바꾸면
각 절이 한 쪽씩 넘긴다. 그래서 ① 제목을 뺀 본문 글자를 배율로 줄이고 ② 길이가
문제되는 칸은 짧은 표현(short.SHORT)으로 바꾼다. 그래도 쪽이 밀리면 ③ 목차의
쪽번호를 실제 쪽에 맞춰 고쳐 다시 변환한다.
"""
import io
import os
import re
import subprocess
import sys
import zipfile
from xml.sax.saxutils import escape, unescape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from trans import TR                                              # noqa: E402
from short import SHORT                                           # noqa: E402

TR = dict(TR)
TR.update(SHORT)

SRC = os.path.join(r'C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강\학부',
                   '2027학년도 1학기 외국인 학부 신·편입 특별전형 모집요강(20261030)_초안_23차.hwpx')
IMG = os.path.join(HERE, 'img')
HWPX = os.path.join(HERE, 'eng.hwpx')
PDF = os.path.join(HERE, 'eng.pdf')
CONV = r'C:\projects\tools\hwp\hwp_conv.py'
KEEP_ABOVE = 1550        # 16pt(목차 머리글)만 그대로 두고, 절 제목은 아래에서 따로 지정
FLOOR = 700
HANGUL = re.compile('[\uac00-\ud7a3]')

# 목차에서 쪽번호가 들어 있는 hp:t 의 자리(0부터) — 1절~11절 차례
TOC_SLOTS = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]
SECTIONS = ['1. Admission Schedule', '2. Admission Procedures', '3. Eligibility',
            '4. Required Documents', '5. Programs Offered', '6. Visa Application',
            '7. Scholarships', '8. Dormitory', '9. Other Information',
            '10. Important Notes', '11. Campus Guide']


def translate(xml, toc=None):
    miss, hit, kept, idx = [], 0, 0, [0]

    def sub(m):
        nonlocal hit, kept
        i = idx[0]
        idx[0] += 1
        if toc and i in toc:
            return '<hp:t>%s</hp:t>' % escape(toc[i])
        ko = unescape(m.group(1))
        if ko in TR:
            hit += 1
            return '<hp:t>%s</hp:t>' % escape(TR[ko])
        if HANGUL.search(ko):
            miss.append(ko)
            return m.group(0)
        kept += 1
        return m.group(0)

    out = re.sub(r'<hp:t>(.*?)</hp:t>', sub, xml, flags=re.S)
    if miss:
        io.open(os.path.join(HERE, 'missing.txt'), 'w', encoding='utf-8').write(
            '\n'.join(dict.fromkeys(miss)))
        raise SystemExit('미번역 %d종 — missing.txt 확인' % len(set(miss)))
    return out, hit, kept


def shrink(hdr, scale):
    n = [0]

    def one(m):
        h = int(m.group(2))
        if h > KEEP_ABOVE or h <= 100:
            return m.group(0)
        new = max(FLOOR, int(round(h * scale / 50.0)) * 50)
        if new != h:
            n[0] += 1
        return '%s%d%s' % (m.group(1), new, m.group(3))

    return re.sub(r'(<hh:charPr\b[^>]*?\bheight=")(\d+)(")', one, hdr), n[0]


TITLE_CHARPR = '95'      # 절 제목(원본 15pt 굵게, 맑은 고딕)
TITLE_PT = 13            # 영문은 길어 15pt 그대로면 상자를 넘는다
MALGUNBD = r'C:\Windows\Fonts\malgunbd.ttf'


def title_width(text, pt=TITLE_PT):
    """제목 칸에 필요한 폭(HWPUNIT). 칸 여백 좌우 6pt + 여유 4pt."""
    from PIL import Image, ImageDraw, ImageFont
    d = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    f = ImageFont.truetype(MALGUNBD, pt * 8)
    w = d.textlength(text, font=f) / 8.0
    return int((w + 12 + 4) * 100 + 99) // 100 * 100


def widen_titles(sec):
    """절 제목 칸을 글월 길이에 맞춰 넓히고, 같은 줄 옆 칸을 그만큼 줄인다."""
    n = [0]

    def one(m):
        body = m.group(0)
        got = [t for t in SECTIONS if '<hp:t>%s</hp:t>' % escape(t) in body]
        if not got:
            return body
        total = int(re.search(r'<hp:sz width="(\d+)"', body).group(1))
        w = min(title_width(got[0]), total - 8000)
        rest = total - w
        cells = [0]

        def cell(c):
            cells[0] += 1
            return '<hp:cellSz width="%d" height="%s"/>' % (w if cells[0] == 1 else rest, c.group(2))

        n[0] += 1
        return re.sub(r'<hp:cellSz width="(\d+)" height="(\d+)"/>', cell, body)

    out = re.sub(r'<hp:tbl\b.*?</hp:tbl>', one, sec, flags=re.S)
    return out, n[0]


def force_break(sec, title):
    """절 제목이 앞 쪽 맨 아래에 홀로 걸리지 않도록 쪽나눔을 준다.

    국문에서는 8절이 11쪽을 꽉 채워 9절이 자연히 12쪽에서 시작했다. 영문은 길이가 달라
    9절 제목만 11쪽 끝에 남는다. 8·10절이 쓰는 방식(바깥 문단 pageBreak="1")을 그대로 쓴다.
    """
    i = sec.find('<hp:t>%s</hp:t>' % escape(title))
    if i < 0:
        return sec, False
    tbl = sec.rfind('<hp:tbl', 0, i)
    p = sec.rfind('<hp:p ', 0, tbl)
    end = sec.find('>', p)
    head = sec[p:end + 1]
    if 'pageBreak="1"' in head:
        return sec, False
    return sec[:p] + head.replace('pageBreak="0"', 'pageBreak="1"', 1) + sec[end + 1:], True


def build(scale, toc=None):
    z = zipfile.ZipFile(SRC)
    sec, hit, kept = translate(z.read('Contents/section0.xml').decode('utf-8'), toc)
    sec, ntitle = widen_titles(sec)
    sec, broke = force_break(sec, '9. Other Information')
    hdr, nsh = shrink(z.read('Contents/header.xml').decode('utf-8'), scale)
    hdr = re.sub(r'(<hh:charPr\b[^>]*\bid="%s"[^>]*\bheight=")\d+(")' % TITLE_CHARPR,
                 r'\g<1>%d\g<2>' % (TITLE_PT * 100), hdr)
    from PIL import Image
    cov, band = io.BytesIO(), io.BytesIO()
    Image.open(os.path.join(IMG, 'cover_en3.png')).convert('RGB').save(
        cov, 'JPEG', quality=92, subsampling=0)
    Image.open(os.path.join(IMG, 'band_en.png')).convert('RGB').save(band, 'PNG', optimize=True)
    repl = {'Contents/section0.xml': sec.encode('utf-8'),
            'Contents/header.xml': hdr.encode('utf-8'),
            'BinData/image9.jpg': cov.getvalue(),
            'BinData/image7.png': band.getvalue()}
    names = z.namelist()
    zo = zipfile.ZipFile(HWPX, 'w', zipfile.ZIP_DEFLATED)
    zo.writestr(zipfile.ZipInfo('mimetype'), z.read('mimetype'), zipfile.ZIP_STORED)
    for n in names[1:]:
        zo.writestr(n, repl.get(n, z.read(n)))
    zo.close()
    print('배율 %.2f  번역 %d  그대로 %d  크기조정 %d  제목칸 %d%s'
          % (scale, hit, kept, nsh, ntitle, '  (목차 쪽번호 보정)' if toc else ''))


def hwp_pids():
    out = subprocess.run(['tasklist', '/fi', 'imagename eq hwp.exe', '/fo', 'csv', '/nh'],
                         capture_output=True, text=True, timeout=30).stdout
    got = set()
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[1].isdigit():
            got.add(parts[1])
    return got


def convert(tries=3):
    """한글 COM 변환은 가끔 응답하지 않는다. 그때 그 시도가 띄운 프로세스만 정리하고 다시 한다."""
    for k in range(1, tries + 1):
        if os.path.exists(PDF):
            os.remove(PDF)
        was = hwp_pids()
        try:
            subprocess.run([sys.executable, CONV, HWPX, PDF, 'PDF'],
                           capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired:
            for p in hwp_pids() - was:
                subprocess.run(['taskkill', '/f', '/pid', p], capture_output=True)
            print('  변환 %d회차 응답 없음, 정리하고 다시 시도' % k)
            continue
        if os.path.exists(PDF):
            break
    if not os.path.exists(PDF):
        raise SystemExit('PDF가 만들어지지 않았다 (%d회 시도)' % tries)
    import fitz
    d = fitz.open(PDF)
    pages = [d[i].get_text() for i in range(d.page_count)]
    d.close()
    return pages


def toc_pages(pages):
    """절 제목이 실제로 몇 쪽에 있는지 찾는다(4쪽 목차는 건너뛴다)."""
    out = {}
    for s, slot in zip(SECTIONS, TOC_SLOTS):
        flat = s.replace(' ', '')
        for i, t in enumerate(pages):
            if i == 3:
                continue
            if flat in re.sub(r'\s+', '', t):
                out[slot] = str(i + 1)
                break
    return out


def report(pages):
    print('쪽수 %d (국문 원본 14쪽)' % len(pages))
    for i, t in enumerate(pages):
        head = [x for x in t.splitlines() if x.strip()][:2]
        print('  %2d쪽 글자%5d  %s' % (i + 1, len(t), ' | '.join(head)[:66]))


def main():
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 0.80
    build(scale)
    pages = convert()
    report(pages)
    toc = toc_pages(pages)
    print('\n목차 쪽번호 →', {SECTIONS[i].split('.')[0]: v for i, (k, v) in enumerate(sorted(toc.items()))})
    if len(toc) < len(SECTIONS):
        print('※ 절 제목을 못 찾은 것이 있다 — 목차 보정을 건너뛴다')
        return
    build(scale, toc)
    pages = convert()
    report(pages)


main()
