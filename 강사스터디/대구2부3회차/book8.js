// 강사스터디 교재 — 손글씨 강의노트(참고자료)를 정리한 판
// 사용법: node study_note.js <출력.pdf>
const fs = require('fs');
const path = require('path');
const katex = require('katex');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const OUT = process.argv[2];
const NM = path.join(__dirname, 'node_modules');
const tex = (s) => s.replace(/\$([^$]+)\$/g, (_, m) => katex.renderToString(m, { throwOnError: true, strict: false }));

// 꺾은선 그래프
function poly(o) {
  const W = o.w || 190, H = o.h || 150, L = 26, B = 24, T = 14, R = 14;
  const X = (x) => L + x / o.xm * (W - L - R), Y = (y) => H - B - y / o.ym * (H - B - T);
  let s = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Nanum Gothic" font-size="10.5">`;
  s += `<line x1="${L - 6}" y1="${Y(0)}" x2="${W - 4}" y2="${Y(0)}" stroke="#222"/><path d="M${W - 4} ${Y(0)} l-6 -3 v6z" fill="#222"/>`;
  s += `<line x1="${X(0)}" y1="${H - B + 6}" x2="${X(0)}" y2="4" stroke="#222"/><path d="M${X(0)} 4 l-3 6 h6z" fill="#222"/>`;
  for (const [x, t] of o.xt || []) s += `<line x1="${X(x)}" y1="${Y(0)}" x2="${X(x)}" y2="${Y(o.pts.reduce((m, p) => (Math.abs(p[0] - x) < 1e-9 ? p[1] : m), 0))}" stroke="#bbb" stroke-dasharray="2 2"/><text x="${X(x)}" y="${Y(0) + 14}" text-anchor="middle">${t}</text>`;
  for (const [y, t] of o.yt || []) s += `<line x1="${X(0)}" y1="${Y(y)}" x2="${X(o.pts.reduce((m, p) => (Math.abs(p[1] - y) < 1e-9 ? p[0] : m), 0))}" y2="${Y(y)}" stroke="#bbb" stroke-dasharray="2 2"/><text x="${X(0) - 5}" y="${Y(y) + 4}" text-anchor="end">${t}</text>`;
  for (const hl of o.hl || []) s += `<polyline points="${hl.map((p) => X(p[0]) + ',' + Y(p[1])).join(' ')}" fill="none" stroke="#9BE27A" stroke-width="7" stroke-linecap="round" opacity=".8"/>`;
  s += `<polyline points="${o.pts.map((p) => X(p[0]) + ',' + Y(p[1])).join(' ')}" fill="none" stroke="#111" stroke-width="1.6"/>`;
  for (const p of o.dots || []) s += `<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="2.6" fill="#D33"/>`;
  for (const l of o.lab || []) s += `<text x="${X(l[0])}" y="${Y(l[1])}" fill="${l[3] || '#111'}" font-size="${l[4] || 10.5}">${l[2]}</text>`;
  return s + `<text x="${W - 70}" y="12" font-size="10.5">${o.name}</text></svg>`;
}
const fG = (extra = {}) => poly({ name: 'y=f(x)', xm: 3.3, ym: 3.3, pts: [[0, 0], [1, 2], [3, 3]], xt: [[1, '1'], [3, '3']], yt: [[2, '2'], [3, '3']], ...extra });
const gG = (extra = {}) => poly({ name: 'y=g(x)', xm: 3.3, ym: 3.3, pts: [[0, 0], [1.5, 3], [3, 0]], xt: [[1.5, '3/2'], [3, '3']], yt: [[3, '3']], ...extra });
const gfG = poly({ name: 'y=g(f(x))', w: 230, h: 170, xm: 3.3, ym: 3.3, pts: [[0, 0], [0.75, 3], [1, 2], [3, 0]], xt: [[0.75, '3/4'], [1, '1'], [3, '3']], yt: [[2, '2'], [3, '3']], dots: [[0.75, 3], [1, 2]],
  hl: [[[0, 0], [0.75, 3]], [[0.75, 3], [1, 2]], [[1, 2], [3, 0]]] });

