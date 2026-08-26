# -*- coding: utf-8 -*-
"""교육비납입증명서_2차.ps1 → _3차.ps1 : 시트 지정 + '납부일자 존재' 필터 + 과정 필터"""
import io, sys
s = io.open('교육비납입증명서_2차.ps1', encoding='utf-8-sig').read()
n = 0
def rep(old, new, cnt=1):
    global s, n
    if s.count(old) != cnt:
        print('!! 치환 실패(%d건): %s' % (s.count(old), old[:70])); sys.exit(1)
    s = s.replace(old, new); n += 1

rep(r'''  [string]$OnlyFile   = "",                        # 지정 시 이 파일의 영문명만 발급(한 줄에 1명)''',
    r'''  [string]$OnlyFile   = "",                        # 지정 시 이 파일의 영문명만 발급(한 줄에 1명)
  [string]$SheetName  = "중복 제외",               # 읽을 시트
  [string]$OnlyProc   = "석사,박사",               # 발급 대상 과정(쉼표 구분, 빈값=전체)
  [string]$SkipRows   = "",                        # 제외할 엑셀 행번호(쉼표 구분)''')

rep(r'''  [string]$OutDir     = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\교육비납입증명서\교육비납입증명서 2차",''',
    r'''  [string]$OutDir     = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\교육비납입증명서\교육비납입증명서 3차",''')

rep(r'''  $wb = $xl.Workbooks.Open($InputFile); $ws = $wb.Worksheets.Item(1)''',
    r'''  $wb = $xl.Workbooks.Open($InputFile)
  $ws = $null
  foreach($sh in $wb.Worksheets){ if($sh.Name -eq $SheetName){ $ws = $sh } }
  if(-not $ws){ $ws = $wb.Worksheets.Item(1) }
  Write-Host ("시트: " + $ws.Name) -ForegroundColor Cyan''')

# 필터: 검증='일치' → 납부일자 존재 + 과정 필터 + 행 제외
rep(r'''    $verify = CellTxt $r 21              # U열 납부액 검증 (입학금 열 추가로 +1)
    if($verify -ne '일치'){ continue }
    $proc  = CellTxt $r 2                # B 과정(학부/석사/박사)''',
    r'''    $proc  = CellTxt $r 2                # B 과정(학부/석사/박사)
    if($procSet.Count -gt 0 -and -not $procSet.ContainsKey($proc)){ continue }
    if($skipSet.ContainsKey([string]$r)){ Write-Host ("  제외(행 $r)") -ForegroundColor Yellow; continue }
    # 발급 기준: 납부일자(S열)에 실제 날짜가 있는 학생만
    $payCell = $ws.Cells.Item($r,19)
    $isDate = $false
    try { if($payCell.Value2 -is [double] -and $payCell.Value2 -gt 40000){ $isDate = $true } } catch {}
    if(-not $isDate){ continue }''')

rep(r'''  $onlySet = @{}''',
    r'''  $procSet = @{}
  foreach($p in ($OnlyProc -split ',')){ if($p.Trim() -ne ''){ $procSet[$p.Trim()] = $true } }
  $skipSet = @{}
  foreach($p in ($SkipRows -split ',')){ if($p.Trim() -ne ''){ $skipSet[$p.Trim()] = $true } }
  $onlySet = @{}''')

io.open('교육비납입증명서_3차.ps1', 'w', encoding='utf-8-sig').write(s)
print('생성 완료: 교육비납입증명서_3차.ps1 (치환 %d건)' % n)
o = io.open('교육비납입증명서_2차.ps1', encoding='utf-8-sig').read()
co = o[o.index('<style>'):o.index('</style>')]; cn = s[s.index('<style>'):s.index('</style>')]
print('CSS(양식) 동일:', co == cn, '(%d bytes)' % len(co))
