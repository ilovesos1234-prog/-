// 학교별 「채수학 교재 적중 리포트」 PDF (블로그용, A4)
// 사용: node blog_report.js <WS>/school/<폴더> <출력.pdf>
// 입력: <폴더>/skeleton.json, <폴더>/match.json {"n":[{"id":교재번호,"level":"일치"|"유사","note":"한 줄 설명"}]}
const fs = require('fs'), path = require('path');
const WS = process.env.WS || '/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad';
const NM = path.join(WS, 'build', 'node_modules');
const katex = require(path.join(NM, 'katex'));
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const dir = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]);
const sk = JSON.parse(fs.readFileSync(path.join(dir, 'skeleton.json'), 'utf8'));
const MF = path.join(dir, 'match.json');
const M = fs.existsSync(MF) ? JSON.parse(fs.readFileSync(MF, 'utf8')) : {};
let texErr = 0;
const CD = path.join(WS, 'corpus');
const C = JSON.parse(fs.readFileSync(path.join(CD, 'corpus.json'), 'utf8'));
const CH = JSON.parse(fs.readFileSync(path.join(CD, 'corpus_html.json'), 'utf8'));
const BOOKCSS = fs.readFileSync(path.join(CD, 'book.css'), 'utf8');
const m = sk.meta;
const tex = (s) => String(s).replace(/\$([^$]+)\$/g, (_, x) => { try { return katex.renderToString(x, { throwOnError: true, strict: false }); } catch (e) { texErr++; console.error('KaTeX:', x, e.message); return x; } });
// $ 없는 한 줄 메모의 x^{2n}, a_n 같은 표기를 위·아래 첨자로
const pretty = (t) => String(t)
  .replace(/([A-Za-z0-9)□])\^\{([^}]+)\}/g, '$1<sup>$2</sup>')
  .replace(/([A-Za-z0-9)□])\^\(([^)]+)\)/g, '$1<sup>$2</sup>')
  .replace(/([A-Za-z0-9)□])\^([A-Za-z0-9]+)/g, '$1<sup>$2</sup>')
  .replace(/([A-Za-z])_\{([^}]+)\}/g, '$1<sub>$2</sub>')
  .replace(/([A-Za-z])_(\d*[a-z]?(?:[+−-]1(?![0-9]))?)/g, '$1<sub>$2</sub>');
const CIRC = ['①', '②', '③', '④', '⑤'];
const b64 = (f) => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
const imgOf = (q) => (q.imgs || []).map((i) => {
  const f = fs.readdirSync(path.join(dir, 'x', 'BinData')).find((x) => x.startsWith(i + '.'));
  return f ? `<img class="ex" src="${b64(path.join(dir, 'x', 'BinData', f))}" style="width:${Math.min(q.imgW || 55, 70)}mm">` : '';
}).join('');
const bookName = (b) => b.replace('_', ' ').replace(/([ⅠⅡⅢⅣⅤⅥⅦ])/, '$1. ').replace(/\.\s+/, '. ');

for (const [n, hs] of Object.entries(M)) for (const h of hs) {
  if (!C[h.id]) console.error(`경고: ${n}번 id ${h.id} 없음`);
  h.level = String(h.level).trim(); if (!['일치', '유사'].includes(h.level)) console.error(`경고: ${n}번 level "${h.level}"`);
}
const rows = sk.Q.map((q) => ({ q, hits: (M[String(q.n)] || []).filter((h) => C[h.id]) }));
const hitRows = rows.filter((r) => r.hits.length);
const nSame = hitRows.filter((r) => r.hits.some((h) => h.level === '일치')).length;
const nSim = hitRows.length - nSame;
const rate = Math.round(hitRows.length / rows.length * 100);
const lvOf = (r) => !r.hits.length ? '' : r.hits.some((h) => h.level === '일치') ? 'same' : 'sim';
const strip = rows.map((r) => `<span class="nb ${lvOf(r)}">${r.q.n}</span>`).join('');
const books = [...new Set(hitRows.flatMap((r) => r.hits.map((h) => bookName(C[h.id].book))))];

