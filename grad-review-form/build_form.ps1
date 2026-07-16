$ErrorActionPreference = 'Stop'

$outDir = 'C:\Users\user\Desktop\★국제협력처\2. 대학원\심사표'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Force $outDir | Out-Null }
$outHwp = Join-Path $outDir '대학원 외국인 지원자 서류평가표.hwp'
$outPdf = Join-Path $outDir '대학원 외국인 지원자 서류평가표(미리보기).pdf'

$logFile = $env:FORM_LOG
function L($m) { if ($logFile) { Add-Content -Path $logFile -Value ("[{0:HH:mm:ss}] {1}" -f (Get-Date), $m) -Encoding UTF8 } }

L "COM 생성"
$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") | Out-Null } catch {}
$hwp.XHwpDocuments.Add(0) | Out-Null
# 창을 숨기지 않으면 한글 창이 포커스를 가져가 사용자의 키 입력이 문서에 섞여 들어간다.
try { $hwp.XHwpWindows.Item(0).Visible = $false } catch {}
L "문서 생성 (창 숨김)"

function Run($a) { $hwp.HAction.Run($a) | Out-Null }

function Ins($t) {
  $s = $hwp.HParameterSet.HInsertText
  $hwp.HAction.GetDefault("InsertText", $s.HSet) | Out-Null
  $s.Text = [string]$t
  $hwp.HAction.Execute("InsertText", $s.HSet) | Out-Null
}

function Font([double]$size, [int]$bold) {
  $s = $hwp.HParameterSet.HCharShape
  $hwp.HAction.GetDefault("CharShape", $s.HSet) | Out-Null
  $s.Height = [int]($size * 100)
  $s.Bold = $bold
  $hwp.HAction.Execute("CharShape", $s.HSet) | Out-Null
}

function AlignC { Run "ParagraphShapeAlignCenter" }
function AlignL { Run "ParagraphShapeAlignLeft" }
function Para { Run "BreakPara" }
function MM($v) { $hwp.MiliToHwpUnit([double]$v) }

# 편집용지 여백 (한글 기본 좌우 30mm → 표가 넘치므로 20mm로 줄인다)
function PageMargins([double]$lr, [double]$tb) {
  $s = $hwp.HParameterSet.HSecDef
  $hwp.HAction.GetDefault("PageSetup", $s.HSet) | Out-Null
  $s.PageDef.LeftMargin = MM $lr
  $s.PageDef.RightMargin = MM $lr
  $s.PageDef.TopMargin = MM $tb
  $s.PageDef.BottomMargin = MM $tb
  $hwp.HAction.Execute("PageSetup", $s.HSet) | Out-Null
}

# $heights: 각 행 높이(mm) 배열
function NewTable([int]$rows, [int]$cols, $widths, $heights) {
  $t = $hwp.HParameterSet.HTableCreation
  $hwp.HAction.GetDefault("TableCreate", $t.HSet) | Out-Null
  $t.Rows = $rows
  $t.Cols = $cols
  $t.WidthType = 2
  $t.HeightType = 1
  $t.WidthValue = MM (($widths | Measure-Object -Sum).Sum)
  $t.HeightValue = MM (($heights | Measure-Object -Sum).Sum)
  $t.CreateItemArray("ColWidth", $cols) | Out-Null
  $cw = $t.ColWidth
  for ($i = 0; $i -lt $cols; $i++) {
    $cw.GetType().InvokeMember("Item", 'SetProperty', $null, $cw, @([int]$i, [int](MM $widths[$i])))
  }
  $t.CreateItemArray("RowHeight", $rows) | Out-Null
  $rh = $t.RowHeight
  for ($i = 0; $i -lt $rows; $i++) {
    $rh.GetType().InvokeMember("Item", 'SetProperty', $null, $rh, @([int]$i, [int](MM $heights[$i])))
  }
  $t.TableProperties.TreatAsChar = 1
  $hwp.HAction.Execute("TableCreate", $t.HSet) | Out-Null
}

function NextCell { Run "TableRightCell" }
function Down([int]$n) { for ($i = 0; $i -lt $n; $i++) { Run "TableLowerCell" } }
function Up([int]$n) { for ($i = 0; $i -lt $n; $i++) { Run "TableUpperCell" } }
function MergeRight([int]$n) {
  Run "TableCellBlock"; Run "TableCellBlockExtend"
  for ($i = 0; $i -lt $n; $i++) { Run "TableRightCell" }
  Run "TableMergeCell"; Run "Cancel"
}
function OutOfTable { Run "MoveDocEnd" }

