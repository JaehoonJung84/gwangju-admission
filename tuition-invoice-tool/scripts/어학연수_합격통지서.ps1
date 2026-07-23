# =============================================================
#  2026학년도 가을학기 한국어 어학연수 과정 합격통지서 생성기
#  · 학생 1명당 1페이지 PDF (OFFER LETTER)
#  · 저장: <OutRoot>\{1. 파키스탄|2. 몽골|3. 그 외 국가}\한글명_영문명.pdf
#  실행: powershell -ExecutionPolicy Bypass -File 어학연수_합격통지서.ps1 [-Only "한글명"] [-Limit N]
# =============================================================
param(
  [string]$MainFile = "C:\Users\user\Desktop\★국제협력처\3. 어학연수\2026년 가을학기 합격통지서(오하선 요청)\2026학년도 가을학기 지원자 명단-오하선.xlsx",
  [string]$OutRoot  = "C:\Users\user\Desktop\★국제협력처\3. 어학연수\2026년 가을학기 합격통지서(오하선 요청)\발행",
  [string]$SealImage = "",
  [string]$LogoImage = "",
  [string]$IssueDate = "",
  [string]$Only      = "",
  [int]$Limit        = 0
)

$AssetDir = Split-Path $PSScriptRoot -Parent
if ($SealImage -eq '') { $p = Join-Path $AssetDir '국제협력처장직인.png'; if (Test-Path $p) { $SealImage = $p } }
if ($LogoImage -eq '') { $p = Join-Path $AssetDir '로고_국영문_full.png'; if (Test-Path $p) { $LogoImage = $p } }

$EdgePaths = @("$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe","${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe")
$Edge = $EdgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Edge) { Write-Host "Microsoft Edge를 찾을 수 없습니다." -ForegroundColor Red; exit 1 }

function DataUri([string]$path){
  if($path -eq '' -or -not (Test-Path $path)){ return '' }
  $ext = ([System.IO.Path]::GetExtension($path)).TrimStart('.').ToLower()
  if($ext -eq 'jpg'){$ext='jpeg'}
  $b64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($path))
  return "data:image/$ext;base64,$b64"
}
$SealUri = DataUri $SealImage
$SealTag = if ($SealUri -ne '') { "<img class='seal' src='$SealUri' alt='직인'/>" } else { "<span class='seal-ph'>(직인)</span>" }
$LogoUri = DataUri $LogoImage
$LogoTag = if ($LogoUri -ne '') { "<img class='logo' src='$LogoUri' alt='광주대학교'/>" } else { '' }

# ---------- 매핑 ----------
# 국적코드(3자리) / 한글명 -> (영문, 한글)
$CTRY = @{
  'MNG'=@('Mongolia','몽골'); 'PAK'=@('Pakistan','파키스탄'); 'KGZ'=@('Kyrgyzstan','키르기즈스탄');
  'VNM'=@('Vietnam','베트남'); 'CHN'=@('China','중국'); 'UZB'=@('Uzbekistan','우즈베키스탄');
  'BGD'=@('Bangladesh','방글라데시'); 'LAO'=@('Laos','라오스');
}
function CtryEn([string]$c){ if($CTRY.ContainsKey($c)){ return $CTRY[$c][0] } else { return $c } }
function CtryKo([string]$c){ if($CTRY.ContainsKey($c)){ return $CTRY[$c][1] } else { return $c } }
function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function NormBirth([string]$s){
  $d = ($s -replace '[^\d]','')
  if($d.Length -ge 8){ return $d.Substring(0,4)+'-'+$d.Substring(4,2)+'-'+$d.Substring(6,2) }
  return $s
}
function CountryFolder([string]$c){
  if($c -eq 'PAK'){return '1. 파키스탄'}
  if($c -eq 'MNG'){return '2. 몽골'}
  return '3. 그 외 국가'
}
function SafeName([string]$s){ return ($s -replace '[\\/:*?"<>|]','').Trim() }

