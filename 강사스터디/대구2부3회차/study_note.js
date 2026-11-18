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

const body = `
<div class="cover"><span class="tag">강사스터디 · 대구 2부 3회차</span><div class="no">9</div><h1>합성함수와 역함수</h1><p>참고자료 2 · 원본 218~233쪽 정리 · 채수학 편집</p></div>

<h2>합성함수</h2>
<div class="src">원본 218쪽</div>
<div class="card"><div class="h"><span class="k">개념</span>합성함수 $g\\circ f$</div><div class="b">
<div class="row"><div>$X\\xrightarrow{\\ f\\ }Y\\xrightarrow{\\ g\\ }Z$<br>$g\\circ f$ : <span class="hl2">$f$를 먼저</span> 거쳐서 <span class="hl3">$g$</span><br>$(g\\circ f)(x)=g(f(x))$</div></div>
<div class="tip"><b>강사 TIP</b> 오른쪽에 있는 함수가 먼저! 학생들이 $g\\circ f$를 '$g$ 다음 $f$'로 읽는 실수를 가장 많이 한다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 1</span>합성함수가 정의되기 위한 $(f,g)$의 개수</div><div class="b">
$X=\\{1,2,3,4\\}$, $Y=\\{1,2,3,4,5\\}$, $Z=\\{1,2\\}$일 때, $g\\circ f$가 정의되기 위한 순서쌍 $(f,g)$의 개수를 구하시오.<br>(단, $f$는 일대일함수이고, 합성함수 $g\\circ f$의 치역과 공역이 같다.)
<div class="row" style="margin-top:2mm"><div>${map}</div><div style="flex:1;min-width:60mm">
<div class="step"><span class="c">① $f$의 개수</span><span>$X$에서 $Y$로의 일대일함수: ${'$'}_5\\mathrm P_4=120${'$'}</span></div>
<div class="step"><span class="c">② $g$ (치역)</span><span><span class="hl1">$f$의 치역 4개</span>에서 <span class="hl2">$\\{1,2\\}$</span>로 가는 함수 중 치역=공역: $2^4-2=14$ <span style="color:#D33">(한쪽으로 몰빵하는 2가지 빼기)</span></span></div>
</div></div>
<div class="wrong"><b>✘ 이렇게 풀면 틀림!</b> &nbsp; ${'$'}_5\\mathrm P_4\\times(2^4-2)${'$'}</div>
<div class="ok"><b style="color:#2e8b57">✔ 합성함수가 정의되려면 $g$도 함수여야 한다</b> — $Y$의 원소 <span style="background:#9BE27A;padding:0 1mm;border-radius:1mm">5</span>(=$f$의 치역에 없는 원소)도 $1,2$ 중 어디로 갈지 정해야 한다 → $\\times2$<br>
${'$'}_5\\mathrm P_4\\times(2^4-2)\\times2=120\\times14\\times2=3360${'$'}</div>
<span class="ans">답 3360</span>
<div class="tip"><b>강사 TIP</b> '합성함수가 정의된다' = $f$, $g$ 각각이 <b>함수</b>여야 한다. $g$의 정의역은 $Y$ 전체이므로 $f$가 가지 않는 원소의 갈 곳까지 세야 한다. $f$와 $g$의 정의역·치역이 주어질 때 $f\\circ g$가 존재하는 것을 고르는 문제도 같은 원리로 출제된다.</div>
</div></div>

<div class="src">원본 219쪽</div>
<div class="card"><div class="h"><span class="k">개념</span>1. 합성함수의 성질</div><div class="b">
<ul><li><b>교환법칙은 성립하지 않는다</b>: $g\\circ f\\ne f\\circ g$ (일반적으로)</li>
<li><b>결합법칙은 성립한다</b>: $(h\\circ g)\\circ f=h\\circ(g\\circ f)$</li></ul>
<b>문제 유형</b> — 두 함수 $f(x)$, $g(x)$가 주어지고<br>(1) $(f\\circ g)(x)$를 구하시오. &nbsp; (2) $(h\\circ f)(x)=g(x)$일 때 $h(x)$를 구하시오.
<div class="tip"><b>강사 TIP</b> (2)는 $f(x)=t$로 치환해 $h(t)$를 구하거나, $f$의 역함수를 오른쪽에 합성해 $h=g\\circ f^{-1}$로 구한다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">개념</span>2. 합성함수의 그래프 그리기</div><div class="b">
① 합성함수의 그래프를 <b>그릴 수 있어야</b> 한다.<br>② 그린 그래프를 이용해 <b>방정식 문제</b>(실근의 개수 등)를 풀 수 있어야 한다.
</div></div>

<h2>합성함수의 그래프</h2>
<div class="src">원본 220~221쪽</div>
<div class="card"><div class="h"><span class="k">예제 2</span>$g(f(x))$의 그래프를 그리시오.</div><div class="b">
<div class="row">${fG()}${gG({ lab: [[0.45, 1.7, 'a', '#D33', 13], [2.3, 1.7, 'b', '#D33', 13]] })}<div>$a:\\ y=2x$<br>$b:\\ y=-2x+6$</div></div>

<div style="margin-top:2mm"><b style="color:#17777a">풀이 1) 서술형 답안용</b> — $f$의 식이 바뀌는 점 $x=1$과, $f(x)=\\dfrac32$인 점 $x=\\dfrac34$를 기준으로 나눈다.</div>
<div class="row">${fG({ yt: [[1.5, '3/2'], [2, '2'], [3, '3']], xt: [[0.75, '3/4'], [1, '1'], [3, '3']], pts: [[0, 0], [0.75, 1.5], [1, 2], [3, 3]], dots: [[0.75, 1.5], [1, 2]], lab: [[0.15, 0.9, 'i)', '#D33'], [0.55, 1.95, 'ii)', '#D33'], [1.8, 2.75, 'iii)', '#D33']] })}
<div style="flex:1;min-width:70mm">
<div class="step"><span class="c">i) $0\\le x<\\dfrac34$</span><span>$f(x)=2x$, $0\\le f(x)<\\dfrac32$ → $a$식에 넣기: $g(f(x))=2(2x)=4x$</span></div>
<div class="step"><span class="c">ii) $\\dfrac34\\le x<1$</span><span>$f(x)=2x$, $\\dfrac32\\le f(x)<2$ → $b$식: $-2(2x)+6=-4x+6$</span></div>
<div class="step"><span class="c">iii) $1\\le x\\le3$</span><span>$f(x)=\\dfrac12x+\\dfrac32$, $2\\le f(x)\\le3$ → $b$식: $-2\\left(\\dfrac12x+\\dfrac32\\right)+6=-x+3$</span></div>
</div></div>

<div style="margin-top:2mm"><b style="color:#17777a">풀이 2) 빠르게 풀기</b> — 나누는 점은 풀이 1과 같다.<br>
① $f(x)$의 식이 변하는 지점 &nbsp; ② $g(x)$가 $x=t$에서 식이 변하면 $f(x)=t$인 지점<br>
각 구간에서 $f$가 지나는 $y$값 범위를 $g$에 넣어 <b>끝점끼리만 이으면</b> 된다.</div>
<div class="step"><span class="c">i)</span><span>$f$: $0\\to\\dfrac32$ ⇒ $g$: $0\\to3$ → $(0,0)$에서 $\\left(\\dfrac34,3\\right)$까지</span></div>
<div class="step"><span class="c">ii)</span><span>$f$: $\\dfrac32\\to2$ ⇒ $g$: $3\\to2$ → $\\left(\\dfrac34,3\\right)$에서 $(1,2)$까지</span></div>
<div class="step"><span class="c">iii)</span><span>$f$: $2\\to3$ ⇒ $g$: $2\\to0$ → $(1,2)$에서 $(3,0)$까지</span></div>
<div class="row" style="justify-content:center">${gfG}<div>$g(f(x))=\\begin{cases}4x & \\left(0\\le x<\\frac34\\right)\\\\ -4x+6 & \\left(\\frac34\\le x<1\\right)\\\\ -x+3 & (1\\le x\\le3)\\end{cases}$</div></div>
<div class="tip"><b>강사 TIP</b> 서술형은 풀이 1처럼 구간·식을 모두 쓰고, 객관식·그래프 개형만 필요할 때는 풀이 2처럼 꺾이는 점 $\\left(\\frac34,3\\right)$, $(1,2)$만 찾아 잇는다. 꺾이는 점은 'f가 꺾이는 곳'과 'f(x)가 g의 꺾이는 x값이 되는 곳' 두 종류뿐이다. </div>
</div></div>
`;

const fonts = ['katex/dist/katex.min.css', '@fontsource/nanum-gothic/400.css', '@fontsource/nanum-gothic/700.css', '@fontsource/nanum-gothic/800.css']
  .map((f) => `<link rel="stylesheet" href="file://${path.join(NM, f)}">`).join('');
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>강사스터디 9 합성함수와 역함수</title>${fonts}<style>${css}</style></head><body>${tex(body + require("./part2.js"))}</body></html>`;
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
