# -*- coding: utf-8 -*-
"""변환이 멈출 때 한글이 숨은 대화상자를 띄우고 있는지 본다.

hwp_conv.py 를 띄운 뒤, 새로 생긴 hwp.exe 의 창을 훑어 대화상자(#32770)와
그 안의 글월을 찍는다. 90초 동안 보다가 끝낸다.
"""
import ctypes
import io
import os
import subprocess
import sys
import time
from ctypes import wintypes

u = ctypes.windll.user32
SRC = os.path.join(r'C:\Users\user\Desktop\★국제협력처\8. 모집요강\2027학년도 모집요강\대학원',
                   '2027학년도 전기 외국인 대학원 신·편입 특별전형 모집요강(20261030)_초안_10차.hwpx')
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe_out.pdf')
CONV = r'C:\projects\tools\hwp\hwp_conv.py'
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe.log')


def pids():
    out = subprocess.run(['tasklist', '/fi', 'imagename eq hwp.exe', '/fo', 'csv', '/nh'],
                         capture_output=True, text=True).stdout
    got = set()
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[1].isdigit():
            got.add(int(parts[1]))
    return got


def windows_of(target):
    found = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(h, _):
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value in target:
            cls = ctypes.create_unicode_buffer(128)
            u.GetClassNameW(h, cls, 128)
            txt = ctypes.create_unicode_buffer(512)
            u.GetWindowTextW(h, txt, 512)
            found.append((h, pid.value, cls.value, txt.value, bool(u.IsWindowVisible(h))))
        return True
    u.EnumWindows(PROC(cb), None)
    return found


def children_text(h):
    out = []
    PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(c, _):
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(c, cls, 128)
        txt = ctypes.create_unicode_buffer(512)
        u.GetWindowTextW(c, txt, 512)
        if txt.value.strip():
            out.append('[%s] %s' % (cls.value, txt.value.strip()))
        return True
    u.EnumChildWindows(h, PROC(cb), None)
    return out


log = io.open(LOG, 'w', encoding='utf-8')
was = pids()
p = subprocess.Popen([sys.executable, '-u', CONV, SRC, DST, 'PDF'],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
log.write('시작, 기존 hwp %d개\n' % len(was))
seen = set()
t0 = time.time()
while time.time() - t0 < 90:
    if p.poll() is not None:
        log.write('변환 프로세스 종료 code=%s\n' % p.returncode)
        break
    mine = pids() - was
    for h, pid, cls, txt, vis in windows_of(mine):
        key = (cls, txt)
        if cls in ('#32770', 'NUIDialog', 'HncDialog') or (txt and key not in seen):
            if key in seen:
                continue
            seen.add(key)
            log.write('\n[%5.1f초] pid=%d cls=%s vis=%s title=%r\n'
                      % (time.time() - t0, pid, cls, vis, txt))
            for line in children_text(h)[:20]:
                log.write('      %s\n' % line)
    time.sleep(2)
log.write('\n관찰 끝 (%.0f초)\n' % (time.time() - t0))
try:
    p.kill()
except Exception:
    pass
for q in pids() - was:
    os.system('taskkill /f /pid %d >nul 2>&1' % q)
log.close()
print(io.open(LOG, encoding='utf-8').read())
