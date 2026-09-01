# 광주대 전자결재 SetSize 오류 방지 확장

## 무엇을 고치나
전자결재 > 결재진행 화면에서 반복되던 경고를 없앤다.

```
[WordController.SetSize] : 최소사이즈 범위를 벗어 났습니다.
```

## 원인 (그룹웨어 서버 코드의 버그)
`/nanum/cflow/document/sanc/inprogress/sanc_inprogresslist_preview.jsp`

```js
if (documentHeight < 150) documentHeight = 150;        // 최소 150 으로 보정한 뒤
var bandDivHeight = $("#bandDiv").outerHeight(true);   // 문서정보 띠
var tabHeadHeight = $("#tabHead").outerHeight(true);   // 탭 머리
NEditorCtrl.SetSize(documentWidth - 6,
                    documentHeight - bandDivHeight - tabHeadHeight - 2);  // 다시 빼서 0 이하가 됨
```

`/nanum/component/wordcontroller/`

```js
if (b < 1 || d < 1) { this.msgBox("[WordController.SetSize] : 최소사이즈 범위를 벗어 났습니다."); return false }
```

미리보기 영역이 좁으면 뺄셈 결과가 0 이하가 되어 경고가 뜬다.
미리보기를 그릴 때마다 `$(window).resize()` 를 직접 호출하므로 계속 반복된다.

## 조치
`SetSize` 에 들어가는 값이 1 미만이면 1 로 올려 전달한다.
전산팀이 서버에서 `Math.max(1, ...)` 로 고치는 것과 같은 효과이며,
값 보정 외에 어떤 동작도 가로채지 않는다.

## 설치 (크롬)
1. 주소창에 `chrome://extensions` 입력
2. 오른쪽 위 **개발자 모드** 켜기
3. **압축해제된 확장 프로그램을 로드** 클릭 → `C:\projects\gw-sanc-fix` 폴더 선택

크롬을 껐다 켜도 유지된다. 빼려면 같은 화면에서 삭제하면 된다.

## 검증
```
node test/selftest.js
```
실제 계산식과 실제 검사 로직을 재현해, 오류 조건이 정상 처리되는지 확인한다.

## 근본 해결
서버 코드 수정이 정식 해결이다. 전산팀 전달용 요약은 위 "원인" 절 그대로 쓰면 된다.
