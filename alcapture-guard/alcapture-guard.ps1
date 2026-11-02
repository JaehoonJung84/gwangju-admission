# 알캡처 가드 - "캡처 이미지 수가 목록 최대 개수를 초과하였습니다(100장)" 예방
#
# 알캡처는 캡처 목록을 아래 폴더의 PNG 파일 개수로 관리하며 100장이 한도다.
# 한도에 닿기 전에 오래된 캡처를 백업 폴더로 "이동"(삭제 아님)해 목록을 비워둔다.
#
# 관찰 사실(2026-09-01):
#  - ALCapture.exe      : 트레이 대기 상태에서는 MainWindowHandle 이 0 인 것이 정상
#  - ALCaptureEditor.exe: 이 프로세스가 "알캡처 결과창"이며 알캡처와 함께 상시 실행됨
#    따라서 프로세스 존재/창핸들만으로는 사용자가 작업 중인지 알 수 없어,
#    실제 화면 표시 여부는 Win32 IsWindowVisible 로 판정한다.
$ErrorActionPreference = 'Stop'

$Root       = 'C:\projects\alcapture-guard'
$LogPath    = Join-Path $Root 'alcapture-guard.log'
$FlagPath   = Join-Path $Root 'pending-restart.flag'
$CaptureDir = Join-Path $env:APPDATA 'ESTsoft\ALCapture'
$BackupRoot = Join-Path $env:USERPROFILE 'Documents\알캡처_캡처백업'
$ExePath    = 'C:\Program Files (x86)\ESTsoft\ALCapture\ALCapture.exe'

$Threshold  = 70   # 캡처가 이 장수 이상 쌓이면 정리 (한도 100)
$KeepCount  = 40   # 최근 이만큼은 목록에 남겨둠
$ForceLimit = 85   # 보류 중 결과창 목록이 이 장수에 닿으면 창이 열려 있어도 재시작
$ForceHours = 12   # 또는 보류가 이 시간을 넘기면 재시작

