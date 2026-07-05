# =============================================================
#  2026-2학기 외국인 재학생 등록금/장학금 자동 산출 스크립트
#  실행: powershell -ExecutionPolicy Bypass -File 등록금계산.ps1
#  다음 학기 재사용 시: 아래 [설정] 상수와 $InputFile 만 수정
# =============================================================

param(
  [string]$InputFile = "C:\projects\admission\2_데이터\★2026-2학기 재학생 장학반영 고지서 생성.xlsx"
)

# ----------------------- [설정] 규정 상수 -----------------------
# 학과 -> 계열 등록금(A)
$TUITION_LOW  = 3077000   # 인문사회 계열
$TUITION_HIGH = 3744000   # 공학·예체능·보건 계열

$DeptLow = @(
  '물류무역학과','무역유통학과','경영학과','회계세무학과',
  '도시·부동산학과','한국어교육과','호텔관광경영학부','항공서비스학과'
)
$DeptHigh = @(
  '기계자동차공학부','컴퓨터공학과','건축학부','뷰티미용학과',
  '시각영상디자인학과','패션ㆍ주얼리디자인학부','호텔외식조리학과',
  '호텔조리제과제빵학과','식품영양학과','심리학과'
)

# 토픽장학금(B) 감면율 : 조건(직전학기 12학점 이상 & 평점 2.5 이상) 충족자만
$TopikRate = @{ '3'=0.40; '4'=0.55; '5'=0.60; '6'=0.65 }
$TOPIK_MIN_CREDIT = 12
$TOPIK_MIN_GPA    = 2.5

# 성적장학금(C)
$MERIT_GPA   = 4.0
$MERIT_AMOUNT = 300000
# ---------------------------------------------------------------

# 열 인덱스 (헤더 3행)
$C_ID=2; $C_NAME=3; $C_DEPT=4; $C_TYPE=6; $C_STATUS=7
$C_A=8; $C_TOPIK=9; $C_B=10; $C_CREDIT=11; $C_GPA=12
$C_C=13; $C_D=14; $C_E=15; $C_F=16; $C_MEMO=17
$FIRST_DATA_ROW = 4

if (-not (Test-Path $InputFile)) { Write-Host "입력 파일을 찾을 수 없습니다: $InputFile" -ForegroundColor Red; exit 1 }

$dir  = Split-Path $InputFile -Parent
$base = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$OutputFile = Join-Path $dir ($base + "_자동계산.xlsx")

# 숫자 파싱 도우미 (공백/콤마 제거, 실패 시 $null)
function ToNum($t) {
  if ($null -eq $t) { return $null }
  $s = ([string]$t).Trim() -replace ',', ''
  if ($s -eq '') { return $null }
  $d = 0.0
  if ([double]::TryParse($s, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$d)) { return $d }
  return $null
}
# 토픽급수 텍스트 -> '3'~'6' 또는 $null
function TopikLevel($t) {
  if ($null -eq $t) { return $null }
  $m = [regex]::Match([string]$t, '[3-6]')
  if ($m.Success) { return $m.Value }
  return $null
}

Write-Host "엑셀 여는 중..." -ForegroundColor Cyan
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open($InputFile)
$ws = $wb.Worksheets.Item(1)

# 마지막 데이터 행
$lastRow = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1

# 집계용
$cntProcessed=0; $cntExchange=0; $cntLow=0; $cntHigh=0
$cntTopikByLevel=@{'3'=0;'4'=0;'5'=0;'6'=0}; $cntTopikSkip=0
$cntMerit=0; $sumF=0.0; $unknownDepts=@{}

