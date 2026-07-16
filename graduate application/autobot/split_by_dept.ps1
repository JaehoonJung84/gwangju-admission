# 지원자 현황 정리본을 (과정 × 지원학과) 별로 분할. 예: 간호학과(석사).xlsx / 간호학과(박사).xlsx
#  - 원본 서식/헤더 유지 (정리본을 복사한 뒤 해당 학과가 아닌 행을 삭제)
#  - 순번은 파일마다 1부터 재부여
#  - 그 파일에서 전부 비어 있는 학력 블록(전문학사/학사/석사)은 열 자체를 삭제
# 사용: powershell -File split_by_dept.ps1 -Src <정리본.xlsx> -OutDir <배포폴더>
param([string]$Src, [string]$OutDir)

$FIRST = 3; $LAST = 41
$C_NO = 1; $C_GWA = 2; $C_NAME = 3; $C_DEPT = 5
# 학력 블록: 시작열, 열 수 (전문학사 K:O=11..15, 학사 P:S=16..19, 석사 T:W=20..23)
$BLOCKS = @(
  @{ name = '전문학사'; start = 11; count = 5 },
  @{ name = '학사';     start = 16; count = 4 },
  @{ name = '석사';     start = 20; count = 4 }
)

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false

# 1) 원본에서 (과정, 학과) 그룹 파악
$wb0 = $xl.Workbooks.Open($Src)
$ws0 = $wb0.Worksheets.Item(1)
$groups = @{}
for ($r = $FIRST; $r -le $LAST; $r++) {
  $name = "$($ws0.Cells.Item($r, $C_NAME).Text)".Trim()
  if (-not $name) { continue }
  $gwa  = "$($ws0.Cells.Item($r, $C_GWA).Text)".Trim()
  $dept = "$($ws0.Cells.Item($r, $C_DEPT).Text)".Trim()
  $key = "$gwa`t$dept"          # 과정 \t 학과
  if (-not $groups.ContainsKey($key)) { $groups[$key] = New-Object System.Collections.ArrayList }
  [void]$groups[$key].Add($r)
}
$wb0.Close($false)

Write-Output "그룹 $($groups.Count)개 / 총 $(($groups.Values | ForEach-Object { $_.Count } | Measure-Object -Sum).Sum)명`n"

# 2) 그룹별 파일 생성
foreach ($key in ($groups.Keys | Sort-Object)) {
  $rows = $groups[$key]                       # 남길 원본 행번호들
  $gwa, $dept = $key -split "`t"
  # 배포용 파일명: (박사)간호학과_12명.xlsx
  $fname = "($gwa)${dept}_$($rows.Count)명.xlsx"
  $dst = Join-Path $OutDir $fname
  Copy-Item -LiteralPath $Src -Destination $dst -Force

  $wb = $xl.Workbooks.Open($dst)
  $ws = $wb.Worksheets.Item(1)

  # 해당 그룹이 아닌 데이터 행 삭제 (아래에서 위로)
  for ($r = $LAST; $r -ge $FIRST; $r--) {
    if ($rows -notcontains $r) { [void]$ws.Rows.Item($r).Delete() }
  }

  $n = $rows.Count
  $newLast = $FIRST + $n - 1

  # 순번 재부여
  for ($i = 0; $i -lt $n; $i++) { $ws.Cells.Item($FIRST + $i, $C_NO).Value2 = $i + 1 }

  # 전부 빈 학력 블록은 열 삭제 (뒤 블록부터 지워야 열 번호가 안 밀림)
  $dropped = @()
  foreach ($b in ($BLOCKS | Sort-Object { $_.start } -Descending)) {
    $used = $false
    for ($r = $FIRST; $r -le $newLast -and -not $used; $r++) {
      for ($c = $b.start; $c -lt ($b.start + $b.count); $c++) {
        if ("$($ws.Cells.Item($r, $c).Text)".Trim()) { $used = $true; break }
      }
    }
    if (-not $used) {
      [void]$ws.Range($ws.Columns.Item($b.start), $ws.Columns.Item($b.start + $b.count - 1)).Delete()
      $dropped += $b.name
    }
  }

  $ws.Cells.Item($FIRST, 1).Select() | Out-Null
  $wb.Save()
  $wb.Close($true)

  $note = if ($dropped) { "  (빈 학력열 삭제: $($dropped -join ', '))" } else { '' }
  Write-Output ("  {0,-36}{1}" -f $fname, $note)
}

$xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
Write-Output "`n출력 폴더: $OutDir"
