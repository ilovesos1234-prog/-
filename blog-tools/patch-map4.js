// 네이버 블로그 자동화: 지도 검색칸에 상호가 안 들어가는 문제 고치기
// (한 번에 넣기를 네이버가 무시함 → 한 글자씩 친다. 못 찾으면 지도 창을 확실히 닫는다)
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-map4.js  (patch-map.js 다음)
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
if (s.includes('// [map4]')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}
if (!s.includes('async closeMapPopup()')) fail('먼저 patch-map.js 를 실행해야 해요.');

const swaps = [
  [
    `    await input.click().catch(() => {});
    await input.fill(query);
    await this.page.keyboard.press('Enter');
    await sleep(3000);`,
    `    await input.click().catch(() => {});
    await input.fill('').catch(() => {});
    await this.typeText(query); // [map4] 한 글자씩 쳐야 네이버가 알아듣는다
    if (!(await input.inputValue().catch(() => ''))) await input.fill(query).catch(() => {});
    await sleep(300);
    await this.page.keyboard.press('Enter');
    await sleep(3000);`,
  ],
  [
    `      this.log(\`"\${query}" 장소를 찾지 못해 지도를 건너뜁니다.\`);
      await this.page.keyboard.press('Escape');
      await sleep(500);
      return false;`,
    `      this.log(\`"\${query}" 장소를 찾지 못해 지도를 건너뜁니다.\`);
      await this.closeMapPopup(); // [map4] 지도 창을 확실히 닫는다
      return false;`,
  ],
];
for (const [a, b] of swaps) {
  if (!s.includes(a)) fail('파일 모양이 예상과 달라요. (지도 검색 부분)');
  s = s.replace(a, b);
}

const backup = file.replace(/\.js$/, '.backup-map4.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 지도 검색칸에 상호가 들어가도록 고쳤어요!');
console.log('바로 전 파일은 naverEditor.backup-map4.js 로 보관했어요.\n');
