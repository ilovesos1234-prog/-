// 3종 세트(시험지 B4 · 손풀이 A4 · 분석표 A4) 생성
// 사용법: node build.js <데이터.js> <출력폴더>
const fs = require('fs');
const path = require('path');
const katex = require('katex');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const D = require(path.resolve(process.argv[2]));
const { META, Q } = D;

const OUT = process.argv[3] || path.join(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
const NM = path.join(__dirname, 'node_modules');

// ---------- 공통 ----------
const tex = (s) => s.replace(/\$([^$]+)\$/g, (_, m) =>
  katex.renderToString(m, { throwOnError: true, displayMode: false, strict: false }));
const CIRC = ['①', '②', '③', '④', '⑤'];
const imgTag = (q) => q.img ? `<div class="fig"><img src="data:image/png;base64,${fs.readFileSync(q.img).toString('base64')}" style="width:${q.imgW || 55}mm"></div>` : '';
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
  let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" font-family="Nanum Gothic" font-size="${o.fs || 11}">`;
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
  for (const g of o.segs || []) {
    s += `<line x1="${X(g.x1)}" y1="${Y(g.y1)}" x2="${X(g.x2)}" y2="${Y(g.y2)}" stroke="${g.c || '#111'}" stroke-width="1" ${g.dash ? 'stroke-dasharray="3 3"' : ''}/>`;
  }
  for (const l of o.labels || []) s += `<text x="${X(l.x)}" y="${Y(l.y)}" fill="${l.c || '#111'}">${l.t}</text>`;
  for (const p of o.pts || []) {
    s += `<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="2.6" fill="${p.open ? '#fff' : (p.c || '#c0392b')}" stroke="${p.c || '#c0392b'}" stroke-width="1.2"/>`;
    if (p.t) s += `<text x="${X(p.x) + 4}" y="${Y(p.y) - 4}" fill="${p.c || '#c0392b'}">${p.t}</text>`;
  }
  return s + '</svg>';
}
const GRAPHS = D.graphs ? D.graphs(plot) : {};

// ---------- 1) 시험지 B4 (채수학 B4 시험지 틀, 2026.09.19 확정) ----------
// B4 257×364 · 2단(단 110.5mm) · 좌우 18mm · 위 8+머리 4 · 아래 8+꼬리 14
// 본문 11.5pt/165% · 수식 11pt · 한쪽 4문제 · 아래 문제는 단 149mm에서 시작(최대 +20mm)
const TYPE = D.TYPE || {};
// 쪽마다 [왼쪽 단, 오른쪽 단], 단마다 [위, 아래] — 앞에서부터 4문제씩
// 긴 문제(q.alone)는 혼자 한 단을 쓴다
const cols = [];
for (let i = 0; i < Q.length;) {
  if (Q[i].alone || (Q[i + 1] && Q[i + 1].alone) || i + 1 >= Q.length) { cols.push([Q[i].n]); i += 1; }
  else { cols.push([Q[i].n, Q[i + 1].n]); i += 2; }
}
const LAYOUT = [];
for (let i = 0; i < cols.length; i += 2) LAYOUT.push(cols.slice(i, i + 2));
const byN = Object.fromEntries(Q.map((q) => [q.n, q]));
const total = Q.reduce((a, q) => a + parseFloat(q.pt), 0);
const nObj = Q.filter((q) => q.type === '객').length;
const nSub = Q.length - nObj;
const ptObj = Q.filter((q) => q.type === '객').reduce((a, q) => a + parseFloat(q.pt), 0);

function qBlock(q, pos) {
  let ch = '';
  if (q.ch) {
    ch = `<div class="chs" ${q.chList ? 'data-one="1"' : ''}>` + q.ch.map((c, i) => q.chList && c.includes('##')
      ? `<span class="c"><span class="pp">${CIRC[i]} ${tex(c.split('##')[0])}</span><span>${tex(c.split('##')[1])}</span></span>`
      : `<span class="c">${CIRC[i]} ${tex(c)}</span>`).join('') + '</div>';
  }
  return `<div class="q ${pos}"><div class="qh"><span class="no">${String(q.n).padStart(2, '0')}</span><span class="pill">채수학 X ${q.tp || TYPE[q.n]}</span></div>
<div class="qt">${tex(q.q)}</div><div class="pt">[${q.pt}점${q.ptGuess ? '*' : ''}]</div>${q.fig ? `<div class="fig">${GRAPHS[q.fig]()}</div>` : ''}${imgTag(q)}${ch}</div>`;
}

