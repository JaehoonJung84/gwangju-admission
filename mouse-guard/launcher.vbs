' mouse-guard를 창 없이 백그라운드로 실행
CreateObject("Wscript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\projects\mouse-guard\mouse-guard.ps1""", 0, False
