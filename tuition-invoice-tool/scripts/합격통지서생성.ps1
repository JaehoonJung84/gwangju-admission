# =============================================================
#  2026-2학기 외국인 신·편입생 OFFER LETTER (합격통지서) PDF 생성기
#  · 예전 OFFER LETTER 서식 기반 + 한글/영문 병기(bilingual)
#  · 명의: 광주대학교 국제협력처장 (보유 직인 자동 적용)
#  실행 예:
#   전체:      powershell -ExecutionPolicy Bypass -File 합격통지서생성.ps1
#   샘플 3장:  powershell -ExecutionPolicy Bypass -File 합격통지서생성.ps1 -Limit 3
# =============================================================
param(
  [string]$InputFile = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\합격자 발표\전산입력\CLAUDE 작업\★2026-2학기 신편입생 장학금 작업_완성본.xlsx",
  [string]$OutDir    = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\합격자 발표\OFFER LETTER",
  [string]$SealImage = "",
  [string]$LogoImage = "",
  [int]$Limit        = 0,
  [string]$Only         = "",   # 수험번호 또는 한글명 일부로 1명만 발급
  [string]$DeptOverride = ""    # -Only와 함께 사용: 학과를 엑셀 값 대신 지정값으로
)

# 기본 자산 경로 (scripts\ 상위 폴더의 이미지)
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

# ---------- 매핑: 학과 -> 영문 학위명 ----------
$DEG = @{
  '글로벌콘텐츠학부'   = 'Bachelor of Global Contents';
  '컴퓨터공학과'       = 'Bachelor of Computer Engineering';
  '무역유통학과'       = 'Bachelor of International Trade and Distribution';
  '경영학과'           = 'Bachelor of Business Administration';
  '뷰티미용학과'       = 'Bachelor of Beauty and Cosmetics';
  '기계자동차공학부'   = 'Bachelor of Mechanical and Automotive Engineering';
  '시각영상디자인학과' = 'Bachelor of Visual Media Design';
  '호텔외식조리학과' = 'Bachelor of Hotel Culinary Arts'; '스포츠과학부' = 'Bachelor of Sport Science';
  '회계세무학과' = 'Bachelor of Accounting and Taxation';
}
function DegEn([string]$ko){ if($DEG.ContainsKey($ko)){ return $DEG[$ko] } else { return $ko } }

# ---------- 매핑: 국가 -> 영문 ----------
$CTRY = @{
  '베트남'='Vietnam'; '중국'='China'; '몽골'='Mongolia'; '파키스탄'='Pakistan';
  '우즈베키스탄'='Uzbekistan'; '라오스'='Laos'; '방글라데시'='Bangladesh'; '키르기즈'='Kyrgyzstan';
  '네팔'='Nepal'; '키르기스스탄'='Kyrgyzstan';
}
function CtryEn([string]$ko){ if($CTRY.ContainsKey($ko)){ return $CTRY[$ko] } else { return $ko } }

# ---------- 라벨 매핑 ----------
function GubunLabel([string]$g){ if($g -match '교환'){ if($g -match '1년'){return '교환학생(1년)'}; if($g -match '6개월'){return '교환학생(6개월)'}; return '교환학생' }; if($g -match '편입'){return '편입학'}; if($g -match '신입'){return '신입학'}; return $g }
function GubunEn([string]$g){ if($g -match '교환'){return 'Exchange Student'}; if($g -match '편입'){return 'Transfer'}; return 'Freshman' }
function TrackKo([string]$t){ switch -Regex ($t) { '영어'{'영어트랙'} '한국어'{'한국어트랙'} '중국어'{'중국어트랙'} default{if($t -eq ''){'-'}else{$t}} } }
function TrackEn([string]$t){ switch -Regex ($t) { '영어'{'English Track'} '한국어'{'Korean Track'} '중국어'{'Chinese Track'} default{'-'} } }
# 수업연한: 신입=4년, 편입(3학년)=2년 (2026학년도 2학기 = 2026.9 입학)
function Duration([string]$g){ if($g -match '교환'){ if($g -match '1년'){ return 'Sep. 2026 – Aug. 2027' } else { return 'Sep. 2026 – Feb. 2027' } }; if($g -match '편입'){ return 'Sep. 2026 – Aug. 2028' } else { return 'Sep. 2026 – Aug. 2030' } }

