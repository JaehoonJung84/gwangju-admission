# =============================================================
#  외국인 유학생 장학금 수혜 증명서 (CERTIFICATE OF SCHOLARSHIP AWARD) PDF 생성기
#  · 교육비납입증명서.ps1 의 서식·서명부를 그대로 쓰고 본문(장학 내역)만 교체
#  · 영문 우선 + 한글 병기 · 명의: 광주대학교 국제협력처장 (보유 직인 자동 적용)
#  실행 예:
#   powershell -File 장학금수혜증명서.ps1 -Name "TUNGALAG NASANTOGTOKH" -KoName "통가락 나상턱터흐" ...
# =============================================================
param(
  [string]$Name       = "TUNGALAG NASANTOGTOKH",   # 성명(영문)
  [string]$KoName     = "통가락 나상턱터흐",       # 성명(한글)
  [string]$Birth      = "2002-10-17",
  [string]$Gender     = "남",
  [string]$CountryKo  = "몽골",
  [string]$StudentNo  = "20266285",                # 학번
  [string]$Gubun      = "신입",
  [string]$Track      = "한국어",
  [string]$Course     = "학부",                    # 학부/석사/박사
  [string]$Dept       = "컴퓨터공학과",
  [double]$Tuition    = 3744000,
  [double]$Rate       = 100,                       # 장학비율(%)
  [double]$Scholarship= 3744000,
  [double]$Paid       = -1,                        # -1 = 자동계산 A-B
  [string]$Basis      = "TOPIK Level 4",           # 장학 선발 근거
  [string]$BasisKo    = "공식 TOPIK 4급",
  [string]$IssueDate  = "",                        # 발급일 (미지정 시 오늘)
  [string]$OutDir     = "C:\Users\user\Desktop\통가락",
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

# ---------- 매핑 (교육비납입증명서.ps1 과 동일) ----------
$DEG_UG = @{
  '글로벌콘텐츠학부'='Bachelor of Global Contents'; '컴퓨터공학과'='Bachelor of Computer Engineering';
  '무역유통학과'='Bachelor of International Trade and Distribution'; '경영학과'='Bachelor of Business Administration';
  '뷰티미용학과'='Bachelor of Beauty and Cosmetics'; '기계자동차공학부'='Bachelor of Mechanical and Automotive Engineering';
  '기계자동차공학과'='Bachelor of Mechanical and Automotive Engineering';
  '시각영상디자인학과'='Bachelor of Visual Media Design'; '사회복지학부'='Bachelor of Social Welfare';
}
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
function PCT($n){ return ('{0:0.##}' -f [double]$n) + '%' }

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
  .title { text-align:center; margin:14px 0 4px; }
  .title .en { font-size:19px; font-weight:800; letter-spacing:2px; color:#12331f; }
  .title .ko { font-size:13.5px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:3px; }
  .sec { font-size:13px; font-weight:800; color:#1b6b3a; margin:10px 2px 5px; }
  .sec .en2 { color:#8aa091; font-weight:700; font-size:11px; }
  table { width:100%; border-collapse:collapse; }
  .grid td, .grid th { border:1px solid #cfe2d5; padding:6px 8px; font-size:12px; text-align:center; }
  .grid th { background:#eaf4ec; color:#2c5a3c; font-weight:700; }
  .grid th .en2 { display:block; color:#8aa091; font-size:9.5px; font-weight:600; margin-top:1px; }
  .amt td { padding:5px 12px; font-size:12.5px; border:1px solid #cfe2d5; }
  .amt .k { background:#eaf4ec; color:#2c5a3c; font-weight:700; width:42%; text-align:left; }
  .amt .k .en2 { color:#8aa091; font-size:10px; font-weight:600; }
  .amt .v { text-align:right; font-variant-numeric:tabular-nums; }
  .amt .plus { color:#1b6b3a; font-weight:700; }
  .amt .total .k, .amt .total .v { border-top:2px solid #1b6b3a; font-weight:800; font-size:15px; color:#12331f; }
  .amt .total .v { color:#1b6b3a; }
  /* 인증 문구 (영문 먼저, 한글 다음) */
  .certify { text-align:center; margin:14px 8px 0; }
  .certify .en { font-size:13px; color:#183a24; line-height:1.9; }
  .certify .en b { color:#1b6b3a; }
  .certify .ko { font-size:11.5px; color:#55685c; line-height:1.8; margin-top:7px; }
  .note { margin-top:10px; font-size:10px; color:#8aa091; line-height:1.7; text-align:center; }
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
    <div class='en'>CERTIFICATE OF SCHOLARSHIP AWARD</div>
    <div class='ko'>장 학 금 수 혜 증 명 서</div>
  </div>

  <div class='sec'>■ Student's Information <span class='en2'>학생 정보</span></div>
  <table class='grid'>
    <tr>
      <th>Name<span class='en2'>성명</span></th>
      <th>Student ID No.<span class='en2'>학번</span></th>
      <th>Date of Birth<span class='en2'>생년월일</span></th>
      <th>Nationality<span class='en2'>국적</span></th>
      <th>Gender<span class='en2'>성별</span></th>
    </tr>
    <tr>
      <td>$($rec.Name)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.KoName)</span></td>
      <td>$($rec.StudentNo)</td>
      <td>$($rec.Birth)</td>
      <td>$($rec.CountryEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CountryKo)</span></td>
      <td>$($rec.GenderEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GenderKo)</span></td>
    </tr>
  </table>
  <table class='grid' style='margin-top:8px'>
    <tr>
      <th style='width:40%'>Course<span class='en2'>학과 · 학위과정</span></th>
      <th>Type<span class='en2'>구분</span></th>
      <th>Track<span class='en2'>과정(트랙)</span></th>
      <th>Semester<span class='en2'>학기</span></th>
    </tr>
    <tr>
      <td>$($rec.CourseEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.CourseKo)</span></td>
      <td>$($rec.GubunEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GubunKo)</span></td>
      <td>$($rec.TrackEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.TrackKo)</span></td>
      <td>$($rec.SemesterEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.SemesterKo)</span></td>
    </tr>
  </table>

  <div class='sec'>■ Scholarship Details <span class='en2'>장학 내역</span></div>
  <table class='amt'>
    <tr><td class='k'>Name of Scholarship <span class='en2'>장학금 명칭</span></td><td class='v'>Korean Language Proficiency Scholarship<br><span style='color:#6b7d70;font-size:10.5px'>한국어능력 우수 장학</span></td></tr>
    <tr><td class='k'>Basis of Award <span class='en2'>선발 근거</span></td><td class='v'>$($rec.Basis)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.BasisKo)</span></td></tr>
    <tr><td class='k'>Tuition Fee (A) <span class='en2'>등록금</span></td><td class='v'>$(KRW $rec.Tuition)</td></tr>
    <tr><td class='k'>Scholarship Rate <span class='en2'>장학 비율</span></td><td class='v'>$(PCT $rec.Rate)</td></tr>
    <tr class='total'><td class='k'>Scholarship Awarded (B) <span class='en2'>장학금 수혜액</span></td><td class='v'>$(KRW $rec.Scholarship)</td></tr>
    <tr><td class='k'>Amount Borne by Student (A - B) <span class='en2'>학생 실부담액</span></td><td class='v'>$(KRW $rec.Paid)</td></tr>
  </table>

  <div class='certify'>
    <div class='en'>This is to certify that the above-mentioned student has been awarded<br>the scholarship stated above by <b>Gwangju University</b> for the $($rec.SemesterEn).</div>
    <div class='ko'>위 학생이 $($rec.SemesterKo)에 상기와 같이 본교의 장학금을 수혜하였음을 증명합니다.</div>
  </div>

  <div class='note'>
    ※ This certificate is issued for proof of scholarship award. &nbsp; 본 증명서는 장학금 수혜 사실 확인용으로 발급되었습니다.<br>
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

if($Paid -lt 0){ $Paid = $Tuition - $Scholarship }

$rec = @{
  Name = $Name; KoName = $KoName; StudentNo = $StudentNo; Birth = $Birth
  CountryEn = (CtryEn $CountryKo); CountryKo = $CountryKo
  GenderEn = (GenderEnF $Gender); GenderKo = (GenderKoF $Gender)
  CourseEn = (CourseEn $Course $Dept); CourseKo = (CourseKoTxt $Course $Dept)
  GubunEn = (GubunEnF $Gubun); GubunKo = (GubunKoF $Gubun)
  TrackEn = (TrackEnF $Track); TrackKo = (TrackKoF $Track)
  SemesterEn = '2026 Fall Semester'; SemesterKo = (SemKo $Course)
  Tuition = $Tuition; Rate = $Rate; Scholarship = $Scholarship; Paid = $Paid
  Basis = $Basis; BasisKo = $BasisKo; IssueEn = $issueEn
}

if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$safe = ($KoName + '_' + $Name) -replace '[\\/:*?"<>|]','_'
$html = Join-Path $env:TEMP ("scholar_" + [guid]::NewGuid().ToString('N') + ".html")
$pdf  = Join-Path $OutDir ("장학금수혜증명서_" + $safe + ".pdf")

[IO.File]::WriteAllText($html, (Build-Html $rec), (New-Object Text.UTF8Encoding $false))
& $Edge --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" "file:///$($html -replace '\\','/')" 2>$null | Out-Null
Start-Sleep -Milliseconds 400
Remove-Item $html -Force -ErrorAction SilentlyContinue

if(Test-Path $pdf){
  Write-Host ("생성 완료: " + $pdf + "  (" + (Get-Item $pdf).Length + " bytes)") -ForegroundColor Green
} else {
  Write-Host "PDF 생성 실패" -ForegroundColor Red
}
