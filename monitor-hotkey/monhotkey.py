# -*- coding: utf-8 -*-
"""단축키로 창을 모니터 사이에서 옮긴다.

집(모니터 1대)에서 사무실 PC(2대)를 원격으로 볼 때, 오른쪽 모니터에 뜬 창을
눈에 보이는 왼쪽으로 끌어오기 위한 도구. 배경에서 조용히 돌면서 단축키만 받는다.

  Ctrl+Alt+←      현재 창을 왼쪽(주) 모니터로
  Ctrl+Alt+→      현재 창을 오른쪽 모니터로
  Ctrl+Alt+Space  현재 창을 반대쪽으로 (토글)
  Ctrl+Alt+A      숨어 있는 창을 전부 왼쪽으로 모으기
  Ctrl+Alt+Z      방금 모은 창들을 원래 자리로 되돌리기
  Ctrl+Alt+H      단축키 목록 보기

Win 키 조합(Win+Shift+←)은 원격 프로그램이 가로채는 경우가 많아 Ctrl+Alt 로 잡았다.
"""
import ctypes, json, os, sys, time
from ctypes import wintypes

u = ctypes.windll.user32
dwm = ctypes.windll.dwmapi
u.SetProcessDPIAware()

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'monhotkey.log')
UNDO = os.path.join(HERE, 'undo.json')

SW_RESTORE, SW_MAXIMIZE = 9, 3
WM_HOTKEY = 0x0312
MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x0001, 0x0002, 0x4000
DWMWA_CLOAKED = 14

HOTKEYS = [
    (1, 0x25, 'left',   'Ctrl+Alt+<-'),
    (2, 0x27, 'right',  'Ctrl+Alt+->'),
    (3, 0x20, 'toggle', 'Ctrl+Alt+Space'),
    (4, 0x41, 'gather', 'Ctrl+Alt+A'),
    (5, 0x5A, 'undo',   'Ctrl+Alt+Z'),
    (6, 0x48, 'help',   'Ctrl+Alt+H'),
]

HELP = """창 옮기기 단축키

  Ctrl+Alt+←        현재 창을 왼쪽(주) 모니터로
  Ctrl+Alt+→        현재 창을 오른쪽 모니터로
  Ctrl+Alt+Space    현재 창을 반대쪽 모니터로
  Ctrl+Alt+A        오른쪽에 숨은 창을 전부 왼쪽으로
  Ctrl+Alt+Z        Ctrl+Alt+A 로 옮긴 창을 되돌리기
  Ctrl+Alt+H        이 도움말

끄기: 작업 관리자에서 pythonw.exe 종료"""


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


def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass
    try:
        if sys.stdout and sys.stdout.isatty():
            print(line)
    except Exception:
        pass


def monitors():
    """왼쪽부터 차례로 모니터 목록을 돌려준다."""
    out = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                              ctypes.POINTER(RECT), ctypes.c_double)

    def cb(h, hdc, lprc, data):
        mi = MONITORINFOEX()
        mi.cbSize = ctypes.sizeof(MONITORINFOEX)
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


def rect_of(h):
    r = RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def cloaked(h):
    """화면에 없는 유령 창(다른 가상 데스크톱, 숨은 스토어 앱)인가"""
    v = ctypes.c_int(0)
    dwm.DwmGetWindowAttribute(wintypes.HWND(h), DWMWA_CLOAKED,
                              ctypes.byref(v), ctypes.sizeof(v))
    return v.value != 0


def windows():
    got = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(h, p):
        if not u.IsWindowVisible(h) or u.IsIconic(h) or cloaked(h):
            return True
        r = rect_of(h)
        if r[2] - r[0] < 200 or r[3] - r[1] < 120:
            return True
        n = ctypes.create_unicode_buffer(400)
        u.GetWindowTextW(h, n, 400)
        if n.value.strip():
            got.append((h, n.value, r))
        return True
    u.EnumWindows(PROC(cb), None)
    return got


def which_monitor(rect, mons):
    """창의 왼쪽 위 모서리가 어느 모니터에 있는지 (못 찾으면 0번)"""
    x, y = rect[0] + 20, rect[1] + 20
    for i, m in enumerate(mons):
        L, T, R, B = m['mon']
        if L <= x < R and T <= y < B:
            return i
    return 0


