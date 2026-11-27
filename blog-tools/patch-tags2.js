// 네이버 블로그 자동화: 발행하면 태그가 사라지는 문제 고치기 (patch-tags.js 다음 단계)
// 원인: 발행 창의 [발행] 확인 버튼이 여러 개 잡혀서 "창이 닫혔다"고 잘못 판단 → 창을 다시 열면서 태그가 지워짐
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-tags2.js
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

if (s.includes('visibleConfirm')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요. 프로그램만 다시 켜 주세요.\n');
  process.exit(0);
}
if (!s.includes('publishLayerOpen')) fail('먼저 patch-tags.js 를 실행해야 해요.');

const swaps = [
  // 1) 확인 버튼: 보이는 것만 고른다
  [
    `  /** 발행 창(확인 버튼)이 열려 있는지 */
  publishLayerOpen() {
    return this.frame.locator(SEL.publishConfirm).first().isVisible().catch(() => false);
  }`,
    `  /** 화면에 실제로 보이는 [발행] 확인 버튼 (같은 이름의 숨은 버튼은 건너뛴다) */
  async visibleConfirm() {
    const loc = this.frame.locator(SEL.publishConfirm);
    const n = await loc.count().catch(() => 0);
    for (let i = 0; i < n; i++) {
      if (await loc.nth(i).isVisible().catch(() => false)) return loc.nth(i);
    }
    return null;
  }

  /** 발행 창이 열려 있는지 — 확인 버튼이나 태그 칸 중 하나라도 보이면 열린 것 */
  async publishLayerOpen() {
    if (await this.visibleConfirm()) return true;
    return this.frame.locator(SEL.tagInput).first().isVisible().catch(() => false);
  }`,
  ],
  // 2) 태그 뒤 Tab 키 빼기 (포커스가 엉뚱한 곳으로 가지 않게)
  [
    `    // 태그 자동완성 목록이 확인 버튼을 가리지 않도록 포커스를 옮긴다
    await this.page.keyboard.press('Tab').catch(() => {});
    await sleep(500);
`,
    `    await sleep(500);
`,
  ],
  // 3) 마지막 확인 버튼도 보이는 것을 누른다
  [
    `    await this.frame.locator(SEL.publishConfirm).first().click();
    await this.page.waitForURL(`,
    `    const confirmBtn = (await this.visibleConfirm()) || this.frame.locator(SEL.publishConfirm).first();
    await confirmBtn.click();
    await this.page.waitForURL(`,
  ],
];

for (const [a, b] of swaps) {
  if (!s.includes(a)) fail('파일 모양이 예상과 달라요.');
  s = s.replace(a, b);
}

const backup = file.replace(/\.js$/, '.backup2.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');

console.log('\n[성공] 태그가 사라지는 문제를 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup2.js 로 보관했어요.');
console.log('이제 프로그램을 다시 켜 주세요:  node server.js\n');
