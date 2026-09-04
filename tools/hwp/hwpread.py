# -*- coding: utf-8 -*-
"""HWP v5 읽기 — 본문 글월과 글자색(빨간 글씨 찾기용)을 뽑아낸다."""
import olefile, zlib, struct, sys, io, json

TAG = 0x10
T_DOC_PROPERTIES   = TAG + 0
T_CHAR_SHAPE       = TAG + 5
T_PARA_HEADER      = TAG + 50
T_PARA_TEXT        = TAG + 51
T_PARA_CHAR_SHAPE  = TAG + 52
T_PARA_LINE_SEG    = TAG + 53
T_CTRL_HEADER      = TAG + 55
T_LIST_HEADER      = TAG + 56
T_TABLE            = TAG + 61

CH_CTRL   = {0, 10, 13, 24, 25, 26, 27, 28, 29, 30, 31}      # 1글자
CH_INLINE = {4, 5, 6, 7, 8, 9, 19, 20}                        # 8글자
CH_EXT    = {1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23} # 8글자


def records(buf):
    """(tag, level, payload, header_offset, payload_offset) 를 차례로 내놓는다."""
    i, n = 0, len(buf)
    while i + 4 <= n:
        h = struct.unpack_from('<I', buf, i)[0]
        tag = h & 0x3FF
        lvl = (h >> 10) & 0x3FF
        sz = (h >> 20) & 0xFFF
        p = i + 4
        if sz == 0xFFF:
            sz = struct.unpack_from('<I', buf, p)[0]
            p += 4
        yield tag, lvl, buf[p:p + sz], i, p
        i = p + sz


def para_text(payload):
    """PARA_TEXT 를 (글자, 그 글자의 문자위치) 목록으로 푼다."""
    out = []
    k, n = 0, len(payload) // 2
    while k < n:
        c = struct.unpack_from('<H', payload, k * 2)[0]
        if c in CH_CTRL:
            out.append(('\n' if c in (10, 13) else '', k))
            k += 1
        elif c in CH_INLINE or c in CH_EXT:
            out.append(('', k))          # 표·그림 등 조종문자 자리
            k += 8
        else:
            out.append((chr(c), k))
            k += 1
    return out


def sections(f):
    ole = olefile.OleFileIO(f)
    head = ole.openstream('FileHeader').read()
    compressed = bool(head[36] & 1)

    def grab(name):
        raw = ole.openstream(name).read()
        return zlib.decompress(raw, -15) if compressed else raw

    doc = grab('DocInfo')
    secs = []
    i = 0
    while True:
        nm = 'BodyText/Section%d' % i
        if not ole.exists(nm):
            break
        secs.append(grab(nm))
        i += 1
    ole.close()
    return doc, secs, compressed


def char_colors(doc):
    """DocInfo 의 글자모양들에서 글자색만 뽑는다. 나온 차례가 곧 charShapeId."""
    cols = []
    for tag, lvl, p, _, _ in records(doc):
        if tag == T_CHAR_SHAPE:
            c = struct.unpack_from('<I', p, 52)[0] if len(p) >= 56 else 0
            cols.append((c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF))   # R,G,B
    return cols


def read(path):
    doc, secs, comp = sections(path)
    cols = char_colors(doc)
    paras = []          # {text, level, runs:[(문자열, (r,g,b))]}
    for si, sec in enumerate(secs):
        cur = None
        for tag, lvl, p, _, _ in records(sec):
            if tag == T_PARA_HEADER:
                cur = {'sec': si, 'lvl': lvl, 'chars': [], 'shapes': []}
                paras.append(cur)
            elif tag == T_PARA_TEXT and cur is not None:
                cur['chars'] = para_text(p)
            elif tag == T_PARA_CHAR_SHAPE and cur is not None:
                cur['shapes'] = [struct.unpack_from('<II', p, k * 8)
                                 for k in range(len(p) // 8)]
    # 글자 위치별 색을 입힌다
    for pa in paras:
        txt = ''.join(c for c, _ in pa['chars'])
        pa['text'] = txt
        runs, sh = [], sorted(pa['shapes'])
        for c, pos in pa['chars']:
            if not c:
                continue
            cid = 0
            for st, i in sh:
                if st <= pos:
                    cid = i
                else:
                    break
            rgb = cols[cid] if cid < len(cols) else (0, 0, 0)
            if runs and runs[-1][1] == rgb:
                runs[-1][0] += c
            else:
                runs.append([c, rgb])
        pa['runs'] = [(a, b) for a, b in runs]
    return paras, cols, comp


def is_red(rgb):
    r, g, b = rgb
    return r >= 130 and r >= g + 60 and r >= b + 60


if __name__ == '__main__':
    path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'text'
    paras, cols, comp = read(path)
    out = io.StringIO()
    if mode == 'red':
        for n, pa in enumerate(paras):
            reds = [t for t, c in pa['runs'] if is_red(c) and t.strip()]
            if reds:
                out.write('[%d] %s\n     ↳ 빨강: %s\n' % (n, pa['text'].strip(), ' | '.join(reds)))
    elif mode == 'json':
        out.write(json.dumps([{'i': n, 'lvl': p['lvl'], 'text': p['text'],
                               'runs': [[t, list(c)] for t, c in p['runs']]}
                              for n, p in enumerate(paras)], ensure_ascii=False, indent=1))
    else:
        for n, pa in enumerate(paras):
            t = pa['text'].rstrip('\n')
            out.write('[%3d|L%d] %s\n' % (n, pa['lvl'], t))
    sys.stdout.buffer.write(out.getvalue().encode('utf-8'))
