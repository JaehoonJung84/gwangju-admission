# 모니터 전환 단축키 (monitor-hotkey)

집(모니터 1대)에서 사무실 PC(듀얼 모니터)를 원격으로 볼 때, 오른쪽 모니터에 뜬 창을
마우스로 끌어오지 않고 단축키로 옮긴다.

| 단축키 | 하는 일 |
|---|---|
| `Ctrl+Alt+←` | 현재 창을 왼쪽(주) 모니터로 |
| `Ctrl+Alt+→` | 현재 창을 오른쪽 모니터로 |
| `Ctrl+Alt+Space` | 현재 창을 반대쪽 모니터로 (토글) |
| `Ctrl+Alt+A` | 오른쪽에 숨은 창을 **전부** 왼쪽으로 모으기 |
| `Ctrl+Alt+Z` | `Ctrl+Alt+A` 로 옮긴 창을 원래 자리로 되돌리기 |
| `Ctrl+Alt+H` | 단축키 목록 보기 |

Windows 기본 `Win+Shift+←/→` 도 같은 일을 하지만, 원격 프로그램이 Win 키를
가로채는 경우가 많아 `Ctrl+Alt` 로 잡았다.

## 실행

로그인할 때 자동으로 뜬다 — 시작프로그램 폴더에 `모니터전환단축키.vbs` 를 넣어 두었다.

    %AppData%\Microsoft\Windows\Start Menu\Programs\Startup\모니터전환단축키.vbs

지금 바로 켜기 / 끄기:

    wscript C:\projects\monitor-hotkey\launcher.vbs      # 켜기 (창 없이)
    작업 관리자에서 pythonw.exe 종료                        # 끄기

## 단축키 없이 명령으로 쓰기

    python monhotkey.py --list      # 모니터·창 목록과 각 창이 있는 모니터
    python monhotkey.py --left      # 활성 창을 왼쪽으로
    python monhotkey.py --right     # 활성 창을 오른쪽으로
    python monhotkey.py --gather    # 전부 왼쪽으로
    python monhotkey.py --undo      # 되돌리기

## 동작 메모

- 모니터는 **왼쪽부터** 1, 2 번이다. 사무실 PC 는 왼쪽 `\.\DISPLAY2`(0~1920, 주),
  오른쪽 `\.\DISPLAY1`(1920~3840).
- 최대화된 창은 최대화를 풀고 옮긴 뒤 다시 최대화한다.
- 최소화된 창, 다른 가상 데스크톱의 창(DWM cloaked)은 건드리지 않는다.
- `Ctrl+Alt+A` 는 옮기기 전 창 위치를 `undo.json` 에 적어 두고, `Ctrl+Alt+Z` 가 그걸 읽어 되돌린다.
- 기록은 `monhotkey.log` 에 남는다.

관련 도구: `C:\projects\tools\openleft.py` (파일을 열면서 왼쪽 모니터로 보내기)
