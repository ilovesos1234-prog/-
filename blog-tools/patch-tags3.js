// 네이버 블로그 자동화: 태그가 엉뚱한 "추천 태그"로 바뀌는 문제 고치기
// 원인: 한 글자씩 치는 동안 네이버 추천 목록이 뜨고, Enter 가 추천 태그를 골라버림
// 해결: 태그를 한 번에 넣고 바로 확정. 확정이 안 되면 예전 방식으로 다시 시도
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-tags3.js
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

if (s.includes('commitTag')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요. 프로그램만 다시 켜 주세요.\n');
  process.exit(0);
}
if (!s.includes('async addTags(')) fail('먼저 patch-tags.js 를 실행해야 해요.');

const oldLoop = `        await input.click();
        await sleep(150);
        await this.typeText(tag);
        await this.page.keyboard.press('Enter');
        added++;`;
const newLoop = `        if (await this.commitTag(input, tag)) added++;`;

const method = `  /**
   * 태그 하나 확정하기.
   * 한 글자씩 치면 네이버 "추천 태그" 목록이 떠서 Enter 가 엉뚱한 태그를 고른다.
   * 그래서 값을 한 번에 넣고 목록이 뜨기 전에 바로 Enter 로 확정한다.
   */
  async commitTag(input, tag) {
    await input.click();
    await input.fill('');
    await input.fill(tag);
    await this.page.keyboard.press('Enter');
    await sleep(350);
    const left = await input.inputValue().catch(() => '');
    if (!left) return true; // 칸이 비었으면 확정된 것
    // 한 번에 넣기를 네이버가 못 알아들었으면 예전처럼 쳐서 넣는다
    await input.fill('');
    await this.typeText(tag);
    await this.page.keyboard.press('Enter');
    await sleep(350);
    return true;
  }

  /** 태그 넣기 — 결과를 로그에 남기고, 못 넣으면 넣을 태그를 알려준다 */`;

if (!s.includes(oldLoop)) fail('파일 모양이 예상과 달라요.');
s = s.replace(oldLoop, newLoop);
const anchor = '  /** 태그 넣기 — 결과를 로그에 남기고, 못 넣으면 넣을 태그를 알려준다 */';
if (!s.includes(anchor)) fail('파일 모양이 예상과 달라요. (태그 넣기 설명 줄)');
s = s.replace(anchor, method);

const backup = file.replace(/\.js$/, '.backup3.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');

console.log('\n[성공] 태그가 엉뚱하게 바뀌는 문제를 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup3.js 로 보관했어요.');
console.log('이제 프로그램을 다시 켜 주세요:  node server.js\n');
