# =============================================================
#  외국인 유학생 교육비납입증명서 (CERTIFICATE OF TUITION PAYMENT) PDF 생성기
#  · 등록금고지서(INVOICE) 표 서식 기반 + 증명 문구/서명부는 증명서 고유
#  · 영문 우선 + 한글 병기 · 명의: 광주대학교 국제협력처장 (보유 직인 자동 적용)
#  · 학부/석사/박사 지원 · 배치 모드는 T열 "납부액 검증"=일치 만 생성
#  실행 예:
#   1건:   powershell -ExecutionPolicy Bypass -File 교육비납입증명서.ps1 -Name "..." ...
#   배치:  powershell -ExecutionPolicy Bypass -File 교육비납입증명서.ps1 `
#            -InputFile "C:\...\★2026-2학기 학부 및 대학원 신편입생 지원자 명단.xlsx"
#          (저장: OutDir\{국가}-{과정}\교육비납입증명서_{수험번호}_{영문명}.pdf)
# =============================================================
param(
  [string]$InputFile  = "",                        # 엑셀 지정 시 배치 모드
  [int]$Limit         = 0,                         # 배치: 0=전체, N=앞에서 N건
  [string]$OnlyFile   = "",                        # 지정 시 이 파일의 영문명만 발급(한 줄에 1명)
  [string]$Name       = "ERDENEBILEG KHALIUN",     # (단건) 성명(영문)
  [string]$KoName     = "에르데네빌렉 할리운",     # (단건) 성명(한글)
  [string]$Birth      = "2004-04-23",
  [string]$Gender     = "여",
  [string]$CountryKo  = "몽골",
  [string]$StudentNo  = "1510924",
  [string]$Gubun      = "신입학",
  [string]$Track      = "한국어",
  [string]$Course     = "학부",                    # 학부/석사/박사
  [string]$Dept       = "경영학과",
  [string]$PayDate    = "2026-08-25",
  [double]$Tuition    = 3167000,
  [double]$Scholarship= 1266800,
  [double]$Paid       = -1,                        # -1 = 자동계산 A-B
  [string]$IssueDate  = "",                        # 발급일 (미지정 시 오늘)
  [string]$OutDir     = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\교육비납입증명서\교육비납입증명서 2차",
  [string]$SealImage  = "",
  [string]$LogoImage  = ""
)

# 기본 자산 경로 (scripts\ 상위 폴더의 이미지)
$AssetDir = Split-Path $PSScriptRoot -Parent
if ($SealImage -eq '') { $p = Join-Path $AssetDir '국제협력처장직인.png'; if (Test-Path $p) { $SealImage = $p } }
if ($LogoImage -eq '') { $p = Join-Path $AssetDir '로고_국영문_full.png'; if (Test-Path $p) { $LogoImage = $p } }

$EdgePaths = @("$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe","${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe")
$Edge = $EdgePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Edge) { Write-Host "Microsoft Edge를 찾을 수 없습니다." -ForegroundColor Red; exit 1 }

