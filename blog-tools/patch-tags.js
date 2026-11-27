// 네이버 블로그 자동화: 발행할 때 태그가 빠지는 문제 + 발행 창이 닫혀 멈추는 문제 고치기
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-tags.js
const fs = require('fs');
const path = require('path');

const file = path.join(process.cwd(), 'src', 'publisher', 'naverEditor.js');
if (!fs.existsSync(file)) {
  console.log('\n[실패] src\\publisher\\naverEditor.js 를 찾지 못했어요.');
  console.log('server.js 가 있는 폴더(네이버블로그자동화)에서 실행해 주세요.\n');
  process.exit(1);
}

const raw = fs.readFileSync(file, 'utf8');
const crlf = raw.includes('\r\n');
let s = raw.replace(/\r\n/g, '\n');

if (s.includes('publishLayerOpen')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요. 프로그램만 다시 켜 주세요.\n');
  process.exit(0);
}

const oldTags = `    const tagInput = this.frame.locator(SEL.tagInput).first();
    if (await tagInput.isVisible().catch(() => false)) {
      for (const tag of post.tags || []) {
        await tagInput.click();
        await this.typeText(tag);
        await this.page.keyboard.press('Enter');
        await sleep(rand(150, 320));
      }
    }
`;

const newTags = `    try {
      await this.addTags(post.tags || []);
    } catch (e) {
      this.log('⚠️ 태그 입력 중 문제가 생겨 태그 없이 계속합니다: ' + e.message.split('\\n')[0]);
    }
    // 태그 자동완성 목록이 확인 버튼을 가리지 않도록 포커스를 옮긴다
    await this.page.keyboard.press('Tab').catch(() => {});
    await sleep(500);
    // 발행 창이 닫혔으면 다시 연다
    if (!(await this.publishLayerOpen())) {
      this.log('발행 창이 닫혀 다시 엽니다.');
      await this.frame.locator(SEL.publishOpen).first().click();
      await sleep(1800);
    }
`;

const methods = `  /** 발행 창 안의 태그 칸 찾기 (창이 늦게 뜰 수 있어 5초까지 기다린다) */
  async findTagInput() {
    const loc = this.frame.locator(SEL.tagInput).first();
    for (let i = 0; i < 10; i++) {
      if (await loc.isVisible().catch(() => false)) return loc;
      await sleep(500);
    }
    return null;
  }

  /** 발행 창(확인 버튼)이 열려 있는지 */
  publishLayerOpen() {
    return this.frame.locator(SEL.publishConfirm).first().isVisible().catch(() => false);
  }

  /** 태그 넣기 — 결과를 로그에 남기고, 못 넣으면 넣을 태그를 알려준다 */
  async addTags(rawTags) {
    const tags = [...new Set(rawTags.map((t) => String(t).replace(/^#+/, '').replace(/\\s+/g, '').trim()).filter(Boolean))].slice(0, 30);
    if (!tags.length) {
      this.log('⚠️ 이 글에는 태그가 없습니다. (검토 화면 맨 아래 태그 칸을 확인해주세요)');
      return 0;
    }
    const input = await this.findTagInput();
    if (!input) {
      const shot = await this.shot('no-tag-input');
      this.log(\`⚠️ 태그 입력 칸을 찾지 못했습니다. 발행 후 직접 넣어주세요. (스크린샷: \${path.basename(shot)})\`);
      this.log('넣을 태그: ' + tags.map((t) => '#' + t).join(' '));
      return 0;
    }
    let added = 0;
    for (const tag of tags) {
      try {
        await input.click();
        await sleep(150);
        await this.typeText(tag);
        await this.page.keyboard.press('Enter');
        added++;
        await sleep(rand(250, 450));
        if (!(await this.publishLayerOpen())) {
          this.log('⚠️ 태그를 넣는 중 발행 창이 닫혀 태그 입력을 멈춥니다.');
          break;
        }
      } catch (e) {
        this.log(\`태그 "\${tag}" 입력 실패: \${e.message.split('\\n')[0]}\`);
      }
    }
    this.log(\`태그 \${added}개 입력: \${tags.slice(0, added).map((t) => '#' + t).join(' ')}\`);
    await this.shot('tags-added');
    return added;
  }

  async publishLayer(post, settings) {`;

const anchor = '  async publishLayer(post, settings) {';
if (!s.includes(oldTags) || !s.includes(anchor)) {
  console.log('\n[실패] 파일 모양이 예상과 달라서 고치지 않았어요. (원본은 그대로예요)');
  console.log('이 화면을 캡처해서 Claude에게 보여주세요.\n');
  process.exit(1);
}

const backup = file.replace(/\.js$/, '.backup.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');

s = s.replace(oldTags, newTags).replace(anchor, methods);
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');

console.log('\n[성공] naverEditor.js 를 고쳤어요!');
console.log('원본은 naverEditor.backup.js 로 보관했어요.');
console.log('이제 이 창을 닫고 프로그램을 다시 켜 주세요:  node server.js\n');
