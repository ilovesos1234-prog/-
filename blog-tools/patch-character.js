// 네이버 블로그 자동화: 글 끝 상담문의·톡톡 카드에 선생님 캐릭터 넣기
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-character.js
const fs = require('fs');
const path = require('path');

const BASE = 'https://raw.githubusercontent.com/ilovesos1234-prog/-/refs/heads/claude/upbeat-hawking-6hp1wt/blog-tools/';
const imagesDir = path.join(process.cwd(), 'src', 'images');
const target = path.join(imagesDir, 'contactCard.js');

async function get(name) {
  const res = await fetch(BASE + name);
  if (!res.ok) throw new Error(`${name} 받기 실패 (${res.status})`);
  return Buffer.from(await res.arrayBuffer());
}

(async () => {
  if (!fs.existsSync(target)) {
    console.log('\n[실패] src\\images\\contactCard.js 를 찾지 못했어요.');
    console.log('server.js 가 있는 폴더(네이버블로그자동화)에서 실행해 주세요.\n');
    process.exit(1);
  }
  try {
    const [card, point, heart] = await Promise.all([get('contactCard.js'), get('character/point.png'), get('character/heart.png')]);
    const backup = path.join(imagesDir, 'contactCard.backup.js');
    if (!fs.existsSync(backup)) fs.copyFileSync(target, backup);
    fs.mkdirSync(path.join(imagesDir, 'character'), { recursive: true });
    fs.writeFileSync(path.join(imagesDir, 'character', 'point.png'), point);
    fs.writeFileSync(path.join(imagesDir, 'character', 'heart.png'), heart);
    fs.writeFileSync(target, card);
    console.log('\n[성공] 상담 카드에 캐릭터를 넣었어요!');
    console.log('원본은 contactCard.backup.js 로 보관했어요.');
    console.log('캐릭터를 바꾸고 싶으면 src\\images\\character 폴더의 point.png(전화), heart.png(톡톡)를 바꾸면 돼요.');
    console.log('이제 프로그램을 다시 켜 주세요:  node server.js\n');
  } catch (e) {
    console.log('\n[실패] ' + e.message + ' — 원본은 그대로예요. 이 화면을 캡처해서 보여주세요.\n');
    process.exit(1);
  }
})();
