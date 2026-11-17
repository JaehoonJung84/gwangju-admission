# -*- coding: utf-8 -*-
"""한글 COM 으로 파일 형식만 바꾼다.  python hwp_conv.py <원본> <결과> <HWP|HWPX|PDF>

주의: 실패해도 반드시 Quit 한다. Quit 을 건너뛰면 창 없는 한글 프로세스가
남아 GDI·핸들을 계속 물고 있다(2026-11-03 에 92개까지 쌓여 화면 입력이 느려짐).
"""
import os
import subprocess
import sys
import win32com.client as W


def pids():
    """현재 떠 있는 hwp.exe PID 집합"""
    try:
        out = subprocess.run(['tasklist', '/fi', 'imagename eq hwp.exe', '/fo', 'csv', '/nh'],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return set()
    got = set()
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[1].isdigit():
            got.add(int(parts[1]))
    return got


def main():
    src, dst, fmt = sys.argv[1], sys.argv[2], sys.argv[3]
    was = pids()                       # 띄우기 전 목록 — 내가 만든 것만 지우려고
    hwp = W.DispatchEx('HWPFrame.HwpObject')   # 사용자가 쓰는 한글 창에 붙지 않도록 새 인스턴스
    mine = pids() - was
    code = 0
    try:
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except Exception:
            pass
        print('open', hwp.Open(src.replace('\\', '/'), '', 'forceopen:true'), flush=True)
        print('save', hwp.SaveAs(dst.replace('\\', '/'), fmt, ''), flush=True)
    except Exception as e:
        print('변환 실패:', e, flush=True)
        code = 1
    finally:
        for fn in (lambda: hwp.Clear(1), lambda: hwp.Quit()):
            try:
                fn()
            except Exception:
                pass
        del hwp
        # Quit 이 안 먹은 경우에 대비해 이번에 띄운 프로세스만 확인 후 정리
        left = mine & pids()
        for p in left:
            os.system('taskkill /f /pid %d >nul 2>&1' % p)
        if left:
            print('남은 한글 프로세스 %d개 정리' % len(left), flush=True)
    sys.exit(code)


main()
