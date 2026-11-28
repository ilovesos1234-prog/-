// 네이버 블로그 자동화: 대시보드 미리보기의 상담 카드를 실제 발행 카드(초록 + 캐릭터 3장)와 똑같이,
// 왼쪽 위 "우리 학원" → "채수학교습소"
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-preview.js  (patch-character.js 다음)
const fs = require('fs');
const path = require('path');

const cwd = process.cwd();
const pub = path.join(cwd, 'public');
const fail = (msg) => {
  console.log('\n[실패] ' + msg + ' (원본은 그대로예요)\n이 화면을 캡처해서 Claude에게 보여주세요.\n');
  process.exit(1);
};
if (!fs.existsSync(path.join(pub, 'app.js'))) fail('public\\app.js 를 찾지 못했어요. server.js 가 있는 폴더에서 실행해 주세요.');

// 1) 캐릭터 그림을 대시보드에서도 쓸 수 있게 복사
const chSrc = path.join(cwd, 'src', 'images', 'character');
const chDst = path.join(pub, 'character');
if (fs.existsSync(chSrc)) {
  fs.mkdirSync(chDst, { recursive: true });
  for (const f of fs.readdirSync(chSrc)) if (f.endsWith('.png')) fs.copyFileSync(path.join(chSrc, f), path.join(chDst, f));
}

const edit = (file, fn) => {
  const p = path.join(pub, file);
  const raw = fs.readFileSync(p, 'utf8');
  const crlf = raw.includes('\r\n');
  const out = fn(raw.replace(/\r\n/g, '\n'));
  if (out === null) return false;
  const bak = p + '.backup';
  if (!fs.existsSync(bak)) fs.writeFileSync(bak, raw, 'utf8');
  fs.writeFileSync(p, crlf ? out.replace(/\n/g, '\r\n') : out, 'utf8');
  return true;
};

let changed = 0;

// 2) app.js 미리보기
changed += edit('app.js', (s) => {
  if (s.includes('[preview-green]')) return null;
  const start = s.indexOf('  return `<div class="contact-preview">');
  if (start < 0) fail('app.js 모양이 예상과 달라요. (상담 안내 미리보기)');
  const end = s.indexOf('</div>`;\n}', start);
  if (end < 0) fail('app.js 모양이 예상과 달라요. (미리보기 끝)');
  const repl = `  // [preview-green] 실제 발행 카드와 같은 모양 (초록 + 캐릭터, 카드 3장)
  const nm = [...new Set(String(name || '').split('·').map((x) => x.trim()).filter(Boolean))].join(' · ') || '채수학교습소';
  const mapQ = place || address;
  const gcard = (ch, icon, title, line, sub, foot) =>
    \`<div class="gc"><img class="gc-ch" src="character/\${ch}.png" alt=""><div class="gc-col"><div class="gc-ic">\${icon}</div><b>\${title}</b><span>\${line}</span><small>\${sub}</small><em>\${foot}</em></div></div>\`;
  return \`<div class="contact-preview">
    <div class="cp-label">⬇️ 네이버에 발행할 때 자동으로 붙는 상담 안내</div>
    <hr class="b-divider">
    \${a.phone ? gcard('point', '📞', '상담문의', '클릭하시면<br>전화로 연결됩니다', '수업 중에는 연결이 어려우니<br>부재 시 문자 남겨주시면<br>연락드리겠습니다 :)', \`\${esc(nm)}<br>\${esc(a.phone)}\`) + \`<p class="cp-link">📞 <a href="tel:\${esc(tel)}">전화 상담 \${esc(a.phone)} (누르면 바로 연결됩니다)</a></p>\` : ''}
    \${talk ? gcard('heart', '💬', '톡톡 상담', '클릭하시면<br>네이버 톡톡으로 연결됩니다', '편한 시간에 메시지 남겨주세요<br>확인 후 바로 답변드리겠습니다 :)', esc(nm)) + \`<p class="cp-link">💬 <a href="\${esc(talk)}" target="_blank">네이버 톡톡으로 문의하기 (카톡처럼 편하게 남겨주세요)</a></p>\` : ''}
    \${mapQ ? \`<a href="https://map.naver.com/p/search/\${encodeURIComponent(mapQ)}" target="_blank" style="text-decoration:none">\` + gcard('bulb', '📍', '오시는 길', esc(address || mapQ).replace(/\\s+(?=\\d)/, '<br>'), '클릭하시면<br>네이버 지도로 연결됩니다', \`\${esc(nm)}\${a.phone ? '<br>' + esc(a.phone) : ''}\`) + '</a>' : ''}
    \${place ? \`<div class="cp-map">🗺️ 지도 · \${esc(place)}</div>\` : ''}
    \${address ? \`<p class="cp-link">📍 \${esc(address)}</p>\` : ''}
  `;
  return s.slice(0, start) + repl + s.slice(end);
});

// 3) 카드 모양
changed += edit('style.css', (s) => {
  if (s.includes('[preview-green]')) return null;
  return (
    s +
    `
/* [preview-green] 초록 상담 카드 미리보기 */
.gc { position: relative; max-width: 360px; aspect-ratio: 1 / 1; margin: 18px auto 8px; background: #1e6b45; color: #fff; border-radius: 6px; overflow: hidden; border-bottom: 8px solid #f2c661; }
.gc::before { content: ''; position: absolute; right: 4px; bottom: 16px; width: 150px; height: 150px; border-radius: 50%; background: #ffffff26; }
.gc-ch { position: absolute; right: 12px; bottom: 10px; height: 72%; }
.gc-col { position: absolute; left: 24px; top: 0; bottom: 0; width: 60%; display: flex; flex-direction: column; justify-content: center; gap: 6px; line-height: 1.35; text-align: left; }
.gc-ic { font-size: 28px; }
.gc b { font-size: 32px; letter-spacing: -1px; color: #fff; }
.gc span { font-size: 13px; font-weight: 700; }
.gc small { font-size: 11px; color: #d7eadf; }
.gc em { font-style: normal; font-size: 13px; font-weight: 800; color: #f2c661; }
`
  );
});

// 4) 왼쪽 위 이름
changed += edit('index.html', (s) => (s.includes('<small>우리 학원</small>') ? s.replace('<small>우리 학원</small>', '<small>채수학교습소</small>') : null));

console.log(changed ? '\n[성공] 대시보드 미리보기를 초록 카드 3장으로 바꿨어요! (왼쪽 위 이름도 채수학교습소)' : '\n[완료] 이미 고쳐진 파일이에요.');
console.log('브라우저에서 Ctrl+F5 로 새로고침하면 보여요.\n');
