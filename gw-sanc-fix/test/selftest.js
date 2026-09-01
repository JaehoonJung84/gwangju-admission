// fix.js 가 실제 오류 조건에서 경고를 막는지 검증
const fs = require('fs');
const vm = require('vm');

function makeCtrl(log) {
  return {
    // /nanum/component/wordcontroller/ 의 실제 검사 로직 재현
    SetSize: function (b, d) {
      if (typeof b !== 'number' || typeof d !== 'number') {
        log.push('숫자아님 경고'); return false;
      }
      if (b < 1 || d < 1) {
        log.push('[WordController.SetSize] : 최소사이즈 범위를 벗어 났습니다.'); return false;
      }
      log.push('정상 SetSize(' + b + ',' + d + ')'); return true;
    }
  };
}

// sanc_inprogresslist_preview.jsp 의 실제 계산식
function calc(clientW, clientH, bandDiv, tabHead) {
  let w = clientW, h = clientH;
  if (w < 300) w = 300;
  if (h < 150) h = 150;
  return [w - 6, h - bandDiv - tabHead - 2];
}

const cases = [
  ['미리보기 접힘(높이 0), 띠 표시',        0,   0,  30, 130],
  ['미리보기 아주 좁음(높이 100)',         1200, 100, 30, 130],
  ['미리보기 정상(높이 600)',              1200, 600, 30, 130],
  ['미리보기 완전 숨김(띠도 0)',            0,   0,   0,   0],
];

for (const patched of [false, true]) {
  console.log('\n===== ' + (patched ? '확장 적용 후' : '확장 적용 전') + ' =====');
  for (const [name, cw, ch, bd, th] of cases) {
    const log = [];
    const ctrl = makeCtrl(log);
    const sandbox = { window: {}, setInterval: () => {}, isFinite };
    sandbox.window.NEditorCtrl = ctrl;
    sandbox.window.addEventListener = () => {};
    if (patched) {
      vm.createContext(sandbox);
      vm.runInContext(fs.readFileSync('C:/projects/gw-sanc-fix/fix.js', 'utf8'), sandbox);
    }
    const [w, h] = calc(cw, ch, bd, th);
    sandbox.window.NEditorCtrl.SetSize(w, h);
    console.log('  ' + name.padEnd(30) + ' 계산값=(' + w + ',' + h + ') -> ' + log[0]);
  }
}
