# -*- coding: utf-8 -*-
"""chrome-x-guard — 크롬 창의 X(닫기)를 누르면 "닫겠습니까?" 를 먼저 묻는다.

왜 필요한가
  크롬은 윈도에서 X 를 누르면 묻지 않고 바로 닫는다. 탭이 열두 개든 서른 개든
  한 번의 오클릭으로 사라지고, Ctrl+Shift+T 로 되살아나지 않는 경우도 있다.

어떻게 하는가
  낮은 수준 마우스 훅(WH_MOUSE_LL)으로 왼쪽 버튼 누름을 먼저 받아서,
  그 자리가 크롬 창의 닫기 버튼인지 확인한다. 버튼 위치를 좌표로 어림하지 않고
  창에 WM_NCHITTEST 를 보내 HTCLOSE 라고 답하는지 묻는다(배율·버전·최대화 무관).
  닫기 버튼이면 그 클릭을 삼키고 확인창을 띄운 뒤, "예" 일 때만 창에
  SC_CLOSE 를 보낸다.

안전 장치
  · 크롬인지 확인은 창 class + 실행파일 이름 둘 다 본다. 같은 class 를 쓰는
    Electron 앱(VS Code, 슬랙 등)은 건드리지 않는다.
  · 창이 응답하지 않으면(ABORTIFHUNG/80ms) 삼키지 않고 그대로 통과시킨다.
    가드가 막혀서 클릭이 먹통이 되는 일이 없도록 '막으면 통과' 로 설계했다.
  · 확인창은 임자 창 없이 띄운다. 크롬을 소유자로 지정하면 가드가 죽을 때
    크롬이 입력 불가로 남는다.
  · 기본 단추는 "아니오". 얼떨결에 Enter 를 쳐도 닫히지 않는다.
  · config.json 의 Enabled 를 false 로 두면 다음 실행부터 아무것도 하지 않는다.
"""
import ctypes
import io
import json
import os
import sys
import threading
import time
from ctypes import wintypes

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'chrome-x-guard.log')

CFG = {'Enabled': True,
       'Targets': ['chrome.exe'],
       'WarnLastWindow': True,
       'HitTestTimeoutMs': 80}
try:
    CFG.update(json.load(io.open(os.path.join(HERE, 'config.json'), encoding='utf-8-sig')))
except Exception:
    pass
for i, a in enumerate(sys.argv):
    if a == '--targets':                      # 시험용: 다른 프로그램으로 바꿔 끼운다
        CFG['Targets'] = sys.argv[i + 1].split(',')

TARGETS = {t.lower() for t in CFG['Targets']}

u32 = ctypes.WinDLL('user32', use_last_error=True)
k32 = ctypes.WinDLL('kernel32', use_last_error=True)

LRESULT = ctypes.c_ssize_t
ULONG_PTR = ctypes.c_size_t
WH_MOUSE_LL = 14
WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0201, 0x0202
WM_NCHITTEST, WM_SYSCOMMAND = 0x0084, 0x0112
SC_CLOSE, HTCLOSE = 0xF060, 20
GA_ROOT = 2
SMTO_ABORTIFHUNG, SMTO_BLOCK = 0x0002, 0x0001
MB_YESNO, MB_ICONQUESTION, MB_DEFBUTTON2 = 0x04, 0x20, 0x100
MB_SETFOREGROUND, MB_TOPMOST = 0x10000, 0x40000
IDYES = 6
WM_REHOOK = 0x8000 + 1                       # WM_APP+1: 훅을 다시 걸라는 내부 신호


class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [('pt', POINT), ('mouseData', wintypes.DWORD), ('flags', wintypes.DWORD),
                ('time', wintypes.DWORD), ('dwExtraInfo', ULONG_PTR)]


HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
ENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

u32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
u32.SetWindowsHookExW.restype = wintypes.HHOOK
u32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
u32.CallNextHookEx.restype = LRESULT
u32.WindowFromPoint.argtypes = [POINT]
u32.WindowFromPoint.restype = wintypes.HWND
u32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
u32.GetAncestor.restype = wintypes.HWND
u32.SendMessageTimeoutW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM,
                                    wintypes.LPARAM, wintypes.UINT, wintypes.UINT,
                                    ctypes.POINTER(ULONG_PTR)]