function Write-Log($msg) {
    if ((Test-Path -LiteralPath $LogPath) -and ((Get-Item -LiteralPath $LogPath).Length -gt 1MB)) {
        Move-Item -LiteralPath $LogPath -Destination "$LogPath.1" -Force
    }
    $line = '{0} | {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

if (-not ('Win32Vis' -as [type])) {
    Add-Type -Namespace '' -Name Win32Vis -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
'@
}

# 결과창이 실제로 화면에 떠 있는지(= 사용자가 보고 있는지)
function Test-ResultWindowVisible {
    foreach ($p in @(Get-Process ALCaptureEditor -ErrorAction SilentlyContinue)) {
        $h = $p.MainWindowHandle
        if ($h -ne 0 -and [Win32Vis]::IsWindowVisible($h) -and -not [Win32Vis]::IsIconic($h)) { return $true }
    }
    return $false
}

# 보류 기록(정리 직전 장수 / 보류 시각)을 읽는다. 옛 형식(빈 파일)이면 파일 시각을 쓴다.
function Get-PendingInfo {
    $info = @{ Before = 0; At = (Get-Item -LiteralPath $FlagPath).LastWriteTime }
    foreach ($line in @(Get-Content -LiteralPath $FlagPath -ErrorAction SilentlyContinue)) {
        if ($line -match '^before=(\d+)$')  { $info.Before = [int]$Matches[1] }
        elseif ($line -match '^at=(.+)$')    { try { $info.At = [datetime]$Matches[1] } catch { } }
    }
    return $info
}

# 정리는 끝났는데 결과창이 열려 있어 재시작을 못 했던 경우, 여기서 다시 시도한다.
function Restart-ALCapture {
    foreach ($p in @(Get-Process ALCapture, ALCaptureEditor -ErrorAction SilentlyContinue)) {
        try { Stop-Process -Id $p.Id -Force -Confirm:$false } catch { }
    }
    Start-Sleep -Milliseconds 1500
    if (Test-Path -LiteralPath $ExePath) {
        Start-Process -FilePath $ExePath -WorkingDirectory (Split-Path $ExePath -Parent)
        return $true
    }
    return $false
}

if (-not (Test-Path -LiteralPath $CaptureDir)) { exit 0 }

if (Test-Path -LiteralPath $FlagPath) {
    # 결과창은 정리 전 목록을 그대로 들고 있다. 보류하는 동안 새 캡처가 쌓이면
    # 화면상 목록이 100장에 닿아 캡처가 막힌다(파일은 64장뿐인데 "초과" 대화상자).
    # 그래서 한도에 가까워지거나 보류가 길어지면 결과창이 열려 있어도 재시작한다.
    # 캡처 파일은 이미 백업 폴더로 옮겨 두었으므로 잃는 것은 없다.
    $pend  = Get-PendingInfo
    $added = @(Get-ChildItem -LiteralPath $CaptureDir -Filter *.png -File |
               Where-Object { $_.LastWriteTime -gt $pend.At }).Count
    $stale = $pend.Before + $added
    $hours = ((Get-Date) - $pend.At).TotalHours
    if ((Test-ResultWindowVisible) -and $stale -lt $ForceLimit -and $hours -lt $ForceHours) {
        exit 0                                  # 아직 보고 있고 여유도 있음. 다음 점검 때 재시도.
    } elseif (Restart-ALCapture) {
        Remove-Item -LiteralPath $FlagPath -Force
        Write-Log ('보류했던 알캡처 재시작 완료 (목록 추정 {0}장, 보류 {1:N1}시간)' -f $stale, $hours)
    } else {
        Remove-Item -LiteralPath $FlagPath -Force
        Write-Log "보류했던 재시작 실패 - 실행파일 없음: $ExePath"
    }
}

$files = @(Get-ChildItem -LiteralPath $CaptureDir -Filter *.png -File |
           Sort-Object LastWriteTime -Descending)
if ($files.Count -lt $Threshold) { exit 0 }   # 평소에는 아무 일도 하지 않음

$before  = $files.Count
$trimmed = 0
$failed  = 0

foreach ($f in @($files | Select-Object -Skip $KeepCount)) {
    try {
        $sub = Join-Path $BackupRoot $f.LastWriteTime.ToString('yyyy-MM')
        if (-not (Test-Path -LiteralPath $sub)) { New-Item -ItemType Directory -Path $sub -Force | Out-Null }
        $dest = Join-Path $sub $f.Name
        if (Test-Path -LiteralPath $dest) {
            $dest = Join-Path $sub ('{0}_{1}{2}' -f $f.BaseName, $f.LastWriteTime.ToString('HHmmssfff'), $f.Extension)
        }
        Move-Item -LiteralPath $f.FullName -Destination $dest -Force
        $trimmed++
    } catch {
        $failed++
    }
}

$after = @(Get-ChildItem -LiteralPath $CaptureDir -Filter *.png -File).Count
$msg = '캡처 {0}장 -> {1}장 (백업 {2}장{3})' -f $before, $after, $trimmed, $(if ($failed) { ", 실패 $failed" } else { '' })

# 결과창이 파일 목록을 메모리에 들고 있으므로, 정리 후에는 재시작해야 카운트가 맞는다.
if ($trimmed -eq 0) {
    Write-Log $msg
} elseif (Test-ResultWindowVisible) {
    Set-Content -LiteralPath $FlagPath -Encoding UTF8 -Value @(
        ('before={0}' -f $before),
        ('at={0}' -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')))
    Write-Log "$msg / 결과창이 열려 있어 재시작 보류(다음 점검 때 재시도)"
} elseif (Restart-ALCapture) {
    Write-Log "$msg / 알캡처 재시작 완료"
} else {
    Write-Log "$msg / 실행파일 없음: $ExePath"
}
