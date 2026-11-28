// 네이버 블로그 자동화: 임시저장 버튼도 남은 팝업에 막히지 않게, 본문 입력이 끝날 때마다 팝업을 닫는다
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-map3.js  (patch-map2.js 다음)
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
if (s.includes('// [map3]')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}
if (!s.includes('async closeLeftoverPopups()')) fail('먼저 patch-map2.js 를 실행해야 해요.');

const swaps = [
  [
    `  async saveDraft() {\n    await this.frame.locator(SEL.saveDraft).first().click();`,
    `  async saveDraft() {\n    await this.closeLeftoverPopups(); // [map3] 남은 팝업이 저장 버튼을 가리지 않게\n    await this.frame.locator(SEL.saveDraft).first().click();`,
  ],
  [
    `    await pub.writeBody(post);\n`,
    `    await pub.writeBody(post);\n    await pub.closeLeftoverPopups(); // [map3]\n`,
  ],
  [
    `    await pub.shot('body-done');\n`,
    `    await pub.closeLeftoverPopups(); // [map3]\n    await pub.shot('body-done');\n`,
  ],
];
for (const [a, b] of swaps) {
  if (!s.includes(a)) fail('파일 모양이 예상과 달라요.');
  s = s.replace(a, b);
}

const backup = file.replace(/\.js$/, '.backup-map3.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 임시저장 전에도 남은 팝업 창을 닫도록 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup-map3.js 로 보관했어요.\n');