u32.SendMessageTimeoutW.restype = LRESULT
u32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
u32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
u32.MessageBoxW.restype = ctypes.c_int
u32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
# 인자형을 지정하지 않으면 64비트에서 핸들이 잘려 프로세스 이름을 영영 못 읽는다
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.OpenProcess.restype = wintypes.HANDLE
k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                           wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
k32.CloseHandle.argtypes = [wintypes.HANDLE]

_name_cache = {}


def log(msg):
    try:
        io.open(LOG, 'a', encoding='utf-8').write(
            '%s  %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
    except Exception:
        pass


def exe_of(pid):
    """pid 의 실행파일 이름. 한 번 본 pid 는 외워 둔다(훅 안에서 빨라야 한다)."""
    if pid in _name_cache:
        return _name_cache[pid]
    name = ''
    h = k32.OpenProcess(0x1000, False, pid)        # QUERY_LIMITED_INFORMATION
    if h:
        buf = ctypes.create_unicode_buffer(520)
        n = wintypes.DWORD(520)
        if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            name = os.path.basename(buf.value).lower()
        k32.CloseHandle(h)
    if len(_name_cache) > 400:
        _name_cache.clear()
    _name_cache[pid] = name
    return name


def win_text(h):
    buf = ctypes.create_unicode_buffer(512)
    u32.GetWindowTextW(h, buf, 512)
    return buf.value


def target_close_button(x, y):
    """(x, y) 가 감시 대상 프로그램 창의 닫기 버튼이면 그 창 손잡이를 돌려준다."""
    h = u32.WindowFromPoint(POINT(x, y))
    if not h:
        return None
    root = u32.GetAncestor(h, GA_ROOT) or h
    cls = ctypes.create_unicode_buffer(128)
    u32.GetClassNameW(root, cls, 128)
    pid = wintypes.DWORD()
    u32.GetWindowThreadProcessId(root, ctypes.byref(pid))
    if exe_of(pid.value) not in TARGETS:
        return None
    res = ULONG_PTR()
    ok = u32.SendMessageTimeoutW(root, WM_NCHITTEST, 0,
                                 ((y & 0xffff) << 16) | (x & 0xffff),
                                 SMTO_ABORTIFHUNG | SMTO_BLOCK,
                                 int(CFG['HitTestTimeoutMs']), ctypes.byref(res))
    if not ok:                                  # 창이 바쁘면 막지 않고 통과시킨다
        return None
    return root if ctypes.c_long(res.value & 0xffffffff).value == HTCLOSE else None


def count_windows(exe):
    """감시 대상의 눈에 보이는 제목 있는 창 수(마지막 창인지 알려 주려고 센다)."""
    n = [0]

    def cb(h, _):
        if u32.IsWindowVisible(h) and win_text(h):
            pid = wintypes.DWORD()
            u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
            if exe_of(pid.value) == exe:
                n[0] += 1
        return True

    u32.EnumWindows(ENUMPROC(cb), 0)
    return n[0]


class Asker(object):
    """확인창은 훅과 다른 실 에서 띄운다(훅은 곧바로 돌아와야 한다)."""

    def __init__(self):
        self.pending = False
        self.job = None
        self.wake = threading.Event()
        t = threading.Thread(target=self.loop, daemon=True)
        t.start()

    def ask(self, hwnd):
        if self.pending:
            return
        self.pending = True
        self.job = hwnd
        self.wake.set()

    def loop(self):
        while True:
            self.wake.wait()
            self.wake.clear()
            h = self.job
            try:
                title = win_text(h)
                pid = wintypes.DWORD()
                u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
                left = count_windows(exe_of(pid.value)) - 1
                body = '%s\n\n이 창을 닫겠습니까?' % (title or '(제목 없음)')
                if CFG.get('WarnLastWindow') and left <= 0:
                    body += '\n\n마지막 창입니다. 닫으면 열려 있는 탭이 모두 함께 닫힙니다.'
                else:
                    body += '\n\n이 창의 탭이 모두 함께 닫힙니다. (남는 창 %d개)' % left
                r = u32.MessageBoxW(None, body, '닫기 확인',
                                    MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2
                                    | MB_SETFOREGROUND | MB_TOPMOST)
                if r == IDYES:
                    u32.PostMessageW(h, WM_SYSCOMMAND, SC_CLOSE, 0)
                    log('닫음  %s' % title[:80])
                else:
                    log('취소  %s' % title[:80])
            except Exception as e:
                log('확인창 오류 %r' % (e,))
            finally:
                self.pending = False


def prewarm():
    """대상 프로그램의 pid·실행파일 이름을 미리 외워 둔다.

    첫 클릭에서 처음 알아보느라 훅이 느려지면, 윈도가 그 훅을 조용히 떼어 버린다.
    """
    def cb(h, _):
        pid = wintypes.DWORD()
        u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
        exe_of(pid.value)
        return True

    u32.EnumWindows(ENUMPROC(cb), 0)


def watchdog(tid, hits):
    """훅이 살아 있는지 지켜본다.

    마우스를 움직였는데도 훅에 아무 소식이 없으면 풀린 것으로 보고 다시 걸게 한다.
    """
    last_hits, last_pt = hits[0], (0, 0)
    while True:
        time.sleep(4.0)
        p = POINT()
        u32.GetCursorPos(ctypes.byref(p))
        now = (p.x, p.y)
        if now != last_pt and hits[0] == last_hits:
            log('훅이 풀린 듯하다 — 다시 건다')
            u32.PostThreadMessageW(tid, WM_REHOOK, 0, 0)
        last_hits, last_pt = hits[0], now


def main():
    # 두 번 실행되면 클릭이 두 번 삼켜진다. 하나만 살아남게 한다.
    k32.CreateMutexW(None, True, 'Global\\ChromeXGuardSingleton')
    if k32.GetLastError() == 183:                               # ALREADY_EXISTS
        return
    if not CFG.get('Enabled', True):
        log('Enabled=false, 아무것도 하지 않는다')
        return

    # 훅 콜백이 늦으면 윈도가 훅을 떼어 낸다. 우선순위를 한 단 올리고 미리 데워 둔다.
    k32.SetPriorityClass(k32.GetCurrentProcess(), 0x00008000)    # ABOVE_NORMAL
    prewarm()

    asker = Asker()
    swallowing = [False]
    hits = [0]

    verbose = '--verbose' in sys.argv

    def proc(code, wparam, lparam):
        if code == 0:
            hits[0] += 1                        # 살아 있음을 알리는 맥박
            ms = ctypes.cast(lparam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            if wparam == WM_LBUTTONDOWN:
                t0 = time.time()
                try:
                    h = target_close_button(ms.pt.x, ms.pt.y)
                except Exception as e:
                    h = None
                    if verbose:
                        log('판별 오류 %r' % (e,))
                if verbose:
                    log('누름 (%d,%d) 대상닫기=%s 걸린시간 %.0fms 대기중=%s'
                        % (ms.pt.x, ms.pt.y, bool(h), (time.time() - t0) * 1000,
                           asker.pending))
                if h:
                    swallowing[0] = True
                    asker.ask(h)
                    return 1                                    # 클릭을 삼킨다
            elif wparam == WM_LBUTTONUP and swallowing[0]:
                swallowing[0] = False                           # 짝이 되는 떼기도 삼킨다
                return 1
        return u32.CallNextHookEx(None, code, wparam, lparam)

    cb = HOOKPROC(proc)                                         # 참조를 반드시 붙들어 둔다
    hook = [u32.SetWindowsHookExW(WH_MOUSE_LL, cb, None, 0)]
    if not hook[0]:
        log('훅 설치 실패 err=%d' % ctypes.get_last_error())
        return
    log('감시 시작  대상=%s' % ','.join(sorted(TARGETS)))
    threading.Thread(target=watchdog, args=(k32.GetCurrentThreadId(), hits),
                     daemon=True).start()

    msg = wintypes.MSG()
    while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == WM_REHOOK:
            u32.UnhookWindowsHookEx(hook[0])
            hook[0] = u32.SetWindowsHookExW(WH_MOUSE_LL, cb, None, 0)
            log('훅 다시 걸었다 (%s)' % ('성공' if hook[0] else '실패'))
            continue
        u32.TranslateMessage(ctypes.byref(msg))
        u32.DispatchMessageW(ctypes.byref(msg))
    u32.UnhookWindowsHookEx(hook[0])


if __name__ == '__main__':
    main()
