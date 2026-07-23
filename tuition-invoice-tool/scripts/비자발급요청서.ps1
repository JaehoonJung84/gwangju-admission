# =============================================================
#  광주대학교 유학생 사증(D-2) 발급 요청서 생성기 (영어트랙)
#  · 학생 1명당 2페이지 PDF (1p: 국문, 2p: 영문)
#  · 입력: ★2026-2학기 신편입생 장학금 작업_완성본.xlsx (트랙='영어'만)
#  실행: powershell -ExecutionPolicy Bypass -File 비자발급요청서.ps1 [-Only "한글명"] [-Limit N]
# =============================================================
param(
  [string]$MainFile = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\비자발급요청서(영어트랙)\★2026-2학기 신편입생 장학금 작업_완성본.xlsx",
  [string]$OutRoot  = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\비자발급요청서(영어트랙)\발행",
  [string]$SealImage = "",
  [string]$LogoImage = "",
  [string]$IssueDate = "",          # 미지정 시 오늘
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
$DEPTMAP = @{
  '컴퓨터공학과'='Department of Computer Engineering'; '경영학과'='Department of Business Administration';
  '무역유통학과'='Department of International Trade and Distribution'; '글로벌콘텐츠학부'='School of Global Contents';
  '뷰티미용학과'='Department of Beauty and Cosmetics'; '기계자동차공학부'='School of Mechanical and Automotive Engineering';
  '시각영상디자인학과'='Department of Visual Media Design'; '사회복지학부'='School of Social Welfare';
}
function DeptEn([string]$ko){ if($DEPTMAP.ContainsKey($ko)){ return $DEPTMAP[$ko] } else { return $ko } }

# 국가 -> (영문국가, 대사관도시_국문, 대사관도시_영문)
$EMB = @{
  '파키스탄'   = @('Pakistan','이슬라마바드','Islamabad, Pakistan');
  '몽골'       = @('Mongolia','울란바토르','Ulaanbaatar, Mongolia');
  '우즈베키스탄'= @('Uzbekistan','타슈켄트','Tashkent, Uzbekistan');
  '방글라데시' = @('Bangladesh','다카','Dhaka, Bangladesh');
  '베트남'     = @('Vietnam','하노이','Hanoi, Vietnam');
  '중국'       = @('China','베이징','Beijing, China');
  '키르기즈'   = @('Kyrgyzstan','비슈케크','Bishkek, Kyrgyzstan');
  '라오스'     = @('Laos','비엔티안','Vientiane, Laos');
}
function CtryEn([string]$ko){ if($EMB.ContainsKey($ko)){ return $EMB[$ko][0] } else { return $ko } }
function EmbKo([string]$ko){ if($EMB.ContainsKey($ko)){ return $EMB[$ko][1] } else { return $ko } }
function EmbEn([string]$ko){ if($EMB.ContainsKey($ko)){ return $EMB[$ko][2] } else { return $ko } }
function HonorKo([string]$s){ if($s -match '여|F'){return '님'}; return '님' }
function HonorEn([string]$s){ if($s -match '여|F'){return 'Ms.'}; return 'Mr.' }
function KRW($n){ if($null -eq $n){return '0'}; return ('{0:N0}' -f [double]$n) }
function SafeName([string]$s){ return ($s -replace '[\\/:*?"<>|]','').Trim() }

# ---------- HTML ----------
function Build-Letter($rec){
  $issKo = $rec.IssueKo
  $issEn = $rec.IssueEn
@"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:18mm 20mm; position:relative; }
  .p1 { page-break-after: always; }
  .frame { height:100%; position:relative; display:flex; flex-direction:column; }
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:10px; }
  .head .logo { width:64px; height:auto; flex:0 0 auto; }
  .head .org { flex:1; }
  .head .org .ko { font-size:15px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:9px; color:#5a6b60; margin-top:4px; line-height:1.5; }

  .doctitle { text-align:center; margin:20px 0 6px; }
  .doctitle .t { font-size:20px; font-weight:800; color:#12331f; letter-spacing:1px; }
  .doctitle .sub { font-size:11px; color:#7d947f; margin-top:3px; }

  .to { font-size:12px; color:#20402b; margin:10px 2px 2px; line-height:1.6; font-weight:700; }
  .salute { font-size:12px; margin:12px 2px 6px; }

  .body { font-size:11.7px; line-height:1.75; color:#222; margin:2px 2px; text-align:justify; }
  .body p { margin:9px 0; }

  table.info { width:100%; border-collapse:collapse; margin:12px 0; }
  table.info td { border:1px solid #cfe2d5; padding:6px 10px; font-size:11px; }
  table.info .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:26%; }

  .sec { font-size:11.5px; font-weight:800; color:#1b6b3a; margin:12px 2px 4px; }
  ul.pts { margin:4px 0 4px 18px; padding:0; font-size:11.3px; line-height:1.7; color:#333; }
  ul.pts li { margin:3px 0; }

  .foot { margin-top:auto; padding-top:14px; text-align:center; }
  .foot .date2 { font-size:12.5px; color:#33463a; margin-bottom:14px; }
  .foot .sign-ko { font-size:22px; font-weight:800; letter-spacing:5px; color:#12331f; display:inline-block; }
  .foot .sign-en { font-size:14px; font-weight:700; color:#33463a; margin-top:14px; }
  .sealwrap { position:relative; letter-spacing:0; }
  .seal { position:absolute; left:50%; top:44%; transform:translate(-50%,-50%); width:52px; height:52px; object-fit:contain; opacity:0.92; }
  .seal-ph { position:absolute; left:50%; top:44%; transform:translate(-50%,-50%); width:48px; height:48px; border:2px dashed #c46; border-radius:50%; color:#c46; font-size:8px; display:flex; align-items:center; justify-content:center; }
</style></head>
<body>

<!-- PAGE 1 : 국문 -->
<div class='page p1'><div class='frame'>
  <div class='head'>
    $LogoTag
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>(61743) 전남광주통합특별시 남구 효덕로 277 · Tel. +82-62-670-2288 · Fax. +82-62-670-2733 · jhjung@gwangju.ac.kr</div>
    </div>
  </div>

  <div class='doctitle'><div class='t'>유학생 사증(D-2) 발급 요청서</div></div>

  <div class='to'>주 $($rec.EmbKo) 대한민국 대사관 영사과 비자 담당자 귀하</div>
  <div class='salute'>존경하는 비자 담당자님께,</div>

  <div class='body'>
    <p>본 서한은 대한민국 광주대학교를 대표하여 <b>$($rec.KoName)</b> 학생의 본교 입학 및 등록 사실을 공식적으로 확인하고, 동 학생에 대한 유학생(D-2) 사증 발급허가 통지서(Visa Grant Notice) 발급을 정중히 요청드리고자 작성되었습니다.</p>
    <table class='info'>
      <tr><td class='k'>성명</td><td>$($rec.KoName) ($($rec.EnName))</td><td class='k'>생년월일</td><td>$($rec.Birth)</td></tr>
      <tr><td class='k'>국적</td><td>$($rec.CountryKo)</td><td class='k'>여권번호</td><td>$($rec.Passport)</td></tr>
      <tr><td class='k'>지원학과</td><td>$($rec.Dept)</td><td class='k'>학위과정</td><td style='white-space:nowrap'>학사(4년제) · 영어트랙</td></tr>
      <tr><td class='k'>입학학기</td><td colspan='3'>2026학년도 2학기(가을학기) · 정규 신입학</td></tr>
    </table>
    <p>위 학생은 본교의 서류 및 영어능력(IELTS $($rec.Ielts)) 심사를 거쳐 정규 학생으로 최종 합격하였으며, 등록 절차를 모두 완료하였습니다. 본 학생의 입국 목적은 광주대학교에서의 정규 학업 수행에 한정되며, 취업·체류 연장 등 비학업적 목적은 포함되어 있지 않음을 본교가 공식적으로 확인드립니다.</p>

    <div class='sec'>■ 장학 및 등록금 납부 확인</div>
    <ul class='pts'>
      <li>본 학생은 <b>영어능력 우수 장학금</b> 수혜자로 선정되어 등록금의 <b>$($rec.RatePct)%</b>($($rec.SchAmt)원)를 감면받았습니다.</li>
      <li>2026학년도 2학기 등록금은 총 $($rec.Tuition)원이며, 장학금 적용 후 학생 부담액 <b>$($rec.NetPay)원</b>은 전액 납부 완료되었습니다.</li>
    </ul>

    <p>상기 내용을 종합적으로 고려하시어 동 학생에 대한 유학생(D-2) 사증 발급을 긍정적으로 검토하여 주시기를 정중히 요청드립니다. 본교는 입국 이후에도 학생의 출결 및 체류 자격 준수 여부를 지속적으로 관리·감독할 것을 약속드립니다. 추가 확인이 필요하신 경우 본교 국제협력처로 언제든지 연락 주시기 바랍니다.</p>
  </div>

  <div class='foot'>
    <div class='date2'>$issKo</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div></div>

<!-- PAGE 2 : 영문 -->
<div class='page'><div class='frame'>
  <div class='head'>
    $LogoTag
    <div class='org'>
      <div class='ko'>광주대학교 국제협력처</div>
      <div class='en'>Office of International Affairs, Gwangju University</div>
      <div class='addr'>277, Hyodeok-ro, Nam-gu, Gwangju 61743, Rep. of Korea · Tel. +82-62-670-2288 · Fax. +82-62-670-2733 · jhjung@gwangju.ac.kr</div>
    </div>
  </div>

  <div class='doctitle'><div class='t'>Request for Issuance of Student Visa (D-2)</div></div>

  <div class='to'>Embassy of the Republic of Korea, $($rec.EmbEn)<br>Consular Section &ndash; Visa Officer</div>
  <div class='salute'>Dear Visa Officer,</div>

  <div class='body'>
    <p>On behalf of Gwangju University, Republic of Korea, we hereby officially confirm the admission and enrollment of <b>$($rec.EnName)</b> and respectfully request the issuance of a Student Visa (D-2) Grant Notice for the student.</p>
    <table class='info'>
      <tr><td class='k'>Name</td><td>$($rec.EnName) ($($rec.KoName))</td><td class='k'>Date of Birth</td><td>$($rec.Birth)</td></tr>
      <tr><td class='k'>Nationality</td><td>$($rec.CountryEn)</td><td class='k'>Passport No.</td><td>$($rec.Passport)</td></tr>
      <tr><td class='k'>Department</td><td>$($rec.DeptEn)</td><td class='k'>Program</td><td style='white-space:nowrap'>Bachelor's · English Track</td></tr>
      <tr><td class='k'>Admission</td><td colspan='3'>Fall Semester 2026 · Full-time Freshman</td></tr>
    </table>
    <p>$($rec.HonorEn) $($rec.EnName) has been officially admitted as a full-time undergraduate student following our review of academic documents and English proficiency (IELTS $($rec.Ielts)), and has completed all enrollment procedures. We officially confirm that the sole purpose of the student's entry into the Republic of Korea is to pursue full-time academic study at Gwangju University, with no intention of employment, extension of stay, or any other non-academic activity.</p>

    <div class='sec'>■ Scholarship &amp; Tuition Payment</div>
    <ul class='pts'>
      <li>The student was awarded the <b>English Proficiency Scholarship</b>, a <b>$($rec.RatePct)%</b> tuition reduction (KRW $($rec.SchAmt)).</li>
      <li>The total tuition for Fall 2026 is KRW $($rec.Tuition); after the scholarship, the student's balance of <b>KRW $($rec.NetPay)</b> has been paid in full.</li>
    </ul>

    <p>In consideration of the above, we respectfully request your favorable consideration for the issuance of a Student Visa (D-2). Gwangju University assures continued supervision of the student's attendance and compliance with visa regulations throughout the study period. Should you require any further verification, please do not hesitate to contact our Office of International Affairs.</p>
  </div>

  <div class='foot'>
    <div class='date2'>$issEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>
</div></div>

</body></html>
"@
}

# ---------- 날짜 ----------
if($IssueDate -eq ''){ $dt = Get-Date } else { $dt = [datetime]::Parse($IssueDate) }
$issueKo = $dt.ToString('yyyy년 M월 d일')
$issueEn = $dt.ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))

# ---------- 엑셀 ----------
Write-Host "엑셀 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($MainFile); $ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }
function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\d.-]',''; if($t -eq ''){return 0.0}; return [double]$t }

$rows = @()
for($r=2; $r -le $last; $r++){
  $trk = CellTxt $r 3
  if($trk -ne '영어'){ continue }
  $ko = CellTxt $r 5
  if($ko -eq ''){ continue }
  if($Only -ne '' -and $ko -ne $Only){ continue }
  $natKo = CellTxt $r 10; $dept = CellTxt $r 11
  $A = CellNum $r 14; $rate = CellNum $r 15; $B = CellNum $r 16; $C = CellNum $r 17
  $rows += [pscustomobject]@{
    KoName=$ko; EnName=(CellTxt $r 7); Birth=(CellTxt $r 8); GenderKo=(CellTxt $r 9)
    CountryKo=$natKo; CountryEn=(CtryEn $natKo); EmbKo=(EmbKo $natKo); EmbEn=(EmbEn $natKo)
    Dept=$dept; DeptEn=(DeptEn $dept); Ielts=(CellTxt $r 13)
    Tuition=(KRW $A); RatePct=[int]([math]::Round($(if($rate -le 1){$rate*100}else{$rate}))); SchAmt=(KRW $B); NetPay=(KRW $C)
    Passport='________________'   # 엑셀에 없음 → 추후 기입
    HonorKo=(HonorKo (CellTxt $r 9)); HonorEn=(HonorEn (CellTxt $r 9))
    IssueKo=$issueKo; IssueEn=$issueEn
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Limit -gt 0){ $rows = @($rows | Select-Object -First $Limit) }
Write-Host ("영어트랙 대상 {0}명" -f $rows.Count) -ForegroundColor Cyan

# ---------- PDF ----------
$tmp = Join-Path $env:TEMP ("gu_visa_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
if(-not (Test-Path $OutRoot)){ New-Item -ItemType Directory -Path $OutRoot -Force | Out-Null }
$i=0; $ok=0; $fail=0
foreach($s in $rows){
  $i++
  $html = Build-Letter $s
  $htmlPath = Join-Path $tmp ("$i.html")
  [System.IO.File]::WriteAllText($htmlPath, $html, $enc)
  $tmpPdf = Join-Path $tmp ("$i.pdf")
  $fname = (SafeName ("$($s.KoName)_$($s.EnName)")) + ".pdf"
  $pdfPath = Join-Path $OutRoot $fname
  $uri = ([System.Uri]$htmlPath).AbsoluteUri
  $eargs = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$tmpPdf"),$uri)
  Start-Process -FilePath $Edge -ArgumentList $eargs -Wait -WindowStyle Hidden
  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }
  if(Test-Path $pdfPath){ $ok++; Write-Host ("  [{0}/{1}] {2}" -f $i,$rows.Count,$fname) }
  else { $fail++; Write-Host ("  [{0}/{1}] 실패: {2}" -f $i,$rows.Count,$s.KoName) -ForegroundColor Red }
}
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ""
Write-Host ("완료! 성공 {0} / 실패 {1}  ->  {2}" -f $ok,$fail,$OutRoot) -ForegroundColor Green
