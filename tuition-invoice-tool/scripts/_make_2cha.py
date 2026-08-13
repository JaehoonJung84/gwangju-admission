# -*- coding: utf-8 -*-
"""대학원_배치생성.ps1 → 대학원_배치생성_2차.ps1 생성.
HTML/CSS 양식 블록은 손대지 않고, 내용이 바뀌는 지점만 정확히 치환한다."""
import io, sys

SRC = '대학원_배치생성.ps1'
DST = '대학원_배치생성_2차.ps1'
s = io.open(SRC, encoding='utf-8-sig').read()
n = 0


def rep(old, new, cnt=1):
    global s, n
    if s.count(old) != cnt:
        print(f'!! 치환 실패({s.count(old)}건): {old[:70]}...')
        sys.exit(1)
    s = s.replace(old, new)
    n += 1


# ── ① 헤더 주석 ──
rep('''#  2026학년도 후기 대학원 신입생 배치 생성기
#  · 학생 1명당 2페이지 PDF (1p: OFFER LETTER, 2p: TUITION INVOICE)
#  · 저장: <OutRoot>\\{1. 중국|2. 베트남|3. 우즈베키스탄|4. 그 외 국가}\\한글명_영문명.pdf
#  · 입력: 지원자 현황 엑셀  (시트1 현황 / 시트2 장학등록금 / 시트3 가상계좌)
#  · 가상계좌: 생년월일(YYMMDD) 기준 매칭, 실패 시 이름 매칭''',
    '''#  2026학년도 후기 대학원 (2차) 합격자 배치 생성기
#  · 학생 1명당 2페이지 PDF (1p: OFFER LETTER, 2p: TUITION INVOICE)
#  · 저장: <OutRoot>\\한글명_영문명.pdf   (국가별 하위폴더 없이 평면 저장)
#  · 입력: 납부자 명단 엑셀 'Sheet1 (2)' 의 대학원 추가분 행범위
#  · 가상계좌: 미배정 → "추후 확정 · To be assigned"
#  · 양식(HTML/CSS)은 1차 스크립트와 동일''')

# ── ② param ──
rep('''  [string]$MainFile = "C:\\Users\\user\\Desktop\\★국제협력처\\2. 대학원\\2026학년도 후기\\합격통지서 등록금고지서\\2026학년도 후기 대학원 지원자 현황_정리본.xlsx",
  [string]$OutRoot  = "C:\\Users\\user\\Desktop\\★국제협력처\\2. 대학원\\2026학년도 후기\\합격통지서 등록금고지서",''',
    '''  [string]$MainFile = "C:\\Users\\user\\Desktop\\★국제협력처\\1. 학부\\2026-2학기\\교육비납입증명서\\납부자 명단(김선경)\\★2026-2학기 학부 및 대학원 신편입생 지원자 명단(입금일자)_20260810 반영.xlsx",
  [string]$OutRoot  = "C:\\Users\\user\\Desktop\\★국제협력처\\1. 학부\\2026-2학기\\합격통지서 등록금고지서\\신편입학(2차)\\대학원",
  [string]$SheetName = "Sheet1 (2)",
  [int]$RowFrom      = 227,
  [int]$RowTo        = 238,''')

# ── ③ 제외자 ──
rep("$EXCLUDE = @('정몽정','응웬반밍','서욱')",
    "$EXCLUDE = @('응웬반밍')          # 불합격")

# ── ③-2 가상계좌 (전산원 생성분, 2026-08-13 캡처) ──
rep("""$AssetDir = Split-Path $PSScriptRoot -Parent""",
    """# 이름 = @(수험번호, 가상계좌, 생년월일YYMMDD)  — 생년월일은 엑셀과 대조용
$ACCTMAP = @{
  '레프엉투이' = @('2026411428','870-400-585608','960701')
  '장가녕'     = @('2026411417','870-400-579089','040828')
  '이모디'     = @('2026421307','870-400-579113','980419')
  '호서'       = @('2026411418','870-400-579159','000923')
  '선소가'     = @('2026412413','870-400-579186','020827')
  '양가군'     = @('2026911419','870-400-579210','840210')
  '김주함'     = @('2026911420','870-400-579256','041215')
  '호효연'     = @('2026911421','870-400-579283','910910')
  '가준희'     = @('2026911416','870-400-579317','020531')
  '주충래'     = @('2026911417','870-400-579380','031203')
  '장화명'     = @('2026911418','870-400-579414','000408')
}

$AssetDir = Split-Path $PSScriptRoot -Parent""")

