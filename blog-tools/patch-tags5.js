// 네이버 블로그 자동화: 카테고리를 고를 때 본문 속 "채수학교습소" 글자(지도·카드)를 잘못 눌러
// 발행 창이 닫히는 문제 고치기 → 그래서 태그 칸을 못 찾고 태그가 빠졌다
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-tags5.js
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

if (s.includes('findCategoryOption')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}

const oldCat = `        const opt = this.frame.getByText(categoryName, { exact: true }).last();
        if (await opt.isVisible({ timeout: 2000 }).catch(() => false)) await opt.click();
        else this.log(\`카테고리 "\${categoryName}"를 찾지 못해 기본 카테고리로 발행합니다.\`);`;
const newCat = `        const opt = await this.findCategoryOption(categoryName);
        if (opt) {
          await opt.click();
          await sleep(500);
        } else {
          this.log(\`카테고리 "\${categoryName}"를 찾지 못해 기본 카테고리로 발행합니다.\`);
          await catBtn.click().catch(() => {}); // 열린 목록만 닫는다
          await sleep(400);
        }`;
if (!s.includes(oldCat)) fail('파일 모양이 예상과 달라요. (카테고리 부분)');
s = s.replace(oldCat, newCat);

const anchor = '  async publishLayer(post, settings) {';
const method = `  /**
   * 카테고리 목록에서 이름이 같은 항목 찾기.
   * 본문(지도·상담 카드)에도 같은 글자가 있어서, 본문 안의 글자는 건너뛴다.
   */
  async findCategoryOption(name) {
    for (let t = 0; t < 8; t++) {
      const loc = this.frame.getByText(name, { exact: true });
      const n = await loc.count().catch(() => 0);
      let pick = null;
      for (let i = 0; i < n; i++) {
        const el = loc.nth(i);
        if (!(await el.isVisible().catch(() => false))) continue;
        const inBody = await el.evaluate((e) => Boolean(e.closest('.se-content, .se-component, .se-documentTitle, .se-popup'))).catch(() => true);
        if (!inBody) pick = el;
      }
      if (pick) return pick;
      await sleep(250);
    }
    return null;
  }

${anchor}`;
if (!s.includes(anchor)) fail('파일 모양이 예상과 달라요. (발행 창 부분)');
s = s.replace(anchor, method);

const backup = file.replace(/\.js$/, '.backup5.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 카테고리를 고를 때 발행 창이 닫히는 문제를 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup5.js 로 보관했어요.\n');