const card = (r) => {
  const q = r.q;
  const ch = q.ch ? `<div class="xch">${q.ch.map((c, i) => `<span>${CIRC[i]} ${tex(c.replace('##', ', '))}</span>`).join('')}</div>` : '';
  const right = r.hits.map((h) => {
    const c = C[h.id];
    return `<div class="bk"><div class="bh"><span class="badge ${h.level === '일치' ? 'same' : 'sim'}">${h.level}</span>
<span class="src">채수학 개념서 문제편 · ${bookName(c.book)} · p.${c.page} · ${c.step.split(' ').slice(0, 2).join(' ')} · ${c.no}번</span></div>
<div class="book">${CH[h.id]}</div>${h.note ? `<div class="note">💬 ${h.note.includes('$') ? tex(h.note) : pretty(h.note)}</div>` : ''}</div>`;
  }).join('');
  return `<section class="card"><div class="ch"><span class="qno">${q.n}번</span><span class="unit">${q.unit} › ${q.sub}</span><span class="pt">${q.type === '서' ? '서술형 · ' : ''}${q.pt}점</span></div>
<div class="two"><div class="exam"><div class="lab">학교 시험</div><div class="qq">${tex(q.q)}</div>${imgOf(q)}${ch}</div>
<div class="ours"><div class="lab">채수학 교재</div>${right}</div></div></section>`;
};

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>${m.school} 적중 리포트</title>
<link rel="stylesheet" href="file://${NM}/katex/dist/katex.min.css">
<link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/400.css"><link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/700.css"><link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/800.css">
<style>
${BOOKCSS.replace(/@page[^}]*}/g, '').replace(/(^|})\s*(body|\*|html)[^{]*{[^}]*}/g, '$1')}
@page{size:A4;margin:12mm 12mm 14mm}
*{box-sizing:border-box}
body{margin:0;font-family:'Nanum Gothic',sans-serif;color:#1c2b24;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}
:root{--g:#2E6B4F;--gd:#245641;--line:#BFD6C9;--R:#E60012;--O:#E08A00}
.hero{border-radius:10px;background:linear-gradient(135deg,#245641,#2E6B4F);color:#fff;padding:7mm 8mm 6mm}
.hero .k{font-size:10pt;opacity:.85;font-weight:700}
.hero h1{margin:1.5mm 0 1mm;font-size:21pt;font-weight:800;letter-spacing:-.5px}
.hero .s{font-size:10.5pt;opacity:.92}
.sum{display:flex;gap:4mm;margin:5mm 0 3mm}
.box{flex:1;border:1.4px solid var(--line);border-radius:8px;padding:3mm 4mm;text-align:center}
.box .v{font-size:20pt;font-weight:800;color:var(--gd)}.box .t{font-size:9pt;color:#6b7a72;font-weight:700}
.box.r .v{color:var(--R)}.box.o .v{color:var(--O)}
.strip{display:flex;flex-wrap:wrap;gap:1.6mm;margin:3mm 0 1.5mm}
.nb{width:8mm;height:8mm;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9pt;font-weight:800;background:#eef2f0;color:#9aa8a0}
.nb.same{background:var(--R);color:#fff}.nb.sim{background:var(--O);color:#fff}
.lg{font-size:8.5pt;color:#6b7a72;margin-bottom:2mm}.lg i{display:inline-block;width:3mm;height:3mm;border-radius:50%;vertical-align:-.3mm;margin:0 1mm 0 3mm}
.used{font-size:9pt;color:#245641;background:#E8F0EC;border-radius:6px;padding:2mm 3mm;margin-bottom:4mm}
.card{border:1.3px solid var(--line);border-radius:8px;margin:0 0 4mm;break-inside:avoid;overflow:hidden}
.card>.ch{display:flex;align-items:center;gap:3mm;background:#E8F0EC;padding:1.6mm 4mm}
.qno{font-weight:800;font-size:12pt;color:var(--gd)}.unit{font-size:8.6pt;color:#4a5a52}.card .pt{margin-left:auto;font-size:8.6pt;color:#6b7a72;font-weight:700}
.two{display:grid;grid-template-columns:1fr 1fr}
.exam,.ours{padding:3mm 4mm}.exam{border-right:1px dashed var(--line)}
.lab{font-size:8pt;font-weight:800;color:#fff;background:#6b7a72;display:inline-block;border-radius:3px;padding:0 2mm;margin-bottom:1.5mm}
.ours>.lab{background:var(--g)}
.qq{font-size:10pt;line-height:1.7}
img.ex{display:block;margin:2mm auto;max-width:100%}
.xch{display:flex;flex-wrap:wrap;gap:1mm 4mm;font-size:9.6pt;margin-top:1.5mm}
.bk+.bk{border-top:1px dashed var(--line);margin-top:2mm;padding-top:2mm}
.bh{display:flex;align-items:center;gap:2mm;margin-bottom:1mm}
.badge{font-size:8.4pt;font-weight:800;color:#fff;border-radius:3px;padding:.2mm 2mm}.badge.same{background:var(--R)}.badge.sim{background:var(--O)}
.src{font-size:7.8pt;color:#245641;font-weight:700}
.book .q{padding:0;border:0!important;display:block}.book .q .qt{font-size:9.6pt}.book .chs{margin-left:0;font-size:9.4pt;grid-template-columns:repeat(3,auto)!important;justify-content:start}
.book svg.fg{width:38mm!important;margin:2mm auto}.book .ans,.book .an{display:none}
.note{font-size:8.6pt;color:#7A4A2A;background:#FFF6E5;border-radius:4px;padding:1mm 2mm;margin-top:1.5mm}
.end{margin-top:5mm;border-top:2px solid var(--g);padding-top:3mm;font-size:9.5pt;color:#245641;line-height:1.7}
</style></head><body>
<div class="hero"><div class="k">채수학 교재 적중 리포트</div><h1>${m.title}</h1><div class="s">${m.subject ? m.subject + ' · ' : ''}시험 범위 ${m.range || ''}</div></div>
<div class="sum"><div class="box"><div class="v">${rows.length}</div><div class="t">전체 문항</div></div>
<div class="box"><div class="v">${hitRows.length}</div><div class="t">교재 적중 문항</div></div>
<div class="box r"><div class="v">${nSame}</div><div class="t">일치 (같은 문제·숫자만 다름)</div></div>
<div class="box o"><div class="v">${nSim}</div><div class="t">유사 (같은 유형·풀이)</div></div>
<div class="box"><div class="v">${rate}%</div><div class="t">적중률</div></div></div>
<div class="strip">${strip}</div>
<div class="lg"><i style="background:#E60012"></i>일치 <i style="background:#E08A00"></i>유사 <i style="background:#eef2f0"></i>해당 없음</div>
${books.length ? `<div class="used">📘 적중 교재: ${books.join(', ')}</div>` : ''}
${hitRows.map(card).join('\n')}
<div class="end"><b>채수학교습소</b> | 수학하는 방법을 가르칩니다 · ☎ 010-8677-2263<br>
<span style="color:#6b7a72;font-size:8.6pt">* 학교 문항은 학습 비교용으로 옮겨 적었습니다. 교재 문항은 채수학 개념서 문제편 원본입니다.</span></div>
</body></html>`;

(async () => {
  const H = OUT.replace(/\.pdf$/, '.html');
  fs.writeFileSync(H, html);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + H, { waitUntil: 'networkidle' });
  await p.pdf({ path: OUT, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: `<div style="width:100%;font-size:7.5pt;color:#6b7a72;text-align:center;font-family:sans-serif">채수학교습소 · ${m.school} 적중 리포트 · <span class="pageNumber"></span>/<span class="totalPages"></span></div>`,
    margin: { top: '12mm', bottom: '14mm', left: '12mm', right: '12mm' } });
  await b.close(); fs.unlinkSync(H);
  if (texErr) { console.error('FAIL KaTeX 오류', texErr); process.exit(1); }
  console.log('OK', path.basename(OUT), `적중 ${hitRows.length}/${rows.length} (일치 ${nSame}, 유사 ${nSim})`);
})().catch((e) => { console.error('FAIL', e); process.exit(1); });
