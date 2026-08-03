# =============================================================
#  생활관(기숙사)·보험료 INVOICE PDF 생성기 (1인 발급용)
#  · 2026-2학기 TUITION INVOICE 서식(한/영 병기) 기반, 항목만 생활관·보험으로 교체
#  · 계좌: 광주은행 1127-020-156948 (2026-1학기 기숙사 INVOICE와 동일)
#  실행 예:
#   powershell -ExecutionPolicy Bypass -File 생활관보험_인보이스.ps1
# =============================================================
param(
  [string]$EnName   = "DAWOOD MUHAMMAD",
  [string]$KoName   = "다우드 무함마드",
  [string]$Birth    = "2007-03-19",
  [string]$GenderKo = "남",
  [string]$CountryKo= "파키스탄",
  [string]$CountryEn= "Pakistan",
  [string]$Dept     = "컴퓨터공학과",
  [string]$DegEn    = "Bachelor of Computer Engineering",
  [string]$GubunKo  = "신입학",
  [string]$GubunEn  = "Freshman",
  [string]$TrackKo  = "영어트랙",
  [string]$TrackEn  = "English Track",
  [double]$DormAmt  = 889000,
  [double]$InsAmt   = 200000,
  [string]$Acct     = "1127-020-156948",
  [string]$OutDir   = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\생활관·보험 INVOICE",
  [string]$SealImage = "",
  [string]$LogoImage = ""
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

function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function KRW($n){ return ('{0:N0}' -f [double]$n) + ' KRW' }

$GenderEnV = GenderEn $GenderKo
$TotalAmt  = $DormAmt + $InsAmt
$DormTxt   = KRW $DormAmt
$InsTxt    = KRW $InsAmt
$TotalTxt  = KRW $TotalAmt
$issueEn   = (Get-Date).ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))

