' 창 없이 auto-worklog.ps1 실행 (예약 작업용 — 검은 콘솔 깜빡임 방지)
Set sh = CreateObject("WScript.Shell")
sh.Run "powershell -NoProfile -ExecutionPolicy Bypass -File ""C:\projects\tools\auto-worklog.ps1""", 0, False
