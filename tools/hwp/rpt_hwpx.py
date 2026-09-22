# -*- coding: utf-8 -*-
"""보고자료(★보고자료 양식 계열) 생성기 — HWPX 주입 방식.

이미 한글이 열어 본 적 있는 보고서를 뼈대로 삼아 HWPX 로 바꾼 뒤,
머리표(제목·일시)와 본문 문단·표만 새로 써 넣고 다시 HWP 로 저장한다.
바이너리(HWP v5) 직접 생성보다 안전하다 — 표가 들어간 문서에서 한글이 열기를 거부하는 일이 없다.

  python rpt_hwpx.py <내용모듈> <작업폴더> <결과파일명>
      예: python rpt_hwpx.py pi_content C:/temp/rpt "보고서.hwp"

내용 모듈에는 TITLE, DATE, BODY 가 있어야 한다. BODY 항목:
  ('sec' , '□ ...')  절 제목(진하게)   ('item', '  ○ ...')  1단계
  ('sub' , '    - ...')  2단계          ('bl'  , '')         빈 줄
  ('table', {'w': [열너비비율...], 'rows': [[셀,...], ...]})  첫 행이 머리행
"""
import importlib, os, re, shutil, subprocess, sys, zipfile
from xml.sax.saxutils import escape

SKEL = (r'C:\Users\user\Desktop\★국제협력처\0. 보고서'
        r'\20260819 2025학년도 후기 외국인 유학생 학위수여식 계획(안).hwp')

PP_BODY = 40          # 본문 문단모양(여백 0) — 여기서 복제해 내어쓰기 문단을 만든다
PP_CELL = 52          # 표 셀 문단모양(가운데)
CP_SEC = 51           # 절 제목 글자모양(진하게)
CP_ITEM = 52          # 본문 글자모양
CP_HEAD = 46          # 표 머리행 글자모양
CP_CELL = 47          # 표 본문행 글자모양
BF_HEAD = 23          # 머리행 테두리·배경
BF_CELL = 24          # 본문행 테두리·배경
BF_TBL = 21           # 표 자체
TBL_W = 50996         # 본문 폭
ROW_H = 1948          # 한 줄짜리 셀 높이

# 줄 종류별 내어쓰기 폭(HWPUNIT) — 앞 공백 + 기호 + 한 칸
INTENT = {'sec': 1670, 'item': 3000, 'sub': 3600, 'bl': 0}   # PDF 실측값


def conv(py, src, dst, fmt):
    r = subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hwp_conv.py'),
                        src, dst, fmt], capture_output=True, text=True, timeout=300)
    if 'save True' not in r.stdout:
        raise SystemExit('한글 변환 실패: %s %s' % (r.stdout, r.stderr))


def para(pp, cp, text=''):
    run = '<hp:run charPrIDRef="%d">%s</hp:run>' % (cp, '<hp:t>%s</hp:t>' % escape(text) if text else '')
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" '
            'merged="0">%s</hp:p>' % (pp, run))


def cell(text, col, row, w, h, head):
    p = ('<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" '
         'merged="0"><hp:run charPrIDRef="%d">%s</hp:run></hp:p>'
         % (PP_CELL, CP_HEAD if head else CP_CELL,
            '<hp:t>%s</hp:t>' % escape(text) if text else ''))
    return ('<hp:tc name="" header="%d" hasMargin="0" protect="0" editable="0" dirty="0" '
            'borderFillIDRef="%d"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" '
            'vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" '
            'hasTextRef="0" hasNumRef="0">%s</hp:subList><hp:cellAddr colAddr="%d" rowAddr="%d"/>'
            '<hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="%d" height="%d"/>'
            '<hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
            % (1 if head else 0, BF_HEAD if head else BF_CELL, p, col, row, w, h))


def table(spec, tid):
    ws, rows = spec['w'], spec['rows']
    tot = sum(ws)
    widths = [int(TBL_W * x / tot) for x in ws]
    widths[-1] += TBL_W - sum(widths)
    trs = []
    for r, row in enumerate(rows):
        tcs = [cell(str(v), c, r, widths[c], ROW_H, r == 0) for c, v in enumerate(row)]
        trs.append('<hp:tr>%s</hp:tr>' % ''.join(tcs))
    tbl = ('<hp:tbl id="%d" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
           'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" '
           'rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="%d" noAdjust="0">'
           '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
           '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="0" allowOverlap="0" '
           'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" '
           'vertOffset="0" horzOffset="0"/><hp:outMargin left="140" right="140" top="140" bottom="140"/>'
           '<hp:inMargin left="510" right="510" top="141" bottom="141"/>%s</hp:tbl>'
           % (tid, len(rows), len(ws), BF_TBL, TBL_W, ROW_H * len(rows), ''.join(trs)))
    return ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="%d">%s<hp:t/></hp:run></hp:p>' % (PP_BODY, CP_SEC, tbl))