# 셀 하나: 정렬 -> 글꼴 -> 텍스트
function Cell([string]$text, [string]$align, [double]$size, [int]$bold) {
  if ($align -eq 'L') { AlignL } else { AlignC }
  Font $size $bold
  if ($text.Length -gt 0) { Ins $text }
}

PageMargins 20 20

L "제목 시작"
AlignC
Font 18 1
Ins "대학원 외국인 지원자 서류평가표"
Para
Font 10 0
Ins "Document Evaluation Form for International Graduate Applicants"
Para

L "표1 시작"
$w1 = @(25, 55, 25, 55)
NewTable 2 4 $w1 @(9, 9)
Cell "지원학과" 'C' 10 1; NextCell
Cell "" 'C' 10 0; NextCell
Cell "학위과정" 'C' 10 1; NextCell
Cell "석사 (      )      박사 (      )" 'C' 10 0; NextCell
Cell "성        명" 'C' 10 1; NextCell
Cell "" 'C' 10 0; NextCell
Cell "국        적" 'C' 10 1; NextCell
Cell "" 'C' 10 0
OutOfTable
L "표1 완료"
Para
L "표2 시작"
$w2 = @(30, 80, 20, 30)
NewTable 7 4 $w2 @(9, 9, 9, 9, 9, 9, 9)

L "표2 생성됨"
Down 6; MergeRight 1; Up 6
L "표2 병합 완료"

$rows = @()
$rows += , @("평가항목", "평가내용", "배점", "평가점수")
$rows += , @("학업성적", "학부(또는 이전 과정) 성적 및 학업 수행능력", "30", "")
$rows += , @("전공 적합성", "지원 전공과 이전 전공의 연계성 및 적합성", "25", "")
$rows += , @("학업계획서", "학업계획의 구체성, 연구 의지 및 목표", "20", "")
$rows += , @("자기소개서", "지원동기, 학업 수행 의지, 발전 가능성", "15", "")
$rows += , @("언어능력", "TOPIK 또는 영어능력 등 학업 수행 가능성", "10", "")

$isHeader = $true
foreach ($r in $rows) {
  for ($c = 0; $c -lt 4; $c++) {
    $align = 'C'
    if ($c -eq 1 -and -not $isHeader) { $align = 'L' }
    $bold = 0
    if ($isHeader) { $bold = 1 }
    Cell $r[$c] $align 10.5 $bold
    NextCell
  }
  $isHeader = $false
  L ("행 입력: " + $r[0])
}
# 총점 행 (병합셀 + 배점 + 평가점수)
Cell "총                점" 'C' 10.5 1; NextCell
Cell "100" 'C' 10.5 1; NextCell
Cell "" 'C' 10.5 1
OutOfTable
Para
AlignL
Font 9 0
Ins "※ 각 평가항목의 배점 범위 내에서 점수를 부여하고, 합계를 총점란에 기입하여 주시기 바랍니다."
Para

L "표3 시작"
$w3 = @(30, 130)
NewTable 2 2 $w3 @(24, 12)
Cell "종 합 의 견" 'C' 10.5 1; NextCell
AlignL; Font 10.5 0
NextCell
Cell "평 가 결 과" 'C' 10.5 1; NextCell
Cell "□ 합격 추천        □ 조건부 합격 추천        □ 불합격 추천" 'C' 11 0
OutOfTable
Para
Para

L "서명란 시작"
AlignC
Font 11 0
Ins "위와 같이 서류평가 결과를 제출합니다."
Para
Para
Ins "2026년          월          일"
Para
Para
Ins "소속학과 :                        평가위원 :                        (서명)"
Para
Para
AlignL
Font 14 1
Ins "국제교류처장 귀하"

# 주의: 한글 COM은 바탕화면 등 사용자 폴더로 직접 SaveAs 하면 보안 확인 때문에 멈춘다.
#       임시 폴더에 저장한 뒤 PowerShell로 복사할 것.
$tmpHwp = Join-Path $env:TEMP 'gradform_build.hwp'
$tmpPdf = Join-Path $env:TEMP 'gradform_build.pdf'

L "임시 저장 시작"
$hwp.SaveAs($tmpHwp, "HWP", "") | Out-Null
L "임시 저장 완료"
if ($env:MAKE_PDF -eq '1') { $hwp.SaveAs($tmpPdf, "PDF", "") | Out-Null; L "PDF 저장 완료" }
$hwp.Quit()

Copy-Item $tmpHwp $outHwp -Force
"HWP: $outHwp (" + (Get-Item $outHwp).Length + " bytes)"
if (Test-Path $tmpPdf) {
  Copy-Item $tmpPdf $outPdf -Force
  "PDF: $outPdf (" + (Get-Item $outPdf).Length + " bytes)"
}