# ---------- HTML (OFFER LETTER 1페이지) ----------
function Build-Offer($rec){
  $issueEn = $rec.IssueEn
@"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:20mm 18mm; position:relative; }
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:10px; }
  .head .logo { width:66px; height:auto; flex:0 0 auto; align-self:center; }
  .head .org { flex:1; }
  .head .org .ko { font-size:15px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12.5px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:9.5px; color:#5a6b60; margin-top:4px; line-height:1.5; }

  .ol .frame { border:2px solid #1b6b3a; height:100%; padding:11mm 12mm 10mm; position:relative; }
  .ol .title { text-align:center; margin:26px 0 4px; }
  .ol .title .en { font-size:31px; font-weight:800; letter-spacing:10px; color:#12331f; }
  .ol .title .ko { font-size:14px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:4px; }
  .ol .fields { margin:16px 4px 0; }
  .ol .fields .row { display:flex; padding:12px 0; border-bottom:1px dotted #cdd9d0; }
  .ol .fields .row:last-child { border-bottom:none; }
  .ol .fields .lab { flex:0 0 40%; font-size:13px; font-weight:700; color:#20402b; }
  .ol .fields .lab .ko2 { display:block; font-size:10px; color:#8aa091; font-weight:600; margin-top:1px; }
  .ol .fields .val { flex:1; font-size:13.5px; color:#1c1c1c; align-self:center; }
  .ol .fields .val .ko2 { display:block; color:#6b7d70; font-size:11px; margin-top:2px; }
  .ol .fields .val .dur { display:block; font-size:11px; color:#7d8d80; margin-top:4px; }
  .ol .fields .val .dur .ko2 { display:inline; }
  .ol .certify { text-align:center; margin:40px 8px 0; }
  .ol .certify .ko { font-size:14.5px; color:#183a24; line-height:1.9; }
  .ol .certify .ko b { color:#1b6b3a; }
  .ol .certify .en { font-size:12px; color:#55685c; line-height:1.8; margin-top:8px; }
  .ol .foot { position:absolute; left:0; right:0; bottom:13mm; text-align:center; }
  .ol .foot .date2 { font-size:13.5px; color:#33463a; letter-spacing:1px; margin-bottom:18px; }
  .ol .foot .sign-ko { font-size:26px; font-weight:800; letter-spacing:6px; color:#12331f; display:inline-block; }
  .ol .foot .sign-en { font-size:15px; font-weight:700; color:#33463a; letter-spacing:1px; margin-top:16px; }
  .ol .sealwrap { position:relative; letter-spacing:0; }
  .ol .seal { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:57px; height:57px; object-fit:contain; opacity:0.92; }
  .ol .seal-ph { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:52px; height:52px; border:2px dashed #c46; border-radius:50%; color:#c46; font-size:9px; display:flex; align-items:center; justify-content:center; }
</style></head>
<body>

<div class='page ol'><div class='frame'>
  <div class='head'>
    $LogoTag
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>(61743) 전남광주통합특별시 남구 효덕로 277 · 277, Hyodeok-ro, Nam-gu, Gwangju, Rep. of Korea<br>
        Tel. +82-62-670-2288 &nbsp; Fax. +82-62-670-2733 &nbsp; E-mail. jhjung@gwangju.ac.kr &nbsp; ie.gwangju.ac.kr</div>
    </div>
  </div>
  <div class='title'><div class='en'>OFFER LETTER</div><div class='ko'>합 격 통 지 서</div></div>
  <div class='fields'>
    <div class='row'><div class='lab'>Name<span class='ko2'>성명</span></div>
      <div class='val'>$($rec.EnName) &nbsp;<span class='ko2'>($($rec.KoName))</span></div></div>
    <div class='row'><div class='lab'>Date of Birth<span class='ko2'>생년월일</span></div>
      <div class='val'>$($rec.Birth)</div></div>
    <div class='row'><div class='lab'>Passport No.<span class='ko2'>여권번호</span></div>
      <div class='val'>$($rec.Passport)</div></div>
    <div class='row'><div class='lab'>Nationality<span class='ko2'>국적</span></div>
      <div class='val'>$($rec.CountryEn) &nbsp;<span class='ko2'>($($rec.CountryKo))</span></div></div>
    <div class='row'><div class='lab'>Course<span class='ko2'>과정</span></div>
      <div class='val'>Korean Language Program &nbsp;<span class='ko2'>(한국어 어학연수 과정)</span>
        <span class='dur'>Duration : $($rec.Duration) &nbsp;<span class='ko2'>(수업연한 1년)</span></span></div></div>
    <div class='row'><div class='lab'>Admission Type<span class='ko2'>전형 · 구분</span></div>
      <div class='val'>Foreign Special Admission · Freshman &nbsp;<span class='ko2'>(외국인 특별전형 · 신입학)</span></div></div>
    <div class='row'><div class='lab'>Entrance Semester<span class='ko2'>입학학기</span></div>
      <div class='val'>September 2026 &nbsp;<span class='ko2'>(2026학년도 가을학기)</span></div></div>
  </div>
  <div class='certify'>
    <div class='ko'>위 사람은 <b>광주대학교 2026학년도 가을학기 한국어 어학연수 과정</b>에<br>합격하였음을 증명합니다.</div>
    <div class='en'>This is to certify that the above-mentioned person has been admitted<br>to the Korean Language Program at Gwangju University for the Fall Semester of 2026.</div>
  </div>
  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div></div>

</body></html>
"@
}

# ---------- 날짜 ----------
if($IssueDate -eq ''){ $dt = Get-Date } else { $dt = [datetime]::Parse($IssueDate) }
$issueEn = $dt.ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))

# ---------- 엑셀 ----------
Write-Host "엑셀 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($MainFile); $ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }

# 헤더 행 탐색 (성명(한글) 이 있는 행)
$hr = 0
for($r=1; $r -le 6; $r++){ if((CellTxt $r 1) -match '성명'){ $hr=$r; break } }
if($hr -eq 0){ $hr = 2 }

$rows = @()
for($r=$hr+1; $r -le $last; $r++){
  $ko = CellTxt $r 1
  if($ko -eq ''){ continue }
  if($Only -ne '' -and $ko -ne $Only){ continue }
  $code = CellTxt $r 3
  $rows += [pscustomobject]@{
    KoName=$ko; EnName=(CellTxt $r 2)
    CountryEn=(CtryEn $code); CountryKo=(CtryKo $code); Code=$code
    GenderKo=(CellTxt $r 4); GenderEn=(GenderEn (CellTxt $r 4))
    Birth=(NormBirth (CellTxt $r 5)); Passport=(CellTxt $r 6)
    Duration='Sep. 2026 – Aug. 2027'
    IssueEn=$issueEn; CountryFolder=(CountryFolder $code)
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Limit -gt 0){ $rows = @($rows | Select-Object -First $Limit) }
Write-Host ("어학연수 대상 {0}명" -f $rows.Count) -ForegroundColor Cyan
$rows | Group-Object CountryFolder | Sort-Object Name | ForEach-Object { Write-Host ("  {0} : {1}명" -f $_.Name, $_.Count) }

# ---------- PDF ----------
$tmp = Join-Path $env:TEMP ("gu_lang_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
if(-not (Test-Path $OutRoot)){ New-Item -ItemType Directory -Path $OutRoot -Force | Out-Null }
$i=0; $ok=0; $fail=0
foreach($s in $rows){
  $i++
  $html = Build-Offer $s
  $htmlPath = Join-Path $tmp ("$i.html")
  [System.IO.File]::WriteAllText($htmlPath, $html, $enc)
  $tmpPdf = Join-Path $tmp ("$i.pdf")
  $outDir = Join-Path $OutRoot $s.CountryFolder
  if(-not (Test-Path $outDir)){ New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
  $fname = (SafeName ("$($s.KoName)_$($s.EnName)")) + ".pdf"
  $pdfPath = Join-Path $outDir $fname
  $uri = ([System.Uri]$htmlPath).AbsoluteUri
  $eargs = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$tmpPdf"),$uri)
  Start-Process -FilePath $Edge -ArgumentList $eargs -Wait -WindowStyle Hidden
  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }
  if(Test-Path $pdfPath){ $ok++; Write-Host ("  [{0}/{1}] {2}\{3}" -f $i,$rows.Count,$s.CountryFolder,$fname) }
  else { $fail++; Write-Host ("  [{0}/{1}] 실패: {2}" -f $i,$rows.Count,$s.KoName) -ForegroundColor Red }
}
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ""
Write-Host ("완료! 성공 {0} / 실패 {1}  ->  {2}" -f $ok,$fail,$OutRoot) -ForegroundColor Green