# ── ④ 학과 영문명 보강 (2차 신규 학과) ──
rep("""  '전기전자공학과'='Electrical and Electronic Engineering';
}""",
    """  '전기전자공학과'='Electrical and Electronic Engineering';
  '임상상담심리학과'='Clinical Counseling Psychology';
  '시각영상디자인'='Visual Media Design'; '시각영상디자인학과'='Visual Media Design';
  '미래융합기술공학과'='Future Convergence Technology Engineering';
}""")

# ── ⑤ 신입/편입 구분 (1차는 전원 신입학이라 고정값이었음) ──
rep("""function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }""",
    """function GenderEn([string]$s){ if($s -match '여|F'){return 'Female'}; if($s -match '남|M'){return 'Male'}; return $s }
function GubunKo([string]$g){ if($g -match '편입'){return '편입학'}; return '신입학' }
function GubunEn([string]$g){ if($g -match '편입'){return 'Transfer'}; return 'Freshman' }""")

# ── ⑤-2 수업연한: 편입은 1년 (1차는 전원 신입이라 이 분기가 없었음) ──
rep("""function Duration([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return 'Sep. 2026 – Aug. 2027' }
  return 'Sep. 2026 – Aug. 2028'
}
function DurationYr([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return '1년' }
  return '2년'
}""",
    """function Duration([string]$deg,[string]$dept,[string]$gub){
  if($gub -match '편입'){ return 'Sep. 2026 – Aug. 2027' }
  if($deg -notmatch '박사' -and $dept -match '법학'){ return 'Sep. 2026 – Aug. 2027' }
  return 'Sep. 2026 – Aug. 2028'
}
function DurationYr([string]$deg,[string]$dept,[string]$gub){
  if($gub -match '편입'){ return '1년' }
  if($deg -notmatch '박사' -and $dept -match '법학'){ return '1년' }
  return '2년'
}""")

rep("""    Duration=(Duration $deg $dept); DurationYr=(DurationYr $deg $dept)""",
    """    Duration=(Duration $deg $dept $gub); DurationYr=(DurationYr $deg $dept $gub)""")

# ── ⑥ HTML 내 구분·납부기간 (그 외 양식은 불변) ──
rep("""      <div class='val'>Foreign Special Admission · Freshman &nbsp;<span class='ko2'>(외국인 특별전형 · 신입학)</span></div></div>""",
    """      <div class='val'>Foreign Special Admission · $($rec.GubunEn) &nbsp;<span class='ko2'>(외국인 특별전형 · $($rec.GubunKo))</span></div></div>""")

rep("""      <td>Freshman<br><span style='color:#6b7d70;font-size:10.5px'>신입학</span></td>""",
    """      <td>$($rec.GubunEn)<br><span style='color:#6b7d70;font-size:10.5px'>$($rec.GubunKo)</span></td>""")

rep("""<td>July 22 – 24, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 7. 22. ~ 7. 24.)</span></td>""",
    """<td>August 18 – 21, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 8. 18. ~ 8. 21.)</span></td>""")

# ── ⑦ 엑셀 읽기: 가상계좌 시트 제거 ──
rep("""# 시트3 가상계좌: 생년월일(YYMMDD) / 이름 -> 계좌
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
$last = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1""",
    """# 가상계좌는 아직 미배정 (전산원 확정 후 재발급)
Write-Host "  가상계좌 미배정 — '추후 확정 · To be assigned' 표기" -ForegroundColor Yellow

$ws = $wb.Worksheets.Item($SheetName)
$last = $RowTo""")

# ── ⑧ 행 루프: 열 매핑 교체 ──
rep("""for($r=3; $r -le $last; $r++){
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
  $exno = if($ExNoByBirth.ContainsKey($bk)){ $ExNoByBirth[$bk] } else { '' }""",
    """for($r=$RowFrom; $r -le $last; $r++){
  $ko = CellTxt $r 6
  if($ko -eq ''){ continue }
  if($EXCLUDE -contains $ko){ $skipped += $ko; continue }
  if($Only -ne '' -and $ko -ne $Only){ continue }

  # 납부자 명단 열: 2과정 3구분 4트랙 5수험번호 6한글명 7영문명 8생년월일 9성별 10국가 11학과
  #                14입학금(A) 15수업료(B) 17장학금(C) 18실납부액(D)
  $deg = CellTxt $r 2; $gub = CellTxt $r 3; $dept = CellTxt $r 11; $natKo = CellTxt $r 10; $trk = CellTxt $r 4
  $birth = CellTxt $r 8; $topik = CellTxt $r 12
  $A = CellNum $r 14; $B = CellNum $r 15; $C = CellNum $r 17; $D = CellNum $r 18
  if($A -eq 0 -and $B -eq 0){ $skipped += "$ko (금액 없음)"; continue }

  $acct = '추후 확정 · To be assigned'
  $exno = CellTxt $r 5
  if($ACCTMAP.ContainsKey($ko)){
    $am = $ACCTMAP[$ko]
    $bk = BirthKey $birth
    if($bk -ne $am[2]){ Write-Host ("  [생년월일 불일치] {0}: 엑셀 {1} / 계좌자료 {2}" -f $ko,$bk,$am[2]) -ForegroundColor Red }
    $exno = $am[0]; $acct = $am[1]
  }""")

