# -*- coding: utf-8 -*-
"""학처장단회의 자료(국제협력처) 만들기 — 교무처 양식 그대로, 칸 안 내용만 바꾼다.

  python hak_build.py <작업폴더>
    1) 양식 HWP → HWPX (한글 COM)
    2) section0.xml 의 머리 칸(제목·일시·작성)과 실시/계획/협의 칸 문단만 교체
    3) HWPX → HWP, PDF (한글 COM)   ※ ★ 경로엔 SaveAs 가 멈추므로 작업폴더에서 만든다
서식 번호는 양식에서 실측한 값(문단 60/61/62/63, 글자 43/53/54/51)만 쓴다.
"""
import os, re, sys, shutil, zipfile
from xml.sax.saxutils import escape
import win32com.client as W
import hak_content as C

FORM = r'C:/Users/user/Desktop/★국제협력처/0. 회의/2. 학처장회의/★ 학처장단회의자료(20260000)-국제협력처(양식).hwp'
WORK = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'hak_work')
os.makedirs(WORK, exist_ok=True)

HEAD_FIRST = (61, 43)   # 칸 첫 소제목
HEAD_NEXT = (62, 43)    # 이후 소제목
ITEM = (60, 53)         # ① 항목(굵게)
DETAIL = (60, 54)       # - 세부 / ※
CIRCLED = ''.join(chr(c) for c in range(0x2460, 0x2474))   # ①~⑳


def hwp_app():
    h = W.Dispatch('HWPFrame.HwpObject')
    h.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
    try:
        h.XHwpWindows.Item(0).Visible = False
    except Exception:
        pass
    return h


def convert(h, src, dst, fmt):
    if not h.Open(src, '', 'forceopen:true'):
        raise SystemExit('열기 실패: ' + src)
    if not h.SaveAs(dst, fmt, ''):
        raise SystemExit('저장 실패: ' + dst)
    h.Clear(1)


def para(pp, cp, text):
    return ('<hp:p id="2147483648" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" '
            'columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>'
            % (pp, cp, escape(text)))


def lines_to_paras(block):
    out, first = [], True
    for raw in block.strip().splitlines():
        t = raw.strip()
        if not t:
            continue
        if re.match(r'^\(\d+\)', t):
            pp, cp = HEAD_FIRST if first else HEAD_NEXT
            first = False
            out.append(para(pp, cp, t))
        elif t[0] in CIRCLED:
            out.append(para(*ITEM, '   ' + t))
        elif t.startswith('※'):
            out.append(para(*DETAIL, '      ' + t))
        elif t.startswith('-'):
            out.append(para(*DETAIL, '    ' + t))
        else:
            raise SystemExit('종류를 모르는 줄: ' + t)
    return ''.join(out)


def replace_cell(xml, row, col, body):
    """cellAddr(col,row) 인 칸의 subList 안 문단을 통째로 바꾼다."""
    addr = '<hp:cellAddr colAddr="%d" rowAddr="%d"/>' % (col, row)
    end = xml.index(addr)
    close = xml.rindex('</hp:subList>', 0, end)
    opn = xml.rindex('<hp:subList ', 0, close)
    opn = xml.index('>', opn) + 1
    inner = xml[opn:close]
    assert '<hp:tbl' not in inner and '<hp:subList' not in inner, '칸 경계 오류 r%d c%d' % (row, col)
    return xml[:opn] + body + xml[close:], inner


def swap_text(xml, old, new):
    tag = '<hp:t>%s</hp:t>' % escape(old)
    assert xml.count(tag) == 1, '머리 칸 글자 찾기 실패: %r (%d)' % (old, xml.count(tag))
    return xml.replace(tag, '<hp:t>%s</hp:t>' % escape(new))


def main():
    h = hwp_app()
    try:
        form = os.path.join(WORK, 'form.hwp')
        shutil.copyfile(FORM, form)
        fx = os.path.join(WORK, 'form.hwpx')
        convert(h, form, fx, 'HWPX')

        z = zipfile.ZipFile(fx)
        items = [(i, z.read(i.filename)) for i in z.infolist()]
        z.close()
        sec = next(d for i, d in items if i.filename == 'Contents/section0.xml').decode('utf-8')

        sec = swap_text(sec, '2026학년도 광주대학교 학⋅처장단회의 회의자료 (교무처)',
                        '2026학년도 광주대학교 학⋅처장단회의 회의자료 (국제협력처)')
        sec = swap_text(sec, ' 2026.9.16.(수) 14:00', ' ' + C.MEETING)
        sec = swap_text(sec, '작성: 처장 김상엽', C.WRITER)

        sec, old = replace_cell(sec, 4, 7, lines_to_paras(C.DONE))
        assert '교무업적팀' in old
        sec, old = replace_cell(sec, 5, 7, lines_to_paras(C.PLAN))
        assert '교무업적팀' in old
        disc = lines_to_paras(C.DISCUSS) if C.DISCUSS.strip() else para(63, 51, ' ')
        sec, old = replace_cell(sec, 6, 7, disc)
        assert '>-<' in old

        out = os.path.join(WORK, 'out.hwpx')
        with zipfile.ZipFile(out, 'w') as zo:
            for info, data in items:
                if info.filename == 'Contents/section0.xml':
                    data = sec.encode('utf-8')
                ct = zipfile.ZIP_STORED if info.filename == 'mimetype' else zipfile.ZIP_DEFLATED
                zo.writestr(info.filename, data, compress_type=ct)

        hwp_out = os.path.join(WORK, 'out.hwp')
        convert(h, out, hwp_out, 'HWP')
        convert(h, hwp_out, os.path.join(WORK, 'out.pdf'), 'PDF')
        print('완료:', hwp_out)
    finally:
        h.Quit()


if __name__ == '__main__':
    main()