$html = @"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:20mm 18mm; position:relative; }
  .frame { border:2px solid #1b6b3a; height:100%; padding:11mm 12mm 10mm; position:relative; display:flex; flex-direction:column; }
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:10px; }
  .head .logo { width:66px; height:auto; flex:0 0 auto; align-self:center; }
  .head .org .ko { font-size:15px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12.5px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:9.5px; color:#5a6b60; margin-top:4px; line-height:1.5; }
  .title { text-align:center; margin:14px 0 4px; }
  .title .en { font-size:30px; font-weight:800; letter-spacing:10px; color:#12331f; }
  .title .ko { font-size:13.5px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:3px; }
  .date { text-align:right; font-size:12px; color:#33463a; margin:12px 2px 16px; }
  .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:11px 2px 6px; }
  .sec .en2 { color:#8aa091; font-weight:700; font-size:11px; }
  table { width:100%; border-collapse:collapse; }
  .grid td, .grid th { border:1px solid #cfe2d5; padding:6px 8px; font-size:12px; text-align:center; }
  .grid th { background:#eaf4ec; color:#2c5a3c; font-weight:700; }
  .grid th .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .amt td { padding:8px 12px; font-size:13px; border:1px solid #cfe2d5; }
  .amt .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:48%; text-align:left; }
  .amt .k .en2 { display:block; color:#8aa091; font-size:10px; font-weight:600; margin-top:1px; }
  .amt .v { text-align:right; font-variant-numeric:tabular-nums; }
  .amt .total .k, .amt .total .v { border-top:2px solid #1b6b3a; font-weight:800; font-size:15px; color:#12331f; }
  .amt .total .v { color:#1b6b3a; }
  .pay td { padding:7px 11px; font-size:12px; border:1px solid #cfe2d5; }
  .pay .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:28%; text-align:left; }
  .pay .k .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .note { margin-top:14px; font-size:10.5px; color:#7d8d80; line-height:1.7; }
  .foot { margin-top:auto; padding-top:10px; text-align:center; }
  .foot .date2 { font-size:13.5px; color:#33463a; letter-spacing:1px; margin-bottom:18px; }
  .foot .sign-ko { font-size:26px; font-weight:800; letter-spacing:6px; color:#12331f; display:inline-block; }
  .foot .sign-en { font-size:15px; font-weight:700; color:#33463a; letter-spacing:1px; margin-top:16px; }
  .sealwrap { position:relative; letter-spacing:0; }
  .seal { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:57px; height:57px; object-fit:contain; opacity:0.92; }
  .seal-ph { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:52px; height:52px; border:2px dashed #c46; border-radius:50%; color:#c46; font-size:9px; display:flex; align-items:center; justify-content:center; }
</style></head>
<body><div class='page'><div class='frame'>

  <div class='head'>
    $LogoTag
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>(61743) 전남광주통합특별시 남구 효덕로 277 · 277, Hyodeok-ro, Nam-gu, Gwangju, Rep. of Korea<br>
        Tel. +82-62-670-2288 &nbsp; Fax. +82-62-670-2733 &nbsp; E-mail. jhjung@gwangju.ac.kr &nbsp; ie.gwangju.ac.kr</div>
    </div>
  </div>

  <div class='title'>
    <div class='en'>INVOICE</div>
    <div class='ko'>생활관비 · 보험료 고지서</div>
  </div>

  <div class='sec'>■ Applicant's Information <span class='en2'>지원자 정보</span></div>
  <table class='grid'>
    <tr>
      <th>Name<span class='en2'>성명</span></th>
      <th>Date of Birth<span class='en2'>생년월일</span></th>
      <th>Nationality<span class='en2'>국적</span></th>
      <th>Gender<span class='en2'>성별</span></th>
      <th>Semester<span class='en2'>입학학기</span></th>
    </tr>
    <tr>
      <td>$EnName<br><span style='color:#6b7d70;font-size:10.5px'>$KoName</span></td>
      <td>$Birth</td>
      <td>$CountryEn<br><span style='color:#6b7d70;font-size:10.5px'>$CountryKo</span></td>
      <td>$GenderEnV<br><span style='color:#6b7d70;font-size:10.5px'>$GenderKo</span></td>
      <td>2026 Fall<br><span style='color:#6b7d70;font-size:10.5px'>2026학년도 2학기</span></td>
    </tr>
  </table>
  <table class='grid' style='margin-top:8px'>
    <tr>
      <th style='width:52%'>Course<span class='en2'>지원학과 · 학위과정</span></th>
      <th>Type<span class='en2'>구분</span></th>
      <th>Track<span class='en2'>과정(트랙)</span></th>
    </tr>
    <tr>
      <td>$DegEn<br><span style='color:#6b7d70;font-size:10.5px'>$Dept</span></td>
      <td>$GubunEn<br><span style='color:#6b7d70;font-size:10.5px'>$GubunKo</span></td>
      <td>$TrackEn<br><span style='color:#6b7d70;font-size:10.5px'>$TrackKo</span></td>
    </tr>
  </table>

  <div class='sec'>■ Amount Due <span class='en2'>납부 내역</span></div>
  <table class='amt'>
    <tr><td class='k'>Dormitory - Fall Semester, 4-person Room <span class='en2'>생활관비(가을학기 · 4인실)</span></td><td class='v'>$DormTxt</td></tr>
    <tr><td class='k'>Health Insurance - 1 Year <span class='en2'>건강보험료(1년)</span></td><td class='v'>$InsTxt</td></tr>
    <tr class='total'><td class='k'>Total Amount Due <span class='en2'>합계</span></td><td class='v'>$TotalTxt</td></tr>
  </table>

  <div class='sec'>■ Payment Information <span class='en2'>납부 정보</span></div>
  <table class='pay'>
    <tr><td class='k'>Bank <span class='en2'>은행</span></td><td>Kwangju Bank 광주은행 &nbsp;(Swift. KWABKRSE)</td></tr>
    <tr><td class='k'>Bank Address <span class='en2'>은행 주소</span></td><td>Jinwol-dong branch of Kwangju bank, 665, Seomun-daero, Nam-gu, Gwangju, Republic of Korea</td></tr>
    <tr><td class='k'>Remittee <span class='en2'>예금주</span></td><td>Gwangju University (Office of International Affairs)<br>광주대학교(국제협력처)</td></tr>
    <tr><td class='k'>Account No. <span class='en2'>계좌번호</span></td><td>$Acct</td></tr>
  </table>

  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>

</div></div></body></html>
"@

if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$tmp = Join-Path $env:TEMP ("gu_dorminv_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
$htmlPath = Join-Path $tmp "inv.html"
[System.IO.File]::WriteAllText($htmlPath, $html, $enc)
$safeName = ($EnName -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
$pdfPath = Join-Path $OutDir ("INVOICE_DORM_INSURANCE_$safeName.pdf")
$tmpPdf  = Join-Path $tmp "inv.pdf"
$uri = ([System.Uri]$htmlPath).AbsoluteUri
$args2 = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$tmpPdf"),$uri)
Start-Process -FilePath $Edge -ArgumentList $args2 -Wait -WindowStyle Hidden
if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
if(Test-Path $pdfPath){ Write-Host ("완료: {0}" -f $pdfPath) -ForegroundColor Green }
else { Write-Host "PDF 생성 실패" -ForegroundColor Red; exit 1 }
