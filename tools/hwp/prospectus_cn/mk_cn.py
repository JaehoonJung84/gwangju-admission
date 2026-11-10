# -*- coding: utf-8 -*-
"""대학원 중문 모집요강 HWPX를 만들고 PDF로 바꾼다.

  python mk_cn.py [본문배율]   예: python mk_cn.py 1.0

영문본과 달리 **본문을 줄이지 않는다**. 중국어가 한국어보다 짧아 사무처가 낸 학부
중문본도 국문과 같은 14쪽에 들어갔다. 대신 두 가지를 손본다.
  ① 한자 글꼴: HWP 는 중국어 글자를 '한자' 로 보므로, header.xml 의 HANJA 글꼴묶음을
     Microsoft YaHei 로 바꾼다(학부 중문본도 YaHei 로 조판돼 있다).
  ② 절 제목 칸: 중문 제목이 칸보다 길면 칸을 넓힌다.
쪽이 밀리면 목차 쪽번호를 실제 쪽에 맞춰 고쳐 다시 변환하는 것은 영문본과 같다.
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
from trans_cn import TR                                          # noqa: E402

SRC = os.path.join(r'C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강\대학원',
                   '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_초안_14차.hwpx')
IMG = os.path.join(HERE, 'img')
HWPX = os.path.join(HERE, 'cn.hwpx')
PDF = os.path.join(HERE, 'cn.pdf')
CONV = r'C:\projects\tools\hwp\hwp_conv.py'
ORIG_PAGES = 15
KEEP_ABOVE = 1550
FLOOR = 700
HANGUL = re.compile('[\uac00-\ud7a3]')
CJK = re.compile('[\u4e00-\u9fff]')

TOC_SLOTS = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
SECTIONS = ['1. 招生日程', '2. 选拔方法', '3. 申请资格', '4. 提交材料',
            '5. 招生专业', '6. 签证申请', '7. 奖学金', '8. 宿舍',
            '9. 其他事项', '10. 注意事项', '11. 主任教授介绍', '12. 校园指南']
BREAKS = []
# 표에서 통째로 빼는 열(머리글로 지정). 주임교수 이름은 한자 표기를 확인할 수 없어 뺀다.
DROP_COLS = ['主任教授']

LINE_SPACE = 0.97                  # 줄간격 조임(YaHei 줄높이 보정). 1.0 이면 원본 그대로
TITLE_PT = 15                      # 원본 절 제목 크기 그대로(중문은 짧아 줄일 까닭이 없다)
YAHEI_BD = r'C:\Windows\Fonts\msyhbd.ttc'
CN_FONT = 'Microsoft YaHei'

# 번역하지 않고 한글 그대로 두는 것(사람 이름·장학금 고유명·건물명).
# 이것들이 남는 것은 정상이므로 '미번역' 으로 세지 않는다.
KEEP_HANGUL = {v for k, v in TR.items() if HANGUL.search(v)}


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


def hanja_font(hdr):
    """중국어 글자가 쓰는 '한자' 글꼴묶음을 통째로 YaHei 로 바꾼다."""
    n = [0]

    def one(m):
        blk = m.group(0)
        if 'lang="HANJA"' not in blk:
            return blk

        def face(f):
            n[0] += 1
            return '%s%s%s' % (f.group(1), CN_FONT, f.group(3))

        return re.sub(r'(<hh:font\b[^>]*?\bface=")([^"]*)(")', face, blk)

    return re.sub(r'<hh:fontface\b[^>]*>.*?</hh:fontface>', one, hdr, flags=re.S), n[0]


def line_space(hdr, factor):
    """줄간격(퍼센트)을 조금 조인다.

    YaHei 는 맑은 고딕보다 줄높이가 커서, 글자 크기가 같아도 쪽이 한 줄씩 넘친다.
    글자를 줄이는 것보다 줄간격을 2~5% 조이는 쪽이 눈에 덜 띈다. 이미 좁은 것
    (130% 미만)은 건드리지 않는다.
    """
    n = [0]

    def one(m):
        v = int(m.group(2))
        if v < 130:
            return m.group(0)
        new = max(100, int(round(v * factor)))
        if new != v:
            n[0] += 1
        return '%s%d%s' % (m.group(1), new, m.group(3))

    return re.sub(r'(<hh:lineSpacing type="PERCENT" value=")(\d+)(")', one, hdr), n[0]


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


def title_width(text, pt=TITLE_PT):
    from PIL import Image, ImageDraw, ImageFont
    d = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    f = ImageFont.truetype(YAHEI_BD, pt * 8, index=0)
    w = d.textlength(text, font=f) / 8.0
    return int((w + 12 + 4) * 100 + 99) // 100 * 100      # 칸 여백 좌우 6pt + 여유 4pt


def widen_titles(sec):
    """절 제목이 칸보다 길 때만 칸을 넓힌다(짧으면 원본 그대로 둔다)."""
    n = [0]

    def one(m):
        body = m.group(0)
        got = [t for t in SECTIONS if '<hp:t>%s</hp:t>' % escape(t) in body]
        if not got:
            return body
        total = int(re.search(r'<hp:sz width="(\d+)"', body).group(1))
        cells = re.findall(r'<hp:cellSz width="(\d+)" height="(\d+)"/>', body)
        if not cells:
            return body
        now = int(cells[0][0])
        want = min(title_width(got[0]), total - 8000)
        if want <= now:
            return body
        rest = total - want
        k = [0]

        def cell(c):
            k[0] += 1
            return '<hp:cellSz width="%d" height="%s"/>' % (want if k[0] == 1 else rest,
                                                            c.group(2))

        n[0] += 1
        return re.sub(r'<hp:cellSz width="(\d+)" height="(\d+)"/>', cell, body)

    return re.sub(r'<hp:tbl\b.*?</hp:tbl>', one, sec, flags=re.S), n[0]


def drop_column(sec, header):
    """머리글이 `header` 인 열을 표에서 통째로 뺀다.

    칸만 지우면 표가 어긋난다. 뒤쪽 열의 colAddr 를 한 칸씩 당기고, colCnt 를 줄이고,
    뺀 너비는 바로 왼쪽 열에 더해 표 전체 너비를 그대로 지킨다.
    """
    tag = '<hp:t>%s</hp:t>' % escape(header)
    n = [0]

    def one(m):
        body = m.group(0)
        if tag not in body:
            return body
        col = w = None
        for tc in re.finditer(r'<hp:tc\b.*?</hp:tc>', body, re.S):
            c = tc.group(0)
            if tag in c:
                col = int(re.search(r'colAddr="(\d+)"', c).group(1))
                w = int(re.search(r'<hp:cellSz width="(\d+)"', c).group(1))
                break
        if col is None or col == 0:
            return body

        # 가로로 병합된 칸이 걸쳐 있으면 손대지 않는다(조용히 망가지는 것을 막는다)
        for tc in re.finditer(r'<hp:tc\b.*?</hp:tc>', body, re.S):
            c = tc.group(0)
            a = int(re.search(r'colAddr="(\d+)"', c).group(1))
            cs = int(re.search(r'colSpan="(\d+)"', c).group(1))
            if cs > 1 and a <= col < a + cs:
                raise SystemExit('가로 병합된 칸이 "%s" 열에 걸쳐 있다 — 손대지 않는다' % header)

        def cell(tc):
            c = tc.group(0)
            a = int(re.search(r'colAddr="(\d+)"', c).group(1))
            if a == col:
                return ''                                   # 이 칸을 뺀다
            if a == col - 1:                                # 왼쪽 열이 뺀 너비를 흡수
                c = re.sub(r'(<hp:cellSz width=")(\d+)(")',
                           lambda s: '%s%d%s' % (s.group(1), int(s.group(2)) + w, s.group(3)), c)
            if a > col:
                c = c.replace('colAddr="%d"' % a, 'colAddr="%d"' % (a - 1), 1)
            return c

        body = re.sub(r'<hp:tc\b.*?</hp:tc>', cell, body, flags=re.S)
        head = body[:body.find('>') + 1]
        cnt = int(re.search(r'colCnt="(\d+)"', head).group(1))
        body = body.replace(head, head.replace('colCnt="%d"' % cnt,
                                               'colCnt="%d"' % (cnt - 1), 1), 1)
        n[0] += 1
        return body

    return re.sub(r'<hp:tbl\b.*?</hp:tbl>', one, sec, flags=re.S), n[0]


def force_break(sec, title):
    """절 제목 표를 품은 '바깥' 문단에 쪽나눔을 준다."""
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
    ndrop = 0
    for h in DROP_COLS:
        sec, k = drop_column(sec, h)
        ndrop += k
    for t in BREAKS:
        sec, _ = force_break(sec, t)
    hdr, nfont = hanja_font(z.read('Contents/header.xml').decode('utf-8'))
    hdr, nls = line_space(hdr, LINE_SPACE)
    hdr, nsh = shrink(hdr, scale)
    from PIL import Image
    cov, band = io.BytesIO(), io.BytesIO()
    Image.open(os.path.join(IMG, 'cover_cn.png')).convert('RGB').save(
        cov, 'JPEG', quality=92, subsampling=0)
    Image.open(os.path.join(IMG, 'band_cn.png')).convert('RGB').save(band, 'PNG', optimize=True)
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
    print('배율 %.2f  줄간격 %.2f(%d곳)  번역 %d  그대로 %d  한자글꼴 %d  크기조정 %d  제목칸 %d  열뺌 %d%s'
          % (scale, LINE_SPACE, nls, hit, kept, nfont, nsh, ntitle, ndrop,
             '  (목차 쪽번호 보정)' if toc else ''))


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
    """절 제목이 실제 몇 쪽인지 찾는다. 목차 쪽 자신은 건너뛴다.

    목차가 몇 쪽인지는 판마다 다르므로(대학원 10차는 4쪽, 14차는 2쪽) 쪽 번호를
    박아 두지 않고 'C O N T E N T S' 가 있는 쪽을 찾아 건너뛴다.
    """
    flats = [re.sub(r'\s+', '', t) for t in pages]
    skip = {i for i, f in enumerate(flats) if 'CONTENTS' in f}
    out = {}
    for s, slot in zip(SECTIONS, TOC_SLOTS):
        flat = s.replace(' ', '')
        for i, f in enumerate(flats):
            if i in skip:
                continue
            if flat in f:
                out[slot] = str(i + 1)
                break
    return out


def report(pages, tag=''):
    """쪽별 내용을 UTF-8 파일에 적는다(cp949 콘솔은 중문을 못 찍는다)."""
    lines = ['쪽수 %d (국문 원본 %d쪽)' % (len(pages), ORIG_PAGES)]
    left = []
    for i, t in enumerate(pages):
        head = [x for x in t.splitlines() if x.strip()][:3]
        lines.append('%2d쪽 글자%5d  %s' % (i + 1, len(t), ' | '.join(head)[:70]))
        for line in t.splitlines():
            if HANGUL.search(line) and line.strip() not in KEEP_HANGUL:
                left.append('%d쪽: %s' % (i + 1, line.strip()[:60]))
    lines.append('')
    lines.append('한글이 남은 줄 %d개 (사람이름·장학금 고유명 제외)' % len(left))
    lines += ['   ' + x for x in left[:20]]
    io.open(os.path.join(HERE, 'report%s.txt' % tag), 'w', encoding='utf-8').write(
        os.linesep.join(lines))
    print('쪽수 %d (국문 %d쪽), 한글 남은 줄 %d개 -> report%s.txt'
          % (len(pages), ORIG_PAGES, len(left), tag))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    scale = float(args[0]) if args else 1.0
    build(scale)
    if '--build' in sys.argv:                 # HWPX 까지만(한글 변환이 막혔을 때)
        return
    pages = convert()
    report(pages, '1')
    toc = toc_pages(pages)
    print('\n목차 쪽번호 →', [toc.get(s, '?') for s in TOC_SLOTS])
    if len(toc) < len(SECTIONS):
        print('[!] 절 제목을 못 찾은 것이 있다. 목차 보정을 건너뛴다')
        return
    build(scale, toc)
    pages = convert()
    report(pages, '2')


main()
