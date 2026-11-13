# -*- coding: utf-8 -*-
import io
p = r'C:/Users/user/.claude/projects/C--projects/memory/meeting-docs-pipeline.md'
s = io.open(p, encoding='utf-8').read()

old = r"""도구: `C:\projects\tools\hwp\prospectus_*` 가 아니라 세션 scratchpad 의 `mtg/bin/`
(`hak_build.py`+`hak_content.py`, `gyo_build.py`+`gyo_content.py`, `hpack.py`)."""
new = r"""도구: `C:\projects\tools\hwp\` 의 `hak2_build.py`+`hak2_content.py`(학처장, 2026-11-13 확립),
`gyo_build.py`+`gyo_content.py`(교무위원). 옛 `hak_build.py` 는 교무처 양식을 쓰는 구버전이라
표를 못 살린다 — **`hak2_*` 를 쓴다.**"""
assert old in s, 'old1'
s = s.replace(old, new)

old2 = '**맨 앞 통계표 두 개는 사람 손이 필요하다.**'
new2 = r"""**2026-11-13 갱신 — 직전 회차 HWP 를 양식으로 삼고 표 문단을 통째로 옮긴다.**
`hak2_build.py` 는 직전 회차 HWP→HWPX 로 바꾼 뒤 바깥표 세 칸
`cellAddr(colAddr=7, rowAddr=4/5/6)` = 실시/계획/협의 안의 문단만 갈아끼운다.
칸 찾기는 `<hp:subList>` 중첩을 **세어서 짝을 맞출 것** — 닫는 태그에서 `rindex` 로 여는 태그를
찾으면 표 안쪽 subList 를 잡는다(옛 `hak_build.replace_cell` 의 한계).
표는 **떠 있는 개체**라 `<hp:p>` 안 run 에 `<hp:tbl>` 로 들어 있고 제목은 `<hp:caption>` 이다 —
그 문단을 **통째로 떼어 다른 칸에 끼우면 표가 따라간다**(옮긴 문단의 바깥
`<hp:linesegarray>` 만 지운다). 그렇게 `[MOU 신규 체결 현황]` 표는 실시사항 맨 앞에 그대로 두고
`모집일정` 표는 계획사항으로 옮겨 재활용했다(20261118 초안).
서식 번호(20261111 실측): 부서 61/43, `① 제목` 60(run 53 공백3 + 43 기호 + 53 제목),
라벨폭6(`일  자`) 63/54, 라벨폭8(`대상부서`) 66/54, `※` 75/54, 빈 줄 63/54.
**작업 폴더는 `C:\projects\mtgwork` 처럼 짧은 경로로** — 긴 Temp scratchpad 경로에서는
COM `Open` 이 멈춘다. 멈춘 뒤에는 창 없는 유령이 남으니
`Get-Process Hwp | ? {$_.MainWindowHandle -eq 0} | % {$_.Kill()}` 로 지우고 다시 하면 된다
(이 명령은 auto 모드에서도 통과했다).

**(옛 양식) 맨 앞 통계표 두 개는 사람 손이 필요하다.**"""
assert old2 in s, 'old2'
s = s.replace(old2, new2, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('updated')
