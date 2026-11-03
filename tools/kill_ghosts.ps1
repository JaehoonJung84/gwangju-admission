# 창 없는 유령 한글/엑셀(COM 자동화 잔재)만 정리한다.
# 문서가 열려 있는 창(=MainWindowHandle 0 아님)은 절대 건드리지 않는다.
$ErrorActionPreference = 'Stop'

function ResSum {
  if (-not ('X.GG' -as [type])) {
    Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern int GetGuiResources(IntPtr h, int f);' -Name GG -Namespace X | Out-Null
  }
  $g = 0; $u = 0; $h = 0
  foreach ($p in Get-Process) {
    try { $g += [X.GG]::GetGuiResources($p.Handle, 0); $u += [X.GG]::GetGuiResources($p.Handle, 1); $h += $p.HandleCount } catch {}
  }
  [pscustomobject]@{ GDI = $g; USER = $u; Handles = $h; Procs = (Get-Process).Count }
}

$b = ResSum
Write-Host ("정리 전 : GDI {0} / USER {1} / 핸들 {2} / 프로세스 {3}" -f $b.GDI, $b.USER, $b.Handles, $b.Procs)

# 1) COM 으로 뜬 창 없는 한글
$hwp = @()
foreach ($c in (Get-CimInstance Win32_Process -Filter "Name='Hwp.exe'")) {
  if ($c.CommandLine -like '*-Automation*-Embedding*') {
    $p = Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue
    if ($p -and $p.MainWindowHandle -eq 0) { $hwp += $c.ProcessId }
  }
}
# 2) 창 없는 엑셀(워크북 없는 자동화 인스턴스)
$xl = @()
foreach ($c in (Get-CimInstance Win32_Process -Filter "Name='EXCEL.EXE'")) {
  $p = Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue
  if ($p -and $p.MainWindowHandle -eq 0) { $xl += $c.ProcessId }
}

Write-Host ("정리 대상 : 한글 {0}개 / 엑셀 {1}개" -f $hwp.Count, $xl.Count)
Write-Host ("보호(창 있는 것) : 한글 {0}개 / 엑셀 {1}개" -f `
  @(Get-Process Hwp -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 }).Count, `
  @(Get-Process EXCEL -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 }).Count)

$n = 0
foreach ($id in ($hwp + $xl)) {
  try { Stop-Process -Id $id -Force; $n++ } catch { Write-Host ("  실패 {0} : {1}" -f $id, $_.Exception.Message) }
}
Start-Sleep -Seconds 3
$a = ResSum
Write-Host ("종료한 프로세스 : {0}개" -f $n)
Write-Host ("정리 후 : GDI {0} / USER {1} / 핸들 {2} / 프로세스 {3}" -f $a.GDI, $a.USER, $a.Handles, $a.Procs)
Write-Host ("되찾음  : GDI {0} / USER {1} / 핸들 {2}" -f ($b.GDI - $a.GDI), ($b.USER - $a.USER), ($b.Handles - $a.Handles))
Write-Host ("남은 한글 {0}개 / 남은 엑셀 {1}개 (열린 문서용)" -f `
  @(Get-Process Hwp -ErrorAction SilentlyContinue).Count, @(Get-Process EXCEL -ErrorAction SilentlyContinue).Count)
