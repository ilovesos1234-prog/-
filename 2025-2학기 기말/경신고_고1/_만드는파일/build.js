// 3종 세트(시험지 B4 · 손풀이 A4 · 분석표 A4) 생성
// 사용법: node build.js <출력폴더>
const fs = require('fs');
const path = require('path');
const katex = require('katex');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { META, Q } = require('./data.js');

const OUT = process.argv[2] || path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
const NM = path.join(__dirname, 'node_modules');

// ---------- 공통 ----------
const tex = (s) => s.replace(/\$([^$]+)\$/g, (_, m) =>
  katex.renderToString(m, { throwOnError: true, displayMode: false, strict: false }));
const CIRC = ['①', '②', '③', '④', '⑤'];
const LV = ['', '하', '중', '상', '최상'];

const fontCss = [
  'katex/dist/katex.min.css',
  '@fontsource/nanum-myeongjo/400.css', '@fontsource/nanum-myeongjo/700.css', '@fontsource/nanum-myeongjo/800.css',
  '@fontsource/nanum-gothic/400.css', '@fontsource/nanum-gothic/700.css', '@fontsource/nanum-gothic/800.css',
  '@fontsource/nanum-pen-script/400.css',
].map((f) => `<link rel="stylesheet" href="file://${path.join(NM, f)}">`).join('\n');

const page = (title, size, css, body) => `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>${title}</title>${fontCss}<style>
@page{size:${size};margin:${size.startsWith('210') ? '12mm 13mm' : '0'}}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.katex{font-size:1.06em}
${css}</style></head><body>${body}</body></html>`;

