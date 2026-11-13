# -*- coding: utf-8 -*-
import sys, win32com.client as W
src, dst, fmt = sys.argv[1], sys.argv[2], sys.argv[3]
h = W.Dispatch('HWPFrame.HwpObject')
h.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
try:
    h.XHwpWindows.Item(0).Visible = False
except Exception:
    pass
try:
    if not h.Open(src, '', 'forceopen:true'):
        raise SystemExit('open fail')
    if not h.SaveAs(dst, fmt, ''):
        raise SystemExit('save fail')
    print('ok', dst)
finally:
    h.Quit()
