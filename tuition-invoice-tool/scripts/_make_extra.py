# -*- coding: utf-8 -*-
"""대학원_배치생성.ps1 → 대학원_추가발급.ps1 (서욱·밀리예브 후시닛딘 2명).
HTML/CSS 양식 블록은 손대지 않고, 데이터·납부기간만 교체한다."""
import io, sys

s = io.open('대학원_배치생성.ps1', encoding='utf-8-sig').read()
n = 0


def rep(old, new, cnt=1):
    global s, n
    if s.count(old) != cnt:
        print('!! 치환 실패(%d건): %s...' % (s.count(old), old[:70]))
        sys.exit(1)
    s = s.replace(old, new)
    n += 1


rep(r'''#  2026학년도 후기 대학원 신입생 배치 생성기''',
    r'''#  2026학년도 후기 대학원 — 추가 합격자 발급기 (서욱 / 밀리예브 후시닛딘)''')

# 학과 영문명 보강 — 토목공학과
rep(r'''  '전기전자공학과'='Electrical and Electronic Engineering';
}''',
    r'''  '전기전자공학과'='Electrical and Electronic Engineering';
  '토목공학과'='Civil Engineering';
}''')

# 납부기간 — 담당자 지시 2026. 8. 20. ~ 8. 21.
rep(r'''<td>July 22 – 24, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 7. 22. ~ 7. 24.)</span></td>''',
    r'''<td>August 20 – 21, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 8. 20. ~ 8. 21.)</span></td>''')

# 엑셀 읽기 블록 → 대상 2명 하드코딩
i = s.index('# ---------- 엑셀 읽기 ----------')
j = s.index('# ---------- PDF 생성 ----------')
s = s[:i] + r'''# ---------- 대상 (납부자 명단 기준) ----------
# 서욱      : r162 + 담당자 지시(입학금 550,000 / 수업료 3,820,000 / 수업연한 2년 6개월 / 계좌 870-400-579478)
# 밀리예브   : r236 값 그대로 (박사·토목공학과·TOPIK 4급 50%)
$SRC = @(
  @{ ExNo='2026412405'; Ko='서욱'; En='XU XU'; Birth='1989-12-03'; Sex='남'
     Nat='중국'; Deg='박사'; Dept='간호학과'; Trk='중국어'
     A=550000.0; B=3820000.0; C=0.0
     Dur='Sep. 2026 – Feb. 2029'; DurYr='2년 6개월'
     Acct='870-400-579478' }
  @{ ExNo='2026412416'; Ko='밀리예브 후시닛딘'; En='MELIEV KHUSNIDDIN KHASAN UGLI'; Birth='1995-08-10'; Sex='남'
     Nat='우즈베키스탄'; Deg='박사'; Dept='토목공학과'; Trk='한국어'
     A=550000.0; B=5015000.0; C=2507500.0
     Dur='Sep. 2026 – Feb. 2029'; DurYr='2년 6개월'
     Acct='추후 확정 · To be assigned' }
)

$rows = @()
foreach($x in $SRC){
  $D = [double]$x.A + [double]$x.B - [double]$x.C
  $pct = if([double]$x.B -gt 0){ [math]::Round(([double]$x.C / [double]$x.B) * 100, 1) } else { 0 }
  $rows += [pscustomobject]@{
    ExNo=$x.ExNo; KoName=$x.Ko; EnName=$x.En; Birth=$x.Birth
    GenderKo=$x.Sex; GenderEn=(GenderEn $x.Sex)
    CountryKo=$x.Nat; CountryEn=(CtryEn $x.Nat)
    Dept=$x.Dept; DegKo=(DegKo $x.Deg); CourseEn=(CourseEn $x.Deg $x.Dept)
    TrackKo=(TrackKo $x.Trk); TrackEn=(TrackEn $x.Trk)
    Duration=$x.Dur; DurationYr=$x.DurYr
    ATxt=(KRW $x.A); BTxt=(KRW $x.B); CTxt=(KRW $x.C); DTxt=(KRW $D); RateTxt=" · $pct%"
    Acct=$x.Acct; HasAcct=($x.Acct -notmatch '추후')
    CountryFolder=(CountryFolder $x.Nat)
  }
  Write-Host ("  " + $x.Ko + " / " + (KRW $D) + " / " + $x.Acct) -ForegroundColor Cyan
}
Write-Host ("대상 " + $rows.Count + "명") -ForegroundColor Cyan
$noAcct = @($rows | Where-Object { -not $_.HasAcct })
if($noAcct.Count -gt 0){ $noAcct | ForEach-Object { Write-Host ("  [계좌미배정] " + $_.KoName) -ForegroundColor Yellow } }

''' + s[j:]
n += 1

rep(r'''  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }''',
    r'''  if(Test-Path $tmpPdf){
    if(Test-Path -LiteralPath $pdfPath){ Remove-Item -LiteralPath $pdfPath -Force -ErrorAction Stop }
    Move-Item -LiteralPath $tmpPdf -Destination $pdfPath -Force -ErrorAction Stop
  }''')

io.open('대학원_추가발급.ps1', 'w', encoding='utf-8-sig').write(s)
print('생성 완료: 대학원_추가발급.ps1 (치환 %d건)' % n)

o = io.open('대학원_배치생성.ps1', encoding='utf-8-sig').read()
co = o[o.index('<style>'):o.index('</style>')]
cn = s[s.index('<style>'):s.index('</style>')]
print('CSS 블록 원본과 동일:', co == cn, '(%d bytes)' % len(co))
