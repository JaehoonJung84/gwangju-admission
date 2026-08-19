# -*- coding: utf-8 -*-
"""대학원_배치생성.ps1 → 대학원_서욱.ps1 (단건 발급).
HTML/CSS 양식 블록은 손대지 않고, 데이터·수업연한·납부기간만 교체한다."""
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
    r'''#  2026학년도 후기 대학원 — 서욱(XU XU) 단건 발급기''')

rep(r'''  [string]$SealImage = "",''',
    r'''  [string]$Acct     = "870-400-579478",
  [string]$SealImage = "",''')

rep(r'''function Duration([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return 'Sep. 2026 – Aug. 2027' }
  return 'Sep. 2026 – Aug. 2028'
}
function DurationYr([string]$deg,[string]$dept){
  if($deg -notmatch '박사' -and $dept -match '법학'){ return '1년' }
  return '2년'
}''',
    r'''function Duration([string]$deg,[string]$dept){ return 'Sep. 2026 – Feb. 2029' }
function DurationYr([string]$deg,[string]$dept){ return '2년 6개월' }''')

rep(r'''<td>July 22 – 24, 2026 &nbsp;<span style='color:#6b7d70'>(2026. 7. 22. ~ 7. 24.)</span></td>''',
    r'''<td>To be announced &nbsp;<span style='color:#6b7d70'>(추후 안내)</span></td>''')

i = s.index('# ---------- 엑셀 읽기 ----------')
j = s.index('# ---------- PDF 생성 ----------')
s = s[:i] + r'''# ---------- 대상 (단건) ----------
# 출처: 납부자 명단 r162 + 담당자 지시(입학금 550,000 / 수업료 3,820,000 / 수업연한 2년 6개월)
$deg = '박사'; $dept = '간호학과'; $natKo = '중국'; $trk = '중국어'; $sexKo = '남'
$A = 550000.0; $B = 3820000.0; $C = 0.0; $D = $A + $B - $C
$pct = if($B -gt 0){ [math]::Round(($C / $B) * 100, 1) } else { 0 }

$rows = @([pscustomobject]@{
  ExNo='2026412405'; KoName='서욱'; EnName='XU XU'; Birth='1989-12-03'
  GenderKo=$sexKo; GenderEn=(GenderEn $sexKo)
  CountryKo=$natKo; CountryEn=(CtryEn $natKo)
  Dept=$dept; DegKo=(DegKo $deg); CourseEn=(CourseEn $deg $dept)
  TrackKo=(TrackKo $trk); TrackEn=(TrackEn $trk)
  Duration=(Duration $deg $dept); DurationYr=(DurationYr $deg $dept)
  ATxt=(KRW $A); BTxt=(KRW $B); CTxt=(KRW $C); DTxt=(KRW $D); RateTxt=" · $pct%"
  Acct=$Acct; HasAcct=$true
  CountryFolder=(CountryFolder $natKo)
})
Write-Host ("대상 1명 — 서욱 XU XU / 실납부액 " + (KRW $D) + " / 계좌 " + $Acct) -ForegroundColor Cyan

''' + s[j:]
n += 1

rep(r'''  if(Test-Path $tmpPdf){ Move-Item -Force $tmpPdf $pdfPath }''',
    r'''  if(Test-Path $tmpPdf){
    if(Test-Path -LiteralPath $pdfPath){ Remove-Item -LiteralPath $pdfPath -Force -ErrorAction Stop }
    Move-Item -LiteralPath $tmpPdf -Destination $pdfPath -Force -ErrorAction Stop
  }''')

io.open('대학원_서욱.ps1', 'w', encoding='utf-8-sig').write(s)
print('생성 완료: 대학원_서욱.ps1 (치환 %d건)' % n)

o = io.open('대학원_배치생성.ps1', encoding='utf-8-sig').read()
co = o[o.index('<style>'):o.index('</style>')]
cn = s[s.index('<style>'):s.index('</style>')]
print('CSS 블록 원본과 동일:', co == cn, '(%d bytes)' % len(co))
