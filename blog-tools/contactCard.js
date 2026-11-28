// 글 마지막에 넣는 "상담문의 / 톡톡 상담" 이미지 (클릭하면 전화·톡톡으로 연결된다)
// 채수학교습소 버전: 왼쪽 글자 + 오른쪽 선생님 캐릭터 (src/images/character/point.png, heart.png)
const fs = require('fs');
const path = require('path');
const { newScrapePage } = require('../browser/browser');
const { THEMES } = require('./cover');

const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const DEFAULT_NAME = '채수학교습소';
const CHAR_DIR = path.join(__dirname, 'character');
// 채수학 초록 테마 (블로그 테마 색 대신 이 색을 쓴다)
const GREEN = { bg: '#1e6b45', ink: '#ffffff', accent: '#f2c661', sub: '#d7eadf' };

const PHONE_ICON = `<svg viewBox="0 0 24 24" width="110" height="110" fill="currentColor"><path d="M6.6 10.8c1.7 3.3 4.3 5.9 7.6 7.6l2.5-2.5c.3-.3.8-.4 1.2-.3 1.3.4 2.7.7 4.1.7.7 0 1.2.5 1.2 1.2V21c0 .7-.5 1.2-1.2 1.2C10.7 22.2 1.8 13.3 1.8 2.2 1.8 1.5 2.3 1 3 1h3.5c.7 0 1.2.5 1.2 1.2 0 1.4.2 2.8.7 4.1.1.4 0 .9-.3 1.2l-2.5 2.3z"/></svg>`;
const PIN_ICON = `<svg viewBox="0 0 24 24" width="110" height="110" fill="currentColor"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>`;
const TALK_ICON = `<svg viewBox="0 0 24 24" width="110" height="110" fill="currentColor"><path d="M12 2C6.5 2 2 5.8 2 10.4c0 2.9 1.9 5.5 4.7 7-.2.8-.8 2.8-.9 3.2-.1.5.2.5.4.4.2-.1 2.9-2 4.1-2.8.6.1 1.1.1 1.7.1 5.5 0 10-3.8 10-8.4S17.5 2 12 2z"/></svg>`;

/** 캐릭터 그림을 data URI로 (없으면 빈 문자열 → 캐릭터 없이 그린다) */
function characterUri(name) {
  try {
    return 'data:image/png;base64,' + fs.readFileSync(path.join(CHAR_DIR, `${name}.png`)).toString('base64');
  } catch {
    return '';
  }
}

/**
 * @param {'phone'|'talk'|'map'} type
 */
async function renderContactCard({ type = 'phone', phone = '', academyName = '', note = '', branch = 'both', address = '' }, dest) {
  const t = GREEN || THEMES[branch] || THEMES.both;
  const isPhone = type === 'phone';
  const isMap = type === 'map';
  const title = isMap ? '오시는 길' : isPhone ? '상담문의' : '톡톡 상담';
  // 주소는 동네와 번지 사이에서 줄을 바꾼다 (예: "대구 수성구 범어동\n261-33, 4층")
  const addr = String(address || '').trim().replace(/\s+(?=\d)/, '\n');
  const line = isMap ? addr || '클릭하시면 지도로 연결됩니다' : isPhone ? '클릭하시면\n전화로 연결됩니다' : '클릭하시면\n네이버 톡톡으로 연결됩니다';
  const sub = note || (isMap ? '클릭하시면\n네이버 지도로 연결됩니다' : isPhone ? '수업 중에는 연결이 어려우니\n부재 시 문자 남겨주시면\n연락드리겠습니다 :)' : '편한 시간에 메시지 남겨주세요\n확인 후 바로 답변드리겠습니다 :)');
  // 초등관·중고등관 이름이 같으면 한 번만 쓴다 (예: "채수학교습소 · 채수학교습소" → "채수학교습소")
  const name = [...new Set(String(academyName || '').split('·').map((s) => s.trim()).filter(Boolean))].join(' · ') || DEFAULT_NAME;
  const ch = characterUri(isMap ? 'bulb' : isPhone ? 'point' : 'heart');
  const icon = isMap ? PIN_ICON : isPhone ? PHONE_ICON : TALK_ICON;
  const showPhone = (isPhone || isMap) && phone;

  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    * { box-sizing: border-box; margin: 0; }
    body { width: 1000px; height: 1000px; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }
    .card { position: relative; width: 100%; height: 100%; background: ${t.bg}; color: ${t.ink}; overflow: hidden; }
    .col { position: absolute; left: 70px; top: 0; bottom: 0; width: ${ch ? 560 : 860}px; display: flex; flex-direction: column; justify-content: center; ${ch ? '' : 'align-items: center; text-align: center;'} }
    .icon { color: ${t.accent}; line-height: 0; }
    h1 { font-size: 118px; font-weight: 900; letter-spacing: -4px; color: #ffffff; line-height: 1.08; margin-top: 26px; }
    .line { font-size: 42px; font-weight: 800; margin-top: 26px; letter-spacing: -1px; line-height: 1.3; white-space: pre-line; }
    .sub { font-size: 29px; line-height: 1.55; margin-top: 24px; color: ${t.sub || t.ink}; white-space: pre-line; word-break: keep-all; }
    .foot { font-size: 34px; font-weight: 800; margin-top: 34px; color: ${t.accent}; line-height: 1.35; }
    .glow { position: absolute; right: 10px; bottom: 50px; width: 420px; height: 420px; border-radius: 50%; background: #fff; opacity: .16; }
    .card::after { content: ''; position: absolute; left: 0; right: 0; bottom: 0; height: 18px; background: ${t.accent}; }
    .ch { position: absolute; right: 36px; bottom: 36px; height: 700px; }
  </style></head><body>
    <div class="card">
      ${ch ? `<div class="glow"></div><img class="ch" src="${ch}">` : ''}
      <div class="col">
        <div class="icon">${icon}</div>
        <h1>${title}</h1>
        <div class="line">${esc(line)}</div>
        <div class="sub">${esc(sub)}</div>
        <div class="foot">${esc(name)}${showPhone ? `<br>${esc(phone)}` : ''}</div>
      </div>
    </div>
  </body></html>`;

  const page = await newScrapePage();
  try {
    await page.setViewportSize({ width: 1000, height: 1000 });
    await page.setContent(html, { waitUntil: 'load' });
    await page.screenshot({ path: dest, type: 'png' });
  } finally {
    await page.close();
  }
  return dest;
}

module.exports = { renderContactCard };
