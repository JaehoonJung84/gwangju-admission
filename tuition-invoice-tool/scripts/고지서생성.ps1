# =============================================================
#  2026-2학기 외국인 재학생 등록금 고지서 PDF 생성기
#  실행 예:
#   전체:      powershell -ExecutionPolicy Bypass -File 고지서생성.ps1
#   샘플 3장:  powershell -ExecutionPolicy Bypass -File 고지서생성.ps1 -Limit 3
#   직인 지정: powershell -ExecutionPolicy Bypass -File 고지서생성.ps1 -SealImage "C:\...\직인.png"
# =============================================================
param(
  [string]$InputFile = "C:\projects\admission\2_데이터\★2026-2학기 재학생 장학반영 고지서 생성_자동계산.xlsx",
  [string]$OutDir    = "C:\projects\admission\4_고지서출력",
  [string]$SealImage = "",          # 직인 이미지 (png/jpg). 없으면 (직인) 자리표시
  [int]$Limit        = 0            # 0 = 전체, N = 앞에서 N명만
)

$EdgePaths = @("$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe","${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe")
$Edge = $EdgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Edge) { Write-Host "Microsoft Edge를 찾을 수 없습니다." -ForegroundColor Red; exit 1 }

# ---------- 한글 -> 로마자(간이 RR) ----------
# 문자열 키 사용: [math]::Floor 결과가 double(5.0)여도 "$a"로 "5" 변환되어 매칭됨
$CHO  = @{'0'='g';'1'='kk';'2'='n';'3'='d';'4'='tt';'5'='r';'6'='m';'7'='b';'8'='pp';'9'='s';'10'='ss';'11'='';'12'='j';'13'='jj';'14'='ch';'15'='k';'16'='t';'17'='p';'18'='h'}
$JUNG = @{'0'='a';'1'='ae';'2'='ya';'3'='yae';'4'='eo';'5'='e';'6'='yeo';'7'='ye';'8'='o';'9'='wa';'10'='wae';'11'='oe';'12'='yo';'13'='u';'14'='wo';'15'='we';'16'='wi';'17'='yu';'18'='eu';'19'='ui';'20'='i'}
$JONG = @{'0'='';'1'='k';'2'='k';'3'='k';'4'='n';'5'='n';'6'='n';'7'='t';'8'='l';'9'='k';'10'='m';'11'='p';'12'='t';'13'='t';'14'='p';'15'='h';'16'='m';'17'='p';'18'='p';'19'='t';'20'='t';'21'='ng';'22'='t';'23'='t';'24'='k';'25'='t';'26'='p';'27'='h'}
function Cap([string]$s){ if($s.Length -eq 0){return $s}; return $s.Substring(0,1).ToUpper()+$s.Substring(1) }
function Romanize([string]$name){
  $out = @()
  foreach($ch in $name.ToCharArray()){
    $code = [int][char]$ch
    if($code -ge 0xAC00 -and $code -le 0xD7A3){
      $s = $code - 0xAC00
      $a=[math]::Floor($s/588); $b=[math]::Floor(($s%588)/28); $c=$s%28
      $syl = [string]$CHO["$a"] + [string]$JUNG["$b"] + [string]$JONG["$c"]
      $out += (Cap $syl)
    }
  }
  $r = ($out -join ' ').Trim()
  if($r -eq ''){ return $name }   # 변환 실패 시 한글 이름 그대로
  return $r
}

# ---------- 금액 포맷 ----------
function Won($n){ if($null -eq $n){return ''}; return ('{0:N0}' -f [double]$n) + '원' }

# ---------- 직인 base64 ----------
$SealTag = ''
if ($SealImage -ne '' -and (Test-Path $SealImage)) {
  $ext = ([System.IO.Path]::GetExtension($SealImage)).TrimStart('.').ToLower()
  if($ext -eq 'jpg'){$ext='jpeg'}
  $b64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($SealImage))
  $SealTag = "<img class='seal' src='data:image/$ext;base64,$b64' alt='직인'/>"
} else {
  $SealTag = "<span class='seal-ph'>(직인)</span>"
}

