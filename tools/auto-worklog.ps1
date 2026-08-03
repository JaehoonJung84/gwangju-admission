# =============================================================
#  GU 자동 작업 저장: git 자동 커밋·푸시 + (선택) Notion 업로드
#  예약 작업(GU-AutoWorklog)이 1시간마다 실행. 수동 실행도 가능.
#  로그: C:\projects\tools\autosave.log
# =============================================================
$ErrorActionPreference = 'Continue'
$LogFile = 'C:\projects\tools\autosave.log'
function Log($msg){ ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg) | Add-Content -Encoding UTF8 $LogFile }

# ---------- 1) git 자동 커밋 + 푸시 ----------
$Repos = @('C:\projects', 'C:\projects\work-notes')
foreach($repo in $Repos){
  if(-not (Test-Path (Join-Path $repo '.git'))){ continue }
  Set-Location $repo
  $dirty = git status --porcelain 2>$null
  if($dirty){
    git add -A 2>$null | Out-Null
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    git commit -m "auto: 작업 자동 저장 ($stamp)" 2>$null | Out-Null
    Log "$repo : 자동 커밋 생성 ($stamp)"
  }
  $ahead = git rev-list --count '@{u}..HEAD' 2>$null
  if($ahead -and [int]$ahead -gt 0){
    $out = git push origin HEAD 2>&1
    if($LASTEXITCODE -eq 0){ Log "$repo : $ahead 개 커밋 푸시 완료" }
    else { Log "$repo : 푸시 실패 - $out" }
  }
}

# ---------- 1.5) 작업일지 md 자동 업로드 (설정 파일 있을 때만) ----------
# 변경 감지는 notion_upload.py 가 한다 (해시 같으면 SKIP, 바뀌면 기존 페이지 교체).
$CfgPath0 = 'C:\projects\tools\autosave-config.json'
if(Test-Path $CfgPath0){
  $mdFiles = Get-ChildItem 'C:\Users\user\Desktop\★국제협력처\작업일지_Claude_*.md' -ErrorAction SilentlyContinue
  foreach($md in $mdFiles){
    $r = & python 'C:\projects\tools\notion_upload.py' $md.FullName 2>&1
    if("$r" -match '^OK'){ Log "작업일지 Notion 업로드(갱신): $($md.Name)" }
    elseif("$r" -match '^SKIP'){ }
    else { Log "작업일지 업로드 실패: $($md.Name) - $r" }
  }
}

# ---------- 2) Notion 업로드 (설정 파일 있을 때만) ----------
# C:\projects\tools\autosave-config.json 형식:
#   { "notionToken": "ntn_xxx", "notionParentPageId": "페이지ID(하이픈 포함 32자)" }
$CfgPath = 'C:\projects\tools\autosave-config.json'
if(Test-Path $CfgPath){
  try {
    $cfg = Get-Content -Raw -Encoding UTF8 $CfgPath | ConvertFrom-Json
    if($cfg.notionToken -and $cfg.notionParentPageId){
      $today = Get-Date -Format 'yyyy-MM-dd'
      $lines = @()
      foreach($repo in $Repos){
        if(-not (Test-Path (Join-Path $repo '.git'))){ continue }
        Set-Location $repo
        $cl = git log --since=midnight --pretty=format:'%h %s' 2>$null
        if($cl){ $lines += "[$([IO.Path]::GetFileName($repo))]"; $lines += ($cl -split "`n") }
      }
      if($lines.Count -gt 0){
        $marker = Join-Path 'C:\projects\tools' ("notion_done_" + $today + "_" + ($lines -join '').GetHashCode() + ".flag")
        if(-not (Test-Path $marker)){
          $blocks = @()
          $blocks += @{ object='block'; type='heading_2'; heading_2=@{ rich_text=@(@{ type='text'; text=@{ content="🗂️ $today 자동 커밋 기록" } }) } }
          foreach($l in $lines){
            $blocks += @{ object='block'; type='bulleted_list_item'; bulleted_list_item=@{ rich_text=@(@{ type='text'; text=@{ content=[string]$l } }) } }
          }
          $body = @{
            parent = @{ page_id = $cfg.notionParentPageId }
            properties = @{ title = @{ title = @(@{ type='text'; text=@{ content="📋 작업 자동 기록 $today $(Get-Date -Format 'HH:mm')" } }) } }
            children = $blocks
          } | ConvertTo-Json -Depth 10
          $hdr = @{ 'Authorization' = "Bearer $($cfg.notionToken)"; 'Notion-Version' = '2022-06-28'; 'Content-Type' = 'application/json' }
          try {
            Invoke-RestMethod -Method Post -Uri 'https://api.notion.com/v1/pages' -Headers $hdr -Body ([Text.Encoding]::UTF8.GetBytes($body)) | Out-Null
            New-Item -ItemType File -Path $marker -Force | Out-Null
            Get-ChildItem 'C:\projects\tools\notion_done_*.flag' | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force
            Log "Notion 업로드 완료 ($($lines.Count)줄)"
          } catch { Log "Notion 업로드 실패: $($_.Exception.Message)" }
        }
      }
    }
  } catch { Log "Notion 설정 읽기 실패: $($_.Exception.Message)" }
} else {
  Log "Notion 설정 없음(autosave-config.json) - git만 저장"
}
