// 네이버 블로그 자동화: 글 끝에 "오시는 길" 카드(전구 캐릭터)를 넣고, 누르면 네이버 지도로 연결
// (상담문의 · 톡톡 상담 · 오시는 길 → 카드 3장)
// 사용법: 프로그램 폴더(server.js 가 있는 곳)에서  node patch-mapcard.js
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
if (s.includes('// [mapcard]')) {
  console.log('\n[완료] 이미 고쳐진 파일이에요.\n');
  process.exit(0);
}

const anchor = `    const placeQuery = branch === 'elementary' && a.placeQueryElementary ? a.placeQueryElementary : a.placeQuery;\n`;
if (!s.includes(anchor)) fail('파일 모양이 예상과 달라요. (지도 부분)');
const block = `    // [mapcard] 오시는 길 카드 — 누르면 네이버 지도로 연결
    {
      const mapAddress = branch === 'elementary' && a.addressElementary ? a.addressElementary : a.address;
      const mapQuery = (branch === 'elementary' && a.placeQueryElementary ? a.placeQueryElementary : a.placeQuery) || mapAddress;
      if (mapQuery) {
        try {
          const file = path.join(dir, 'contact-map.png');
          await renderContactCard({ type: 'map', phone: a.phone, academyName, branch, address: mapAddress }, file);
          this.log('오시는 길 사진 + 지도 링크 넣는 중');
          await this.insertImage(file);
          await this.linkLastImage('https://map.naver.com/p/search/' + encodeURIComponent(mapQuery));
          await this.gotoEnd();
        } catch (e) {
          this.log('오시는 길 카드를 넣지 못했습니다: ' + e.message.split('\\n')[0]);
        }
      }
    }

`;
s = s.replace(anchor, block + anchor);

const backup = file.replace(/\.js$/, '.backup-mapcard.js');
if (!fs.existsSync(backup)) fs.writeFileSync(backup, raw, 'utf8');
fs.writeFileSync(file, crlf ? s.replace(/\n/g, '\r\n') : s, 'utf8');
console.log('\n[성공] 글 끝에 "오시는 길" 카드를 넣도록 고쳤어요! (카드 3장)');
console.log('바로 전 파일은 naverEditor.backup-mapcard.js 로 보관했어요.\n');
