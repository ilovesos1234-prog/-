// 네이버 블로그 자동화: 컴퓨터를 켜면 프로그램이 저절로 켜지고 대시보드가 열리게 한다
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node make-autostart.js
// 끄려면:  node make-autostart.js 끄기
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const cwd = process.cwd();
if (process.platform !== 'win32') {
  console.log('\n[실패] 윈도우 컴퓨터에서만 쓸 수 있어요.\n');
  process.exit(1);
}
if (!fs.existsSync(path.join(cwd, 'server.js'))) {
  console.log('\n[실패] server.js 가 있는 폴더(네이버블로그자동화)에서 실행해 주세요.\n');
  process.exit(1);
}

const startup = path.join(process.env.APPDATA, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup');
const lnk = path.join(startup, '블로그자동화.lnk');

if ((process.argv[2] || '').includes('끄')) {
  if (fs.existsSync(lnk)) fs.unlinkSync(lnk);
  console.log('\n[완료] 자동 시작을 껐어요.\n');
  process.exit(0);
}

// 1) 프로그램 폴더에 시작 파일 (영어만 써서 글자가 깨지지 않게)
const bat = path.join(cwd, 'autostart.bat');
fs.writeFileSync(bat, '@echo off\r\ncd /d "%~dp0"\r\nnode server.js --open\r\n', 'ascii');

// 2) 윈도우 시작 프로그램 폴더에 바로 가기 (한글 경로도 되도록 PowerShell 로 만든다)
const q = (s) => "'" + String(s).replace(/'/g, "''") + "'";
const ps = [
  `$s = (New-Object -ComObject WScript.Shell).CreateShortcut(${q(lnk)})`,
  `$s.TargetPath = ${q(bat)}`,
  `$s.WorkingDirectory = ${q(cwd)}`,
  `$s.WindowStyle = 7`,
  `$s.Description = '네이버 블로그 자동화'`,
  `$s.Save()`,
].join('; ');
try {
  execFileSync('powershell.exe', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', Buffer.from(ps, 'utf16le').toString('base64')], { stdio: 'pipe' });
} catch (e) {
  console.log('\n[실패] 시작 프로그램에 넣지 못했어요: ' + String(e.stderr || e.message).slice(0, 300) + '\n이 화면을 캡처해서 보여주세요.\n');
  process.exit(1);
}
if (!fs.existsSync(lnk)) {
  console.log('\n[실패] 바로 가기가 만들어지지 않았어요. 이 화면을 캡처해서 보여주세요.\n');
  process.exit(1);
}
console.log('\n[성공] 이제 컴퓨터를 켜면 블로그 자동화가 저절로 켜지고 대시보드가 열려요!');
console.log('  - 까만 창은 작업표시줄에 작게(최소화) 떠 있어요. 닫지 마세요.');
console.log('  - 끄고 싶으면:  node make-autostart.js 끄기\n');
