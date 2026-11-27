// 네이버 블로그 자동화: 태그 넣는 방법을 "한 글자씩 치고 Enter"(태그가 실제로 붙던 방식)로 되돌리고,
// 추천 태그로 바뀌었는지 로그와 사진으로 남긴다.
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-tags4.js
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

if (s.includes('tagBoxText')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}
const start = s.indexOf('  async commitTag(input, tag) {');
if (start < 0) fail('먼저 patch-tags3.js 를 실행해야 해요.');
const end = s.indexOf('\n  }\n', start) + 4;

const method = `  /** 태그 칸 둘레의 글자 (붙은 태그 확인용) */
  async tagBoxText(input) {
    return input
      .evaluate((el) => {
        let box = el.parentElement;
        for (let i = 0; i < 4 && box && box.parentElement; i++) {
          if ((box.innerText || '').includes('#')) break;
          box = box.parentElement;
        }
        return (box && box.innerText) || '';
      })
      .catch(() => '');
  }

  /**
   * 태그 하나 넣기: 한 글자씩 치고 Enter (네이버가 태그로 인정하는 방식).
   * 추천 태그로 바뀌면 로그에 남긴다.
   */
  async commitTag(input, tag) {
    await input.click();
    await sleep(150);
    await this.typeText(tag);
    await sleep(300);
    if (!this.tagShotDone) {
      this.tagShotDone = true;
      await this.shot('tag-typing'); // 추천 목록이 뜨는지 확인용 사진
    }
    const before = await this.tagBoxText(input);
    await this.page.keyboard.press('Enter');
    await sleep(400);
    const after = await this.tagBoxText(input);
    const plain = (t) => t.replace(/[#\\s]/g, '');
    if (after !== before && !plain(after).includes(plain(tag))) {
      this.log(\`⚠️ 태그 "\${tag}" 가 다른 태그로 바뀐 것 같아요.\`);
    }
    return true;
  }
`;
s = s.slice(0, start) + method + s.slice(end);

const backup = file.replace(/\.js$/, '.backup4.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 태그를 한 글자씩 넣는 방식으로 되돌렸어요.');
console.log('바로 전 파일은 naverEditor.backup4.js 로 보관했어요.\n');
