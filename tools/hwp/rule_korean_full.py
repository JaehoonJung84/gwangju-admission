# -*- coding: utf-8 -*-
"""「외국인 유학생 입학 시행세칙」 개정(안) 전문 — 한국어 연수 이수의무 면제·환불 명확화.

2026-09-29 회차의 '전문 최종안'(파란 글씨 = 지난 회차 개정분)을 틀로 쓰고,
이번 규정심의위원회 지적사항에 따른 추가 개정분만 빨간 글씨로 끼워 넣는다.

입력은 그 전문을 한글로 HWPX 로 저장한 파일이다. HWP 로 직접 고치면 문단마다
들어 있는 줄 정보(linesegarray)를 한글이 그대로 믿어 버려 새 문단이 줄바꿈되지
않는다. HWPX 는 줄 정보를 빼 두면 한글이 열 때 다시 흘려 주므로, 고친 문단과
새 문단에서는 linesegarray 를 지운다.

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
PP_BODY = 26        # 본문 문단모양

#  ── 제4조제6호 : 단서를 다시 쓴다 ────────────────────────────────
H6_KEEP = ('  6. 이중언어과정으로 입학하는 경우, 입학 후 1년 이내에 200시간 이상의 '
           '한국어 연수를 이수하여야 한다. ')
H6_NEW = ('다만, 제1호 또는 제4호에 해당하는 자는 그러하지 아니하며, 그 기준일과 '
          '연수비 환불에 관한 사항은 제4조의2에서 정하는 바에 따른다.')

#  ── 제4조의2 신설 ────────────────────────────────────────────────
ART42 = [
    ('제4조의2(한국어 연수 이수의무의 면제 및 연수비 환불) ', '<신설 %s>' % DATE),
    ('  ① 제4조제6호 단서에 따라 한국어 연수 이수의무를 면제받으려는 자는 같은 조 '
     '제1호 또는 제4호의 요건을 갖춘 사실을 증명하는 서류를 국제협력처에 '
     '제출하여야 한다.', None),
    ('  ② 제1항의 요건을 갖춘 날(이하 “요건충족일”이라 한다)은 한국어능력시험'
     '(TOPIK, TOPIK IBT) 또는 GU-TOPIK의 성적 발표일로 하며, 제4조제4호에 해당하는 '
     '경우에는 어학연수과정 수료일과 GU-TOPIK 성적 발표일 중 늦은 날로 한다.', None),
    ('  ③ 한국어 연수 이수의무의 면제 범위는 다음 각 호와 같다.', None),
    ('    1. 요건충족일이 입학하는 학기의 개강일 이전인 경우: 한국어 연수를 '
     '이수하지 아니한다.', None),
    ('    2. 요건충족일이 입학하는 학기의 개강일 후인 경우: 요건충족일의 다음 날부터 '
     '남은 연수시간의 이수를 면제한다.', None),
    ('  ④ 제3항제2호에 따라 이수를 면제받은 자가 연수비를 납부한 경우에는 다음 '
     '산식에 따라 산정한 금액을 환불한다. 이 경우 국제협력처장은 제1항의 서류를 '
     '접수한 날부터 30일 이내에 본인 명의의 계좌로 지급한다.', None),
    ('      환불액 = 납부한 연수비 × 남은 연수시간 ÷ 전체 연수시간', None),
    ('  ⑤ 연수비의 납부 및 환불에 관하여 이 세칙에서 정하지 아니한 사항은 '
     '「한국어 어학연수과정 운영 시행세칙」에서 정하는 바에 따른다.', None),
]

#  ── 부칙 : 적용례 한 조 신설, 경과조치는 제3조로 밀린다 ──────────
SUP_APPLY = ('제2조(적용례) 제4조제6호 및 제4조의2의 개정규정은 이 세칙 시행 당시 '
             '재학 중인 자에게도 적용한다.')
SUP_TRANS_HEAD = '제3조(경과조치) '
SUP_TRANS_BODY = '제12조의 개정 규정은 2026학년도 2학기 학생모집부터 적용한다.'


def para(pp, runs):
    """줄 정보를 달지 않은 새 문단 — 한글이 열 때 알아서 줄을 흘린다."""
    body = ''.join('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, escape(t))
                   for cp, t in runs)
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" '
            'merged="0">%s</hp:p>' % (pp, body))


def rewrite(p, runs):
    """있는 문단의 글월만 갈아 끼우고 줄 정보는 버린다."""
    head = p[:p.index('>') + 1]
    pp = int(re.search(r'paraPrIDRef="(\d+)"', head).group(1))
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
        elif txt.startswith('제5조'):                              # 앞에 제4조의2 를 끼운다
            new = ''
            for body, note in ART42:
                runs = [(R_BODY, body)] + ([(R_NOTE, note)] if note else [])
                new += para(PP_BODY, runs)
            ps[i] = new + para(PP_BODY, [(R_BODY, ' ')]) + p
            done['art42'] = 1
        elif txt.startswith('제12조(입학 취소)'):                  # 신설 표시 날짜 맞춤
            ps[i] = p.replace('2026.10.00.', DATE)
            done['art12'] = 1
        elif txt.startswith('제1조(시행일)'):                      # 부칙 시행일
            ps[i] = rewrite(p, [(CS_BLUE, '제1조(시행일) 이 세칙은 %s부터 시행한다.'
                                 % START)])
            done['sup1'] = 1
        elif txt.startswith('제2조(경과조치)'):                    # 적용례 신설 + 번호 조정
            ps[i] = (para(PP_BODY, [(R_BODY, SUP_APPLY)])
                     + rewrite(p, [(R_BODY, SUP_TRANS_HEAD), (CS_BLUE, SUP_TRANS_BODY)]))
            done['sup2'] = 1

    for k in ('head_date', 'h6', 'art42', 'art12', 'sup1', 'sup2'):
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
    print('빨간 글자모양 %d·%d 추가 (글자모양 %d개)' % (R_BODY, R_NOTE, R_NOTE + 1))
    print('문단 %d개 → %d개' % (len(ps), len(re.findall(r'<hp:p\b', sec))))
    print('만든 파일: %s  %d 바이트' % (out, os.path.getsize(out)))


if __name__ == '__main__':
    o = os.path.abspath(sys.argv[2])
    os.makedirs(os.path.dirname(o), exist_ok=True)
    build(os.path.abspath(sys.argv[1]), o)
