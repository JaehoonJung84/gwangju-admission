# -*- coding: utf-8 -*-
"""「외국인 유학생 입학 시행세칙」 개정(안) 전문 — 한국어 연수 면제 기준일·환불 명확화.

2026-09-29 회차의 '전문 최종안'(파란 글씨 = 지난 회차 개정분)을 틀로 쓰고,
이번 규정심의위원회 지적사항에 따른 추가 개정분만 빨간 글씨로 넣는다.
조문을 새로 만들지 않고 제4조제6호 단서와 부칙 경과조치 안에서 해결한다.

입력은 그 전문을 한글로 HWPX 로 저장한 파일이다. HWP 를 직접 고치면 문단마다 들어 있는
줄 정보(linesegarray)를 한글이 그대로 믿어 버려 고친 문단이 줄바꿈되지 않는다. HWPX 는
줄 정보를 빼 두면 한글이 열 때 다시 흘려 주므로, 고친 문단에서는 그것을 지운다.

  python rule_korean_full.py <원본.hwpx> <결과.hwpx>
"""
import os, re, sys, zipfile
from xml.sax.saxutils import escape

DATE = '2026.00.00.'
START = '2026년 00월 00일'

CS_BODY = 29        # 본문 검정
CS_NOTE = 39        # <개정 …> 표시 검정
CS_BLUE = 44        # 지난 회차 개정분(파랑)
CS_BLUE_NOTE = 45   # 지난 회차 개정표시(파랑)
R_BODY, R_NOTE = 46, 47

#  ── 제4조제6호 : 단서 한 문장에 기준일·면제 범위·환불을 모두 담는다 ──
H6_KEEP = ('  6. 이중언어과정으로 입학하는 경우, 입학 후 1년 이내에 200시간 이상의 '
           '한국어 연수를 이수하여야 한다. ')
H6_NEW = ('다만, 제1호 또는 제4호의 요건을 입학하는 학기의 개강일 이전에 갖춘 경우에는 '
          '이를 이수하지 아니하며, 연수 중에 갖춘 경우에는 그 요건을 갖춘 날'
          '(성적 발표일을 말한다)의 다음 날부터 남은 연수의 이수를 면제하고 납부한 '
          '연수비 중 남은 연수시간에 해당하는 금액을 환불한다.')

#  ── 부칙 : 조를 늘리지 않고 경과조치 한 줄에 함께 적는다 ──────────
SUP_HEAD = '제2조(경과조치) '
SUP_NEW = '제4조제6호의 개정규정은 이 세칙 시행 당시 재학 중인 자에게도 적용하고, '
SUP_KEEP = '제12조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.'


def rewrite(p, runs):
    """있는 문단의 글월만 갈아 끼우고 줄 정보는 버린다."""
    head = p[:p.index('>') + 1]
    return head + ''.join(
        '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, escape(t))
        for cp, t in runs) + '</hp:p>'


def add_reds(header):
    """파란 글자모양을 복제해 빨간 글자모양을 목록 끝에 번호가 끊기지 않게 붙인다."""
    els = dict((int(re.search(r'id="(\d+)"', e).group(1)), e)
               for e in re.findall(r'<hh:charPr\b.*?</hh:charPr>', header, re.S))
    cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)"', header).group(1))
    assert cnt == len(els) == R_BODY, '글자모양 수가 어긋난다 (%d)' % cnt
    made = ''
    for new_id, src in ((R_BODY, CS_BLUE), (R_NOTE, CS_BLUE_NOTE)):
        e = re.sub(r'id="\d+"', 'id="%d"' % new_id, els[src], count=1)
        made += re.sub(r'textColor="#[0-9A-Fa-f]{6}"', 'textColor="#FF0000"', e, count=1)
    header = header.replace('<hh:charProperties itemCnt="%d"' % cnt,
                            '<hh:charProperties itemCnt="%d"' % (cnt + 2), 1)
    i = header.index('</hh:charProperties>')
    return header[:i] + made + header[i:]


def build(src, out):
    z = zipfile.ZipFile(src)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    get = lambda n: next(d for i, d in items if i.filename == n).decode('utf-8')
    hdr = add_reds(get('Contents/header.xml'))
    sec = get('Contents/section0.xml')

    ps = [m.group(0) for m in re.finditer(r'<hp:p\b[^>]*>.*?</hp:p>', sec, re.S)]
    done = {}
    for i, p in enumerate(ps):
        txt = ''.join(re.findall(r'<hp:t>(.*?)</hp:t>', p, re.S))
        if txt.startswith('2026. 10. 00.'):                       # 최근 개정일자
            ps[i] = rewrite(p, [(CS_BLUE, '2026. 00. 00.')])
            done['head_date'] = 1
        elif txt.startswith('  6. 이중언어과정으로'):              # 제4조제6호
            ps[i] = rewrite(p, [
                (CS_BODY, H6_KEEP),
                (R_BODY, H6_NEW),
                (CS_BODY, '<신설 2025.05.14.>'),
                (CS_NOTE, '<개정 2025.07.09.>'),
                (R_NOTE, '<개정 %s>' % DATE)])
            done['h6'] = 1
        elif txt.startswith('제12조(입학 취소)'):                  # 신설 표시 날짜 맞춤
            ps[i] = p.replace('2026.10.00.', DATE)
            done['art12'] = 1
        elif txt.startswith('제1조(시행일)'):                      # 부칙 시행일
            ps[i] = rewrite(p, [(CS_BLUE, '제1조(시행일) 이 세칙은 %s부터 시행한다.'
                                 % START)])
            done['sup1'] = 1
        elif txt.startswith('제2조(경과조치)'):                    # 경과조치에 적용 범위 추가
            ps[i] = rewrite(p, [(CS_BLUE, SUP_HEAD), (R_BODY, SUP_NEW),
                                (CS_BLUE, SUP_KEEP)])
            done['sup2'] = 1

    for k in ('head_date', 'h6', 'art12', 'sup1', 'sup2'):
        assert k in done, '못 찾은 고칠 자리: %s' % k

    pos, new_sec = 0, []
    for m, p in zip(re.finditer(r'<hp:p\b[^>]*>.*?</hp:p>', sec, re.S), ps):
        new_sec.append(sec[pos:m.start()])
        new_sec.append(p)
        pos = m.end()
    new_sec.append(sec[pos:])
    sec = ''.join(new_sec)

    repl = {'Contents/header.xml': hdr.encode('utf-8'),
            'Contents/section0.xml': sec.encode('utf-8')}
    with zipfile.ZipFile(out, 'w') as zo:
        for info, data in items:
            zo.writestr(info.filename, repl.get(info.filename, data),
                        zipfile.ZIP_STORED if info.filename == 'mimetype'
                        else zipfile.ZIP_DEFLATED)
    print('고친 자리 %d곳, 문단 %d개 (조문 신설 없음)' % (len(done), len(ps)))
    print('만든 파일: %s  %d 바이트' % (out, os.path.getsize(out)))


if __name__ == '__main__':
    o = os.path.abspath(sys.argv[2])
    os.makedirs(os.path.dirname(o), exist_ok=True)
    build(os.path.abspath(sys.argv[1]), o)
