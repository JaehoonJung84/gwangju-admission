#!/bin/bash
# 배치 실행기
#   ./batch.sh check          → 전원 검토 모드(저장 안 함), MISS/경고만 요약
#   ./batch.sh save           → 전원 2단계 저장(INSERT → UPDATE)
# 대상: data/ 의 NN_*.json 중 인자로 준 순번들 (없으면 04~28 전체)
cd "$(dirname "$0")"
MODE="$1"; shift
LIST=("$@")
if [ ${#LIST[@]} -eq 0 ]; then
  FILES=$(ls data/[0-9][0-9]_*.json | grep -Ev 'data/(01|02)_')
else
  FILES=""
  for n in "${LIST[@]}"; do FILES="$FILES $(ls data/${n}_*.json 2>/dev/null)"; done
fi

for f in $FILES; do
  name=$(basename "$f" .json)
  if [ "$MODE" = "check" ]; then
    out=$(node fill_applicant.js "$f" --reset 2>&1)
    bad=$(echo "$out" | grep -E 'MISS|⚠|❌')
    dept=$(echo "$out" | grep 'gdhlDeptCd =')
    rb=$(echo "$out" | grep -A1 'read-back' | tail -1)
    if [ -n "$bad" ]; then
      echo "❌ $name"; echo "$bad" | sed 's/^/      /'
    else
      echo "✅ $name  |  ${dept#OK   }  |  $rb"
    fi
  elif [ "$MODE" = "save" ]; then
    m1=$(node fill_applicant.js "$f" submit --reset 2>&1 | grep -E '시스템 메시지|MISS|❌|⚠')
    m2=$(node fill_applicant.js "$f" submit --load  2>&1 | grep -E '시스템 메시지|MISS|❌|⚠')
    echo "── $name"
    echo "   INSERT: ${m1:-(메시지 없음)}"
    echo "   UPDATE: ${m2:-(메시지 없음)}"
  fi
done
