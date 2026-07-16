#!/bin/bash
# 차수 이동: 차수3에서 삭제 → 차수2로 신규 등록(2단계) → 결과 출력
#   ./move_chasu.sh 04 05 06 ...
# ⚠ 삭제는 복구 불가. 데이터는 data/*.json 에 있으므로 재등록은 가능.
cd "$(dirname "$0")"
FROM_SEMS=3
TO_CHASU=2

for n in "$@"; do
  f=$(ls data/${n}_*.json 2>/dev/null | head -1)
  if [ -z "$f" ]; then echo "❌ $n: JSON 없음"; continue; fi
  name=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$f','utf8')).name_kr)")

  d=$(node delete_applicant.js "$name" --sems=$FROM_SEMS --go 2>&1 | grep -oE '삭제를 완료했습니다|[^|]*오류[^|]*' | head -1)
  i=$(node fill_applicant.js "$f" submit --reset --chasu=$TO_CHASU 2>&1 | grep -E '시스템 메시지|MISS|❌' | head -2 | tr '\n' ' ')
  u=$(node fill_applicant.js "$f" submit --load  --chasu=$TO_CHASU 2>&1 | grep -E '시스템 메시지|MISS|❌' | head -2 | tr '\n' ' ')

  echo "── $n $name"
  echo "   삭제(차수3): ${d:-⚠ 확인필요}"
  echo "   등록(차수2): ${i:-⚠ 확인필요}"
  echo "   학력반영   : ${u:-⚠ 확인필요}"
done
