# =============================================================
#  장학금 수혜 증명서 (CERTIFICATE OF SCHOLARSHIP AWARD) - 교무처 발급 양식
#  · 학사지원처 자동발급 「Certificate of Education Expense Payment」 서식을 그대로 복제
#  · 하단 서명부(교무처장 서명 이미지 + Sang-Youp Kim / Dean of Academic affairs)는 원본 그대로 사용 - 수정 금지
#  · 본문(장학 내역)만 교체
#  실행 예:
#   powershell -File 장학금수혜증명서_교무처양식.ps1 -DocNo 00997
# =============================================================
param(
  [string]$DocNo      = "00997",                   # 증명서 번호
  [string]$Name       = "TUNGALAG NASANTOGTOKH",   # 성명(영문)
  [string]$KoName     = "통가락 나상턱터흐",       # 성명(한글, 파일명용)
  [string]$RRN        = "021017-7220039",          # 외국인등록번호
  [string]$Addr       = "Unit 611, Sejong Gositel, 9-11, Pilmun-daero 253beon-gil, Dong-gu, Gwangju, Republic of Korea",
  [string]$StudentNo  = "20266285",                # 학번
  [string]$Relation   = "Self",                    # 신청인과의 관계
  [string]$SemesterEn = "2026 2nd Semester",       # 학기(영문)
  [string]$FeeType    = "Tuition Fee",
  [string]$SchName    = "Korean Language Proficiency Scholarship",
  [string]$Basis      = "Official TOPIK Level 4",  # 장학 선발 근거
  [double]$Tuition    = 3744000,                   # 총 교육비 (A)
  [double]$Reduction  = 3744000,                   # 감면/면제 (B-1)
  [double]$DirectPaid = 0,                         # 학생 직접 지급 (B-2)
  [double]$Rate       = 100,                       # 장학 비율(%)
  [string]$IssueDate  = "",                        # 발급일 (미지정 시 오늘)
  [string]$OutDir     = "C:\Users\user\Desktop\통가락",
  [string]$SignImage  = "",
  [string]$OutFile    = ""                       # 출력 파일명(미지정 시 자동)
)

$AssetDir = Split-Path $PSScriptRoot -Parent
if ($SignImage -eq '') { $p = Join-Path $AssetDir '교무처장_서명.jpg'; if (Test-Path $p) { $SignImage = $p } }

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
function KRW($n){ return ('{0:N0}' -f [double]$n) }
function PCT($n){ return ('{0:0.##}' -f [double]$n) + '%' }

$SignUri = DataUri $SignImage
$SignTag = if ($SignUri -ne '') { "<img class='sign' src='$SignUri' alt='signature'/>" } else { '' }