def place(h, target):
    """창을 target 모니터의 작업영역 안으로 옮긴다. 최대화 상태는 유지한다."""
    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    u.GetWindowPlacement(h, ctypes.byref(wp))
    was_max = (wp.showCmd == SW_MAXIMIZE)
    if was_max:
        u.ShowWindow(h, SW_RESTORE)
        time.sleep(0.2)
    r = rect_of(h)
    w, ht = r[2] - r[0], r[3] - r[1]
    wl, wt, wr, wb = target['work']
    w = min(w, wr - wl)
    ht = min(ht, wb - wt)
    x = wl + max(0, (wr - wl - w) // 2)
    y = wt + max(0, (wb - wt - ht) // 3)
    u.MoveWindow(h, x, y, w, ht, True)
    if was_max:
        time.sleep(0.15)
        u.ShowWindow(h, SW_MAXIMIZE)
    return was_max


def front():
    h = u.GetForegroundWindow()
    if not h:
        return None
    n = ctypes.create_unicode_buffer(400)
    u.GetWindowTextW(h, n, 400)
    cls = ctypes.create_unicode_buffer(200)
    u.GetClassNameW(h, cls, 200)
    if cls.value in ('Progman', 'WorkerW', 'Shell_TrayWnd'):     # 바탕화면·작업표시줄
        return None
    return h, n.value


def move_front(where):
    mons = monitors()
    if len(mons) < 2:
        log('모니터가 1대뿐이라 옮길 곳이 없습니다.')
        return
    f = front()
    if not f:
        log('옮길 창을 찾지 못했습니다.')
        return
    h, title = f
    cur = which_monitor(rect_of(h), mons)
    if where == 'left':
        tgt = 0
    elif where == 'right':
        tgt = len(mons) - 1
    else:
        tgt = (cur + 1) % len(mons)
    if tgt == cur:
        log('이미 모니터%d 입니다: %s' % (cur + 1, title[:40]))
        return
    place(h, mons[tgt])
    u.SetForegroundWindow(h)
    log('%s → 모니터%d: %s' % (where, tgt + 1, title[:40]))


def gather():
    """왼쪽 모니터 밖에 있는 창을 전부 왼쪽으로 모은다. 되돌릴 수 있게 자리를 적어 둔다."""
    mons = monitors()
    if len(mons) < 2:
        log('모니터가 1대뿐입니다.')
        return
    saved, n = [], 0
    for h, title, r in windows():
        if which_monitor(r, mons) == 0:
            continue
        wp = WINDOWPLACEMENT()
        wp.length = ctypes.sizeof(WINDOWPLACEMENT)
        u.GetWindowPlacement(h, ctypes.byref(wp))
        saved.append({'h': int(h), 'rect': r, 'max': wp.showCmd == SW_MAXIMIZE,
                      'title': title})
        place(h, mons[0])
        n += 1
    try:
        with open(UNDO, 'w', encoding='utf-8') as f:
            json.dump(saved, f, ensure_ascii=False)
    except Exception as e:
        log('되돌리기 정보 저장 실패: %s' % e)
    log('왼쪽으로 모은 창 %d개' % n)


def undo():
    if not os.path.exists(UNDO):
        log('되돌릴 기록이 없습니다.')
        return
    try:
        with open(UNDO, encoding='utf-8') as f:
            saved = json.load(f)
    except Exception as e:
        log('되돌리기 기록을 읽지 못했습니다: %s' % e)
        return
    n = 0
    for s in saved:
        h = s['h']
        if not u.IsWindow(h):
            continue
        L, T, R, B = s['rect']
        if s['max']:
            u.ShowWindow(h, SW_RESTORE)
            time.sleep(0.15)
        u.MoveWindow(h, L, T, R - L, B - T, True)
        if s['max']:
            time.sleep(0.15)
            u.ShowWindow(h, SW_MAXIMIZE)
        n += 1
    log('되돌린 창 %d개' % n)
    try:
        os.remove(UNDO)
    except Exception:
        pass


def show_help():
    u.MessageBoxW(0, HELP, '모니터 전환 단축키', 0x40)


ACTIONS = {
    'left':   lambda: move_front('left'),
    'right':  lambda: move_front('right'),
    'toggle': lambda: move_front('toggle'),
    'gather': gather,
    'undo':   undo,
    'help':   show_help,
}


def daemon():
    ok, fail = [], []
    for hid, vk, action, label in HOTKEYS:
        if u.RegisterHotKey(None, hid, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, vk):
            ok.append(label)
        else:
            fail.append(label)
    if not ok:
        log('단축키를 하나도 등록하지 못했습니다. 이미 켜져 있는지 확인하세요.')
        return
    msg = '시작 — 등록: ' + ', '.join(ok)
    if fail:
        msg += ' / 실패(다른 프로그램이 쓰는 중): ' + ', '.join(fail)
    log(msg)
    m = wintypes.MSG()
    try:
        while u.GetMessageW(ctypes.byref(m), None, 0, 0) != 0:
            if m.message == WM_HOTKEY:
                for hid, vk, action, label in HOTKEYS:
                    if m.wParam == hid:
                        try:
                            ACTIONS[action]()
                        except Exception as e:
                            log('%s 처리 중 오류: %s' % (label, e))
                        break
    finally:
        for hid, _, _, _ in HOTKEYS:
            u.UnregisterHotKey(None, hid)
        log('종료')


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == '--list':
        mons = monitors()
        for i, m in enumerate(mons):
            print('모니터%d %s %s' % (i + 1, m['name'], m['mon']))
        for h, t, r in windows():
            print('  %-44s %-12s 모니터%d' % (t[:44], str(r[:2]),
                                              which_monitor(r, mons) + 1))
    elif arg in ('--left', '--right', '--toggle'):
        move_front(arg[2:])
    elif arg == '--gather':
        gather()
    elif arg == '--undo':
        undo()
    else:
        daemon()


main()
