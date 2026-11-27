// 채수학 블로그 자동화 고침 모음 — 한 번에 받고 순서대로 적용한다
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node update.js
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const BASE = 'https://raw.githubusercontent.com/ilovesos1234-prog/-/refs/heads/claude/upbeat-hawking-6hp1wt/blog-tools/';
const STEPS = ['patch-tags.js', 'patch-tags2.js', 'patch-tags3.js', 'patch-tags4.js', 'patch-character.js'];
const dir = path.join(process.cwd(), 'blog-fix');

(async () => {
  if (!fs.existsSync(path.join(process.cwd(), 'server.js'))) {
    console.log('\n[실패] server.js 가 있는 폴더(네이버블로그자동화)에서 실행해 주세요.\n');
    process.exit(1);
  }
  fs.mkdirSync(dir, { recursive: true });
  for (const name of STEPS) {
    const res = await fetch(BASE + name + '?v=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) {
      console.log(`\n[실패] ${name} 받기 실패 (${res.status})\n`);
      process.exit(1);
    }
    fs.writeFileSync(path.join(dir, name), Buffer.from(await res.arrayBuffer()));
  }
  for (const name of STEPS) {
    console.log(`--- ${name}`);
    try {
      execFileSync(process.execPath, [path.join(dir, name)], { stdio: 'inherit', cwd: process.cwd() });
    } catch {
      console.log(`\n[멈춤] ${name} 에서 문제가 생겼어요. 이 화면을 캡처해서 보여주세요.\n`);
      process.exit(1);
    }
  }
  // 여러 글 한꺼번에 임시저장·발행하는 도구도 프로그램 폴더에 둔다
  const res = await fetch(BASE + 'batch.js?v=' + Date.now(), { cache: 'no-store' });
  if (res.ok) fs.writeFileSync(path.join(process.cwd(), 'batch.js'), Buffer.from(await res.arrayBuffer()));
  console.log('\n===== 모두 끝났어요! 이제  node server.js  로 프로그램을 켜 주세요. =====\n');
})();