for ($r=$FIRST_DATA_ROW; $r -le $lastRow; $r++) {
  $id   = ([string]$ws.Cells.Item($r,$C_ID).Text).Trim()
  $name = ([string]$ws.Cells.Item($r,$C_NAME).Text).Trim()
  if ($id -eq '' -and $name -eq '') { continue }   # 빈 행 건너뜀

  $dept = ([string]$ws.Cells.Item($r,$C_DEPT).Text).Trim()
  $type = ([string]$ws.Cells.Item($r,$C_TYPE).Text).Trim()
  $memo = @()

  # 교환학생 제외
  if ($type -eq '교환') {
    $ws.Cells.Item($r,$C_MEMO).Value2 = '교환-산출제외'
    $cntExchange++
    continue
  }

  # ① 등록금(A)
  $A = $null
  if     ($DeptLow  -contains $dept) { $A = $TUITION_LOW;  $cntLow++ }
  elseif ($DeptHigh -contains $dept) { $A = $TUITION_HIGH; $cntHigh++ }
  else {
    if ($unknownDepts.ContainsKey($dept)) { $unknownDepts[$dept]++ } else { $unknownDepts[$dept]=1 }
    $ws.Cells.Item($r,$C_MEMO).Value2 = "학과-계열미매핑($dept)"
    continue   # 임의 배정 금지: 이 학생은 비우고 넘어감
  }

  # ② 토픽장학금(B)
  $B = 0.0
  $lvl    = TopikLevel $ws.Cells.Item($r,$C_TOPIK).Text
  $credit = ToNum $ws.Cells.Item($r,$C_CREDIT).Text
  $gpa    = ToNum $ws.Cells.Item($r,$C_GPA).Text
  if ($null -ne $lvl) {
    $condOk = ($null -ne $credit -and $credit -ge $TOPIK_MIN_CREDIT -and $null -ne $gpa -and $gpa -ge $TOPIK_MIN_GPA)
    if ($condOk) {
      $B = [math]::Round($A * $TopikRate[$lvl], 0)
      $cntTopikByLevel[$lvl]++
    } else {
      $memo += "토픽조건미충족(${credit}학점/${gpa})"
      $cntTopikSkip++
    }
  }

  # ③ 성적장학금(C)
  $C = 0.0
  if ($null -ne $gpa -and $gpa -ge $MERIT_GPA) { $C = $MERIT_AMOUNT; $cntMerit++ }

  # ④ 공로장학금(D): 기존 입력값 보존(없으면 0)
  $D = ToNum $ws.Cells.Item($r,$C_D).Text
  if ($null -eq $D) { $D = 0.0 }

  # ⑤ 합계·실납부
  $E = $B + $C + $D
  $F = $A - $E

  # 기입
  # 이 Excel COM 환경은 Value2에 [double] 할당 시 InvalidCast가 발생 → 정수로 캐스팅
  $ws.Cells.Item($r,$C_A).Value2 = [int]$A
  $ws.Cells.Item($r,$C_B).Value2 = [int]$B
  $ws.Cells.Item($r,$C_C).Value2 = [int]$C
  $ws.Cells.Item($r,$C_E).Value2 = [int]$E
  $ws.Cells.Item($r,$C_F).Value2 = [int]$F
  foreach ($c in @($C_A,$C_B,$C_C,$C_D,$C_E,$C_F)) { $ws.Cells.Item($r,$c).NumberFormat = '#,##0' }
  if ($memo.Count -gt 0) { $ws.Cells.Item($r,$C_MEMO).Value2 = ($memo -join '; ') }

  $cntProcessed++; $sumF += $F
}

# 저장 (xlsx = 51)
if (Test-Path $OutputFile) { Remove-Item $OutputFile -Force }
$wb.SaveAs($OutputFile, 51)
$wb.Close($false)
$xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ws) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
[GC]::Collect(); [GC]::WaitForPendingFinalizers()

# ---- 요약 출력 ----
Write-Host ""
Write-Host "===== 산출 완료 =====" -ForegroundColor Green
Write-Host ("출력 파일 : {0}" -f $OutputFile)
Write-Host ("산출 인원 : {0}명  (교환 제외 {1}명)" -f $cntProcessed, $cntExchange)
Write-Host ("등록금    : 저단가 {0}명 / 고단가 {1}명" -f $cntLow, $cntHigh)
Write-Host ("토픽장학금: 3급 {0} · 4급 {1} · 5급 {2} · 6급 {3} 명 (조건미충족 {4}명)" -f `
  $cntTopikByLevel['3'],$cntTopikByLevel['4'],$cntTopikByLevel['5'],$cntTopikByLevel['6'],$cntTopikSkip)
Write-Host ("성적장학금: {0}명 (평점 {1} 이상)" -f $cntMerit, $MERIT_GPA)
Write-Host ("실납부액 합계 : {0:N0} 원" -f $sumF)
if ($unknownDepts.Count -gt 0) {
  Write-Host ""
  Write-Host "[주의] 계열 미매핑 학과(수동 확인 필요):" -ForegroundColor Yellow
  $unknownDepts.GetEnumerator() | ForEach-Object { Write-Host ("  - {0} : {1}명" -f $_.Key, $_.Value) -ForegroundColor Yellow }
}