# ---------- 매핑 ----------
# 학부 (인보이스 스크립트와 동일 + 사회복지학부)
$DEG_UG = @{
  '글로벌콘텐츠학부'='Bachelor of Global Contents'; '컴퓨터공학과'='Bachelor of Computer Engineering';
  '무역유통학과'='Bachelor of International Trade and Distribution'; '경영학과'='Bachelor of Business Administration';
  '뷰티미용학과'='Bachelor of Beauty and Cosmetics'; '기계자동차공학부'='Bachelor of Mechanical and Automotive Engineering';
  '시각영상디자인학과'='Bachelor of Visual Media Design'; '사회복지학부'='Bachelor of Social Welfare';
}
# 대학원 (대학원_배치생성 스크립트와 동일)
$DEPT_GR = @{
  '간호학과'='Nursing'; '법학과'='Law'; '컴퓨터공학과'='Computer Engineering';
  '뷰티미용학과'='Beauty and Cosmetics'; '회계세무학과'='Accounting and Taxation';
  '한국어교육과'='Korean Language Education'; '호텔관광경영학과'='Hotel and Tourism Management';
  '물류유통경영학과'='Logistics and Distribution Management'; '평생교육학과'='Lifelong Education';
  '한국어문화교육콘텐츠학과'='Korean Language, Culture Education and Contents';
  '전기전자공학과'='Electrical and Electronic Engineering';
}
function GrDeptEn([string]$ko){ if($DEPT_GR.ContainsKey($ko)){ return $DEPT_GR[$ko] } else { return $ko } }
function CourseEn([string]$proc,[string]$dept){
  if($proc -match '박사'){ return "Doctoral Program in " + (GrDeptEn $dept) }
  if($proc -match '석사'){ return "Master's Program in " + (GrDeptEn $dept) }
  if($DEG_UG.ContainsKey($dept)){ return $DEG_UG[$dept] } else { return $dept }
}
function CourseKoTxt([string]$proc,[string]$dept){
  if($proc -match '박사'){ return "$dept · 박사과정" }
  if($proc -match '석사'){ return "$dept · 석사과정" }
  return $dept
}
function SemKo([string]$proc){ if($proc -match '석사|박사'){ return '2026학년도 후기' } else { return '2026학년도 2학기' } }
$CTRY = @{ '베트남'='Vietnam';'중국'='China';'몽골'='Mongolia';'파키스탄'='Pakistan';'우즈베키스탄'='Uzbekistan';'라오스'='Laos';'방글라데시'='Bangladesh';'키르기즈'='Kyrgyzstan'; }
function CtryEn([string]$ko){ if($CTRY.ContainsKey($ko)){ return $CTRY[$ko] } else { return $ko } }
function GubunKoF([string]$g){ if($g -match '편입'){return '편입학'}; if($g -match '신입'){return '신입학'}; return $g }
function GubunEnF([string]$g){ if($g -match '편입'){return 'Transfer'}; return 'Freshman' }
function GenderEnF([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function GenderKoF([string]$s){ if($s -match '여|F'){return '여'}; if($s -match '남|M'){return '남'}; return $s }
function TrackKoF([string]$t){ switch -Regex ($t) { '영어'{'영어트랙'} '한국어'{'한국어트랙'} '중국어'{'중국어트랙'} default{if($t -eq ''){'-'}else{$t}} } }
function TrackEnF([string]$t){ switch -Regex ($t) { '영어'{'English Track'} '한국어'{'Korean Track'} '중국어'{'Chinese Track'} default{'-'} } }
function KRW($n){ if($null -eq $n){return '0 KRW'}; return ('{0:N0}' -f [double]$n) + ' KRW' }

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

# ---------- HTML 템플릿 ----------
function Build-Html($rec){
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
  .title { text-align:center; margin:16px 0 6px; }
  .title .en { font-size:25px; font-weight:800; letter-spacing:4px; color:#12331f; }
  .title .ko { font-size:13.5px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:3px; }
  .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:12px 2px 6px; }
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
  /* 인증 문구 (영문 먼저, 한글 다음) */
  .certify { text-align:center; margin:22px 8px 0; }
  .certify .en { font-size:13px; color:#183a24; line-height:1.9; }
  .certify .en b { color:#1b6b3a; }
  .certify .ko { font-size:11.5px; color:#55685c; line-height:1.8; margin-top:7px; }
  .note { margin-top:14px; font-size:10px; color:#8aa091; line-height:1.7; text-align:center; }
  .foot { margin-top:auto; padding-top:10px; text-align:center; }
  .foot .date2 { font-size:13.5px; color:#33463a; letter-spacing:1px; margin-bottom:16px; }
  .foot .sign-ko { font-size:24px; font-weight:800; letter-spacing:6px; color:#12331f; display:inline-block; }
  .foot .sign-en { font-size:14px; font-weight:700; color:#33463a; letter-spacing:1px; margin-top:14px; }
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
      <div class='addr'>(61743) 광주광역시 남구 효덕로 277 · 277, Hyodeok-ro, Nam-gu, Gwangju, Rep. of Korea<br>
        Tel. +82-62-670-2288 &nbsp; Fax. +82-62-670-2733 &nbsp; E-mail. jhjung@gwangju.ac.kr &nbsp; ie.gwangju.ac.kr</div>
    </div>
  </div>

  <div class='title'>
    <div class='en'>CERTIFICATE OF TUITION PAYMENT</div>
    <div class='ko'>교 육 비 납 입 증 명 서</div>
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
      <td>$($rec.Name)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.KoName)</span></td>
      <td>$($rec.Birth)</td>
      <td>$($rec.CountryEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CountryKo)</span></td>
      <td>$($rec.GenderEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GenderKo)</span></td>
      <td>$($rec.SemesterEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.SemesterKo)</span></td>
    </tr>
  </table>
  <table class='grid' style='margin-top:8px'>
    <tr>
      <th style='width:52%'>Course<span class='en2'>지원학과 · 학위과정</span></th>
      <th>Type<span class='en2'>구분</span></th>
      <th>Track<span class='en2'>과정(트랙)</span></th>
    </tr>
    <tr>
      <td>$($rec.CourseEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CourseKo)</span></td>
      <td>$($rec.GubunEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GubunKo)</span></td>
      <td>$($rec.TrackEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.TrackKo)</span></td>
    </tr>
  </table>

  <div class='sec'>■ Payment Details <span class='en2'>납부 내역</span></div>
  <table class='amt'>
    <tr><td class='k'>Date of Payment <span class='en2'>납부일자</span></td><td class='v'>$($rec.PayDate)</td></tr>
    <tr><td class='k'>Tuition (A) <span class='en2'>등록금</span></td><td class='v'>$(KRW $rec.Tuition)</td></tr>
    <tr><td class='k'>Scholarship (B) <span class='en2'>장학금</span></td><td class='v $(if([double]$rec.Scholarship -gt 0){'minus'})'>$(if([double]$rec.Scholarship -gt 0){'- ' + (KRW $rec.Scholarship)}else{'-'})</td></tr>
    <tr class='total'><td class='k'>Amount Paid (A - B) <span class='en2'>실 납부액</span></td><td class='v'>$(KRW $rec.Paid)</td></tr>
  </table>

  <div class='certify'>
    <div class='en'>This is to certify that the above-mentioned student has paid<br>the tuition fee to <b>Gwangju University</b> as stated above.</div>
    <div class='ko'>위 학생이 상기와 같이 본교에 교육비(등록금)를 납부하였음을 증명합니다.</div>
  </div>

  <div class='note'>
    ※ This certificate is issued for proof of tuition payment. &nbsp; 본 증명서는 교육비 납입 사실 확인용으로 발급되었습니다.<br>
    ※ Inquiries : Office of International Affairs, Gwangju University &nbsp; TEL. +82-62-670-2288
  </div>

  <div class='foot'>
    <div class='date2'>$($rec.IssueEn)</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>

</div></div></body></html>
"@
}

# ---------- 발급일 ----------
if($IssueDate -eq ''){ $d = Get-Date } else { $d = [datetime]$IssueDate }
$issueEn = $d.ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))

# ---------- 대상 목록 구성 ----------
$recs = @()
if($InputFile -ne ''){
  # ===== 배치 모드: T열 "납부액 검증" = 일치 만 =====
  Write-Host "엑셀에서 명단 읽는 중..." -ForegroundColor Cyan
  $xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
  $wb = $xl.Workbooks.Open($InputFile); $ws = $wb.Worksheets.Item(1)
  $last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
  function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }
  function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\d.]',''; $v=0.0; if([double]::TryParse($t,[ref]$v)){ return $v }; return 0.0 }
  $onlySet = @{}
  if($OnlyFile -ne ''){
    foreach($ln in (Get-Content -LiteralPath $OnlyFile -Encoding UTF8)){
      $k = ($ln.ToUpper() -replace '[^A-Z]','')
      if($k -ne ''){ $onlySet[$k] = $true }
    }
    Write-Host ("명단 필터: {0}명" -f $onlySet.Count) -ForegroundColor Cyan
  }
  for($r=2;$r -le $last;$r++){
    $verify = CellTxt $r 21              # U열 납부액 검증 (입학금 열 추가로 +1)
    if($verify -ne '일치'){ continue }
    $proc  = CellTxt $r 2                # B 과정(학부/석사/박사)
    $gubun = CellTxt $r 3                # C 구분(신입/편입)
    $trk   = CellTxt $r 4                # D 트랙
    $exno  = CellTxt $r 5                # E 수험번호
    $ko    = CellTxt $r 6                # F 한글명
    $en    = CellTxt $r 7                # G 영문명
    if($onlySet.Count -gt 0){
      $kk = ($en.ToUpper() -replace '[^A-Z]','')
      if(-not $onlySet.ContainsKey($kk)){ continue }
    }
    $birth = CellTxt $r 8                # H 생년월일
    $sex   = CellTxt $r 9                # I 성별
    $nat   = CellTxt $r 10               # J 국가명
    $dept  = CellTxt $r 11               # K 학부(과)
    $adm = CellNum $r 14                 # N 입학금
    $tui = CellNum $r 15                 # O 수업료
    $A = $adm + $tui                     # 등록금(A) = 입학금 + 수업료 (대학원은 입학금 포함)
    $B = CellNum $r 17                   # Q 장학금(B)
    $C = CellNum $r 18                   # R 실납부액(C)
    $S = CellNum $r 20                   # T 납부금액
    $payd  = CellTxt $r 19               # S 납부일자
    if($A -le 0){ $A = $C + $B }         # 금액 열이 비어 있으면 실납부액+장학금으로 보정
    if($C -le 0 -and $S -gt 0){ $C = $S }
    if([math]::Abs(($A - $B) - $C) -gt 0.5){
      Write-Host ("  경고: {0} {1} 금액 불일치 (A-B={2:N0}, C={3:N0}) → C 기준으로 생성" -f $exno,$en,($A-$B),$C) -ForegroundColor Yellow
    }
    $recs += [pscustomobject]@{
      Proc=$proc; StudentNo=$exno; Name=$en; KoName=$ko; Birth=$birth
      GenderEn=(GenderEnF $sex); GenderKo=(GenderKoF $sex)
      CountryKo=$nat; CountryEn=(CtryEn $nat)
      CourseEn=(CourseEn $proc $dept); CourseKo=(CourseKoTxt $proc $dept)
      GubunKo=(GubunKoF $gubun); GubunEn=(GubunEnF $gubun)
      TrackKo=(TrackKoF $trk); TrackEn=(TrackEnF $trk)
      SemesterEn='2026 Fall'; SemesterKo=(SemKo $proc); PayDate=$payd
      Tuition=$A; Scholarship=$B; Paid=$C
      IssueEn=$issueEn; SubDir=("{0}-{1}" -f $nat,$proc)
    }
  }
  $wb.Close($false); $xl.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()
  if($Limit -gt 0){ $recs = @($recs | Select-Object -First $Limit) }
}else{
  # ===== 단건 모드 =====
  if($Paid -lt 0){ $Paid = [double]$Tuition - [double]$Scholarship }
  $recs += [pscustomobject]@{
    Proc=$Course; StudentNo=$StudentNo; Name=$Name; KoName=$KoName; Birth=$Birth
    GenderEn=(GenderEnF $Gender); GenderKo=(GenderKoF $Gender)
    CountryKo=$CountryKo; CountryEn=(CtryEn $CountryKo)
    CourseEn=(CourseEn $Course $Dept); CourseKo=(CourseKoTxt $Course $Dept)
    GubunKo=(GubunKoF $Gubun); GubunEn=(GubunEnF $Gubun)
    TrackKo=(TrackKoF $Track); TrackEn=(TrackEnF $Track)
    SemesterEn='2026 Fall'; SemesterKo=(SemKo $Course); PayDate=$PayDate
    Tuition=$Tuition; Scholarship=$Scholarship; Paid=$Paid
    IssueEn=$issueEn; SubDir=''
  }
}

Write-Host ("대상: {0}건 (직인: {1})" -f $recs.Count, $(if($SealTag -match 'img'){'있음'}else{'없음-자리표시'})) -ForegroundColor Cyan

# ---------- PDF 생성 ----------
if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$tmp = Join-Path $env:TEMP ("gu_edu_" + [System.Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$enc = New-Object System.Text.UTF8Encoding($true)
$okCnt = 0; $failCnt = 0; $i = 0
foreach($s in $recs){
  $i++
  $html = Build-Html $s
  $htmlPath = Join-Path $tmp ("$($s.StudentNo).html")
  [System.IO.File]::WriteAllText($htmlPath, $html, $enc)
  $safeName = ($s.Name -replace '[\\/:*?"<>|]','_') -replace '\s+','_'
  if($safeName -eq ''){ $safeName = $s.StudentNo }
  $destDir = if($s.SubDir -ne ''){ Join-Path $OutDir $s.SubDir } else { $OutDir }
  if(-not (Test-Path $destDir)){ New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
  $pdfPath = Join-Path $destDir ("교육비납입증명서_$($s.StudentNo)_$safeName.pdf")
  $tmpPdf  = Join-Path $tmp ("$($s.StudentNo).pdf")   # 공백/한글 없는 임시 경로로 렌더 (Edge 인자 안전)
  $uri = ([System.Uri]$htmlPath).AbsoluteUri
  $args = @('--headless=new','--disable-gpu','--no-pdf-header-footer',"--user-data-dir=$tmp\ud",("--print-to-pdf=$tmpPdf"),$uri)
  Start-Process -FilePath $Edge -ArgumentList $args -Wait -WindowStyle Hidden
  $ok = $false
  if(Test-Path $tmpPdf){
    try {
      if(Test-Path $pdfPath){ Remove-Item $pdfPath -Force -ErrorAction Stop }   # 뷰어에 열려 있으면 여기서 실패
      Move-Item -Force $tmpPdf $pdfPath -ErrorAction Stop
      $ok = $true
    } catch {
      Write-Host ("  기존 PDF를 덮어쓸 수 없습니다(뷰어에 열려 있는지 확인): {0}" -f $pdfPath) -ForegroundColor Red
    }
  }
  if($ok){ $okCnt++; Write-Host ("  [{0}/{1}] {2}  {3}  → {4}" -f $i,$recs.Count,$s.StudentNo,$s.Name,$s.SubDir) }
  else   { $failCnt++; Write-Host ("  [{0}/{1}] 실패: {2}  {3}" -f $i,$recs.Count,$s.StudentNo,$s.Name) -ForegroundColor Red }
}
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
if($InputFile -ne ''){
  Write-Host "--- 폴더별 생성 건수 ---" -ForegroundColor Cyan
  $recs | Group-Object SubDir | Sort-Object Name | ForEach-Object { Write-Host ("  {0}: {1}건" -f $_.Name, $_.Count) }
}
Write-Host ("완료! 성공 {0}건 / 실패 {1}건  출력 폴더: {2}" -f $okCnt,$failCnt,$OutDir) -ForegroundColor Green
if($failCnt -gt 0){ exit 1 }
