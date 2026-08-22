# -*- coding: utf-8 -*-
"""교육비납입증명서.ps1 → 교육비납입증명서_2차.ps1
증명서 양식(HTML/CSS)은 그대로 두고, ①현재 엑셀 열 매핑 ②명단 필터 ③출력 폴더만 손본다."""
import io, sys
s = io.open('교육비납입증명서.ps1', encoding='utf-8-sig').read()
n = 0
def rep(old, new, cnt=1):
    global s, n
    if s.count(old) != cnt:
        print('!! 치환 실패(%d건): %s' % (s.count(old), old[:70])); sys.exit(1)
    s = s.replace(old, new); n += 1

# ① 명단 필터 파라미터 추가
rep(r'''  [int]$Limit         = 0,                         # 배치: 0=전체, N=앞에서 N건''',
    r'''  [int]$Limit         = 0,                         # 배치: 0=전체, N=앞에서 N건
  [string]$OnlyFile   = "",                        # 지정 시 이 파일의 영문명만 발급(한 줄에 1명)''')

# ② 출력 폴더 기본값 → 2차
rep(r'''  [string]$OutDir     = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\교육비납입증명서",''',
    r'''  [string]$OutDir     = "C:\Users\user\Desktop\★국제협력처\1. 학부\2026-2학기\교육비납입증명서\교육비납입증명서 2차",''')

# ③ 현재 엑셀 열 매핑으로 교정 (입학금 열이 N에 추가되어 그 이후가 한 칸씩 밀림)
rep(r'''    $verify = CellTxt $r 20              # T열 납부액 검증
    if($verify -ne '일치'){ continue }''',
    r'''    $verify = CellTxt $r 21              # U열 납부액 검증 (입학금 열 추가로 +1)
    if($verify -ne '일치'){ continue }''')

rep(r'''    $A = CellNum $r 14                   # N 수업료(A)
    $B = CellNum $r 16                   # P 장학금(B)
    $C = CellNum $r 17                   # Q 실납부액(C)
    $S = CellNum $r 19                   # S 납부금액
    $payd  = CellTxt $r 18               # R 납부일자
    if($A -le 0){ $A = $C + $B }         # 대학원: 수업료 열이 비어 있으면 실납부액+장학금으로 보정''',
    r'''    $adm = CellNum $r 14                 # N 입학금
    $tui = CellNum $r 15                 # O 수업료
    $A = $adm + $tui                     # 등록금(A) = 입학금 + 수업료 (대학원은 입학금 포함)
    $B = CellNum $r 17                   # Q 장학금(B)
    $C = CellNum $r 18                   # R 실납부액(C)
    $S = CellNum $r 20                   # T 납부금액
    $payd  = CellTxt $r 19               # S 납부일자
    if($A -le 0){ $A = $C + $B }         # 금액 열이 비어 있으면 실납부액+장학금으로 보정''')

# ④ 명단 필터 적용
rep(r'''  for($r=2;$r -le $last;$r++){''',
    r'''  $onlySet = @{}
  if($OnlyFile -ne ''){
    foreach($ln in (Get-Content -LiteralPath $OnlyFile -Encoding UTF8)){
      $k = ($ln.ToUpper() -replace '[^A-Z]','')
      if($k -ne ''){ $onlySet[$k] = $true }
    }
    Write-Host ("명단 필터: {0}명" -f $onlySet.Count) -ForegroundColor Cyan
  }
  for($r=2;$r -le $last;$r++){''')

rep(r'''    $en    = CellTxt $r 7                # G 영문명''',
    r'''    $en    = CellTxt $r 7                # G 영문명
    if($onlySet.Count -gt 0){
      $kk = ($en.ToUpper() -replace '[^A-Z]','')
      if(-not $onlySet.ContainsKey($kk)){ continue }
    }''')

io.open('교육비납입증명서_2차.ps1', 'w', encoding='utf-8-sig').write(s)
print('생성 완료: 교육비납입증명서_2차.ps1 (치환 %d건)' % n)
o = io.open('교육비납입증명서.ps1', encoding='utf-8-sig').read()
co = o[o.index('<style>'):o.index('</style>')]; cn = s[s.index('<style>'):s.index('</style>')]
print('CSS 블록 원본과 동일:', co == cn, '(%d bytes)' % len(co))
