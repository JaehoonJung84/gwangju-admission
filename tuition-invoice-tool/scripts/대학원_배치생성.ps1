# =============================================================
#  2026학년도 후기 대학원 신입생 배치 생성기
#  · 학생 1명당 2페이지 PDF (1p: OFFER LETTER, 2p: TUITION INVOICE)
#  · 저장: <OutRoot>\{1. 중국|2. 베트남|3. 우즈베키스탄|4. 그 외 국가}\한글명_영문명.pdf
#  · 입력: 지원자 현황 엑셀  (시트1 현황 / 시트2 장학등록금 / 시트3 가상계좌)
#  · 가상계좌: 생년월일(YYMMDD) 기준 매칭, 실패 시 이름 매칭
#  실행: powershell -ExecutionPolicy Bypass -File 대학원_배치생성.ps1 [-Limit N]
# =============================================================
param(
  [string]$MainFile = "C:\Users\user\Desktop\★국제협력처\2. 대학원\2026학년도 후기\합격통지서 등록금고지서\2026학년도 후기 대학원 지원자 현황_정리본.xlsx",
  [string]$OutRoot  = "C:\Users\user\Desktop\★국제협력처\2. 대학원\2026학년도 후기\합격통지서 등록금고지서",
  [string]$SealImage = "",
  [string]$LogoImage = "",
  [int]$Limit        = 0,
  [string]$Only      = ""    # 특정 학생 한글명만 생성 (샘플 확인용)
)

# 불합격자 (발급 제외)
$EXCLUDE = @('정몽정','응웬반밍','서욱')

$AssetDir = Split-Path $PSScriptRoot -Parent
if ($SealImage -eq '') { $p = Join-Path $AssetDir '국제협력처장직인.png'; if (Test-Path $p) { $SealImage = $p } }
if ($LogoImage -eq '') { $p = Join-Path $AssetDir '로고_국영문_full.png'; if (Test-Path $p) { $LogoImage = $p } }

$EdgePaths = @("$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe","${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe")
$Edge = $EdgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Edge) { Write-Host "Microsoft Edge를 찾을 수 없습니다." -ForegroundColor Red; exit 1 }

# ---------- 이미지 -> data URI ----------
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
$DEPTMAP = @{
  '간호학과'='Nursing'; '법학과'='Law'; '컴퓨터공학과'='Computer Engineering';
  '뷰티미용학과'='Beauty and Cosmetics'; '회계세무학과'='Accounting and Taxation';
  '한국어교육과'='Korean Language Education'; '호텔관광경영학과'='Hotel and Tourism Management';
  '물류유통경영학과'='Logistics and Distribution Management'; '평생교육학과'='Lifelong Education';
  '한국어문화교육콘텐츠학과'='Korean Language, Culture Education and Contents';
  '전기전자공학과'='Electrical and Electronic Engineering';
}
function DeptEn([string]$ko){ if($DEPTMAP.ContainsKey($ko)){ return $DEPTMAP[$ko] } else { return $ko } }
function CourseEn([string]$deg,[string]$dept){
  $d = DeptEn $dept
  if($deg -match '박사'){ return "Doctoral Program in $d" } else { return "Master's Program in $d" }
}
function DegKo([string]$deg){ if($deg -match '박사'){ return '박사과정' } else { return '석사과정' } }

$CTRY = @{ '베트남'='Vietnam';'중국'='China';'몽골'='Mongolia';'우즈베키스탄'='Uzbekistan';'라오스'='Laos';'파키스탄'='Pakistan';'방글라데시'='Bangladesh';'키르기즈'='Kyrgyzstan'; }
function CtryEn([string]$ko){ if($CTRY.ContainsKey($ko)){ return $CTRY[$ko] } else { return $ko } }
function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function TrackKo([string]$t){ switch -Regex ($t) { '영어'{'영어트랙'} '한국어'{'한국어트랙'} '중국어'{'중국어트랙'} default{if($t -eq ''){'-'}else{$t}} } }
function TrackEn([string]$t){ switch -Regex ($t) { '영어'{'English Track'} '한국어'{'Korean Track'} '중국어'{'Chinese Track'} default{'-'} } }