# ── ⑨ 레코드에 구분 추가 + 성별 열 ──
rep("""  $rows += [pscustomobject]@{
    ExNo=$exno; KoName=$ko; EnName=(CellTxt $r 4); Birth=$birth
    GenderKo=(CellTxt $r 15); GenderEn=(GenderEn (CellTxt $r 15))""",
    """  $rows += [pscustomobject]@{
    ExNo=$exno; KoName=$ko; EnName=(CellTxt $r 7); Birth=$birth
    GenderKo=(CellTxt $r 9); GenderEn=(GenderEn (CellTxt $r 9))
    GubunKo=(GubunKo $gub); GubunEn=(GubunEn $gub)""")

# ── ⑨-2 회계 서식의 0 표시("-")를 숫자 0으로 읽도록 보강 ──
rep("""function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\\d.-]',''; if($t -eq ''){return 0.0}; return [double]$t }""",
    """function CellNum($r,$c){ $t=(CellTxt $r $c) -replace '[^\\d.]',''; if($t -eq ''){return 0.0}; $d=0.0; if([double]::TryParse($t,[ref]$d)){ return $d }; return 0.0 }""")

# ── ⑩ 출력 경로: 국가별 폴더 없이 평면 저장 ──
rep("""  $outDir = Join-Path $OutRoot $s.CountryFolder
  if(-not (Test-Path $outDir)){ New-Item -ItemType Directory -Path $outDir -Force | Out-Null }""",
    """  $outDir = $OutRoot
  if(-not (Test-Path $outDir)){ New-Item -ItemType Directory -Path $outDir -Force | Out-Null }""")

# ── ⑪ 덮어쓰기 실패 방지: 기존 파일 먼저 삭제 후 이동, 실제 갱신 여부까지 확인 ──
rep("""  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }""",
    """  $moveErr = ''
  if(Test-Path $tmpPdf){
    try {
      if(Test-Path -LiteralPath $pdfPath){ Remove-Item -LiteralPath $pdfPath -Force -ErrorAction Stop }
      Move-Item -LiteralPath $tmpPdf -Destination $pdfPath -Force -ErrorAction Stop
    } catch {
      $moveErr = '파일이 다른 프로그램에서 열려 있어 교체 실패 (PDF 뷰어를 닫고 다시 실행하세요)'
    }
  }""")

rep("""  if(Test-Path $pdfPath){ $ok++; Write-Host ("  [{0}/{1}] {2}\\{3}" -f $i,$rows.Count,$s.CountryFolder,$fname) }""",
    """  $fresh = (Test-Path -LiteralPath $pdfPath) -and ((Get-Item -LiteralPath $pdfPath).LastWriteTime -gt (Get-Date).AddMinutes(-5))
  if($fresh){ $ok++; Write-Host ("  [{0}/{1}] {2}" -f $i,$rows.Count,$fname) }
  elseif(Test-Path -LiteralPath $pdfPath){ $fail++; Write-Host ("  [{0}/{1}] 갱신 안 됨(옛 파일 유지): {2}  {3}" -f $i,$rows.Count,$fname,$moveErr) -ForegroundColor Red }""")

io.open(DST, 'w', encoding='utf-8-sig').write(s)
print(f'생성 완료: {DST}  (치환 {n}건)')

# HTML/CSS 스타일 블록이 원본과 동일한지 확인
o = io.open(SRC, encoding='utf-8-sig').read()
css_o = o[o.index('<style>'):o.index('</style>')]
css_n = s[s.index('<style>'):s.index('</style>')]
print('CSS 블록 원본과 동일:', css_o == css_n, f'({len(css_o)} bytes)')
