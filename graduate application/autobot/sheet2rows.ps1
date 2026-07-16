# Sheet2(대학원 지원자)를 셀 배열 JSON으로 덤프. 엑셀이 열려 있어도 되도록 사본을 뜬다.
param([string]$Path, [string]$Out)
$tmp = [System.IO.Path]::GetTempFileName() + '.xlsx'
Copy-Item -LiteralPath $Path -Destination $tmp -Force
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($tmp)
function ReadEntry($name) {
  $e = $zip.Entries | Where-Object { $_.FullName -eq $name }
  if (-not $e) { return $null }
  $sr = New-Object System.IO.StreamReader($e.Open(), [System.Text.Encoding]::UTF8)
  $txt = $sr.ReadToEnd(); $sr.Close(); return $txt
}
function ColToIdx([string]$ref) {
  $col = [regex]::Match($ref, '^([A-Z]+)').Groups[1].Value
  [int]$n = 0
  foreach ($ch in $col.ToCharArray()) { $n = $n * 26 + ([int][char]$ch - 64) }
  return ($n - 1)
}
$shared = New-Object System.Collections.ArrayList
$ssTxt = ReadEntry 'xl/sharedStrings.xml'
if ($ssTxt) { [xml]$ss = $ssTxt; foreach ($si in $ss.sst.si) { [void]$shared.Add([string]$si.InnerText) } }
[xml]$sheet = ReadEntry 'xl/worksheets/sheet2.xml'
$rows = New-Object System.Collections.ArrayList
foreach ($row in $sheet.worksheet.sheetData.row) {
  $cells = @{}; [int]$maxc = 0
  foreach ($cell in $row.c) {
    [int]$ci = ColToIdx $cell.r
    if ($ci -gt $maxc) { $maxc = $ci }
    if ($cell.t -eq 's') { $cells[$ci] = $shared[[int]$cell.v] }
    elseif ($cell.t -eq 'inlineStr') { $cells[$ci] = [string]$cell.is.InnerText }
    else { $cells[$ci] = [string]$cell.v }
  }
  $arr = @()
  for ($i = 0; $i -le 30; $i++) { if ($cells.ContainsKey($i)) { $arr += [string]$cells[$i] } else { $arr += '' } }
  [void]$rows.Add([pscustomobject]@{ r = [int]$row.r; c = $arr })
}
$zip.Dispose(); Remove-Item $tmp -Force
$rows | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $Out
Write-Output ("rows=" + $rows.Count + " -> " + $Out)
