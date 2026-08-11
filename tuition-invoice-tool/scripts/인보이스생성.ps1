# =============================================================
#  2026-2학기 외국인 신·편입생 INVOICE (등록금 고지서) PDF 생성기
#  · 예전 INVOICE 서식 기반 + 한글/영문 병기(bilingual)
#  · 명의: 광주대학교 국제협력처장 (보유 직인 자동 적용)
#  · 가상계좌(Payment Information)는 전산원 확정 후 -VirtualAcct 로 주입하거나
#    학생별 계좌 엑셀 열을 연결. 미지정 시 "추후 확정 / To be assigned" 표기.
#  실행 예:
#   전체:      powershell -ExecutionPolicy Bypass -File 인보이스생성.ps1
#   샘플 3장:  powershell -ExecutionPolicy Bypass -File 인보이스생성.ps1 -Limit 3
# =============================================================
param(
  [string]$InputFile = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\합격자 발표\전산입력\CLAUDE 작업\★2026-2학기 신편입생 장학금 작업_완성본.xlsx",
  [string]$OutDir    = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\합격자 발표\TUITION INVOICE",
  [string]$SealImage = "",
  [string]$LogoImage = "",
  [int]$AcctCol      = 0,           # 가상계좌번호 엑셀 열번호 (0 = 미지정→자리표시)
  [int]$Limit        = 0,
  [string]$Only         = "",   # 수험번호 또는 한글명 일부로 1명만 발급
  [string]$DeptOverride = "",   # -Only와 함께 사용: 학과를 엑셀 값 대신 지정값으로
  [string]$PayPeriodEn  = "July 20 – 24, 2026",      # 납부기간(영문)
  [string]$PayPeriodKo  = "2026. 7. 20. ~ 7. 24."     # 납부기간(국문)
)

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
$DEG = @{
  '글로벌콘텐츠학부'='Bachelor of Global Contents'; '컴퓨터공학과'='Bachelor of Computer Engineering';
  '무역유통학과'='Bachelor of International Trade and Distribution'; '경영학과'='Bachelor of Business Administration';
  '뷰티미용학과'='Bachelor of Beauty and Cosmetics'; '기계자동차공학부'='Bachelor of Mechanical and Automotive Engineering';
  '시각영상디자인학과'='Bachelor of Visual Media Design';
  '호텔외식조리학과'='Bachelor of Hotel Culinary Arts'; '스포츠과학부'='Bachelor of Sport Science';
  '회계세무학과'='Bachelor of Accounting and Taxation';
}
function DegEn([string]$ko){ if($DEG.ContainsKey($ko)){ return $DEG[$ko] } else { return $ko } }
$CTRY = @{ '베트남'='Vietnam';'중국'='China';'몽골'='Mongolia';'파키스탄'='Pakistan';'우즈베키스탄'='Uzbekistan';'라오스'='Laos';'방글라데시'='Bangladesh';'키르기즈'='Kyrgyzstan';'네팔'='Nepal';'키르기스스탄'='Kyrgyzstan'; }
function CtryEn([string]$ko){ if($CTRY.ContainsKey($ko)){ return $CTRY[$ko] } else { return $ko } }
function GubunKo([string]$g){ if($g -match '교환'){ if($g -match '1년'){return '교환학생(1년)'}; if($g -match '6개월'){return '교환학생(6개월)'}; return '교환학생' }; if($g -match '편입'){return '편입학'}; if($g -match '신입'){return '신입학'}; return $g }
function GubunEn([string]$g){ if($g -match '교환'){return 'Exchange Student'}; if($g -match '편입'){return 'Transfer'}; return 'Freshman' }
function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function TrackKo([string]$t){ switch -Regex ($t) { '영어'{'영어트랙'} '한국어'{'한국어트랙'} '중국어'{'중국어트랙'} default{if($t -eq ''){'-'}else{$t}} } }
function TrackEn([string]$t){ switch -Regex ($t) { '영어'{'English Track'} '한국어'{'Korean Track'} '중국어'{'Chinese Track'} default{'-'} } }
function KRW($n){ if($null -eq $n){return '0 KRW'}; return ('{0:N0}' -f [double]$n) + ' KRW' }

