# -*- coding: utf-8 -*-
"""한글 COM 으로 파일 형식만 바꾼다.  python hwp_conv.py <원본> <결과> <HWP|HWPX|PDF>"""
import sys
import win32com.client as W

src, dst, fmt = sys.argv[1], sys.argv[2], sys.argv[3]
hwp = W.DispatchEx('HWPFrame.HwpObject')   # 사용자가 쓰는 한글 창에 붙지 않도록 새 인스턴스
hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
try:
    hwp.XHwpWindows.Item(0).Visible = False
except Exception:
    pass
print('open', hwp.Open(src.replace('\\', '/'), '', 'forceopen:true'), flush=True)
print('save', hwp.SaveAs(dst.replace('\\', '/'), fmt, ''), flush=True)
hwp.Clear(1)
hwp.Quit()