# 수업연한: 모두 2년 / 단 석사 법학과만 1년
function Duration([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return 'Sep. 2026 – Aug. 2027' }
  return 'Sep. 2026 – Aug. 2028'
}
function DurationYr([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return '1년' }
  return '2년'
}
function KRW($n){ if($null -eq $n){return '0 KRW'}; return ('{0:N0}' -f [double]$n) + ' KRW' }
function CountryFolder([string]$ko){
  if($ko -match '중국'){return '1. 중국'}
  if($ko -match '베트남'){return '2. 베트남'}
  if($ko -match '우즈벡|우즈베키스탄'){return '3. 우즈베키스탄'}
  return '4. 그 외 국가'
}
function SafeName([string]$s){ return ($s -replace '[\\/:*?"<>|]','').Trim() }
# 생년월일 -> YYMMDD 6자리 키
function BirthKey([string]$s){
  $d = ($s -replace '[^\d]','')
  if($d.Length -ge 8){ return $d.Substring(2,6) }
  if($d.Length -gt 0){ return $d.PadLeft(6,'0') }
  return ''
}

# ---------- 결합(2페이지) HTML ----------
function Build-Combined($rec){
  $issueEn = (Get-Date).ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
@"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:20mm 18mm; position:relative; }
  .p1 { page-break-after: always; }
  /* 공통 레터헤드 */
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:10px; }
  .head .logo { width:66px; height:auto; flex:0 0 auto; align-self:center; }
  .head .org { flex:1; }
  .head .org .ko { font-size:15px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12.5px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:9.5px; color:#5a6b60; margin-top:4px; line-height:1.5; }

  /* ===== OFFER LETTER (.ol) ===== */
  .ol .frame { border:2px solid #1b6b3a; height:100%; padding:11mm 12mm 10mm; position:relative; }
  .ol .title { text-align:center; margin:26px 0 4px; }
  .ol .title .en { font-size:31px; font-weight:800; letter-spacing:10px; color:#12331f; }
  .ol .title .ko { font-size:14px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:4px; }
  .ol .fields { margin:8px 4px 0; }
  .ol .fields .row { display:flex; padding:11px 0; border-bottom:1px dotted #cdd9d0; }
  .ol .fields .row:last-child { border-bottom:none; }
  .ol .fields .lab { flex:0 0 40%; font-size:13px; font-weight:700; color:#20402b; }
  .ol .fields .lab .ko2 { display:block; font-size:10px; color:#8aa091; font-weight:600; margin-top:1px; }
  .ol .fields .val { flex:1; font-size:13.5px; color:#1c1c1c; align-self:center; }
  .ol .fields .val .ko2 { display:block; color:#6b7d70; font-size:11px; margin-top:2px; }
  .ol .fields .val .dur { display:block; font-size:11px; color:#7d8d80; margin-top:4px; }
  .ol .fields .val .dur .ko2 { display:inline; }
  .ol .certify { text-align:center; margin:34px 8px 0; }
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

  /* ===== TUITION INVOICE (.inv) ===== */
  .inv .frame { border:2px solid #1b6b3a; height:100%; padding:11mm 12mm 10mm; position:relative; display:flex; flex-direction:column; }
  .inv .title { text-align:center; margin:4px 0 2px; }
  .inv .title .en { font-size:30px; font-weight:800; letter-spacing:10px; color:#12331f; }
  .inv .title .ko { font-size:13.5px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:3px; }
  .inv .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:7px 2px 4px; }
  .inv .sec .en2 { color:#8aa091; font-weight:700; font-size:11px; }
  .inv table { width:100%; border-collapse:collapse; }
  .inv .grid td, .inv .grid th { border:1px solid #cfe2d5; padding:5px 8px; font-size:12px; text-align:center; }
  .inv .grid th { background:#eaf4ec; color:#2c5a3c; font-weight:700; }
  .inv .grid th .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .inv .amt td { padding:5px 12px; font-size:13px; border:1px solid #cfe2d5; }
  .inv .amt .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:50%; text-align:left; white-space:nowrap; }
  .inv .amt .k .en2 { color:#8aa091; font-size:10px; font-weight:600; }
  .inv .amt .v { text-align:right; font-variant-numeric:tabular-nums; }
  .inv .amt .minus { color:#b03a3a; }
  .inv .amt .total .k, .inv .amt .total .v { border-top:2px solid #1b6b3a; font-weight:800; font-size:15px; color:#12331f; }
  .inv .amt .total .v { color:#1b6b3a; }
  .inv .pay td { padding:5px 11px; font-size:12px; border:1px solid #cfe2d5; }
  .inv .pay .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:28%; text-align:left; }
  .inv .pay .k .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .inv .pay .todo { color:#b06a1a; font-weight:700; }
  .inv .foot { margin-top:auto; padding-top:8px; text-align:center; }
  .inv .foot .date2 { font-size:13.5px; color:#33463a; letter-spacing:1px; margin-bottom:14px; }
  .inv .foot .sign-ko { font-size:26px; font-weight:800; letter-spacing:6px; color:#12331f; display:inline-block; }
  .inv .foot .sign-en { font-size:15px; font-weight:700; color:#33463a; letter-spacing:1px; margin-top:16px; }
  .inv .sealwrap { position:relative; letter-spacing:0; }
  .inv .seal { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:57px; height:57px; object-fit:contain; opacity:0.92; }
  .inv .seal-ph { position:absolute; left:52%; top:46%; transform:translate(-50%,-50%); width:52px; height:52px; border:2px dashed #c46; border-radius:50%; color:#c46; font-size:9px; display:flex; align-items:center; justify-content:center; }
</style></head>
<body>

<!-- PAGE 1 : OFFER LETTER -->
<div class='page p1 ol'><div class='frame'>
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
    <div class='row'><div class='lab'>Nationality<span class='ko2'>국적</span></div>
      <div class='val'>$($rec.CountryEn) &nbsp;<span class='ko2'>($($rec.CountryKo))</span></div></div>
    <div class='row'><div class='lab'>Course<span class='ko2'>지원학과 · 학위과정</span></div>
      <div class='val'>$($rec.CourseEn) &nbsp;<span class='ko2'>($($rec.Dept) · $($rec.DegKo))</span>
        <span class='dur'>Duration : $($rec.Duration) &nbsp;<span class='ko2'>(수업연한 $($rec.DurationYr))</span></span></div></div>
    <div class='row'><div class='lab'>Admission Type<span class='ko2'>전형 · 구분</span></div>
      <div class='val'>Foreign Special Admission · Freshman &nbsp;<span class='ko2'>(외국인 특별전형 · 신입학)</span></div></div>
    <div class='row'><div class='lab'>Track<span class='ko2'>과정 (트랙)</span></div>
      <div class='val'>$($rec.TrackEn) &nbsp;<span class='ko2'>($($rec.TrackKo))</span></div></div>
    <div class='row'><div class='lab'>Entrance Semester<span class='ko2'>입학학기</span></div>
      <div class='val'>September 2026 &nbsp;<span class='ko2'>(2026학년도 후기)</span></div></div>
  </div>
  <div class='certify'>
    <div class='ko'>위 사람은 <b>광주대학교 2026학년도 후기 외국인 특별전형</b>에<br>합격하였음을 증명합니다.</div>
    <div class='en'>This is to certify that the above-mentioned person has been admitted<br>to Gwangju University for the Fall Semester of 2026.</div>
  </div>
  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div></div>

<!-- PAGE 2 : TUITION INVOICE -->
<div class='page inv'><div class='frame'>
  <div class='head'>
    $LogoTag
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>(61743) 전남광주통합특별시 남구 효덕로 277 · 277, Hyodeok-ro, Nam-gu, Gwangju, Rep. of Korea<br>
        Tel. +82-62-670-2288 &nbsp; Fax. +82-62-670-2733 &nbsp; E-mail. jhjung@gwangju.ac.kr &nbsp; ie.gwangju.ac.kr</div>
    </div>
  </div>
  <div class='title'><div class='en'>TUITION INVOICE</div><div class='ko'>등 록 금 고 지 서</div></div>

  <div class='sec'>■ Applicant's Information <span class='en2'>지원자 정보</span></div>
  <table class='grid'>
    <tr><th>Name<span class='en2'>성명</span></th><th>Date of Birth<span class='en2'>생년월일</span></th><th>Nationality<span class='en2'>국적</span></th><th>Gender<span class='en2'>성별</span></th><th>Semester<span class='en2'>입학학기</span></th></tr>
    <tr>
      <td>$($rec.EnName)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.KoName)</span></td>
      <td>$($rec.Birth)</td>
      <td>$($rec.CountryEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CountryKo)</span></td>
      <td>$($rec.GenderEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GenderKo)</span></td>
      <td style='white-space:nowrap'>2026 Fall<br><span style='color:#6b7d70;font-size:10.5px'>2026학년도 후기</span></td>
    </tr>
  </table>
  <table class='grid' style='margin-top:8px'>
    <tr><th style='width:52%'>Course<span class='en2'>지원학과 · 학위과정</span></th><th>Type<span class='en2'>구분</span></th><th>Track<span class='en2'>과정(트랙)</span></th></tr>
    <tr>
      <td>$($rec.CourseEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.Dept) · $($rec.DegKo)</span></td>
      <td>Freshman<br><span style='color:#6b7d70;font-size:10.5px'>신입학</span></td>
      <td>$($rec.TrackEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.TrackKo)</span></td>
    </tr>
  </table>

  <div class='sec'>■ Amount Due <span class='en2'>납부 내역</span></div>
  <table class='amt'>
    <tr><td class='k'>Admission Fee (A) <span class='en2'>입학금</span></td><td class='v'>$($rec.ATxt)</td></tr>
    <tr><td class='k'>Tuition (B) <span class='en2'>수업료</span></td><td class='v'>$($rec.BTxt)</td></tr>
    <tr><td class='k'>Scholarship (C)$($rec.RateTxt) <span class='en2'>장학금</span></td><td class='v minus'>- $($rec.CTxt)</td></tr>
    <tr class='total'><td class='k'>Amount Due (A+B-C) <span class='en2'>실 납부액</span></td><td class='v'>$($rec.DTxt)</td></tr>
  </table>

  <div class='sec'>■ Payment Information <span class='en2'>납부 정보</span></div>
  <table class='pay'>
    <tr><td class='k'>Bank <span class='en2'>은행</span></td><td>Kwangju Bank 광주은행 &nbsp;(Swift. KWABKRSE)</td></tr>
    <tr><td class='k'>Bank Address <span class='en2'>은행 주소</span></td><td>Jinwol-dong branch of Kwangju bank, 665, Seomun-daero, Nam-gu, Gwangju, Republic of Korea</td></tr>
    <tr><td class='k'>Remittee <span class='en2'>예금주</span></td><td>Gwangju University (Office of International Affairs)<br>광주대학교(국제협력처)</td></tr>
    <tr><td class='k'>Account No. <span class='en2'>계좌번호</span></td><td class='todo'>$($rec.Acct)</td></tr>
    <tr><td class='k'>Payment Period <span class='en2'>납부기간</span></td><td>July 22 – 24, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 7. 22. ~ 7. 24.)</span></td></tr>
  </table>

  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div></div>

</body></html>
"@
}

# ---------- 엑셀 읽기 ----------
Write-Host "엑셀 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($MainFile)

# 시트3 가상계좌: 생년월일(YYMMDD) / 이름 -> 계좌
$wsA = $wb.Worksheets.Item(3)
$lastA = $wsA.UsedRange.Row + $wsA.UsedRange.Rows.Count - 1
$AcctByBirth = @{}; $AcctByName = @{}; $ExNoByBirth = @{}
for($r=2; $r -le $lastA; $r++){
  $nm = ([string]$wsA.Cells.Item($r,7).Text).Trim()
  $bd = ([string]$wsA.Cells.Item($r,8).Text).Trim()
  $ac = ([string]$wsA.Cells.Item($r,9).Text).Trim()
  $ex = ([string]$wsA.Cells.Item($r,6).Text).Trim()
  if($ac -eq ''){ continue }
  $bk = BirthKey $bd
  if($bk -ne ''){ $AcctByBirth[$bk] = $ac; $ExNoByBirth[$bk] = $ex }
  if($nm -ne ''){ $AcctByName[$nm] = $ac }
}
Write-Host ("  가상계좌 {0}건" -f $AcctByBirth.Count) -ForegroundColor Cyan

# 시트1 현황
$ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }
function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\d.-]',''; if($t -eq ''){return 0.0}; return [double]$t }

$rows = @(); $skipped = @()
for($r=3; $r -le $last; $r++){
  $ko = CellTxt $r 3
  if($ko -eq ''){ continue }
  if($EXCLUDE -contains $ko){ $skipped += $ko; continue }
  if($Only -ne '' -and $ko -ne $Only){ continue }

  $deg = CellTxt $r 2; $dept = CellTxt $r 11; $natKo = CellTxt $r 14; $trk = CellTxt $r 12
  $birth = CellTxt $r 16; $topik = CellTxt $r 13
  $A = CellNum $r 7; $B = CellNum $r 8; $C = CellNum $r 9; $D = CellNum $r 10
  if($A -eq 0 -and $B -eq 0){ $skipped += "$ko (금액 없음)"; continue }

  $bk = BirthKey $birth
  $acct = ''
  if($AcctByBirth.ContainsKey($bk)){ $acct = $AcctByBirth[$bk] }
  elseif($AcctByName.ContainsKey($ko)){ $acct = $AcctByName[$ko] }
  else { $acct = '추후 확정 · To be assigned' }
  $exno = if($ExNoByBirth.ContainsKey($bk)){ $ExNoByBirth[$bk] } else { '' }

  # 장학률 = 장학금 / 수업료 (학부 양식과 동일하게 "0%" 형식)
  $pct = if($B -gt 0){ [math]::Round(($C / $B) * 100, 1) } else { 0 }
  $rateTxt = " · $pct%"

  $rows += [pscustomobject]@{
    ExNo=$exno; KoName=$ko; EnName=(CellTxt $r 4); Birth=$birth
    GenderKo=(CellTxt $r 15); GenderEn=(GenderEn (CellTxt $r 15))
    CountryKo=$natKo; CountryEn=(CtryEn $natKo)
    Dept=$dept; DegKo=(DegKo $deg); CourseEn=(CourseEn $deg $dept)
    TrackKo=(TrackKo $trk); TrackEn=(TrackEn $trk)
    Duration=(Duration $deg $dept); DurationYr=(DurationYr $deg $dept)
    ATxt=(KRW $A); BTxt=(KRW $B); CTxt=(KRW $C); DTxt=(KRW $D); RateTxt=$rateTxt
    Acct=$acct; HasAcct=($acct -notmatch '추후')
    CountryFolder=(CountryFolder $natKo)
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Limit -gt 0){ $rows = @($rows | Select-Object -First $Limit) }
Write-Host ("대상 {0}명 / 제외 {1}명 ({2})" -f $rows.Count, $skipped.Count, ($skipped -join ', ')) -ForegroundColor Cyan
$noAcct = @($rows | Where-Object { -not $_.HasAcct })
if($noAcct.Count -gt 0){ $noAcct | ForEach-Object { Write-Host ("  [계좌누락] {0} {1}" -f $_.KoName,$_.EnName) -ForegroundColor Yellow } }
$rows | Group-Object CountryFolder | Sort-Object Name | ForEach-Object { Write-Host ("  {0} : {1}명" -f $_.Name, $_.Count) }

# ---------- PDF 생성 ----------
$tmp = Join-Path $env:TEMP ("gu_grad_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
$i=0; $ok=0; $fail=0
foreach($s in $rows){
  $i++
  $html = Build-Combined $s
  $key = (SafeName $s.KoName)
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
Write-Host ("완료! 성공 {0} / 실패 {1}  →  {2}" -f $ok,$fail,$OutRoot) -ForegroundColor Green