function buildExam() {
  const css = `
body{font-family:'Nanum Gothic',sans-serif;font-size:11.5pt;line-height:165%}
.katex{font-size:${(11 / 11.5).toFixed(4)}em}
.sheet{width:257mm;height:364mm;position:relative;page-break-after:always;overflow:hidden}
.sheet:last-child{page-break-after:auto}
.head{position:absolute;top:8mm;left:18mm;right:18mm;height:4mm;font-size:7.5pt;line-height:4mm;color:#777;display:flex;justify-content:space-between}
.body{position:absolute;top:12mm;left:18mm;width:221mm;bottom:22mm;display:grid;grid-template-columns:110.5mm 110.5mm}
.col{position:relative;height:100%}
.col.l{border-right:.8px solid #333;padding-right:5mm}
.col.r{padding-left:5mm}
.q{position:absolute;left:0;right:0}
.col.l .q{right:5mm}.col.r .q{left:5mm}
.q.top{top:2mm}
.qh{display:flex;align-items:center;gap:2.2mm;margin-bottom:1.2mm}
.no{font-weight:800;font-size:14pt;color:#000;background:#fff;line-height:1}
.pill{background:#e3f4e1;color:#1b2a5a;font-size:9pt;font-weight:700;border-radius:99px;padding:.6mm 3mm;line-height:1.3;white-space:nowrap}
.qt{text-align:justify;word-break:keep-all}
.pt{text-align:right;font-size:9.5pt;color:#333;line-height:1.4;margin-top:.5mm}
.chs{display:grid;grid-auto-rows:32pt;align-items:center}
.chs .c{white-space:nowrap;justify-self:start}
.chs .pp{display:inline-block;width:52%}
.cen{text-align:center;margin:1mm 0}
.ind{margin:.5mm 0 .5mm 8mm}
.box{border:1px solid #111;padding:1.5mm 3.5mm;margin:1.5mm 0}
.fig{text-align:center;margin:0}
.title{position:absolute;top:12mm;left:18mm;right:18mm}
.foot{position:absolute;bottom:8mm;left:18mm;right:18mm;height:14mm;display:flex;align-items:flex-end;justify-content:space-between;font-size:8.5pt;color:#555;border-top:.6px solid #bbb;padding-bottom:1mm}
.foot b{color:#111}
`;
  // 선택지: 가장 넓은 선택지가 (칸 너비 − 3mm) 안에 드는 가장 큰 수 5→3→2→1
  // 아래 문제: 단 149mm에서 시작, 위 문제가 넘으면 20mm까지만 내림, 문항 사이 최소 22mm
  const script = `<script>window.__done=false;document.fonts.ready.then(()=>{
const mm=96/25.4, warn=[];
document.querySelectorAll('.chs').forEach(g=>{
  const cs=[...g.children]; const W=g.clientWidth;
  const need=Math.max(...cs.map(c=>c.scrollWidth));
  let n=1; if(!g.dataset.one){for(const k of [5,3,2,1]){if(need<=W/k-3*mm){n=k;break;}}}
  g.style.gridTemplateColumns='repeat('+n+',1fr)'; g.dataset.n=n;
});
document.querySelectorAll('.col').forEach(col=>{
  const top=col.querySelector('.q.top'), bot=col.querySelector('.q.bot'); if(!bot)return;
  if(!top)return; const topEnd=top.offsetTop+top.offsetHeight; let y=149*mm;
  if(topEnd+22*mm>y) y=Math.min(topEnd+22*mm,169*mm);
  if(topEnd+22*mm>169*mm) warn.push('간격부족 '+bot.querySelector('.no').textContent);
  bot.style.top=y+'px';
  if(y+bot.offsetHeight>col.clientHeight) warn.push('넘침 '+bot.querySelector('.no').textContent);
});
window.__warn=warn; window.__done=true;});</script>`;
  let body = '';
  LAYOUT.forEach((pg, pi) => {
    body += `<section class="sheet"><div class="head"><span>채수학 · ${META.title}</span><span>${META.subject} · ${Q.length}문항 · 만점 ${total.toFixed(2)}점</span></div><div class="body">`;
    body += pg.map((col, ci) => `<div class="col ${ci ? 'r' : 'l'}">` +
      col.map((n, k) => qBlock(byN[n], k ? 'bot' : 'top')).join('') + '</div>').join('');
    body += `</div><div class="foot"><span>${META.title} · ${META.subject} &nbsp; <b>${pi + 1}</b> / ${LAYOUT.length}</span><span><b>B4</b> · ☎ 010-8677-2263</span></div></section>`;
  });
  return page(`${META.title} (시험지 B4)`, '257mm 364mm', css, body + script);
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
.prob .fig{text-align:center}.prob .fig img{max-width:45mm}
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
    body += `<div class="card"><div class="ch"><span class="n">${q.n}</span><span class="tag">${q.sub} · ${tex(q.key)} · ${q.pt}점${q.ptGuess ? '(추정)' : ''} · 난이도 ${LV[q.lv]}</span>
<span class="ans">정답 ${tex(q.ans)}</span></div>
<div class="prob">${tex(q.q)}${imgTag(q)}${chs}</div>
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
.many td{padding:.75mm 1.5mm}
.many .bar{margin:.7mm 0}
.many .kpi{margin:3mm 0}
.many .row{margin-top:3mm}
.many .note{margin-top:3mm;line-height:1.55}
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
<td class="l">${q.sub}</td><td class="l">${tex(q.key)}</td><td><span class="lv lv${q.lv}">${LV[q.lv]}</span></td><td>${q.pt}${q.ptGuess ? '*' : ''}</td><td><b>${tex(q.ans)}</b></td></tr>`).join('');
  const body = `<div class="wrap${Q.length > 20 ? ' many' : ''}">
<div class="top"><div><h1>${META.title} 분석표</h1><div class="s">${META.subject} · ${META.units}</div></div>
<div class="tot">만점<b>${total.toFixed(2)}점</b></div></div>
<div class="kpi"><div><small>전체 문항</small><b>${Q.length}</b>문항</div><div><small>선택형</small><b>${nObj}</b>문항 · ${ptObj.toFixed(2)}점</div>
<div><small>서술형</small><b>${nSub}</b>문항 · ${(total - ptObj).toFixed(2)}점</div><div><small>상 · 최상 비율</small><b>${lvs[3] + lvs[4]}</b>문항 (${Math.round((lvPt[3] + lvPt[4]) / total * 100)}%)</div></div>
<table><thead><tr><th style="width:8mm">번호</th><th style="width:14mm">유형</th><th style="width:34mm">단원</th><th>핵심 개념</th><th style="width:13mm">난이도</th><th style="width:12mm">배점</th><th style="width:24mm">정답</th></tr></thead>
<tbody>${rows}</tbody></table>
<div class="row"><div class="panel"><h3>단원별 배점</h3>${bars(subs, (v) => v.p, (v) => `${v.n}문항 ${v.p.toFixed(1)}점`)}</div>
<div class="panel"><h3>난이도별 배점</h3>${bars(Object.fromEntries(Object.entries(lvs).map(([k, n]) => [LV[k], { n, p: lvPt[k] }])), (v) => v.p, (v) => `${v.n}문항 ${v.p.toFixed(1)}점`)}</div></div>
<div class="note">${META.note(units, total)}</div>
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
    await pg.waitForFunction(() => window.__done !== false);
    const w = await pg.evaluate(() => window.__warn);
    if (w && w.length) console.log('경고', w);
    await pg.pdf({ path: path.join(OUT, name + '.pdf'), printBackground: true, preferCSSPageSize: true, ...fmt });
    console.log('ok', name);
  }
  await browser.close();
})();