// ---------- 그래프(SVG) ----------
function plot(o) {
  const W = o.w || 300, H = o.h || 230, pad = 14;
  const X = (x) => pad + (x - o.x0) / (o.x1 - o.x0) * (W - 2 * pad);
  const Y = (y) => H - pad - (y - o.y0) / (o.y1 - o.y0) * (H - 2 * pad);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-family="Nanum Gothic" font-size="11">`;
  s += `<line x1="${X(o.x0)}" y1="${Y(0)}" x2="${X(o.x1)}" y2="${Y(0)}" stroke="#555" stroke-width=".8"/>`;
  s += `<line x1="${X(0)}" y1="${Y(o.y0)}" x2="${X(0)}" y2="${Y(o.y1)}" stroke="#555" stroke-width=".8"/>`;
  s += `<text x="${X(o.x1) - 6}" y="${Y(0) - 4}" fill="#555">x</text><text x="${X(0) + 4}" y="${Y(o.y1) + 9}" fill="#555">y</text>`;
  s += `<text x="${X(0) - 9}" y="${Y(0) + 11}" fill="#555">O</text>`;
  for (const a of o.asym || []) {
    if (a.x !== undefined) s += `<line x1="${X(a.x)}" y1="${Y(o.y0)}" x2="${X(a.x)}" y2="${Y(o.y1)}" stroke="#999" stroke-dasharray="3 3"/>`;
    else s += `<line x1="${X(o.x0)}" y1="${Y(a.y)}" x2="${X(o.x1)}" y2="${Y(a.y)}" stroke="${a.c || '#999'}" stroke-dasharray="3 3"/>`;
    if (a.t) s += `<text x="${a.x !== undefined ? X(a.x) + 3 : X(o.x1) - 22}" y="${a.x !== undefined ? Y(o.y1) + 10 : Y(a.y) - 3}" fill="${a.c || '#777'}">${a.t}</text>`;
  }
  for (const f of o.fns) {
    let d = '', pen = false;
    const N = 600;
    for (let i = 0; i <= N; i++) {
      const x = f.a + (f.b - f.a) * i / N, y = f.f(x);
      if (!isFinite(y) || y < o.y0 - 1 || y > o.y1 + 1) { pen = false; continue; }
      d += (pen ? 'L' : 'M') + X(x).toFixed(1) + ' ' + Y(y).toFixed(1);
      pen = true;
    }
    s += `<path d="${d}" fill="none" stroke="${f.c || '#1b3a8a'}" stroke-width="${f.w || 1.8}" ${f.dash ? 'stroke-dasharray="5 3"' : ''} clip-path="inset(0)"/>`;
    if (f.t) s += `<text x="${X(f.tx)}" y="${Y(f.ty)}" fill="${f.c || '#1b3a8a'}">${f.t}</text>`;
  }
  for (const p of o.pts || []) {
    s += `<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="2.6" fill="${p.open ? '#fff' : (p.c || '#c0392b')}" stroke="${p.c || '#c0392b'}" stroke-width="1.2"/>`;
    if (p.t) s += `<text x="${X(p.x) + 4}" y="${Y(p.y) - 4}" fill="${p.c || '#c0392b'}">${p.t}</text>`;
  }
  return s + '</svg>';
}
const GRAPHS = {
  g9: () => plot({ x0: -3, x1: 3.5, y0: -1, y1: 4, fns: [
    { f: (x) => -Math.sqrt(x + 2) + 3, a: -2, b: 3.5, t: 'y=−√(x+2)+3', tx: 0.6, ty: 1.9 },
    { f: (x) => -x + 1, a: -3, b: 3.5, c: '#c0392b', dash: 1, w: 1.2, t: 'k=1', tx: -2.9, ty: 3.5 },
    { f: (x) => -x + 0.75, a: -3, b: 3.5, c: '#2e8b57', dash: 1, w: 1.2, t: 'k=3/4 (접함)', tx: 1.1, ty: -0.7 },
  ], pts: [{ x: -2, y: 3, t: '(−2, 3)' }, { x: -1.75, y: 2.5, c: '#2e8b57' }] }),
  g13: () => plot({ x0: -0.6, x1: 11, y0: -0.6, y1: 8, asym: [{ x: 3, t: 'x=3' }, { y: 2, t: 'y=2' }, { y: 4, c: '#c0392b', t: 'y=4' }], fns: [
    { f: (x) => Math.abs(6 / (x - 3) - 2), a: 0.0001, b: 2.999 },
    { f: (x) => Math.abs(6 / (x - 3) - 2), a: 3.001, b: 11 },
  ], pts: [{ x: 0, y: 4, open: 1 }, { x: 6, y: 0, t: '(6, 0)' }] }),
  g20: () => plot({ w: 330, x0: -9, x1: 6, y0: -2, y1: 2.2, asym: [{ y: 1, t: '' }], fns: [
    { f: () => 1, a: -9, b: -1 },
    { f: () => -1, a: -1, b: 0 },
    { f: (u) => (u - 1) / (u + 1), a: 0, b: 6, t: 'u≥0', tx: 3.2, ty: 0.15 },
    { f: (u) => 4 / 18 * (u + 7), a: -9, b: 6, c: '#c0392b', dash: 1, w: 1.1, t: 'm=4', tx: -3.4, ty: 1.55 },
    { f: (u) => 1 / 18 * (u + 7), a: -9, b: 6, c: '#2e8b57', dash: 1, w: 1.1, t: 'm=1 (접함)', tx: 2.8, ty: 0.85 },
  ], pts: [{ x: -7, y: 0, t: '(−7, 0)', c: '#333' }, { x: -1, y: 1, open: 1, c: '#333' }, { x: -1, y: -1, open: 1, c: '#333' }, { x: 5, y: 2 / 3, c: '#2e8b57' }] }),
};

// ---------- 1) 시험지 B4 ----------
function qBlock(q) {
  const short = !q.chList && q.ch && q.ch.every((c) => c.length < 22);
  let ch = '';
  if (q.ch) {
    ch = `<div class="ch ${q.chList ? 'list' : short ? 'row5' : 'row3'}">` +
      q.ch.map((c, i) => q.chList ? `<span><b>${CIRC[i]}</b> ${tex(c.split('##')[0])}</span><span>${tex(c.split('##')[1])}</span>` : `<span><b>${CIRC[i]}</b> ${tex(c)}</span>`).join('') + '</div>';
  }
  return `<div class="q"><div class="qt"><span class="qn">${q.n}.</span> ${tex(q.q)}</div>
<div class="pt">[${q.pt}점]</div>${ch}</div>`;
}
const LAYOUT = [
  [[1, 2, 3], [4, 5, 6]],
  [[7, 8, 9], [10, 11, 12]],
  [[13, 14], [15, 16]],
  [[17, 18], [19, 20]],
];
const byN = Object.fromEntries(Q.map((q) => [q.n, q]));
const total = Q.reduce((a, q) => a + parseFloat(q.pt), 0);
const nObj = Q.filter((q) => q.type === '객').length;
const nSub = Q.length - nObj;
const ptObj = Q.filter((q) => q.type === '객').reduce((a, q) => a + parseFloat(q.pt), 0);

function buildExam() {
  const css = `
body{font-family:'Nanum Myeongjo',serif;font-size:10.6pt;line-height:1.75}
.sheet{width:257mm;height:364mm;padding:14mm 13mm 12mm;position:relative;page-break-after:always;display:flex;flex-direction:column}
.sheet:last-child{page-break-after:auto}
.hd{border:1.6px solid #111;display:grid;grid-template-columns:1fr auto;margin-bottom:5mm}
.hd .t{padding:3.5mm 5mm;border-right:1px solid #111}
.hd .t .s1{font-family:'Nanum Gothic';font-size:9.5pt;color:#444;letter-spacing:.5px}
.hd .t .s2{font-size:20pt;font-weight:800;letter-spacing:-.5px;margin-top:1mm}
.hd .f{display:grid;grid-template-columns:auto 34mm;font-family:'Nanum Gothic';font-size:9.5pt}
.hd .f div{border-bottom:1px solid #111;padding:1.8mm 3mm;display:flex;align-items:center}
.hd .f div:nth-child(odd){background:#f1f1f1;border-right:1px solid #111;font-weight:700}
.hd .f div:nth-last-child(-n+2){border-bottom:0}
.info{font-family:'Nanum Gothic';font-size:9pt;border-top:1px solid #111;border-bottom:1px solid #111;padding:1.4mm 2mm;margin:-2mm 0 4mm;text-align:center}
.cols{flex:1;display:grid;grid-template-columns:1fr 1fr;column-gap:0;min-height:0}
.col{display:flex;flex-direction:column;padding:0 5mm}
.col:first-child{border-right:1px solid #111;padding-left:0}
.col:last-child{padding-right:0}
.q{flex:1;padding-top:1mm}
.qt{text-align:justify;word-break:keep-all}
.qn{font-family:'Nanum Gothic';font-weight:800;font-size:12.5pt;margin-right:1mm}
.pt{text-align:right;font-size:9pt;color:#333;margin:.5mm 0 1.5mm}
.ch{display:grid;row-gap:1.6mm;column-gap:2mm}
.ch.row5{grid-template-columns:repeat(5,1fr)}
.ch.row3{grid-template-columns:repeat(3,1fr)}
.ch.list{grid-template-columns:1fr 1fr}
.ch b{font-weight:400}
.cen{text-align:center;margin:1.5mm 0}
.ind{margin:1mm 0 1mm 10mm}
.box{border:1px solid #111;padding:2mm 3.5mm;margin:2mm 0}
.ft{position:absolute;bottom:5mm;left:0;right:0;text-align:center;font-family:'Nanum Gothic';font-size:9pt;color:#555}
`;
  let body = '';
  LAYOUT.forEach((pg, pi) => {
    body += '<section class="sheet">';
    if (pi === 0) {
      body += `<div class="hd"><div class="t"><div class="s1">${META.year}학년도 2학기 기말고사 기출</div>
<div class="s2">${META.school} 1학년 · ${META.subject}</div></div>
<div class="f"><div>반 / 번호</div><div></div><div>이 름</div><div></div><div>점 수</div><div></div></div></div>
<div class="info">■ 총 ${LAYOUT.length}면 ${Q.length}문항 &nbsp;■ 만점 ${total.toFixed(2)}점 &nbsp;/&nbsp; ■ 선택형 ${nObj}문항 ${ptObj.toFixed(2)}점 &nbsp;■ 서술형 ${nSub}문항 ${(total - ptObj).toFixed(2)}점</div>`;
    }
    body += '<div class="cols">' + pg.map((col) =>
      '<div class="col">' + col.map((n) => qBlock(byN[n])).join('') + '</div>').join('') + '</div>';
    body += `<div class="ft">${META.title} · ${META.subject} &nbsp;&nbsp; ${pi + 1} / ${LAYOUT.length}</div></section>`;
  });
  return page(`${META.title} (시험지 B4)`, '257mm 364mm', css, body);
}

// ---------- 2) 손풀이 A4 ----------
function buildSol() {
  const css = `
body{font-family:'Nanum Myeongjo',serif;font-size:10pt}
.wrap{padding:0}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5px solid #1b2a5a;padding-bottom:2mm;margin-bottom:5mm}
.top h1{margin:0;font-family:'Nanum Gothic';font-weight:800;font-size:17pt;color:#1b2a5a}
.top span{font-family:'Nanum Gothic';font-size:9pt;color:#555}
.card{break-inside:avoid;border:1px solid #cfd5e3;border-radius:2.5mm;margin-bottom:5mm;overflow:hidden}
.ch{display:flex;align-items:center;gap:3mm;background:#eef1f8;padding:1.8mm 4mm;font-family:'Nanum Gothic'}
.ch .n{font-weight:800;font-size:13pt;color:#1b2a5a}
.ch .tag{font-size:8.5pt;color:#555}
.ch .ans{margin-left:auto;font-size:9.5pt;font-weight:700;color:#c0392b}
.prob{padding:2.5mm 4mm;font-size:9.2pt;line-height:1.7;color:#333;border-bottom:1px dashed #cfd5e3;word-break:keep-all}
.prob .box{border:1px solid #888;padding:1.5mm 3mm;margin:1.5mm 0}
.prob .cen{text-align:center}
.prob .ind{margin-left:8mm}
.prob .chs{margin-top:1mm;color:#555}
.body{display:flex;gap:4mm;padding:3mm 5mm 4mm}
.hand{flex:1;font-family:'Nanum Pen Script',cursive;font-size:17.5pt;line-height:1.5;color:#1a3c8f}
.hand .katex{font-size:.66em;color:#1a3c8f}
.hand li{margin:0 0 1mm}
.hand ol{margin:0;padding-left:6mm}
.hand .fin{margin-top:1.5mm;display:inline-block;border:2px solid #c0392b;color:#c0392b;border-radius:2mm;padding:0 3mm}
.hand .fin .katex{color:#c0392b}
.gr{flex:0 0 auto;align-self:center}
.foot{font-family:'Nanum Gothic';font-size:8pt;color:#888;text-align:center;margin-top:3mm}
`;
  let body = `<div class="wrap"><div class="top"><h1>${META.title} · 손풀이</h1><span>${META.subject} · ${Q.length}문항 · 정답은 빠른정답과 대조 완료</span></div>`;
  for (const q of Q) {
    const chs = q.ch ? `<div class="chs">${q.ch.map((c, i) => `${CIRC[i]} ${tex(c.replace('##', ', '))}`).join(' &nbsp; ')}</div>` : '';
    body += `<div class="card"><div class="ch"><span class="n">${q.n}</span><span class="tag">${q.sub} · ${tex(q.key)} · ${q.pt}점 · 난이도 ${LV[q.lv]}</span>
<span class="ans">정답 ${tex(q.ans)}</span></div>
<div class="prob">${tex(q.q)}${chs}</div>
<div class="body"><div class="hand"><ol>${q.sol.map((l) => `<li>${tex(l)}</li>`).join('')}</ol>
<span class="fin">답 ${tex(q.fin)}</span></div>${q.graph ? `<div class="gr">${GRAPHS[q.graph]()}</div>` : ''}</div></div>`;
  }
  body += '</div>';
  return page(`${META.title} (손풀이)`, '210mm 297mm', css, body);
}

// ---------- 3) 분석표 A4 ----------
function buildAna() {
  const css = `
body{font-family:'Nanum Gothic',sans-serif;font-size:8.6pt;color:#1d2433}
.wrap{width:210mm;height:297mm;padding:11mm 12mm;display:flex;flex-direction:column}
.top{background:#1b2a5a;color:#fff;border-radius:2.5mm;padding:4mm 6mm;display:flex;justify-content:space-between;align-items:center}
.top h1{margin:0;font-size:16pt;font-weight:800}
.top .s{font-size:9pt;opacity:.85;margin-top:1mm}
.top .tot{text-align:right;font-size:9pt}
.top .tot b{font-size:15pt;display:block}
.kpi{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:4mm 0}
.kpi div{border:1px solid #d7dceb;border-radius:2mm;padding:2.5mm 3.5mm}
.kpi small{color:#667;display:block;font-size:7.8pt}
.kpi b{font-size:13pt}
table{width:100%;border-collapse:collapse}
th{background:#eef1f8;color:#1b2a5a;font-weight:800;padding:1.6mm 1mm;border-bottom:1.5px solid #1b2a5a;font-size:8.2pt}
td{padding:1.25mm 1.5mm;border-bottom:1px solid #e3e6ef;text-align:center;vertical-align:middle}
td.l{text-align:left}
tr.sub td{background:#fbfaf4}
.lv{display:inline-block;min-width:9mm;border-radius:1mm;padding:.3mm 1.2mm;font-weight:800;font-size:7.8pt}
.lv1{background:#e5f6ee;color:#1e7a50}.lv2{background:#e8eefb;color:#2b4fa8}.lv3{background:#fdf0dc;color:#b06a00}.lv4{background:#fbe3e3;color:#b42c2c}
.row{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm}
.panel{border:1px solid #d7dceb;border-radius:2mm;padding:3mm 4mm}
.panel h3{margin:0 0 2mm;font-size:9.5pt;color:#1b2a5a}
.bar{display:grid;grid-template-columns:30mm 1fr 18mm;align-items:center;gap:2mm;margin:1.4mm 0}
.bar .t{height:4mm;background:#eef1f8;border-radius:1mm;overflow:hidden}
.bar .t i{display:block;height:100%;background:#1b2a5a}
.bar .v{text-align:right;color:#444}
.note{margin-top:4mm;border-left:3px solid #c9a24b;background:#fbf7ec;padding:3mm 4mm;line-height:1.65}
.note b{color:#1b2a5a}
.katex{font-size:1em}
`;
  const units = {};
  const subs = {};
  const lvs = { 1: 0, 2: 0, 3: 0, 4: 0 };
  const lvPt = { 1: 0, 2: 0, 3: 0, 4: 0 };
  for (const q of Q) {
    const p = parseFloat(q.pt);
    units[q.unit] = (units[q.unit] || 0) + p;
    subs[q.sub] = subs[q.sub] || { n: 0, p: 0 };
    subs[q.sub].n++; subs[q.sub].p += p;
    lvs[q.lv]++; lvPt[q.lv] += p;
  }
  const bars = (obj, val, lab) => Object.entries(obj).map(([k, v]) =>
    `<div class="bar"><span>${k}</span><span class="t"><i style="width:${(val(v) / total * 100).toFixed(1)}%"></i></span><span class="v">${lab(v)}</span></div>`).join('');
  const rows = Q.map((q) => `<tr class="${q.type === '서' ? 'sub' : ''}"><td><b>${q.n}</b></td><td>${q.type === '객' ? '선택형' : '서술형'}</td>
<td class="l">${q.sub}</td><td class="l">${tex(q.key)}</td><td><span class="lv lv${q.lv}">${LV[q.lv]}</span></td><td>${q.pt}</td><td><b>${tex(q.ans)}</b></td></tr>`).join('');
  const body = `<div class="wrap">
<div class="top"><div><h1>${META.title} 분석표</h1><div class="s">${META.subject} · 집합과 명제 / 함수와 그래프</div></div>
<div class="tot">만점<b>${total.toFixed(2)}점</b></div></div>
<div class="kpi"><div><small>전체 문항</small><b>${Q.length}</b>문항</div><div><small>선택형</small><b>${nObj}</b>문항 · ${ptObj.toFixed(2)}점</div>
<div><small>서술형</small><b>${nSub}</b>문항 · ${(total - ptObj).toFixed(2)}점</div><div><small>상 · 최상 비율</small><b>${lvs[3] + lvs[4]}</b>문항 (${Math.round((lvPt[3] + lvPt[4]) / total * 100)}%)</div></div>
<table><thead><tr><th style="width:8mm">번호</th><th style="width:14mm">유형</th><th style="width:34mm">단원</th><th>핵심 개념</th><th style="width:13mm">난이도</th><th style="width:12mm">배점</th><th style="width:14mm">정답</th></tr></thead>
<tbody>${rows}</tbody></table>
<div class="row"><div class="panel"><h3>단원별 배점</h3>${bars(subs, (v) => v.p, (v) => `${v.n}문항 ${v.p.toFixed(1)}점`)}</div>
<div class="panel"><h3>난이도별 배점</h3>${bars(Object.fromEntries(Object.entries(lvs).map(([k, n]) => [LV[k], { n, p: lvPt[k] }])), (v) => v.p, (v) => `${v.n}문항 ${v.p.toFixed(1)}점`)}</div></div>
<div class="note"><b>총평</b> &nbsp;공통수학2 후반부(명제 ~ 유리·무리함수) 범위로, 함수와 그래프가 배점의 약 ${Math.round(units['함수와 그래프'] / total * 100)}%를 차지한다.
1~7번은 기본 개념 확인 문항이지만, 8번부터는 진리집합·역함수 존재 조건·그래프 교점 개수처럼 <b>그래프를 직접 그려 판단</b>해야 하는 문항이 이어진다.
서술형 18~20번은 역함수의 대칭성과 외접원(18), 합성함수 방정식을 두 방정식으로 나누어 공통근까지 따지는 문제(19),
절댓값 유리함수를 치환해 직선의 기울기로 경우를 나누는 문제(20)로, 변별력이 가장 큰 구간이다.
<br><b>대비 포인트</b> &nbsp;① $f(a)=f(b)$ 꼴은 대칭축을 이용해 두 방정식으로 나누기 ② 무리함수와 직선은 $\\sqrt{\\ }$를 $t$로 치환해 이차방정식 근의 조건으로 ③ 유리함수 위 점과 점근선 교점 사이 거리는 산술·기하평균.
<br><span style="color:#888">※ 배점은 원본 표기 그대로이며 4번이 4.83점이라 합계가 ${total.toFixed(2)}점입니다.</span></div>
</div>`;
  return page(`${META.title} (분석표)`, 'A4', css, tex(body));
}

(async () => {
  const docs = [
    [`${META.title} (시험지 B4)`, buildExam(), { width: '257mm', height: '364mm' }],
    [`${META.title} (손풀이)`, buildSol(), { format: 'A4' }],
    [`${META.title} (분석표)`, buildAna(), { format: 'A4' }],
  ];
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const pg = await browser.newPage();
  for (const [name, html, fmt] of docs) {
    const hp = path.join(__dirname, name + '.html');
    fs.writeFileSync(hp, html);
    await pg.goto('file://' + hp, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.pdf({ path: path.join(OUT, name + '.pdf'), printBackground: true, preferCSSPageSize: true, ...fmt });
    console.log('ok', name);
  }
  await browser.close();
})();
