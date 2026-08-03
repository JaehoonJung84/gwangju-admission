# =============================================================
#  자동 저장 설치 스크립트 (1회 실행)
#  1) Claude Code에 git push 권한 허용 추가
#  2) 1시간마다 auto-worklog.ps1 실행하는 예약 작업 등록
#  실행: 프롬프트에  ! powershell -ExecutionPolicy Bypass -File C:\projects\tools\setup-autosave.ps1
# =============================================================
$ErrorActionPreference = 'Stop'

# ---------- 1) git push 권한 추가 ----------
$SettingsPath = 'C:\projects\.claude\settings.local.json'
$json = Get-Content -Raw -Encoding UTF8 $SettingsPath | ConvertFrom-Json
$allow = @($json.permissions.allow)
$toAdd = @('Bash(git push*)', 'PowerShell(git push*)')
$added = @()
foreach($rule in $toAdd){
  if($allow -notcontains $rule){ $allow += $rule; $added += $rule }
}
if($added.Count -gt 0){
  $json.permissions.allow = $allow
  $out = $json | ConvertTo-Json -Depth 10
  [IO.File]::WriteAllText($SettingsPath, $out, [Text.UTF8Encoding]::new($false))
  Write-Host ("권한 추가됨: " + ($added -join ', ')) -ForegroundColor Green
} else {
  Write-Host "권한은 이미 설정돼 있음" -ForegroundColor Yellow
}

# ---------- 2) 예약 작업 등록 (매시간) ----------
$TaskName = 'GU-AutoWorklog'
$Cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\projects\tools\auto-worklog.ps1'
cmd /c "schtasks /delete /tn $TaskName /f >nul 2>&1"
cmd /c "schtasks /create /tn $TaskName /tr `"$Cmd`" /sc hourly /mo 1 /st 09:10 /f"
if($LASTEXITCODE -ne 0){ Write-Host "예약 작업 등록 실패" -ForegroundColor Red; exit 1 }
Write-Host "예약 작업 '$TaskName' 등록 완료 (매시간 실행)" -ForegroundColor Green

# ---------- 3) 즉시 1회 실행해서 검증 ----------
Write-Host "즉시 1회 실행..." -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File C:\projects\tools\auto-worklog.ps1
Write-Host "완료. 로그: C:\projects\tools\autosave.log" -ForegroundColor Green
Get-Content C:\projects\tools\autosave.log -Tail 5
