# -*- coding: utf-8 -*-
"""크롬 세션 파일(SNSS)을 정식으로 해석해 창·탭 구성을 되살린다.

파일 = "SNSS" + 버전(int32) + [길이(uint16) + 명령(1바이트) + 내용] 반복.
필요한 명령만 읽는다.
  0  탭을 창에 붙임 (window_id, tab_id)
  2  창 안 탭 순서 (tab_id, index)
  6  탭 이동 기록 갱신 (tab_id, index, 주소, 제목 …)  ← Pickle
  7  탭이 보고 있던 기록 번호 (tab_id, index)
 16  탭 닫힘 (tab_id)
 17  창 닫힘 (window_id)
 20  활성 창 (window_id)
"""
import io
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


class Pickle(object):
    def __init__(self, raw):
        (self.size,) = struct.unpack_from('<i', raw, 0)
        self.buf = raw[4:4 + self.size]
        self.pos = 0

    def _take(self, n):
        if self.pos + n > len(self.buf):
            raise EOFError
        out = self.buf[self.pos:self.pos + n]
        self.pos += (n + 3) & ~3          # 4바이트 경계로 맞춤
        return out

    def i32(self):
        return struct.unpack('<i', self._take(4))[0]

    def s(self):
        n = self.i32()
        if n < 0 or n > 1 << 20:
            raise EOFError
        return self._take(n).decode('utf-8', 'replace')

    def s16(self):
        n = self.i32()
        if n < 0 or n > 1 << 20:
            raise EOFError
        return self._take(n * 2).decode('utf-16-le', 'replace')


def commands(path):
    raw = io.open(path, 'rb').read()
    if raw[:4] != b'SNSS':
        raise SystemExit('SNSS 파일이 아니다: %s' % path)
    pos = 8
    while pos + 2 <= len(raw):
        (n,) = struct.unpack_from('<H', raw, pos)
        pos += 2
        if n == 0 or pos + n > len(raw):
            break
        yield raw[pos], raw[pos + 1:pos + n]
        pos += n


def parse(path):
    tab_win, tab_idx, navs, cur = {}, {}, {}, {}
    dead_tab, dead_win, active = set(), set(), [None]
    for cid, body in commands(path):
        try:
            if cid == 0 and len(body) >= 8:
                w, t = struct.unpack_from('<ii', body, 0)
                tab_win[t] = w
            elif cid == 2 and len(body) >= 8:
                t, i = struct.unpack_from('<ii', body, 0)
                tab_idx[t] = i
            elif cid == 6:
                # 하나의 Pickle 안에 tab_id, 기록번호, 주소, 제목이 차례로 들어 있다
                p = Pickle(body)
                t = p.i32()
                idx = p.i32()
                url = p.s()
                title = p.s16()
                navs.setdefault(t, {})[idx] = (url, title)
            elif cid == 7 and len(body) >= 8:
                t, i = struct.unpack_from('<ii', body, 0)
                cur[t] = i
            elif cid == 16 and len(body) >= 4:
                dead_tab.add(struct.unpack_from('<i', body, 0)[0])
            elif cid == 17 and len(body) >= 4:
                dead_win.add(struct.unpack_from('<i', body, 0)[0])
            elif cid == 20 and len(body) >= 4:
                active[0] = struct.unpack_from('<i', body, 0)[0]
        except (EOFError, struct.error, UnicodeDecodeError):
            continue

    # X 를 누른 순간 크롬이 모든 탭·창에 '닫힘' 을 적어 두므로, 닫힘 표시를 걸러내면
    # 되살릴 것이 하나도 남지 않는다. 되살리기가 목적이니 닫힌 것까지 모두 담는다.
    wins = {}
    for t, w in tab_win.items():
        if t not in navs:
            continue
        hist = navs[t]
        i = cur.get(t)
        if i not in hist:
            i = max(hist)
        wins.setdefault(w, []).append((tab_idx.get(t, 999), t, hist[i], len(hist)))
    for w in wins:
        wins[w].sort()
    return wins, active[0]


def main():
    wins, active = parse(os.path.join(HERE, sys.argv[1]))
    total = sum(len(v) for v in wins.values())
    lines = ['창 %d개 / 탭 %d개 (활성 창 %s)' % (len(wins), total, active)]
    html = ['<!DOCTYPE html><meta charset="utf-8"><title>되살린 크롬 탭 %d개</title>'
            '<style>body{font:14px "Malgun Gothic",sans-serif;margin:30px;max-width:980px}'
            'h3{margin:26px 0 8px}li{margin:5px 0;line-height:1.45}'
            'small{color:#888}a{color:#1558d6}</style>'
            '<h2>되살린 크롬 탭 — 창 %d개, 탭 %d개</h2>'
            '<p><small>클릭해서 필요한 것만 다시 열면 됩니다.</small></p>'
            % (total, len(wins), total)]
    for w, tabs in sorted(wins.items(), key=lambda kv: -len(kv[1])):
        mark = ' (마지막에 보던 창)' if w == active else ''
        lines.append('')
        lines.append('[창 %d] 탭 %d개%s' % (w, len(tabs), mark))
        html.append('<h3>창 %d — 탭 %d개%s</h3><ol>' % (w, len(tabs), mark))
        for _, t, (url, title), n in tabs:
            lines.append('  %-52s %s' % (url[:52], title[:44]))
            esc = url.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
            lab = (title or url).replace('&', '&amp;').replace('<', '&lt;')
            html.append('<li><a href="%s">%s</a><br><small>%s</small></li>' % (esc, lab, esc))
        html.append('</ol>')
    io.open(os.path.join(HERE, 'tabs.html'), 'w', encoding='utf-8').write('\n'.join(html))
    io.open(os.path.join(HERE, 'tabs.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
    print('tabs.html / tabs.txt 기록, 탭 %d개' % total)


if __name__ == "__main__":
    main()