def add_parapr(header, intents):
    """paraPr 40 을 복제해 내어쓰기만 다른 문단모양을 추가하고 {폭: id} 를 돌려준다."""
    src = re.search(r'<hh:paraPr id="%d".*?</hh:paraPr>' % PP_BODY, header, re.S).group(0)
    cnt = int(re.search(r'<hh:paraProperties itemCnt="(\d+)"', header).group(1))
    made, new = {}, []
    for w in sorted(set(intents)):
        if w == 0:
            made[w] = PP_BODY
            continue
        x = src.replace('id="%d"' % PP_BODY, 'id="%d"' % cnt, 1)
        # 왼쪽 여백은 0 그대로 두고 내어쓰기만 준다(앞 공백은 글자로 넣는다).
        # HwpUnitChar 가지의 값은 default 가지의 절반이다.
        x = x.replace('<hc:intent value="0" unit="HWPUNIT"/>',
                      '<hc:intent value="%d" unit="HWPUNIT"/>' % (-w), 1)
        x = x.replace('<hc:intent value="0" unit="HWPUNIT"/>',
                      '<hc:intent value="%d" unit="HWPUNIT"/>' % (-2 * w), 1)
        made[w] = cnt
        new.append(x)
        cnt += 1
    header = header.replace('<hh:paraProperties itemCnt="%s"'
                            % re.search(r'<hh:paraProperties itemCnt="(\d+)"', header).group(1),
                            '<hh:paraProperties itemCnt="%d"' % cnt, 1)
    header = header.replace('</hh:paraProperties>', ''.join(new) + '</hh:paraProperties>', 1)
    return header, made


def main():
    mod = importlib.import_module(sys.argv[1])
    work = os.path.abspath(sys.argv[2])
    outname = sys.argv[3] if len(sys.argv) > 3 else '보고서.hwp'
    os.makedirs(work, exist_ok=True)
    py = sys.executable

    skel = os.path.join(work, '_skel.hwp')
    shutil.copyfile(SKEL, skel)
    sx = os.path.join(work, '_skel.hwpx')
    if not os.path.exists(sx):
        conv(py, skel, sx, 'HWPX')

    z = zipfile.ZipFile(sx)
    items = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    get = lambda n: next(d for i, d in items if i.filename == n).decode('utf-8')
    sec, hdr = get('Contents/section0.xml'), get('Contents/header.xml')

    hdr, ppid = add_parapr(hdr, [INTENT[k] for k, _ in mod.BODY if k in INTENT])

    # 머리표 제목·일시 교체
    def swap(x, old, new):
        tag = '<hp:t>%s</hp:t>' % escape(old)
        assert x.count(tag) == 1, '머리표 글자 못 찾음: %r' % old
        return x.replace(tag, '<hp:t>%s</hp:t>' % escape(new))
    ttl = re.search(r'<hp:t>([^<]*계획\(안\))</hp:t>', sec).group(1)
    dat = re.search(r'<hp:t>(\s*일시:[^<]*)</hp:t>', sec).group(1)
    sec = swap(sec, ttl, mod.TITLE)
    sec = swap(sec, dat, mod.DATE)

    # 본문 = 머리표 표 문단 다음부터 구역 끝까지 전부 교체
    # 머리표(첫 표)를 담은 문단의 끝 — 표 안 셀 문단이 아니라 표가 닫힌 뒤의 </hp:p> 여야 한다
    tbl_close = sec.index('</hp:tbl>', sec.index('<hp:tbl ')) + len('</hp:tbl>')
    head_tbl_end = sec.index('</hp:p>', tbl_close) + len('</hp:p>')
    tail = sec.index('</hs:sec>')
    body, tid = [], 1000000001
    for kind, val in mod.BODY:
        if kind == 'table':
            body.append(table(val, tid)); tid += 1
        elif kind == 'bl':
            body.append(para(PP_BODY, CP_ITEM))
        else:
            body.append(para(ppid[INTENT[kind]], CP_SEC if kind == 'sec' else CP_ITEM, val))
    sec = sec[:head_tbl_end] + ''.join(body) + sec[tail:]

    out_hwpx = os.path.join(work, '_out.hwpx')
    with zipfile.ZipFile(out_hwpx, 'w') as zo:
        for info, data in items:
            if info.filename == 'Contents/section0.xml':
                data = sec.encode('utf-8')
            elif info.filename == 'Contents/header.xml':
                data = hdr.encode('utf-8')
            zo.writestr(info.filename, data,
                        zipfile.ZIP_STORED if info.filename == 'mimetype' else zipfile.ZIP_DEFLATED)

    out_hwp = os.path.join(work, outname)
    conv(py, out_hwpx, out_hwp, 'HWP')
    conv(py, out_hwp, os.path.splitext(out_hwp)[0] + '.pdf', 'PDF')
    print('완료:', out_hwp)


if __name__ == '__main__':
    main()
