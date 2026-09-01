param(
  [string]$Day = '',            # 입금일 yyyy-MM-dd (생략하면 은행에서 읽은 첫 건의 날짜)
  [string]$Dest = '',           # 수입처리 파일을 놓을 폴더 (생략하면 아래 기본 경로)
  [switch]$SkipBank             # 은행 읽기 건너뛰기 (data\bank_rows.tsv 를 그대로 씀)
)
# 전형료 수입처리 자동화 — 은행 읽기 → 명단 대조 → 수입처리 엑셀 생성까지.
# ASCII only.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$data = Join-Path $root 'data'
$py = 'python'
if ($Dest -eq '') {
  $Dest = [IO.File]::ReadAllText((Join-Path $root 'dest_path.txt'), [Text.Encoding]::UTF8).Trim()
}

Write-Output '=== 1) 은행 거래내역 읽기'
if (-not $SkipBank) {
  & node (Join-Path $root 'bank_read.js')
  if ($LASTEXITCODE -ne 0) { throw 'bank read failed' }
} else {
  Write-Output '   (건너뜀)'
}

$rowsFile = Join-Path $data 'bank_rows.tsv'
$bank = @([IO.File]::ReadAllLines($rowsFile, [Text.Encoding]::UTF8) |
          Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($bank.Count -lt 1) { throw 'no deposits found' }
Write-Output ("   입금 {0}건" -f $bank.Count)

if ($Day -eq '') {
  $first = ($bank[0] -split "`t")[2]                 # 거래일시 e.g. 2026/09/01 18:32:10
  $Day = ($first -replace '[/.]', '-').Substring(0, 10)
}
Write-Output ("   입금일 {0}" -f $Day)

Write-Output '=== 2) 지원자 명단 대조'
$payTsv = Join-Path $data 'payers.tsv'
& $py (Join-Path $root 'match_payer.py') '--tsv' $rowsFile | Out-File -FilePath $payTsv -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw 'some payers were not matched - check the message above' }
Get-Content $payTsv | Where-Object { $_ } | ForEach-Object { Write-Output ('   ' + $_) }

Write-Output '=== 3) 증빙 캡쳐 정리 / 결의일 계산'
& $py (Join-Path $root 'prep.py') $Day

Write-Output '=== 4) 수입처리 엑셀 만들기'
$dateText = [IO.File]::ReadAllText((Join-Path $data 'date.txt'), [Text.Encoding]::UTF8)
$stamp = $Day -replace '-', ''
$outName = [IO.File]::ReadAllText((Join-Path $root 'name_pattern.txt'), [Text.Encoding]::UTF8).Trim()
$out = Join-Path $Dest ($outName -replace 'YYYYMMDD', $stamp)
& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'make_income.ps1') `
    -Rows $payTsv -DateText $dateText -Out $out -Pic (Join-Path $data 'bank_crop.png')

Write-Output ''
Write-Output ('완료 : ' + $out)
Write-Output ('수입결의일 : ' + [IO.File]::ReadAllText((Join-Path $data 'resolve.txt'), [Text.Encoding]::UTF8))
Write-Output '다음 단계 : ERP 수입결의서 작성 (erp_income.js)'
