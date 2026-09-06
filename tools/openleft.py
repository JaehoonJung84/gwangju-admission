# -*- coding: utf-8 -*-
"""파일을 열고, 그 창을 왼쪽 모니터로 옮긴다.

집에서 Chrome 원격 데스크톱으로 사무실 듀얼모니터 PC 를 볼 때
집 모니터가 하나라 왼쪽 화면만 보이는 상황을 위한 도구.

  python openleft.py "파일경로"            → 열고 왼쪽으로
  python openleft.py --move "창제목일부"    → 이미 떠 있는 창만 옮기기
  python openleft.py --list               → 창 목록과 현재 모니터
"""
import ctypes, os, sys, time
from ctypes import wintypes

u = ctypes.windll.user32
u.SetProcessDPIAware()

SW_RESTORE, SW_MAXIMIZE = 9, 3


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)]


class MONITORINFOEX(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_ulong), ('rcMonitor', RECT), ('rcWork', RECT),
                ('dwFlags', ctypes.c_ulong), ('szDevice', ctypes.c_wchar * 32)]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [('length', ctypes.c_uint), ('flags', ctypes.c_uint),
                ('showCmd', ctypes.c_uint), ('ptMinX', ctypes.c_long),
                ('ptMinY', ctypes.c_long), ('ptMaxX', ctypes.c_long),
                ('ptMaxY', ctypes.c_long), ('rcNormal', RECT)]


def monitors():
    out = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                              ctypes.POINTER(RECT), ctypes.c_double)

    def cb(h, hdc, lprc, data):
        mi = MONITORINFOEX(); mi.cbSize = ctypes.sizeof(MONITORINFOEX)
        u.GetMonitorInfoW(h, ctypes.byref(mi))
        out.append({'name': mi.szDevice,
                    'mon': (mi.rcMonitor.left, mi.rcMonitor.top,
                            mi.rcMonitor.right, mi.rcMonitor.bottom),
                    'work': (mi.rcWork.left, mi.rcWork.top,
                             mi.rcWork.right, mi.rcWork.bottom)})
        return 1
    u.EnumDisplayMonitors(0, None, PROC(cb), 0)
    out.sort(key=lambda m: m['mon'][0])
    return out


def windows():
    got = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(h, p):
        if not u.IsWindowVisible(h):
            return True
        r = RECT(); u.GetWindowRect(h, ctypes.byref(r))
        if r.right - r.left < 200 or r.bottom - r.top < 120:
            return True
        n = ctypes.create_unicode_buffer(400)
        u.GetWindowTextW(h, n, 400)
        if n.value.strip():
            got.append((h, n.value, (r.left, r.top, r.right, r.bottom)))
        return True
    u.EnumWindows(PROC(cb), None)
    return got


def on_left(rect, left):
    """창의 왼쪽 위 모서리가 왼쪽 모니터 안에 있는가"""
    L, T, R, B = left['mon']
    x, y = rect[0] + 20, rect[1] + 20
    return L <= x < R and T <= y < B


def move_left(h, left):
    """창을 왼쪽 모니터로 옮긴다. 최대화 상태면 풀었다가 다시 최대화한다."""
    wp = WINDOWPLACEMENT(); wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    u.GetWindowPlacement(h, ctypes.byref(wp))
    was_max = (wp.showCmd == SW_MAXIMIZE)
    if was_max:
        u.ShowWindow(h, SW_RESTORE)
        time.sleep(0.25)
    r = RECT(); u.GetWindowRect(h, ctypes.byref(r))
    w, ht = r.right - r.left, r.bottom - r.top
    wl, wt, wr, wb = left['work']
    w = min(w, wr - wl); ht = min(ht, wb - wt)
    x = wl + max(0, (wr - wl - w) // 2)
    y = wt + max(0, (wb - wt - ht) // 3)
    u.MoveWindow(h, x, y, w, ht, True)
    if was_max:
        time.sleep(0.2)
        u.ShowWindow(h, SW_MAXIMIZE)
    u.SetForegroundWindow(h)
    return was_max


def main():
    mons = monitors()
    left = mons[0]
    if '--list' in sys.argv:
        print('모니터 %d대 · 왼쪽 = %s %s' % (len(mons), left['name'], left['mon']))
        for h, t, r in windows():
            print('  %-46s %s  %s' % (t[:46], r[:2],
                                      '왼쪽' if on_left(r, left) else '★오른쪽'))
        return

    if '--move' in sys.argv:
        key = sys.argv[sys.argv.index('--move') + 1]
        n = 0
        for h, t, r in windows():
            if key in t and not on_left(r, left):
                move_left(h, left); n += 1
                print('옮김:', t[:50])
        print('옮긴 창 %d개' % n)
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print('파일 없음:', path); sys.exit(1)
    base = os.path.splitext(os.path.basename(path))[0]
    before = {h for h, t, r in windows()}
    os.startfile(path)
    print('열기 요청:', os.path.basename(path))

    target = None
    for i in range(60):                      # 최대 30초 기다린다
        time.sleep(0.5)
        for h, t, r in windows():
            if h in before:
                continue
            if base[:12] in t or (i > 10 and h not in before):
                target = (h, t, r); break
        if target:
            break
    if not target:
        print('새 창을 못 찾았습니다. 이미 열려 있었을 수 있습니다.')
        print('  → python openleft.py --move "제목일부" 로 옮기세요.')
        return
    h, t, r = target
    time.sleep(1.0)                          # 창이 자리를 잡을 시간
    r2 = RECT(); u.GetWindowRect(h, ctypes.byref(r2))
    rect = (r2.left, r2.top, r2.right, r2.bottom)
    if on_left(rect, left):
        print('이미 왼쪽 모니터에 떴습니다: %s %s' % (t[:44], rect[:2]))
    else:
        was = move_left(h, left)
        print('오른쪽에 떠서 왼쪽으로 옮겼습니다%s: %s' % (' (최대화 유지)' if was else '', t[:44]))


main()