const map = `<svg width="210" height="150" viewBox="0 0 210 150" font-family="Nanum Gothic" font-size="12">
<text x="22" y="14">X</text><text x="98" y="14">Y</text><text x="172" y="14">Z</text>
<text x="55" y="11" font-size="11" fill="#C2622B">f</text><text x="132" y="11" font-size="11" fill="#1F7A8C">g</text>
<line x1="34" y1="10" x2="92" y2="10" stroke="#333"/><line x1="110" y1="10" x2="166" y2="10" stroke="#333"/>
${[1, 2, 3, 4].map((v, i) => `<text x="24" y="${36 + i * 24}">${v}</text><line x1="34" y1="${32 + i * 24}" x2="92" y2="${32 + i * 24}" stroke="#555" marker-end="url(#a)"/>`).join('')}
<rect x="94" y="22" width="16" height="96" rx="7" fill="#FFF3A0"/>
${[1, 2, 3, 4].map((v, i) => `<text x="98" y="${36 + i * 24}">${v}</text>`).join('')}
<circle cx="102" cy="132" r="9" fill="#9BE27A"/><text x="98" y="136">5</text>
<rect x="168" y="22" width="16" height="48" rx="7" fill="#FFD8B0"/><text x="172" y="36">1</text><text x="172" y="60">2</text>
<defs><marker id="a" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6z" fill="#555"/></marker></defs></svg>`;

const css = `
@page{size:A4;margin:14mm 14mm 16mm}
*{box-sizing:border-box}
body{margin:0;font-family:'Nanum Gothic',sans-serif;color:#1d2433;font-size:10pt;line-height:1.75;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.katex{font-size:1.05em}
.cover{height:265mm;display:flex;flex-direction:column;justify-content:center;align-items:center;background:linear-gradient(160deg,#0f3b40,#0b2a30 55%,#14656b);color:#fff;border-radius:4mm;page-break-after:always}
.cover .tag{background:#1fb5b5;color:#062a2d;font-weight:800;border-radius:99px;padding:1mm 5mm;font-size:10pt}
.cover .no{font-size:90pt;font-weight:800;line-height:1;margin:8mm 0 4mm}
.cover h1{margin:0;font-size:28pt;letter-spacing:2pt}
.cover p{opacity:.8;margin-top:6mm}
h2{break-after:avoid;font-size:15pt;margin:0 0 4mm;padding:2mm 4mm;border-left:5px solid #17a2a2;background:#eaf7f7;color:#0f3b40}
.card{border:1px solid #cfe3e3;border-radius:3mm;margin:0 0 5mm;break-inside:avoid;overflow:hidden}
.card .h{background:#0f3b40;color:#fff;padding:1.6mm 4mm;font-weight:800;display:flex;gap:3mm;align-items:center}
.card .h .k{background:#1fb5b5;color:#062a2d;border-radius:2mm;padding:0 2.5mm;font-size:8.5pt}
.card .b{padding:3mm 5mm}
.row{display:flex;gap:6mm;align-items:center;flex-wrap:wrap}
.wrong{border:1.5px solid #D33;background:#fff4f3;border-radius:2mm;padding:2mm 4mm;margin:2mm 0}
.wrong b{color:#D33}
.ok{border:1.5px solid #2e8b57;background:#f1faf4;border-radius:2mm;padding:2mm 4mm;margin:2mm 0}
.ans{display:inline-block;background:#2E6B4F;color:#fff;font-weight:800;border-radius:2mm;padding:.5mm 4mm;margin-top:2mm}
.tip{margin-top:3mm;background:#fff6e5;border-left:4px solid #f0a020;padding:2mm 4mm;border-radius:0 2mm 2mm 0}
.tip b{color:#b06a00}
.hl1{background:#FFF3A0}.hl2{background:#FFD8B0}.hl3{background:#C9F0FF}
ol,ul{margin:1mm 0;padding-left:6mm}
.step{display:grid;grid-template-columns:22mm 1fr;gap:1mm 3mm;margin:1mm 0}
.step .c{font-weight:800;color:#17777a}
.src{font-size:8pt;color:#8B95A1;text-align:right;margin-top:-2mm;margin-bottom:3mm}
`;

const body = require('./part8.js');

const fonts = ['katex/dist/katex.min.css', '@fontsource/nanum-gothic/400.css', '@fontsource/nanum-gothic/700.css', '@fontsource/nanum-gothic/800.css']
  .map((f) => `<link rel="stylesheet" href="file://${path.join(NM, f)}">`).join('');
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>강사스터디 8 함수</title>${fonts}<style>${css}</style></head><body>${tex(body)}</body></html>`;
(async () => {
  const hp = OUT.replace(/\.pdf$/, '.html');
  fs.writeFileSync(hp, html);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage();
  await p.goto('file://' + hp, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: OUT, printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:7.5pt;color:#888;text-align:center;font-family:sans-serif">채수학 · 강사스터디 대구 2부 3회차 · <span class="pageNumber"></span></div>' });
  await b.close();
  console.log('ok', OUT);
})();