if($IssueDate -eq ''){ $d = Get-Date } else { $d = [datetime]$IssueDate }
$IssueEn = $d.ToString('MMMM d, yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))
$Borne   = $Tuition - $Reduction - $DirectPaid

$html = @"
<!doctype html><html lang='en'><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  html,body { margin:0; padding:0; }
  .pg { position:relative; width:595pt; height:842pt; color:#000;
        font-family:'Noto Sans KR','Malgun Gothic',sans-serif; }
  .frame { position:absolute; left:41.2pt; top:64.4pt; width:509.2pt; height:729.8pt; border:1.44pt solid #000; }
  .abs { position:absolute; }
  .docno { left:63.5pt; top:80.5pt; font-size:11pt; }
  .title { left:41.2pt; top:97pt; width:509.2pt; text-align:center; font-size:19pt; font-weight:700; }

  table { position:absolute; border-collapse:collapse; table-layout:fixed; }
  td { border:0.72pt solid #000; padding:0 4pt; font-size:8pt; vertical-align:middle; }
  .lbl { text-align:center; }
  .val { font-size:10pt; }
  .valb { font-size:10pt; font-weight:700; }
  .thick-t { border-top:1.44pt solid #000 !important; }
  .thick-b { border-bottom:1.44pt solid #000 !important; }
  .nol { border-left:0 !important; }
  .nor { border-right:0 !important; }

  .sechead { left:41.2pt; top:318.5pt; width:509.2pt; text-align:center; font-size:15pt; font-weight:700; }
  .unit { left:41.2pt; top:327.8pt; width:505pt; text-align:right; font-size:7.5pt; font-weight:700; }

  #det td { font-size:7.5pt; text-align:center; line-height:1.25; }
  #det td.num { text-align:right; font-size:9pt; font-weight:700; padding-right:4pt; }
  #det td.tot { font-size:9pt; font-weight:700; }
  #det td.sm { font-size:6.5pt; line-height:1.2; }
  #det td.xs { font-size:5.8pt; line-height:1.2; }

  .req { left:45pt; top:536pt; width:501pt; text-align:center; font-size:8pt; font-weight:700; line-height:1.25; }
  .reqdate { left:41.2pt; top:558.5pt; width:509.2pt; text-align:center; font-size:10pt; font-weight:700; }
  .applicant { left:41.2pt; top:575pt; width:509.2pt; text-align:center; font-size:11pt; }
  .hr1 { left:42.7pt; top:598.4pt; width:507.7pt; border-top:0.72pt solid #000; }
  .cert { left:47.5pt; top:600.5pt; font-size:9pt; font-weight:700; }
  .certdate { left:41.2pt; top:617.5pt; width:509.2pt; text-align:center; font-size:12pt; font-weight:700; }
  .sign { position:absolute; left:331.75pt; top:656pt; width:207pt; height:54pt; object-fit:contain; }
  .hr2 { left:328pt; top:711pt; width:216pt; border-top:0.9pt solid #000; }
  .signer { left:339pt; top:714.5pt; font-family:'Times New Roman',Times,serif; font-size:12pt; }
  .signer2 { left:339pt; top:734.8pt; font-family:'Times New Roman',Times,serif; font-size:12pt; }
  .fn { left:45.5pt; font-size:6.6pt; line-height:1.25; }
</style></head>
<body><div class='pg'>
  <div class='frame'></div>

  <div class='abs docno'>No. $DocNo</div>
  <div class='abs title'>Certificate of Scholarship Award</div>

  <!-- 기관 정보 -->
  <table style="left:41.2pt; top:147.7pt; width:509.2pt;">
    <colgroup><col style="width:84pt"><col style="width:131.2pt"><col style="width:120.8pt"><col style="width:173.2pt"></colgroup>
    <tr style="height:27.7pt">
      <td class='lbl thick-t nol'>&#9312; Name of<br>Institution</td>
      <td class='val thick-t'>Gwangju University</td>
      <td class='lbl thick-t'>&#9313; Business Registration No.</td>
      <td class='valb thick-t nor'>410-82-02287</td>
    </tr>
    <tr style="height:27.8pt">
      <td class='lbl nol'>&#9314; Representative</td>
      <td class='val'>Kim Dong-jin</td>
      <td class='lbl'>&#9315; Telephone No.</td>
      <td class='valb nor'>+82-62-670-2114</td>
    </tr>
    <tr style="height:27.8pt">
      <td class='lbl nol'>&#9316; Address</td>
      <td class='val' colspan='3' style="border-right:0">277 Hyodeok-ro, Nam-gu, Gwangju, Republic of Korea</td>
    </tr>
  </table>

  <!-- 신청인 -->
  <table style="left:41.2pt; top:231pt; width:509.2pt;">
    <colgroup><col style="width:41.2pt"><col style="width:42.8pt"><col style="width:132pt"><col style="width:120pt"><col style="width:173.2pt"></colgroup>
    <tr style="height:27pt">
      <td class='lbl nol' rowspan='2' style="font-size:7.5pt">Applicant</td>
      <td class='lbl'>&#9317; Name</td>
      <td class='val'>$Name</td>
      <td class='lbl'>&#9318; Resident Registration No.</td>
      <td class='valb nor'>$RRN</td>
    </tr>
    <tr style="height:28.4pt">
      <td class='lbl'>&#9319; Address</td>
      <td colspan='3' class='nor' style="font-size:8pt">$Addr</td>
    </tr>
  </table>

  <!-- 학생 -->
  <table style="left:41.2pt; top:286.4pt; width:509.2pt;">
    <colgroup><col style="width:41.2pt"><col style="width:42.8pt"><col style="width:109.5pt"><col style="width:119.3pt"><col style="width:63.7pt"><col style="width:40.5pt"><col style="width:92.2pt"></colgroup>
    <tr style="height:27.8pt">
      <td class='lbl nol thick-b'>Student</td>
      <td class='lbl thick-b'>&#9320; Name</td>
      <td class='val thick-b' style="font-size:9pt">$Name</td>
      <td class='lbl thick-b'>&#9321; Relationship to Applicant</td>
      <td class='thick-b' style="text-align:center;font-size:9pt">$Relation</td>
      <td class='lbl thick-b' style="font-size:7pt">Student ID<br>No.</td>
      <td class='valb thick-b nor'>$StudentNo</td>
    </tr>
  </table>

  <div class='abs sechead'>Scholarship Details</div>
  <div class='abs unit'>(Unit: KRW, Korean Won)</div>

  <!-- 장학 내역 -->
  <table id='det' style="left:41.2pt; top:348.7pt; width:509.2pt;">
    <colgroup><col style="width:68pt"><col style="width:52pt"><col style="width:125pt"><col style="width:68pt"><col style="width:66pt"><col style="width:60pt"><col style="width:70.2pt"></colgroup>
    <tr style="height:13.5pt">
      <td class='thick-t nol' rowspan='2'>&#9322; Semester</td>
      <td class='thick-t' rowspan='2'>&#9323; Type</td>
      <td class='thick-t' rowspan='2'>&#9324; Name of<br>Scholarship</td>
      <td class='thick-t' rowspan='2'>&#9325; Total<br>Education<br>Expenses (A)</td>
      <td class='thick-t' colspan='2' style="font-size:8pt">&#9326; Scholarship Awarded (B)</td>
      <td class='thick-t nor' rowspan='2'>Education Expenses<br>Borne by Student<br>(C = A - B)</td>
    </tr>
    <tr style="height:24.8pt">
      <td class='sm'>Tuition Reduction<br>/ Waiver</td>
      <td class='sm'>Directly Paid<br>to Student</td>
    </tr>
    <tr style="height:20.4pt">
      <td class='tot nol'>$SemesterEn</td>
      <td>$FeeType</td>
      <td>$SchName</td>
      <td class='num'>$(KRW $Tuition)</td>
      <td class='num'>$(KRW $Reduction)</td>
      <td class='num'>$(KRW $DirectPaid)</td>
      <td class='num nor'>$(KRW $Borne)</td>
    </tr>
    <tr style="height:20.4pt"><td class='nol'>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td class='nor'></td></tr>
    <tr style="height:20.4pt"><td class='nol'>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td class='nor'></td></tr>
    <tr style="height:20.4pt"><td class='nol'>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td class='nor'></td></tr>
    <tr style="height:20.4pt"><td class='nol'>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td class='nor'></td></tr>
    <tr style="height:21pt">
      <td class='tot nol' colspan='3' style="text-align:right;padding-right:8pt">Total (KRW)</td>
      <td class='num'>$(KRW $Tuition)</td>
      <td class='num'>$(KRW $Reduction)</td>
      <td class='num'>$(KRW $DirectPaid)</td>
      <td class='num nor'>$(KRW $Borne)</td>
    </tr>
    <tr style="height:20.3pt">
      <td class='nol' colspan='3' style="text-align:right;padding-right:8pt;font-size:8.5pt">Basis of Award / Scholarship Rate</td>
      <td class='tot nor' colspan='4' style="text-align:center">$Basis &nbsp;&middot;&nbsp; $(PCT $Rate)</td>
    </tr>
  </table>

  <div class='abs req'>I hereby request certification that the scholarship stated above has been awarded<br>for the semester indicated.</div>
  <div class='abs reqdate'>$IssueEn</div>
  <div class='abs applicant'>Applicant</div>
  <div class='abs hr1'></div>

  <div class='abs cert'>I hereby certify that the above scholarship has been awarded as stated.</div>
  <div class='abs certdate'>$IssueEn</div>
  $SignTag
  <div class='abs hr2'></div>
  <div class='abs signer'>Sang-Youp Kim</div>
  <div class='abs signer2'>Dean of Academic affairs</div>

  <div class='abs fn' style="top:761pt">* The scholarship stated above is applied as a reduction of the tuition fee for the semester indicated and is not paid to the student in cash.</div>
  <div class='abs fn' style="top:769.3pt">* This certificate may be changed due to subsequent adjustment of the scholarship. If any changes occur afterward, please obtain a reissued certificate before use.</div>
</div></body></html>
"@

if(-not (Test-Path $OutDir)){ New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$safe = ($KoName + '_' + $Name) -replace '[\\/:*?"<>|]','_'
$tmp = Join-Path $env:TEMP ("sch_" + [guid]::NewGuid().ToString('N') + ".html")
if($OutFile -eq ""){ $OutFile = "장학금수혜증명서_" + $safe + ".pdf" }
$pdf = Join-Path $OutDir $OutFile

[IO.File]::WriteAllText($tmp, $html, (New-Object Text.UTF8Encoding $false))
& $Edge --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" "file:///$($tmp -replace '\\','/')" 2>$null | Out-Null
Start-Sleep -Milliseconds 500
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

if(Test-Path $pdf){
  Write-Host ("생성 완료: " + $pdf + "  (" + (Get-Item $pdf).Length + " bytes)") -ForegroundColor Green
} else {
  Write-Host "PDF 생성 실패" -ForegroundColor Red
}