# ---------- HTML 템플릿 ----------
function Build-Html($rec){
  # 장학금 항목(0이 아닌 것만)
  $schRows = ''
  foreach($it in @(@('토픽 어학장학금 (TOPIK)',$rec.B), @('성적우수 장학금 (Merit)',$rec.C), @('공로 장학금 (Contribution)',$rec.D))){
    if([double]$it[1] -gt 0){
      $schRows += "<tr class='sch'><td class='lbl'>― $($it[0])</td><td class='amt minus'>△ $(Won $it[1])</td></tr>`n"
    }
  }
  if($schRows -eq ''){ $schRows = "<tr class='sch'><td class='lbl'>― 장학금 해당 없음</td><td class='amt'>0원</td></tr>`n" }

  $issueDate = (Get-Date).ToString('yyyy년 M월 d일')
@"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1a1a2e; }
  .page { width:210mm; height:297mm; padding:22mm 20mm; position:relative; }
  .frame { border:2.5px solid #1b3a6b; border-radius:6px; height:100%; padding:14mm 13mm; position:relative; }
  .uni { text-align:center; color:#1b3a6b; letter-spacing:2px; font-size:15px; font-weight:700; }
  .uni .en { display:block; font-size:10px; letter-spacing:1px; color:#5a6b8c; font-weight:600; margin-top:2px; }
  h1 { text-align:center; font-size:30px; letter-spacing:14px; margin:16px 0 2px; color:#12233f; }
  .sub { text-align:center; font-size:12px; letter-spacing:3px; color:#7a869c; margin-bottom:26px; }
  .rule { height:3px; background:linear-gradient(90deg,#1b3a6b,#4a79c9); margin:0 0 22px; border-radius:2px; }
  table { width:100%; border-collapse:collapse; }
  .info td { padding:9px 12px; font-size:13.5px; border:1px solid #d3dae8; }
  .info .k { background:#eef3fb; color:#33456b; width:32%; font-weight:700; }
  .info .en2 { color:#8a94a8; font-size:10.5px; font-weight:600; }
  .money { margin-top:24px; }
  .money caption { text-align:left; font-size:13px; font-weight:700; color:#1b3a6b; padding:0 0 8px; letter-spacing:1px; }
  .money td { padding:11px 14px; font-size:14px; border-bottom:1px solid #e3e8f0; }
  .money .lbl { color:#33456b; }
  .money .amt { text-align:right; font-variant-numeric:tabular-nums; }
  .money .tuition td { font-weight:700; }
  .money .minus { color:#b03a3a; }
  .money .total td { border-top:2.5px solid #1b3a6b; border-bottom:none; padding-top:14px; font-size:18px; font-weight:800; color:#12233f; }
  .money .total .amt { color:#1b3a6b; }
  .note { margin-top:20px; font-size:11px; color:#8a94a8; line-height:1.7; }
  .foot { position:absolute; left:0; right:0; bottom:6mm; text-align:center; }
  .foot .date { font-size:13px; color:#33456b; margin-bottom:12px; letter-spacing:2px; }
  .foot .sign { font-size:19px; font-weight:800; letter-spacing:6px; color:#12233f; position:relative; display:inline-block; }
  .seal { position:absolute; right:-70px; top:50%; transform:translateY(-50%); width:74px; height:74px; object-fit:contain; }
  .seal-ph { position:absolute; right:-64px; top:50%; transform:translateY(-50%); width:58px; height:58px; border:2px dashed #c46; border-radius:50%; color:#c46; font-size:11px; display:flex; align-items:center; justify-content:center; }
</style></head>
<body><div class='page'><div class='frame'>
  <div class='uni'>광주대학교 국제협력처<span class='en'>OFFICE OF INTERNATIONAL AFFAIRS, GWANGJU UNIVERSITY</span></div>
  <h1>등록금 고지서</h1>
  <div class='sub'>TUITION PAYMENT NOTICE</div>
  <div class='rule'></div>

  <table class='info'>
    <tr><td class='k'>성명 <span class='en2'>Name</span></td><td>$($rec.EnName)</td></tr>
    <tr><td class='k'>학번 <span class='en2'>Student No.</span></td><td>$($rec.Id)</td></tr>
    <tr><td class='k'>입학학기 <span class='en2'>Admission</span></td><td>$($rec.Year)학년도</td></tr>
    <tr><td class='k'>입학학과 <span class='en2'>Department</span></td><td>$($rec.Dept)</td></tr>
    <tr><td class='k'>과정 <span class='en2'>Track</span></td><td>English Track</td></tr>
  </table>

  <table class='money'>
    <caption>■ 등록금 산정 내역 &nbsp; Tuition Details</caption>
    <tr class='tuition'><td class='lbl'>수업료 (Tuition)</td><td class='amt'>$(Won $rec.A)</td></tr>
    $schRows
    <tr class='total'><td class='lbl'>실납부액 (Amount Due)</td><td class='amt'>$(Won $rec.F)</td></tr>
  </table>

  <div class='note'>
    ※ 본 고지서는 장학금이 반영된 최종 실납부액입니다. &nbsp; This notice reflects the final amount payable after scholarships.<br>
    ※ 문의 : 광주대학교 국제협력처 (Office of International Affairs) &nbsp; TEL. 062-670-2569
  </div>

  <div class='foot'>
    <div class='date'>$issueDate</div>
    <div class='sign'>광주대학교 국제협력처장$SealTag</div>
  </div>
</div></div></body></html>
"@
}

# ---------- 데이터 읽기 ----------
Write-Host "엑셀에서 데이터 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($InputFile); $ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellNum($r,$c){ $t=([string]$ws.Cells.Item($r,$c).Text).Trim() -replace '[^\d.-]',''; if($t -eq ''){return 0.0}; return [double]$t }
$students = @()
for($r=4;$r -le $last;$r++){
  $id = ([string]$ws.Cells.Item($r,2).Text).Trim()
  $nm = ([string]$ws.Cells.Item($r,3).Text).Trim()
  if($id -eq '' -and $nm -eq ''){continue}
  $type = ([string]$ws.Cells.Item($r,6).Text).Trim()
  $A = CellNum $r 8
  if($type -eq '교환' -or $A -le 0){ continue }   # 교환/미매핑 제외
  $students += [pscustomobject]@{
    Id=$id; KoName=$nm; EnName=(Romanize $nm)
    Year=$(if($id.Length -ge 4){$id.Substring(0,4)}else{''})
    Dept=([string]$ws.Cells.Item($r,4).Text).Trim()
    A=$A; B=(CellNum $r 10); C=(CellNum $r 13); D=(CellNum $r 14); F=(CellNum $r 16)
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Limit -gt 0){ $students = $students | Select-Object -First $Limit }
Write-Host ("대상 학생: {0}명 (직인: {1})" -f $students.Count, $(if($SealTag -match 'img'){'있음'}else{'없음-자리표시'})) -ForegroundColor Cyan

# ---------- PDF 생성 ----------
if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir | Out-Null }
$tmp = Join-Path $env:TEMP ("gu_gozi_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
$i=0
foreach($s in $students){
  $i++
  $html = Build-Html $s
  $htmlPath = Join-Path $tmp ("$($s.Id).html")
  [System.IO.File]::WriteAllText($htmlPath, $html, $enc)
  $safeName = ($s.EnName -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
  $pdfPath = Join-Path $OutDir ("$($s.Id)_$safeName.pdf")
  $uri = ([System.Uri]$htmlPath).AbsoluteUri
  $args = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$pdfPath"),$uri)
  Start-Process -FilePath $Edge -ArgumentList $args -Wait -WindowStyle Hidden
  if(Test-Path $pdfPath){ Write-Host ("  [{0}/{1}] {2}  {3}" -f $i,$students.Count,$s.Id,$s.EnName) }
  else { Write-Host ("  [{0}/{1}] 실패: {2}" -f $i,$students.Count,$s.Id) -ForegroundColor Red }
}
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ""
Write-Host ("완료! 출력 폴더: {0}" -f $OutDir) -ForegroundColor Green


