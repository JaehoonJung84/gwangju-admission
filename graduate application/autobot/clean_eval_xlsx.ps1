# 대학원 지원자 현황(학과 평가용) 정리본 생성
#  - 날짜(생년월일/졸업일자) → YYYY-MM-DD 텍스트로 통일 (엑셀 직렬번호/점표기 혼재 해소)
#  - 성적 만점 표기 통일: 4→4.0, 4.50→4.5 (환산은 하지 않음, 100점 만점은 원본 유지)
#  - 학과명/영문명/전공 오타 정리
# 사용: powershell -File clean_eval_xlsx.ps1 -Src <원본.xlsx> -Dst <정리본.xlsx>
param([string]$Src, [string]$Dst)

Copy-Item -LiteralPath $Src -Destination $Dst -Force

$EPOCH = [datetime]'1899-12-30'
$log = New-Object System.Collections.ArrayList

function Norm-Date($v) {
  if ($null -eq $v -or "$v".Trim() -eq '') { return $null }
  $s = "$v".Trim()
  if ($s -match '^\d{5}(\.\d+)?$') { return $EPOCH.AddDays([double]$s).ToString('yyyy-MM-dd') }   # 엑셀 직렬번호
  if ($s -match '^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\.?$') {
    return ('{0:0000}-{1:00}-{2:00}' -f [int]$Matches[1], [int]$Matches[2], [int]$Matches[3])
  }
  return "!$s"   # 파싱 실패 표시
}

function Norm-Score($v) {
  if ($null -eq $v -or "$v".Trim() -eq '') { return $null }
  $s = "$v".Trim()
  if ($s -notmatch '^([\d.]+)\s*/\s*([\d.]+)$') { return "!$s" }
  $num = $Matches[1]; $den = [double]$Matches[2]
  if ([math]::Abs($den - 100) -lt 0.01) { return "$num/100" }          # 100점 만점: 원본 유지
  $d = switch ([math]::Round($den, 1)) { 4.5 { '4.5' } 4.3 { '4.3' } 4.0 { '4.0' } default { $null } }
  if (-not $d) { return "!$s" }
  return ('{0:0.00}/{1}' -f [double]$num, $d)                           # GPA: 소수 2자리로 통일
}

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open($Dst)
$ws = $wb.Worksheets.Item(1)

$FIRST = 3; $LAST = 41
$DATE_COLS  = @(10, 15, 19, 23)   # J 생년월일, O/S/W 졸업일자
$SCORE_COLS = @(12, 17, 21)       # L, Q, U 성적

for ($r = $FIRST; $r -le $LAST; $r++) {
  $no   = $ws.Cells.Item($r, 1).Text
  $name = $ws.Cells.Item($r, 3).Text
  if (-not $name) { continue }

  foreach ($c in $DATE_COLS) {
    $cell = $ws.Cells.Item($r, $c)
    $old = $cell.Value2
    $new = Norm-Date $old
    if ($null -eq $new) { continue }
    if ($new.StartsWith('!')) { [void]$log.Add("  ⚠ $no $name : 날짜 파싱실패 [$($cell.Address($false,$false))] '$($new.Substring(1))'"); continue }
    $cell.NumberFormat = '@'      # 텍스트로 고정 → 표시 형식이 어디서든 동일
    $cell.Value2 = $new
  }

  foreach ($c in $SCORE_COLS) {
    $cell = $ws.Cells.Item($r, $c)
    $old = $cell.Text
    $new = Norm-Score $old
    if ($null -eq $new) { continue }
    if ($new.StartsWith('!')) { [void]$log.Add("  ⚠ $no $name : 성적 형식이상 [$($cell.Address($false,$false))] '$($new.Substring(1))'"); continue }
    if ($new -ne $old) {
      $cell.NumberFormat = '@'
      $cell.Value2 = $new
    }
  }

  # 지원학과 통일
  $dept = $ws.Cells.Item($r, 5)
  $dv = "$($dept.Text)".Trim()
  if ($dv -eq '뷰티미용학') { $dept.Value2 = '뷰티미용학과'; [void]$log.Add("  · $no $name : 지원학과 뷰티미용학 → 뷰티미용학과") }
  if ($dv -eq '경영학')     { $dept.Value2 = '경영학과';     [void]$log.Add("  · $no $name : 지원학과 경영학 → 경영학과") }

  # 영문명 공백 정리
  $en = $ws.Cells.Item($r, 4)
  $ev = "$($en.Text)".Trim() -replace '\s+', ' '
  if ($ev -and $ev -ne "$($en.Text)") { $en.Value2 = $ev; [void]$log.Add("  · $no $name : 영문명 공백 정리") }

  # 전공 오타
  foreach ($c in @(14, 18, 22)) {
    $m = $ws.Cells.Item($r, $c)
    if ("$($m.Text)".Trim() -eq '유아밭달및건강관리') { $m.Value2 = '유아발달및건강관리'; [void]$log.Add("  · $no $name : 전공 오타 수정 (유아밭달 → 유아발달)") }
  }

  # 학교명 오타 (전문학사 K / 학사 P / 석사 T)
  $SCHOOL_FIX = @{
    '사마르칸튼국립외국어대'   = '사마르칸트국립외국어대'      # 원서 서류상 '사마르칸트'
    '타슈켄트국립동박학대학교' = '타슈켄트국립동방학대학교'    # Oriental Studies = 동방학
  }
  foreach ($c in @(11, 16, 20)) {
    $s = $ws.Cells.Item($r, $c)
    $sv = "$($s.Text)".Trim()
    if ($SCHOOL_FIX.ContainsKey($sv)) {
      $s.Value2 = $SCHOOL_FIX[$sv]
      [void]$log.Add("  · $no $name : 학교명 오타 수정 ($sv → $($SCHOOL_FIX[$sv]))")
    }
  }
}

# 드엉팟팅(순번 21) 생년월일: 졸업일자가 잘못 들어가 있었음 → 원서 시스템 기준 2001-01-23
for ($r = $FIRST; $r -le $LAST; $r++) {
  if ("$($ws.Cells.Item($r,3).Text)".Trim() -eq '드엉팟팅') {
    $b = $ws.Cells.Item($r, 10)
    [void]$log.Add("  · 21 드엉팟팅 : 생년월일 '$($b.Text)' → 2001-01-23 (졸업일자가 잘못 입력돼 있었음)")
    $b.NumberFormat = '@'; $b.Value2 = '2001-01-23'
  }
}

$wb.Save()
$wb.Close($true)
$xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ws) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

Write-Output "정리본: $Dst"
Write-Output "── 변경/경고 ──"
$log | ForEach-Object { Write-Output $_ }
