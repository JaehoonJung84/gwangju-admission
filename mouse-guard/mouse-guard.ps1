# =============================================================
#  mouse-guard.ps1 — 마우스 포인터 속도 감시 + 자동 복원
#  · 20초마다 실제(런타임) 속도·가속 설정을 확인
#  · 기준값(config.json)과 다르면:
#      1) 로그에 변경 내용 + 그 시점 프로세스 목록·원격접속 여부 기록 (범인 추적)
#      2) 즉시 기준값으로 복원
#  · 속도를 일부러 바꾸고 싶으면 config.json의 Sensitivity를 고치면 됨
# =============================================================
$ErrorActionPreference = 'SilentlyContinue'

# 중복 실행 방지 (로그온 시 자동시작 + 수동시작이 겹쳐도 1개만 유지)
$mutex = New-Object System.Threading.Mutex($false, 'Global\MouseGuardSingleton')
if (-not $mutex.WaitOne(0)) { exit }

$Base   = $PSScriptRoot
$Cfg    = Get-Content (Join-Path $Base 'config.json') -Raw | ConvertFrom-Json
$Log    = Join-Path $Base 'mouse-guard.log'
$SnapDir = Join-Path $Base 'snapshots'
if (-not (Test-Path $SnapDir)) { New-Item -ItemType Directory -Path $SnapDir -Force | Out-Null }

Add-Type @'
using System;
using System.Runtime.InteropServices;
public class SPI {
  [DllImport("user32.dll", SetLastError=true)]
  public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, ref int pvParam, uint fWinIni);
  [DllImport("user32.dll", SetLastError=true)]
  public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, int[] pvParam, uint fWinIni);
  [DllImport("user32.dll", SetLastError=true)]
  public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);
}
'@

function Get-RuntimeSpeed { $s = 0; [SPI]::SystemParametersInfo(0x70, 0, [ref]$s, 0) | Out-Null; return $s }
function Get-RuntimeAccel { $a = New-Object int[] 3; [SPI]::SystemParametersInfo(0x03, 0, $a, 0) | Out-Null; return $a }  # [T1, T2, Speed]
function Set-Speed($v)    { [SPI]::SystemParametersInfo(0x71, 0, [IntPtr]$v, 3) | Out-Null }   # SPIF_UPDATEINIFILE|SENDCHANGE
function Set-Accel($t1, $t2, $sp) { [SPI]::SystemParametersInfo(0x04, 0, ([int[]]@($t1, $t2, $sp)), 3) | Out-Null }

function Write-Log($msg) {
  $line = "{0} | {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
  Add-Content -Path $Log -Value $line -Encoding UTF8
}

function Test-RemoteActive {
  # Chrome 원격 데스크톱(remoting_host)에 현재 연결이 붙어 있는지
  $pids = (Get-Process remoting_host -ErrorAction SilentlyContinue).Id
  if (-not $pids) { return 'CRD꺼짐' }
  $conn = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
          Where-Object { $pids -contains $_.OwningProcess -and $_.RemoteAddress -notmatch '^(127\.|::1)' }
  if ($conn) { return 'CRD원격접속중' } else { return 'CRD대기중' }
}

function Save-Snapshot($stamp) {
  $f = Join-Path $SnapDir ("{0}_processes.txt" -f $stamp)
  Get-Process | Sort-Object Name -Unique |
    ForEach-Object { "{0,-30} {1,-8} {2}" -f $_.Name, $_.Id, $_.Path } |
    Out-File $f -Encoding UTF8
  return $f
}

Write-Log ("가드 시작 (기준: 속도={0}, 가속={1}/{2}/{3})" -f $Cfg.Sensitivity, $Cfg.MouseSpeed, $Cfg.MouseThreshold1, $Cfg.MouseThreshold2)

while ($true) {
  $rt  = Get-RuntimeSpeed
  $acc = Get-RuntimeAccel
  $reg = [int](Get-ItemProperty 'HKCU:\Control Panel\Mouse').MouseSensitivity

  $speedBad = ($rt -ne $Cfg.Sensitivity) -or ($reg -ne $Cfg.Sensitivity)
  $accelBad = ($acc[0] -ne $Cfg.MouseThreshold1) -or ($acc[1] -ne $Cfg.MouseThreshold2) -or ($acc[2] -ne $Cfg.MouseSpeed)

  if ($speedBad -or $accelBad) {
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $snap  = Save-Snapshot $stamp
    $remote = Test-RemoteActive
    if ($speedBad) {
      Write-Log ("변경 감지! 속도 런타임={0} 레지스트리={1} (기준 {2}) | {3} | 스냅샷: {4}" -f $rt, $reg, $Cfg.Sensitivity, $remote, (Split-Path $snap -Leaf))
      Set-Speed $Cfg.Sensitivity
    }
    if ($accelBad) {
      Write-Log ("가속설정 변경 감지! T1/T2/Speed = {0}/{1}/{2} (기준 {3}/{4}/{5}) | {6}" -f $acc[0], $acc[1], $acc[2], $Cfg.MouseThreshold1, $Cfg.MouseThreshold2, $Cfg.MouseSpeed, $remote)
      Set-Accel $Cfg.MouseThreshold1 $Cfg.MouseThreshold2 $Cfg.MouseSpeed
    }
    Write-Log ("기준값으로 복원 완료 (현재 속도={0})" -f (Get-RuntimeSpeed))
  }
  Start-Sleep -Seconds 20
}