# ---------- HTML 템플릿 ----------
function Build-Html($rec){
  $issueEn = (Get-Date).ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
@"
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
  .date b { color:#1b6b3a; }
  .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:11px 2px 6px; }
  .sec .en2 { color:#8aa091; font-weight:700; font-size:11px; }
  table { width:100%; border-collapse:collapse; }
  .grid td, .grid th { border:1px solid #cfe2d5; padding:6px 8px; font-size:12px; text-align:center; }
  .grid th { background:#eaf4ec; color:#2c5a3c; font-weight:700; }
  .grid th .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .amt td { padding:8px 12px; font-size:13px; border:1px solid #cfe2d5; }
  .amt .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:42%; text-align:left; }
  .amt .k .en2 { color:#8aa091; font-size:10px; font-weight:600; }
  .amt .v { text-align:right; font-variant-numeric:tabular-nums; }
  .amt .minus { color:#b03a3a; }
  .amt .total .k, .amt .total .v { border-top:2px solid #1b6b3a; font-weight:800; font-size:15px; color:#12331f; }
  .amt .total .v { color:#1b6b3a; }
  .pay td { padding:7px 11px; font-size:12px; border:1px solid #cfe2d5; }
  .pay .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:28%; text-align:left; }
  .pay .k .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .pay .todo { color:#b06a1a; font-weight:700; }
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
    <div class='en'>TUITION INVOICE</div>
    <div class='ko'>등 록 금 고 지 서</div>
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
      <td>$($rec.EnName)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.KoName)</span></td>
      <td>$($rec.Birth)</td>
      <td>$($rec.CountryEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CountryKo)</span></td>
      <td>$($rec.GenderEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GenderKo)</span></td>
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
      <td>$($rec.DegEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.Dept)</span></td>
      <td>$($rec.GubunEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GubunKo)</span></td>
      <td>$($rec.TrackEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.TrackKo)</span></td>
    </tr>
  </table>

  <div class='sec'>■ Amount Due <span class='en2'>납부 내역</span></div>
  <table class='amt'>
    <tr><td class='k'>Tuition (A) <span class='en2'>등록금</span></td><td class='v'>$($rec.ATxt)</td></tr>
    <tr><td class='k'>Scholarship (B)$($rec.RateTxt) <span class='en2'>장학금</span></td><td class='v minus'>- $($rec.BTxt)</td></tr>
    <tr class='total'><td class='k'>Amount Due (A - B) <span class='en2'>실 납부액</span></td><td class='v'>$($rec.CTxt)</td></tr>
  </table>

  <div class='sec'>■ Payment Information <span class='en2'>납부 정보</span></div>
  <table class='pay'>
    <tr><td class='k'>Bank <span class='en2'>은행</span></td><td>Kwangju Bank 광주은행 &nbsp;(Swift. KWABKRSE)</td></tr>
    <tr><td class='k'>Bank Address <span class='en2'>은행 주소</span></td><td>Jinwol-dong branch of Kwangju bank, 665, Seomun-daero, Nam-gu, Gwangju, Republic of Korea</td></tr>
    <tr><td class='k'>Remittee <span class='en2'>예금주</span></td><td>Gwangju University (Office of International Affairs)<br>광주대학교(국제협력처)</td></tr>
    <tr><td class='k'>Account No. <span class='en2'>계좌번호</span></td><td class='todo'>$($rec.Acct)</td></tr>
    <tr><td class='k'>Payment Period <span class='en2'>납부기간</span></td><td>$PayPeriodEn &nbsp;<span style='color:#6b7d70'>($PayPeriodKo)</span></td></tr>
  </table>

  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>

</div></div></body></html>
"@
}

# ---------- 데이터 읽기 ----------
Write-Host "엑셀에서 명단 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($InputFile); $ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }
function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\d.-]',''; if($t -eq ''){return 0.0}; return [double]$t }
$rows = @()
for($r=2;$r -le $last;$r++){
  $exno = CellTxt $r 4
  $ko   = CellTxt $r 5
  if($exno -eq '' -and $ko -eq ''){ continue }
  $g = CellTxt $r 2; $dept = CellTxt $r 10; $natKo = CellTxt $r 9; $trk = CellTxt $r 3
  $A = CellNum $r 13; $B = CellNum $r 15; $C = CellNum $r 16
  $rate = CellTxt $r 14
  $rows += [pscustomobject]@{
    ExNo=$exno; KoName=$ko; EnName=(CellTxt $r 6); Birth=(CellTxt $r 7)
    GenderEn=(GenderEn (CellTxt $r 8)); GenderKo=(CellTxt $r 8); CountryKo=$natKo; CountryEn=(CtryEn $natKo)
    Dept=$dept; DegEn=(DegEn $dept); GubunKo=(GubunKo $g); GubunEn=(GubunEn $g)
    TrackKo=(TrackKo $trk); TrackEn=(TrackEn $trk)
    ATxt=(KRW $A); BTxt=(KRW $B); CTxt=(KRW $C)
    RateTxt=$(if($rate -ne ''){" · $rate"}else{''})
    Acct=$(if($AcctCol -gt 0){ $av=(CellTxt $r $AcctCol); if($av -ne ''){$av}else{'추후 확정 · To be assigned'} }else{'추후 확정 · To be assigned'})
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Only -ne ''){ $rows = @($rows | Where-Object { $_.ExNo -eq $Only -or $_.KoName -match [regex]::Escape($Only) }) }
if($DeptOverride -ne ''){ foreach($x in $rows){ $x.Dept = $DeptOverride; $x.DegEn = (DegEn $DeptOverride) } }
if($Limit -gt 0){ $rows = @($rows | Select-Object -First $Limit) }
Write-Host ("대상: {0}명 (직인: {1})" -f $rows.Count, $(if($SealTag -match 'img'){'있음'}else{'없음-자리표시'})) -ForegroundColor Cyan

# ---------- PDF 생성 ----------
if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$tmp = Join-Path $env:TEMP ("gu_inv_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
$i=0
foreach($s in $rows){
  $i++
  $html = Build-Html $s
  $htmlPath = Join-Path $tmp ("$($s.ExNo).html")
  [System.IO.File]::WriteAllText($htmlPath, $html, $enc)
  $safeName = ($s.EnName -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
  if($safeName -eq ''){ $safeName = $s.ExNo }
  $pdfPath = Join-Path $OutDir ("TUITION INVOICE_$($s.ExNo)_$safeName.pdf")
  $tmpPdf  = Join-Path $tmp ("$($s.ExNo).pdf")
  $uri = ([System.Uri]$htmlPath).AbsoluteUri
  $args = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$tmpPdf"),$uri)
  Start-Process -FilePath $Edge -ArgumentList $args -Wait -WindowStyle Hidden
  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }
  if(Test-Path $pdfPath){ Write-Host ("  [{0}/{1}] {2}  {3}" -f $i,$rows.Count,$s.ExNo,$s.EnName) }
  else { Write-Host ("  [{0}/{1}] 실패: {2}" -f $i,$rows.Count,$s.ExNo) -ForegroundColor Red }
}
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ""
Write-Host ("완료! 출력 폴더: {0}" -f $OutDir) -ForegroundColor Green
