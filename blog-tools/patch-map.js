// 네이버 블로그 자동화: 지도(장소) 창에서 검색칸을 못 찾아 창이 열린 채 멈추는 문제 고치기
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-map.js
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
if (s.includes('closeMapPopup')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}

const swaps = [
  [
    `  mapSearchInput: '.se-popup input[type="text"], .se-popup input[type="search"]',`,
    `  mapSearchInput: 'input[placeholder*="장소"], .se-popup input[type="text"], .se-popup input[type="search"], .se-popup input:not([type])',`,
  ],
  [
    `    await this.frame.locator(SEL.mapBtn).first().click();
    await sleep(2000);
    const input = this.frame.locator(SEL.mapSearchInput).first();
    if (!(await input.isVisible().catch(() => false))) {
      this.log('장소 검색창을 찾지 못해 지도를 건너뜁니다.');
      return false;
    }`,
    `    await this.frame.locator(SEL.mapBtn).first().click();
    // 지도 창이 늦게 뜰 수 있어 10초까지 검색칸을 기다린다
    let input = null;
    for (let i = 0; i < 20 && !input; i++) {
      await sleep(500);
      const loc = this.frame.locator(SEL.mapSearchInput);
      const n = await loc.count().catch(() => 0);
      for (let k = 0; k < n; k++) {
        if (await loc.nth(k).isVisible().catch(() => false)) {
          input = loc.nth(k);
          break;
        }
      }
    }
    if (!input) {
      this.log('장소 검색창을 찾지 못해 지도를 건너뜁니다.');
      await this.closeMapPopup();
      return false;
    }
    await input.click().catch(() => {});`,
  ],
  [
    `  /** 장소(스마트플레이스 지도) 삽입 */`,
    `  /** 열려 있는 지도 창 닫기 (열린 채로 두면 다음 글자가 모두 막힌다) */
  async closeMapPopup() {
    const x = this.frame.locator('.se-popup-close-button, .se-popup button[class*="close"]').first();
    if (await x.isVisible().catch(() => false)) await x.click().catch(() => {});
    else await this.page.keyboard.press('Escape').catch(() => {});
    await sleep(800);
  }

  /** 장소(스마트플레이스 지도) 삽입 */`,
  ],
];
for (const [a, b] of swaps) {
  if (!s.includes(a)) fail('파일 모양이 예상과 달라요. (지도 부분)');
  s = s.replace(a, b);
}

const backup = file.replace(/\.js$/, '.backup-map.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 지도 창이 열린 채 멈추는 문제를 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup-map.js 로 보관했어요.\n');
