# 신입학 수험번호생성 엑셀 3개를 양식(template)에 맞춰 한 파일로 병합
#  - 각 원본의 1열(구분/순번)을 떼고, 2~14열 → 양식 1~13열로 매핑
#  - 모든 값은 원본 그대로(텍스트) 보존. 우편번호/주민번호/코드/날짜가 숫자로 뭉개지지 않게 텍스트 서식
#  - 데이터 이상(빈 필수값 등)은 로그로 보고
# 사용: powershell -File merge_suhum.ps1
$ErrorActionPreference='Stop'

$FOLDER="C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\합격자 발표\전산입력\신입학"
$TEMPLATE="C:\Users\user\Downloads\ipsi_suhum_create_excel (2).xls"
$OUT="$FOLDER\2026-2학기 신입학 수험번호생성_통합(오하선+김유성+이심은).xls"

$SOURCES=@(
  @{ label='오하선'; path="$FOLDER\ipsi_suhum_create-오하선.xls" },
  @{ label='김유성'; path="$FOLDER\ipsi_suhum_create_excel_김유성.xls" },
  @{ label='이심은'; path="$FOLDER\2026학년도 신입생 명단(이심은).xlsx" }
)

# 양식 헤더(1~13) — 원본 col 2~14가 여기에 매핑됨
$HEAD=@('수험번호','이름','영문이름','주민번호','연락처','전형코드','학부(과)코드','출신고교코드','고교 졸업일','우편번호','기본주소','상세주소','국가코드')
# 사람이 확인해야 하는 필수 열(양식 기준 열번호): 이름2 영문3 주민4 전형6 학부7 국가13
$REQUIRED=@{2='이름';3='영문이름';4='주민번호';6='전형코드';7='학부(과)코드';13='국가코드'}

$xl=New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
try {

# 1) 세 원본을 읽어 배열로 (각 행 = 양식 13열 값)
$all=New-Object System.Collections.ArrayList
$log=New-Object System.Collections.ArrayList
foreach($s in $SOURCES){
  # 잠금 대비 사본
  $copy=Join-Path $env:TEMP ("suhum_"+[guid]::NewGuid().ToString()+[System.IO.Path]::GetExtension($s.path))
  Copy-Item -LiteralPath $s.path -Destination $copy -Force
  $wb=$xl.Workbooks.Open($copy,0,$true)
  $ws=$wb.Worksheets.Item('Sheet1')
  $ur=$ws.UsedRange; $rows=$ur.Rows.Count
  $cnt=0
  for($r=2;$r -le $rows;$r++){
    # 원본 3열(이름=양식 2열)이 비면 빈 행으로 간주
    if(-not "$($ws.Cells.Item($r,3).Text)".Trim()){ continue }
    $vals=@()
    for($c=2;$c -le 14;$c++){ $vals += "$($ws.Cells.Item($r,$c).Text)".Trim() }
    [void]$all.Add([pscustomobject]@{ src=$s.label; srcRow=$r; v=$vals })
    $cnt++
    # 필수값 점검
    foreach($tc in ($REQUIRED.Keys | Sort-Object)){
      if(-not $vals[$tc-1]){ [void]$log.Add("  ⚠ [$($s.label)] 원본 R$r $($ws.Cells.Item($r,3).Text): $($REQUIRED[$tc]) 비어있음") }
    }
    # 주민번호 형식(######-#######) 점검
    $ssn=$vals[3]
    if($ssn -and $ssn -notmatch '^\d{6}-\d{7}$'){ [void]$log.Add("  ⚠ [$($s.label)] 원본 R$r $($ws.Cells.Item($r,3).Text): 주민번호 형식 이상 '$ssn'") }
  }
  [void]$log.Add("  · $($s.label): $cnt 명")
  $wb.Close($false)
  Remove-Item $copy -Force
}

# 2) 양식 복사 후 데이터 기록
Copy-Item -LiteralPath $TEMPLATE -Destination $OUT -Force
$wbO=$xl.Workbooks.Open($OUT)
$wsO=$wbO.Worksheets.Item('Sheet1')
# 기존 예시행(2행 이하) 정리
$last=$wsO.UsedRange.Rows.Count
if($last -ge 2){ $wsO.Range("A2:M$([Math]::Max(2,$last))").Clear() | Out-Null }
# 전체 텍스트 서식
$total=$all.Count
$wsO.Range("A1:M$($total+1)").NumberFormat='@'
# 헤더 재기입(안전)
for($c=1;$c -le 13;$c++){ $wsO.Cells.Item(1,$c).Value2=$HEAD[$c-1] }
# 데이터
$r=2
foreach($item in $all){
  for($c=1;$c -le 13;$c++){ $wsO.Cells.Item($r,$c).Value2=$item.v[$c-1] }
  $r++
}
$wsO.Columns.AutoFit() | Out-Null
$wsO.Cells.Item(1,1).Select() | Out-Null

$wbO.Save()
$wbO.Close($true)

} finally {
  $xl.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null
}

Write-Output "통합 파일: $OUT"
Write-Output "총 $total 명"
Write-Output "`n── 보고 ──"
$log | ForEach-Object { Write-Output $_ }
