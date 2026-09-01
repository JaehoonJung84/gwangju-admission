param(
  [Parameter(Mandatory=$true)][string]$Rows,     # UTF-8 TSV : name_ko <TAB> name_en <TAB> course <TAB> dept <TAB> amount
  [Parameter(Mandatory=$true)][string]$DateText, # e.g. "2026. 9. 1.(hwa)" -- read from a UTF-8 file by run.ps1
  [Parameter(Mandatory=$true)][string]$Out,      # result .xlsx
  [string]$Pic = '',                             # bank capture png (optional)
  [string]$Template = ''
)
# ASCII only. Every Korean string comes from UTF-8 data files, never from this script:
# PowerShell 5.1 reads .ps1 as ANSI and would corrupt Korean literals.
$ErrorActionPreference = 'Stop'

if ($Template -eq '') { $Template = Join-Path (Join-Path $PSScriptRoot 'template') 'form_base.xlsx' }
if (-not (Test-Path $Template)) { throw ('template not found: ' + $Template) }

$lines = @([IO.File]::ReadAllLines($Rows, [Text.Encoding]::UTF8) |
           Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$n = $lines.Count
if ($n -lt 1) { throw 'no rows' }
Write-Output ("depositors: {0}" -f $n)

try { $excel = [Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application') }
catch { $excel = New-Object -ComObject Excel.Application }
$excel.Visible = $false
$excel.DisplayAlerts = $false

$wb = $excel.Workbooks.Open($Template)
$ws = $wb.Worksheets.Item(1)

# Grow the table by inserting rows just above the total row, so the total row
# keeps its own merge, label and borders.
for ($i = 2; $i -le $n; $i++) {
  $ws.Rows.Item(6).Insert(-4121, 0) | Out-Null   # -4121 = xlDown, 0 = format from above
}

for ($i = 0; $i -lt $n; $i++) {
  $f = $lines[$i] -split "`t"
  $r = 5 + $i
  $ws.Cells.Item($r, 1).Value2 = [string]($i + 1)
  $ws.Cells.Item($r, 2).Value2 = $f[0]
  $ws.Cells.Item($r, 3).Value2 = $f[1]
  $ws.Cells.Item($r, 4).Value2 = $f[2]
  $ws.Cells.Item($r, 5).Value2 = $f[3]
  $ws.Cells.Item($r, 6).Value2 = [double]$f[4]
  Write-Output ("  row {0}: {1} / {2} / {3}" -f $r, $f[0], $f[3], $f[4])
}

$last = 4 + $n
$tot = $last + 1
$ws.Cells.Item($tot, 6).Formula = ('=SUM(F5:F{0})' -f $last)
$ws.Cells.Item(3, 6).Value2 = $DateText

# Replace the bank capture, keeping the original left edge and size.
if ($Pic -ne '' -and (Test-Path $Pic)) {
  $L = 0; $W = 603; $H = 217.785
  if ($ws.Shapes.Count -ge 1) {
    $old = $ws.Shapes.Item(1)
    $L = $old.Left; $W = $old.Width; $H = $old.Height
    $old.Delete()
  }
  $T = $ws.Rows.Item($tot + 2).Top
  $null = $ws.Shapes.AddPicture($Pic, $false, $true, $L, $T, $W, $H)
  Write-Output ("  capture placed under the table (top={0})" -f $T)
}

if (Test-Path $Out) { Remove-Item $Out -Force }
$wb.SaveAs($Out, 51)
Write-Output ('saved: ' + $Out)
$wb.Close($false)
