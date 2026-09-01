// 광주대 전자결재(나눔) 미리보기 SetSize 오류 방지
//
// 원인: /nanum/cflow/document/sanc/inprogress/sanc_inprogresslist_preview.jsp 의
//       $(window).on("resize") 에서
//         documentHeight 를 최소 150 으로 보정한 뒤
//         bandDivHeight(문서정보 띠) 와 tabHeadHeight(탭 머리) 를 다시 빼기 때문에
//       미리보기 영역이 좁으면 0 이하가 되어
//         NEditorCtrl.SetSize(가로, 0 이하)
//       가 호출되고, /nanum/component/wordcontroller/ 의
//         if (b < 1 || d < 1) msgBox("[WordController.SetSize] : 최소사이즈 범위를 벗어 났습니다.")
//       가 매번 경고창을 띄운다. 미리보기를 그릴 때마다 resize 를 직접 호출하므로 반복된다.
//
// 조치: SetSize 로 들어가는 값이 1 미만이면 1 로 올려서 전달한다.
//       (전산팀이 서버에서 Math.max(1, ...) 로 고치는 것과 같은 효과)
//       값을 바꾸는 것 외에 어떤 동작도 가로채지 않는다.

(function () {
  'use strict';

  var TARGETS = ['NEditorCtrl', 'AttachList'];
  var MARK = '__setSizeClamped__';

  function clamp(v) {
    if (typeof v !== 'number' || !isFinite(v)) return v; // 숫자가 아니면 원래 검사에 맡긴다
    return v < 1 ? 1 : v;
  }

  function patch(obj) {
    if (!obj || typeof obj !== 'object') return;
    if (typeof obj.SetSize !== 'function') return;
    if (obj.SetSize[MARK]) return;

    var original = obj.SetSize;
    var wrapped = function (w, h) {
      return original.call(this, clamp(w), clamp(h));
    };
    wrapped[MARK] = true;

    try {
      obj.SetSize = wrapped;
    } catch (e) {
      /* 쓰기 금지면 그대로 둔다 */
    }
  }

  function sweep() {
    for (var i = 0; i < TARGETS.length; i++) {
      try {
        patch(window[TARGETS[i]]);
      } catch (e) {
        /* 접근 불가한 프레임은 무시 */
      }
    }
  }

  sweep();
  setInterval(sweep, 500);
  window.addEventListener('DOMContentLoaded', sweep);
  window.addEventListener('load', sweep);
})();
