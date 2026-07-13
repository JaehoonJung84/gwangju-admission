$ErrorActionPreference = 'Stop'
$outDir = 'C:\Users\user\Desktop\★국제협력처\2. 대학원\심사표'
$outHwp = Join-Path $outDir '광주대 대학원 서류심사표(초안).hwp'
$outPdf = Join-Path $env:TEMP 'claude\C--projects\dcce4a26-f75e-4fb0-9beb-017b6b4c9c6c\scratchpad\preview.pdf'

$hwp = New-Object -ComObject HWPFrame.HwpObject
try { $hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") | Out-Null } catch {}
$hwp.XHwpDocuments.Add(0) | Out-Null

function Run($a) { $hwp.HAction.Run($a) | Out-Null }
function Ins($t) {
  $s = $hwp.HParameterSet.HInsertText
  $hwp.HAction.GetDefault("InsertText", $s.HSet) | Out-Null
  $s.Text = $t
  $hwp.HAction.Execute("InsertText", $s.HSet) | Out-Null
}
function Font($size, $bold) {
  if ($null -eq $bold) { throw "Font() called with NULL bold (size=$size) at: $((Get-PSCallStack)[1].Position.Text)" }
  $s = $hwp.HParameterSet.HCharShape
  $hwp.HAction.GetDefault("CharShape", $s.HSet) | Out-Null
  $s.Height = [int]($size * 100)
  $s.Bold = $bold
  $hwp.HAction.Execute("CharShape", $s.HSet) | Out-Null
}
function AlignC { Run "ParagraphShapeAlignCenter" }
function AlignL { Run "ParagraphShapeAlignLeft" }
function AlignR { Run "ParagraphShapeAlignRight" }
function Para { Run "BreakPara" }
function MM($v) { $hwp.MiliToHwpUnit([double]$v) }

function NewTable($rows, $cols, $widths, $rowH) {
  $t = $hwp.HParameterSet.HTableCreation
  $hwp.HAction.GetDefault("TableCreate", $t.HSet) | Out-Null
  $t.Rows = $rows
  $t.Cols = $cols
  $t.WidthType = 2
  $t.HeightType = 1
  $t.WidthValue = MM ($widths | Measure-Object -Sum).Sum
  $t.HeightValue = MM ($rowH * $rows)
  $t.CreateItemArray("ColWidth", $cols) | Out-Null
  $cw = $t.ColWidth
  for ($i = 0; $i -lt $cols; $i++) {
    $cw.GetType().InvokeMember("Item", 'SetProperty', $null, $cw, @([int]$i, [int](MM $widths[$i])))
  }
  $t.TableProperties.TreatAsChar = 1
  $hwp.HAction.Execute("TableCreate", $t.HSet) | Out-Null
}
# 셀 채우기: 순서대로 이동하며 입력 (align: 'C' 또는 'L')
function Cell($text, $align) {
  if ($align -eq 'L') { AlignL } else { AlignC }
  if ($text) { Ins $text }
}
function NextCell { Run "TableRightCell" }
function Down($n) { for ($i = 0; $i -lt $n; $i++) { Run "TableLowerCell" } }
function Up($n) { for ($i = 0; $i -lt $n; $i++) { Run "TableUpperCell" } }
function MergeRight($n) {
  Run "TableCellBlock"
  Run "TableCellBlockExtend"
  for ($i = 0; $i -lt $n; $i++) { Run "TableRightCell" }
  Run "TableMergeCell"
  Run "Cancel"
}
function MergeDown($n) {
  Run "TableCellBlock"
  Run "TableCellBlockExtend"
  for ($i = 0; $i -lt $n; $i++) { Run "TableLowerCell" }
  Run "TableMergeCell"
  Run "Cancel"
}
function OutOfTable { Run "MoveDocEnd" }

# ── 제목 ───────────────────────────────────────────────
AlignC
Font 16 1
Ins "2026학년도 후기 대학원 외국인 특별전형 서류심사 평가표"
Para
Font 10 0
Ins "일반대학원 (    )     사회복지전문대학원 (    )     보건상담정책대학원 (    )     /     석사 (    )     박사 (    )"
Para
Para

# ── 인적사항 표 (1행 6열) ──────────────────────────────
$w1 = @(25, 32, 25, 30, 22, 31)
NewTable 1 6 $w1 9
$hdr = @('지원학과', '', '수험번호', '', '성 명', '')
for ($i = 0; $i -lt 6; $i++) {
  if ($i % 2 -eq 0) { Font 10 1 } else { Font 10 0 }
  Cell $hdr[$i] 'C'
  if ($i -lt 5) { NextCell }
}
OutOfTable
Para
AlignL
Font 10 0
Ins "※ 전형방법 : 서류심사 100 % (면접 없음)"
Para
Para

# ── 평가표 (8행 5열) ───────────────────────────────────
$w2 = @(27, 32, 58, 32, 16)
NewTable 8 5 $w2 12

# 병합 (아래→위 순서)
Down 7; MergeRight 3; Up 7            # 합계 행: 1~4열 병합
Down 6; MergeRight 1; Up 6            # 학업·연구계획 행
Down 5; MergeRight 1; Up 5            # 어학능력 행
Down 3; MergeDown 1; Up 3             # 전공적합성 세로 병합
Down 1; MergeDown 1                   # 학업역량 세로 병합
Up 1

# 셀 입력 (병합 후 시각적 순서)
$cells = @(
  @('영 역', 'C', 1), @('구분 (배점)', 'C', 1), @('평 가 기 준', 'C', 1), @('평 가 척 도', 'C', 1), @('취득점수', 'C', 1),

  @('학업역량'+[char]10+'( 40 )', 'C', 1),
  @('학 업 성 적 ( 25 )', 'C', 0), @('최종학력 성적(GPA)의 우수성', 'L', 0), @('25 · 20 · 15 · 10 · 5', 'C', 0), @('', 'C', 0),
  @('학 력 요 건 ( 15 )', 'C', 0), @('정규 학위과정 이수 및 학위 취득(예정)의 확실성', 'L', 0), @('15 · 12 · 9 · 6 · 3', 'C', 0), @('', 'C', 0),

  @('전공적합성'+[char]10+'( 25 )', 'C', 1),
  @('전 공 일 치 도 ( 15 )', 'C', 0), @('선수전공과 지원학과의 연계성', 'L', 0), @('15 · 12 · 9 · 6 · 3', 'C', 0), @('', 'C', 0),
  @('연구·실무 경력 ( 10 )', 'C', 0), @('논문·연구실적, 관련 경력 및 자격증', 'L', 0), @('10 · 8 · 6 · 4 · 2', 'C', 0), @('', 'C', 0),

  @('어 학 능 력 ( 20 )', 'C', 1), @('강의 수학이 가능한 어학 수준 (TOPIK 또는 공인 영어성적)', 'L', 0), @('20 · 16 · 12 · 8 · 4', 'C', 0), @('', 'C', 0),

  @('학업·연구계획 ( 15 )', 'C', 1), @('지원동기의 타당성, 학업·연구계획의 구체성 및 실현가능성', 'L', 0), @('15 · 12 · 9 · 6 · 3', 'C', 0), @('', 'C', 0),

  @('합       계     ( 100점 만점 )', 'C', 1), @('', 'C', 0)
)
for ($i = 0; $i -lt $cells.Count; $i++) {
  $c = $cells[$i]
  Font 10 $c[2]
  Cell $c[0] $c[1]
  if ($i -lt $cells.Count - 1) { NextCell }
}
OutOfTable
Para
AlignL
Font 9 0
Ins "※ 평가척도 중 하나를 선택하여 취득점수란에 숫자로 기입합니다."
Para
Ins "※ 학업성적(4.5 만점 환산) : 4.0 이상 25 / 3.5 이상 20 / 3.0 이상 15 / 2.5 이상 10 / 2.5 미만 5"
Para
Ins "※ 어학능력 : TOPIK 6급 20 / 5급 16 / 4급 12 / 3급 8 / 3급 미만·미제출 4"
Para
Ins "     (영어트랙 : TOEFL iBT 90·IELTS 6.5 이상 20 / 80·6.0 이상 16 / 71·5.5 이상 12 / 59·5.0 이상 8 / 기준 미만 4)"
Para
Para

# ── 판정 표 (3행 2열) ──────────────────────────────────
$w3 = @(30, 135)
NewTable 3 2 $w3 12
Font 10 1; Cell '전공 일치 여부' 'C'; NextCell
Font 10 0; Cell '일치 (      )        불일치 (      )        ※ 불일치 시 전공 보충과목 이수 대상 (석사 6학점, 박사 9학점)' 'L'; NextCell
Font 10 1; Cell '종 합 의 견' 'C'; NextCell
Font 10 0; AlignL; Para; Para; NextCell
Font 10 1; Cell '판          정' 'C'; NextCell
Font 12 1; Cell '합  격  (            )                        불 합 격  (            )' 'C'
OutOfTable
Para
Para

# ── 마무리 ────────────────────────────────────────────
AlignC
Font 11 0
Ins "위와 같이 평가하여 제출합니다."
Para
Para
Ins "2026년          월          일"
Para
Para
Ins "소속학과 :                            심사위원 :                            (서명)"
Para
Para
AlignL
Font 13 1
Ins "국제교류처장 귀하"

$hwp.SaveAs($outHwp, "HWP", "") | Out-Null
$hwp.SaveAs($outPdf, "PDF", "") | Out-Null
$hwp.Quit()
"HWP: " + (Get-Item $outHwp).Length + " bytes"
"PDF: " + (Get-Item $outPdf).Length + " bytes"
