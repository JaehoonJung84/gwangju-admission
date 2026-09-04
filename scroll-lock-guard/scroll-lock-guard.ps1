# =============================================================
#  scroll-lock-guard.ps1 — Scroll Lock 켜짐 감시 + 자동 해제
#  · Scroll Lock 이 켜지면 엑셀에서 방향키가 셀 이동 대신 화면 스크롤이 된다.
#  · 몇 초마다 상태를 확인해 켜져 있으면
#      1) 언제·무슨 창에서·원격접속 중이었는지 로그에 남기고 (원인 추적)
#      2) 곧바로 꺼 준다.
#  · 일부러 Scroll Lock 을 쓰고 싶으면 config.json 의 Enabled 를 false 로.
# =============================================================
$ErrorActionPreference = 'SilentlyContinue'

# 중복 실행 방지 (자동시작 + 수동시작이 겹쳐도 하나만 산다)
$mutex = New-Object System.Threading.Mutex($false, 'Global\ScrollLockGuardSingleton')
if (-not $mutex.WaitOne(0)) { exit }

$Base = $PSScriptRoot
$Log  = Join-Path $Base 'scroll-lock-guard.log'
$CfgP = Join-Path $Base 'config.json'
$Cfg  = Get-Content $CfgP -Raw | ConvertFrom-Json

Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public class KB {
  [DllImport("user32.dll")] public static extern short GetKeyState(int vKey);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, IntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  // CharSet 을 지정하지 않으면 한글 창 제목이 ?? 로 깨진다
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder s, int n);

  public const int VK_SCROLL = 0x91;
  public static bool IsOn(int vk) { return (GetKeyState(vk) & 1) != 0; }
  public static void Tap(byte vk) {
    keybd_event(vk, 0x45, 0x0001, IntPtr.Zero);              // EXTENDEDKEY
    System.Threading.Thread.Sleep(50);
    keybd_event(vk, 0x45, 0x0001 | 0x0002, IntPtr.Zero);     // KEYUP
    System.Threading.Thread.Sleep(150);
  }
  public static string Foreground() {
    IntPtr h = GetForegroundWindow();
    if (h == IntPtr.Zero) return "(없음)";
    uint pid = 0; GetWindowThreadProcessId(h, out pid);
    StringBuilder sb = new StringBuilder(300); GetWindowText(h, sb, 300);
    string name = "?";
    try { name = System.Diagnostics.Process.GetProcessById((int)pid).ProcessName; } catch {}
    return name + " / " + sb.ToString();
  }
}
'@

function Write-Log($msg) {
  Add-Content -Path $Log -Encoding UTF8 -Value ("{0} | {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
}

function Test-RemoteActive {
  # Chrome 원격 데스크톱에 지금 실제로 연결이 붙어 있는지 (mouse-guard 와 같은 판정)
  $pids = (Get-Process remoting_host -ErrorAction SilentlyContinue).Id
  if (-not $pids) { return 'CRD꺼짐' }
  $conn = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
          Where-Object { $pids -contains $_.OwningProcess -and $_.RemoteAddress -notmatch '^(127\.|::1)' }
  if ($conn) { return 'CRD원격접속중' } else { return 'CRD대기중' }
}

$interval = [int]$Cfg.IntervalSeconds
if ($interval -lt 1) { $interval = 3 }
Write-Log ("가드 시작 (확인 주기 {0}초, 자동해제 {1})" -f $interval, $Cfg.Enabled)

$wasOn = $false
while ($true) {
  $on = [KB]::IsOn([KB]::VK_SCROLL)

  if ($on -and -not $wasOn) {
    # 켜진 그 순간의 정황을 남긴다 — 반복되면 이 로그가 범인을 가리킨다
    Write-Log ("Scroll Lock 켜짐 감지 | {0} | 앞창: {1}" -f (Test-RemoteActive), [KB]::Foreground())
    if ($Cfg.Enabled) {
      [KB]::Tap([byte][KB]::VK_SCROLL)
      $now = [KB]::IsOn([KB]::VK_SCROLL)
      Write-Log ("자동 해제 {0}" -f $(if ($now) { '실패 — 아직 켜져 있음' } else { '완료' }))
      $on = $now
    } else {
      Write-Log '자동 해제 꺼져 있음 (config.json 의 Enabled=false)'
    }
  }
  $wasOn = $on
  Start-Sleep -Seconds $interval
}