# ---------- HTML 템플릿 ----------
function Build-Html($rec){
  $issueKo = (Get-Date).ToString('yyyy. M. d.')
  $issueEn = (Get-Date).ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
@"
<!doctype html><html lang='ko'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; color:#1c1c1c; }
  .page { width:210mm; height:297mm; padding:20mm 18mm; position:relative; }
  .frame { border:2px solid #1b6b3a; height:100%; padding:11mm 12mm 10mm; position:relative; }
  /* 상단 레터헤드 */
  .head { display:flex; align-items:center; gap:14px; border-bottom:2px solid #1b6b3a; padding-bottom:10px; }
  .head .logo { width:66px; height:auto; flex:0 0 auto; align-self:center; }
  .head .org { flex:1; }
  .head .org .ko { font-size:15px; font-weight:800; color:#1b6b3a; letter-spacing:0.5px; }
  .head .org .en { font-size:12.5px; font-weight:700; color:#20402b; margin-top:1px; }
  .head .org .addr { font-size:9.5px; color:#5a6b60; margin-top:4px; line-height:1.5; }
  /* 제목 */
  .title { text-align:center; margin:26px 0 4px; }
  .title .en { font-size:31px; font-weight:800; letter-spacing:10px; color:#12331f; }
  .title .ko { font-size:14px; font-weight:700; letter-spacing:8px; color:#7d947f; margin-top:4px; }
  /* 정보 필드 (영문 우선·큰글씨 / 한글 보조·작은글씨) */
  .fields { margin:8px 4px 0; }
  .fields .row { display:flex; padding:11px 0; border-bottom:1px dotted #cdd9d0; }
  .fields .row:last-child { border-bottom:none; }
  .fields .lab { flex:0 0 40%; font-size:13px; font-weight:700; color:#20402b; }
  .fields .lab .ko2 { display:block; font-size:10px; color:#8aa091; font-weight:600; margin-top:1px; }
  .fields .val { flex:1; font-size:13.5px; color:#1c1c1c; align-self:center; }
  .fields .val .ko2 { display:block; color:#6b7d70; font-size:11px; margin-top:2px; }
  .fields .val .dur { display:block; font-size:11px; color:#7d8d80; margin-top:4px; }
  .fields .val .dur .ko2 { display:inline; }
  /* 인증 문구 */
  .certify { text-align:center; margin:34px 8px 0; }
  .certify .ko { font-size:14.5px; color:#183a24; line-height:1.9; }
  .certify .ko b { color:#1b6b3a; }
  .certify .en { font-size:12px; color:#55685c; line-height:1.8; margin-top:8px; }
  /* 서명 */
  .foot { position:absolute; left:0; right:0; bottom:13mm; text-align:center; }
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
    <div class='en'>OFFER LETTER</div>
    <div class='ko'>합 격 통 지 서</div>
  </div>

  <div class='fields'>
    <div class='row'><div class='lab'>Name<span class='ko2'>성명</span></div>
      <div class='val'>$($rec.EnName) &nbsp;<span class='ko2'>($($rec.KoName))</span></div></div>
    <div class='row'><div class='lab'>Date of Birth<span class='ko2'>생년월일</span></div>
      <div class='val'>$($rec.Birth)</div></div>
    <div class='row'><div class='lab'>Nationality<span class='ko2'>국적</span></div>
      <div class='val'>$($rec.CountryEn) &nbsp;<span class='ko2'>($($rec.CountryKo))</span></div></div>
    <div class='row'><div class='lab'>Course<span class='ko2'>지원학과 · 학위과정</span></div>
      <div class='val'>$($rec.DegEn) &nbsp;<span class='ko2'>($($rec.Dept))</span>
        <span class='dur'>Duration : $($rec.Duration) &nbsp;<span class='ko2'>(수업연한)</span></span></div></div>
    <div class='row'><div class='lab'>Admission Type<span class='ko2'>전형 · 구분</span></div>
      <div class='val'>Foreign Special Admission · $($rec.GubunEn) &nbsp;<span class='ko2'>(외국인 특별전형 · $($rec.GubunKo))</span></div></div>
    <div class='row'><div class='lab'>Track<span class='ko2'>과정 (트랙)</span></div>
      <div class='val'>$($rec.TrackEn) &nbsp;<span class='ko2'>($($rec.TrackKo))</span></div></div>
    <div class='row'><div class='lab'>Entrance Semester<span class='ko2'>입학학기</span></div>
      <div class='val'>September 2026 &nbsp;<span class='ko2'>(2026학년도 2학기)</span></div></div>
  </div>

  <div class='certify'>
    <div class='ko'>위 사람은 <b>광주대학교 2026학년도 2학기 외국인 특별전형</b>에<br>합격하였음을 증명합니다.</div>
    <div class='en'>This is to certify that the above-mentioned person has been admitted<br>to Gwangju University for the Fall Semester of 2026.</div>
  </div>

  <div class='foot'>
    <div class='date2'>$issueEn</div>
    <div class='sign-ko'>광주대학교 국제협력처<span class='sealwrap'>장$SealTag</span></div>
    <div class='sign-en'>Director of International Affairs, Gwangju University</div>
  </div>

</div></div></body></html>
"@
}

# ---------- 데이터 읽기 ----------
Write-Host "엑셀에서 합격자 명단 읽는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application; $xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($InputFile); $ws = $wb.Worksheets.Item(1)
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1
function CellTxt($r,$c){ return ([string]$ws.Cells.Item($r,$c).Text).Trim() }
$rows = @()
for($r=2;$r -le $last;$r++){
  $exno = CellTxt $r 4
  $ko   = CellTxt $r 5
  if($exno -eq '' -and $ko -eq ''){ continue }
  $g = CellTxt $r 2
  $dept = CellTxt $r 10
  $natKo = CellTxt $r 9
  $trk  = CellTxt $r 3
  $rows += [pscustomobject]@{
    ExNo=$exno; KoName=$ko; EnName=(CellTxt $r 6); Birth=(CellTxt $r 7)
    CountryKo=$natKo; CountryEn=(CtryEn $natKo)
    Dept=$dept; DegEn=(DegEn $dept)
    GubunKo=(GubunLabel $g); GubunEn=(GubunEn $g); Duration=(Duration $g)
    TrackKo=(TrackKo $trk); TrackEn=(TrackEn $trk)
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null; [GC]::Collect(); [GC]::WaitForPendingFinalizers()

if($Only -ne ''){ $rows = @($rows | Where-Object { $_.ExNo -eq $Only -or $_.KoName -match [regex]::Escape($Only) }) }
if($DeptOverride -ne ''){ foreach($x in $rows){ $x.Dept = $DeptOverride; $x.DegEn = (DegEn $DeptOverride) } }
if($Limit -gt 0){ $rows = @($rows | Select-Object -First $Limit) }
Write-Host ("대상 합격자: {0}명 (직인: {1})" -f $rows.Count, $(if($SealTag -match 'img'){'있음'}else{'없음-자리표시'})) -ForegroundColor Cyan

# ---------- PDF 생성 ----------
if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$tmp = Join-Path $env:TEMP ("gu_offer_" + [System.Guid]::NewGuid().ToString('N'))
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
  $pdfPath = Join-Path $OutDir ("OFFER LETTER_$($s.ExNo)_$safeName.pdf")
  $tmpPdf  = Join-Path $tmp ("$($s.ExNo).pdf")   # 공백/한글 없는 임시 경로로 렌더 (Edge 인자 안전)
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
