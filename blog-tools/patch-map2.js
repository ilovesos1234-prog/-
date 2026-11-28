// 네이버 블로그 자동화: 발행 버튼을 누르기 전에 남아 있는 팝업(지도 창 등)을 닫는다
// 증상: "se-popup-dim ... intercepts pointer events" 로 발행 버튼을 30초 동안 못 누름
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-map2.js
const fs = require('fs');
const path = require('path');

const file = path.join(process.cwd(), 'src', 'publisher', 'naverEditor.js');
const fail = (msg) => {
  console.log('\n[실패] ' + msg + ' (원본은 그대로예요)\n이 화면을 캡처해서 Claude에게 보여주세요.\n');
  process.exit(1);
};
if (!fs.existsSync(file)) fail('src\\publisher\\naverEditor.js 를 찾지 못했어요. server.js 가 있는 폴더에서 실행해 주세요.');

const raw = fs.readFileSync(file, 'utf8');
const crlf = raw.includes('\r\n');
let s = raw.replace(/\r\n/g, '\n');
if (s.includes('closeLeftoverPopups')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}

const anchor = '  async publishLayer(post, settings) {\n';
const open = `    await this.frame.locator(SEL.publishOpen).first().click();\n`;
const i = s.indexOf(anchor);
if (i < 0 || s.indexOf(open, i) !== i + anchor.length) fail('파일 모양이 예상과 달라요. (발행 창 부분)');

const method = `  /** 본문 위에 남아 있는 팝업(지도 창 등)을 모두 닫는다 — 열려 있으면 발행 버튼이 눌리지 않는다 */
  async closeLeftoverPopups() {
    for (let t = 0; t < 4; t++) {
      const dim = this.frame.locator('.se-popup-dim');
      const n = await dim.count().catch(() => 0);
      let open = false;
      for (let k = 0; k < n; k++) if (await dim.nth(k).isVisible().catch(() => false)) open = true;
      if (!open) return;
      if (t === 0) this.log('열려 있는 팝업 창을 닫고 발행합니다.');
      const x = this.frame.locator('.se-popup-close-button, .se-popup button[class*="close"]');
      const m = await x.count().catch(() => 0);
      let clicked = false;
      for (let k = 0; k < m; k++) {
        if (await x.nth(k).isVisible().catch(() => false)) {
          await x.nth(k).click().catch(() => {});
          clicked = true;
          break;
        }
      }
      if (!clicked) await this.page.keyboard.press('Escape').catch(() => {});
      await sleep(800);
    }
  }

${anchor}    await this.closeLeftoverPopups();
`;
s = s.slice(0, i) + method + s.slice(i + anchor.length);

const backup = file.replace(/\.js$/, '.backup-map2.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 발행 전에 남은 팝업 창을 닫도록 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup-map2.js 로 보관했어요.\n');
