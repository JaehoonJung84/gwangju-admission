' scroll-lock-guard 를 창 없이 백그라운드로 실행
CreateObject("Wscript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\projects\scroll-lock-guard\scroll-lock-guard.ps1""", 0, False
