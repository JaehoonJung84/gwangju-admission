param([string]$Path)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
function ReadEntry($name) {
  $e = $zip.Entries | Where-Object { $_.FullName -eq $name }
  if (-not $e) { return $null }
  $sr = New-Object System.IO.StreamReader($e.Open(), [System.Text.Encoding]::UTF8)
  $txt = $sr.ReadToEnd(); $sr.Close(); return $txt
}
function ColToIdx([string]$ref) {
  $m = [regex]::Match($ref, '^([A-Z]+)')
  $col = $m.Groups[1].Value
  [int]$n = 0
  foreach ($ch in $col.ToCharArray()) { $n = $n * 26 + ([int][char]$ch - 64) }
  return ($n - 1)
}
$shared = New-Object System.Collections.ArrayList
$ssTxt = ReadEntry 'xl/sharedStrings.xml'
if ($ssTxt) { [xml]$ss = $ssTxt; foreach ($si in $ss.sst.si) { [void]$shared.Add([string]$si.InnerText) } }
[xml]$wb = ReadEntry 'xl/workbook.xml'
[xml]$rels = ReadEntry 'xl/_rels/workbook.xml.rels'
$rmap = @{}
foreach ($r in $rels.Relationships.Relationship) { $rmap[$r.Id] = $r.Target }
$idx = 0
foreach ($s in $wb.workbook.sheets.sheet) {
  $idx++
  $rid = $s.GetAttribute('r:id'); if (-not $rid) { $rid = $s.id }
  $target = $rmap[$rid]
  if ($target -notmatch '^/') { $target = 'xl/' + $target } else { $target = $target.TrimStart('/') }
  Write-Output ("`n================ SHEET $idx : '" + $s.name + "'  ($target) ================")
  [xml]$sheet = ReadEntry $target
  foreach ($row in $sheet.worksheet.sheetData.row) {
    $cells = @{}; [int]$maxc = 0
    foreach ($cell in $row.c) {
      [int]$ci = ColToIdx $cell.r
      if ($ci -gt $maxc) { $maxc = $ci }
      $val = ''
      if ($cell.t -eq 's') { $val = $shared[[int]$cell.v] }
      elseif ($cell.t -eq 'inlineStr') { $val = [string]$cell.is.InnerText }
      else { $val = [string]$cell.v }
      $cells[$ci] = $val
    }
    $parts = @()
    for ($i = 0; $i -le $maxc; $i++) { if ($cells.ContainsKey($i) -and $cells[$i] -ne '') { $parts += ("[$i]" + $cells[$i]) } }
    if ($parts.Count -gt 0) { Write-Output ("R" + $row.r + ": " + ($parts -join ' | ')) }
  }
}
$zip.Dispose()
