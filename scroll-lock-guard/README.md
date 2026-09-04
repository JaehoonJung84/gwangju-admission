# scroll-lock-guard

엑셀에서 **방향키를 눌러도 셀이 안 움직이고 화면만 스크롤되는** 증상을 막는 가드.
원인은 언제나 하나 — **Scroll Lock 이 켜져 있는 것**이다. 엑셀 상태 표시줄 왼쪽 아래에
`Scroll Lock` 이라고 떠 있으면 그 상태다.

## 하는 일

3초마다 Scroll Lock 상태를 보고, 켜져 있으면

1. 그 순간의 정황을 `scroll-lock-guard.log` 에 남기고 (언제 / 원격접속 중이었는지 / 어느 창이 앞에 있었는지)
2. 곧바로 꺼 준다.

로그가 쌓이면 **누가 켜는지** 가 드러난다. 지금까지의 후보는 두 가지다.

- 손이 미끄러져 `ScrLk` 키를 누름 (PrtSc·Pause 옆이라 잘 눌린다)
- Chrome 원격 데스크톱으로 집에서 접속했다 끊을 때 잠금키 상태가 어긋남

`CRD원격접속중` 이 찍힌 기록이 반복되면 두 번째, `CRD대기중`·`CRD꺼짐` 뿐이면 첫 번째다.
마우스 속도 건(`C:\projects\mouse-guard`)처럼 **소프트웨어를 먼저 의심했다가 하드웨어가
범인이었던 전례**가 있으니, 로그가 말해줄 때까지 단정하지 말 것.

## 왜 "컴퓨터를 오래 켜놓으면" 그런가

시간이 흘러서가 아니다. Scroll Lock 은 **한 번 켜지면 끌 때까지 그대로**다.
재부팅하면 꺼진 상태로 시작하므로, 부팅 후 오래 지날수록 그 사이에 한 번 켜졌을 확률이
높아지는 것뿐이다. "재부팅하면 괜찮아지더라" 도 같은 이유다.

## 파일

| 파일 | 몫 |
|---|---|
| `scroll-lock-guard.ps1` | 감시·해제 본체 |
| `config.json` | `Enabled`(자동해제 켜고 끄기), `IntervalSeconds`(확인 주기) |
| `launcher.vbs` | 검은 창 안 뜨게 백그라운드로 띄우는 실행기 |
| `scroll-lock-guard.log` | 기록 |

Scroll Lock 을 일부러 쓰고 싶으면 `config.json` 의 `Enabled` 를 `false` 로 바꾼다
(그래도 켜진 사실은 로그에 남는다).

## 자동시작

로그온할 때 자동으로 뜬다.

```
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
  ScrollLockGuard = wscript.exe "C:\projects\scroll-lock-guard\launcher.vbs"
```

## 살아있는지 확인하는 법

프로세스 이름으로 찾으면 **검색 명령 자체가 걸려들어** 헛것을 본다.
반드시 뮤텍스로 확인할 것.

```powershell
try { [System.Threading.Mutex]::OpenExisting('Global\ScrollLockGuardSingleton'); '살아있음' }
catch { '꺼져 있음' }
```

수동으로 띄우려면 `wscript.exe C:\projects\scroll-lock-guard\launcher.vbs`.

## 만든 사람이 확인한 것 (2026-09-04)

- 증상 발생 당시 Scroll Lock 이 실제로 켜져 있었음 (엑셀 상태 표시줄 + `GetKeyState` 양쪽 확인)
- 껐더니 바로 정상 — 부팅 후 1일 15시간 경과 시점, Chrome 원격 데스크톱 상주 중이었음
- 가드가 1~3초 안에 잡아서 끄는 것을 두 번 실측
