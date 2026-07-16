# 학과별 지원자 서류 PDF 파일명 정리
#   기존: "박사 - 간호학 - 마숙현.pdf"  →  "(박사)간호학과_마숙현.pdf"
#   학과/과정은 파일명이 아니라 정리본 엑셀(지원학과 열)을 기준으로 매칭한다.
#   (기존 파일명의 학과 표기가 모집요강과 달라 신뢰할 수 없음)
# 사용: powershell -File rename_docs.ps1 -Roster <정리본.xlsx> -DocDir <서류폴더> [-Go]
param([string]$Roster, [string]$DocDir, [switch]$Go)

# 파일명에 쓴 이름 ↔ 명부 이름이 다른 경우
$ALIAS = @{
  '곽천량' = '곽전량'      # 파일명 오타 (명부·원서 모두 곽전량)
}

function Key($s) { ("$s" -replace '[·\s]', '') }   # 매칭용: 가운뎃점·공백 제거

# 1) 정리본에서 이름 → (과정, 지원학과) 표 만들기
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open($Roster)
$ws = $wb.Worksheets.Item(1)
$map = @{}
for ($r = 3; $r -le 41; $r++) {
  $name = "$($ws.Cells.Item($r,3).Text)".Trim()
  if (-not $name) { continue }
  $map[(Key $name)] = @{
    name = $name
    gwa  = "$($ws.Cells.Item($r,2).Text)".Trim()
    dept = "$($ws.Cells.Item($r,5).Text)".Trim()
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
Write-Output "명부 $($map.Count)명 로드`n"

# 2) PDF 순회
$ok = 0; $miss = @()
foreach ($f in (Get-ChildItem -LiteralPath $DocDir -Filter *.pdf | Sort-Object Name)) {
  # 이름 = 마지막 ' - ' 뒤 조각
  $parts = [regex]::Split($f.BaseName, '\s*-\s*')
  $raw = $parts[-1].Trim()
  $lookup = if ($ALIAS.ContainsKey($raw)) { $ALIAS[$raw] } else { $raw }

  $hit = $map[(Key $lookup)]
  if (-not $hit) { $miss += "$($f.Name)  (이름 '$raw' 을 명부에서 못 찾음)"; continue }

  $new = "($($hit.gwa))$($hit.dept)_$($hit.name).pdf"
  if ($f.Name -eq $new) { Write-Output ("  = {0}" -f $f.Name); $ok++; continue }

  $note = ''
  if ((Key $raw) -ne (Key $hit.name)) { $note = "   ← 이름 수정 ($raw → $($hit.name))" }
  Write-Output ("  {0,-46} -> {1}{2}" -f $f.Name, $new, $note)
  if ($Go) { Rename-Item -LiteralPath $f.FullName -NewName $new }
  $ok++
}

Write-Output "`n대상 $ok 건"
if ($miss) { Write-Output "`n[매칭 실패]"; $miss | ForEach-Object { Write-Output "  ⚠ $_" } }
if (-not $Go) { Write-Output "`n(드라이런: -Go 를 붙이면 실제로 이름 변경)" }
