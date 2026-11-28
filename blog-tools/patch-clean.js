// 네이버 블로그 자동화: 글쓰기 화면에 예전에 쓰던 내용이 남아 있으면 지우고 새로 쓴다
// 증상: 임시저장 제목이 "범어동 수학학원 경신범어동 초등 수학학원, 분수…" 처럼 두 글이 섞임
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-clean.js
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
if (s.includes('async clearEditor()')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}

const callOld = `    await pub.shot('editor-open');\n\n    log('제목 입력');\n`;
const callNew = `    await pub.shot('editor-open');\n    await pub.clearEditor();\n\n    log('제목 입력');\n`;
if (!s.includes(callOld)) fail('파일 모양이 예상과 달라요. (제목 입력 부분)');
s = s.replace(callOld, callNew);

const anchor = '  /** 도구 모음 드롭다운에서 옵션 고르기 */';
const method = `  /** 글쓰기 화면에 남은 예전 내용(자동 저장 복구 등)이 있는지 */
  editorDirty() {
    return this.frame
      .evaluate(() => {
        const title = (document.querySelector('.se-documentTitle')?.innerText || '').trim();
        const body = [...document.querySelectorAll('.se-component')].filter((c) => !c.classList.contains('se-documentTitle'));
        const text = body.map((c) => c.innerText || '').join('').trim();
        return Boolean(title) || body.length > 1 || Boolean(text);
      })
      .catch(() => false);
  }

  /** 예전 내용이 남아 있으면 모두 지우고 빈 화면에서 시작한다 */
  async clearEditor() {
    if (!(await this.editorDirty())) return;
    this.log('글쓰기 화면에 예전 내용이 남아 있어 지우고 새로 씁니다.');
    for (let t = 0; t < 3 && (await this.editorDirty()); t++) {
      const body = this.frame.locator(SEL.bodyParagraph).first();
      if (await body.count().catch(() => 0)) {
        await body.click().catch(() => {});
        await this.page.keyboard.press('Control+A');
        await this.page.keyboard.press('Delete');
        await sleep(600);
      }
      const title = this.frame.locator(SEL.title).first();
      await title.click().catch(() => {});
      await this.page.keyboard.press('Control+A');
      await this.page.keyboard.press('Delete');
      await sleep(400);
    }
    if (await this.editorDirty()) this.log('⚠️ 예전 내용을 다 지우지 못했어요. 저장된 글을 꼭 확인해 주세요.');
  }

${anchor}`;
if (!s.includes(anchor)) fail('파일 모양이 예상과 달라요. (도구 모음 부분)');
s = s.replace(anchor, method);

const backup = file.replace(/\.js$/, '.backup-clean.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 예전 내용이 섞이지 않도록 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup-clean.js 로 보관했어요.\n');
