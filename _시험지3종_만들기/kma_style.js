// KMA 견본 틀(문제 2×2 → 정답 → 해설)로 교재 문제 풀이집 만들기
// 사용법: node kma_style.js <데이터.js> <출력.pdf>
const fs = require('fs');
const path = require('path');
const katex = require('katex');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const D = require(path.resolve(process.argv[2]));
const OUT = process.argv[3];
const TEACHER = process.argv[4] === 'teacher';  // 교사용: 풀이가 문제 바로 아래
const NM = path.join(__dirname, 'node_modules');
const tex = (s) => s.replace(/\$([^$]+)\$/g, (_, m) => katex.renderToString(m, { throwOnError: true, strict: false }));
const CIRC = ['①', '②', '③', '④', '⑤'];

const css = `
@page{size:A4;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:'Nanum Gothic',sans-serif;color:#1A1A1A;font-size:9.5pt;line-height:1.75;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.katex{font-size:1.05em}
.page{position:relative;width:595.28pt;height:841.89pt;page-break-after:always;overflow:hidden}
.page:last-child{page-break-after:auto}
.hd{position:absolute;left:42.5pt;right:42.5pt;top:26pt;display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1.2pt solid #2E6B4F;padding-bottom:4pt}
.hd .l{font-weight:800;color:#245641;font-size:10pt}
.hd .l small{display:block;font-weight:700;color:#1A1A1A;font-size:12.5pt;letter-spacing:-.3pt}
.hd .r{font-size:8pt;color:#6b7280;text-align:right}
.nm{position:absolute;right:42.5pt;top:66pt;font-size:9pt;color:#444}
.nm span{display:inline-block;border-bottom:.6pt solid #888;width:70pt;margin:0 10pt 0 4pt}
.ft{position:absolute;left:42.5pt;right:42.5pt;bottom:20pt;display:flex;justify-content:space-between;font-size:8pt;color:#6b7280;border-top:.5pt solid #CFD6DA;padding-top:4pt}
.ft b{color:#245641}
.body{position:absolute;left:42.5pt;top:80.7pt;width:510.28pt;height:698.79pt}
.spot{position:absolute;width:245.1pt;height:337.4pt;overflow:hidden}
.spot.r{border-left:.5pt solid #CFD6DA;padding-left:10pt}
.no{font-size:10.5pt;font-weight:800;line-height:1.1;margin-bottom:3pt}
.src{display:inline-block;background:#E8F0EC;border:.5pt solid #BFD6C9;color:#245641;font-size:7.5pt;font-weight:700;border-radius:7pt;padding:.5pt 5pt;margin-left:4pt;vertical-align:1pt}
.q{text-align:justify;word-break:keep-all}
.ch{display:grid;grid-template-columns:repeat(3,1fr);row-gap:2pt;margin-top:4pt}
.ch.one{grid-template-columns:1fr}
.box{border:.6pt solid #555;border-radius:3pt;padding:3pt 6pt;margin:4pt 0}
.fig{text-align:center;margin:3pt 0}
.ttl{font-size:13pt;font-weight:800;color:#245641;border-bottom:1pt solid #2E6B4F;padding-bottom:3pt;margin-bottom:9pt}
.agrid{display:grid;grid-template-columns:1fr 1fr;gap:6pt 16pt;font-size:11.5pt}
.agrid div{display:flex;gap:6pt;align-items:center;min-height:22pt;border-bottom:.5pt dotted #CFD6DA;padding:2pt 1pt}
.agrid b{color:#245641;min-width:38pt}
.anote{margin-top:12pt;font-size:8.5pt;color:#8B95A1}
.sol{column-count:2;column-gap:20pt;column-rule:.5pt solid #E3E8EA;height:670pt;column-fill:auto}
.s{break-inside:avoid;margin-bottom:10pt}
.s b.n{font-size:10.5pt;font-weight:800;display:block;line-height:1.2;margin-bottom:2pt}
.s .a{display:inline-block;margin-top:2pt;color:#C2362B;font-weight:800;border:1pt solid #C2362B;border-radius:4pt;padding:0 5pt}
.s .t{color:#245641;font-weight:700}
.tsol{margin-top:5pt;border-top:.8pt dashed #2E6B4F;padding-top:4pt;color:#1d3f8f;font-size:8.8pt;line-height:1.6}
.tsol .k{display:inline-block;background:#2E6B4F;color:#fff;font-size:7.5pt;font-weight:800;border-radius:3pt;padding:0 4pt;margin-right:4pt}
.tsol .a{display:inline-block;margin-top:2pt;color:#C2362B;font-weight:800;border:1pt solid #C2362B;border-radius:4pt;padding:0 5pt}
.tsol .t{color:#245641;font-weight:700}
.tmark{color:#C2362B;font-weight:800;margin-left:6pt;font-size:9pt}
`;
const head = (pg) => `<div class="hd"><div class="l">생각이 다른 수학, 채수학<small>${D.META.title}</small></div><div class="r">${TEACHER ? '<b style="color:#C2362B">교사용</b>' : '학생용'} · 채수학 편집<br>${D.META.sub}</div></div>
<div class="ft"><span>채수학교습소 | 수학하는 방법을 가르칩니다</span><b>${pg}</b><span>☎ 010-8677-2263</span></div>`;

let pages = [];
// 문제: 2×2
for (let i = 0; i < D.Q.length; i += 4) {
  const four = D.Q.slice(i, i + 4);
  const spot = (q, k) => {
    const left = k % 2 ? 260.1 : 5, top = k < 2 ? 0 : 349.4;
    const ch = q.ch ? `<div class="ch ${q.chOne ? 'one' : ''}">${q.ch.map((c, j) => `<span>${CIRC[j]} ${tex(c)}</span>`).join('')}</div>` : '';
    return `<div class="spot ${k % 2 ? 'r' : ''}" style="left:${left}pt;top:${top}pt"><div class="no">${q.n}${q.tag ? `<span class="src">${q.tag}</span>` : ''}</div><div class="q">${tex(q.q)}</div>${q.fig ? `<div class="fig">${q.fig}</div>` : ''}${ch}${TEACHER ? `<div class="tsol"><span class="k">풀이</span>${q.sol.map((l) => `<div>${tex(l)}</div>`).join('')}<span class="a">답 ${tex(q.ans)}</span></div>` : ''}</div>`;
  };
  pages.push((i === 0 && !TEACHER ? '<div class="nm">이름 <span></span>점수 <span></span></div>' : '') + `<div class="body">${four.map(spot).join('')}</div>`);
}
// 정답
pages.push(`<div class="body"><div class="ttl">정답</div><div class="agrid">${D.Q.map((q) => `<div><b>${q.n}</b> ${tex(q.ans)}</div>`).join('')}</div>${D.META.anote ? `<div class="anote">${tex(D.META.anote)}</div>` : ''}</div>`);
// 해설
const per = D.META.solPer || 9;
for (let i = 0; !TEACHER && i < D.Q.length; i += per) {
  pages.push(`<div class="body"><div class="ttl">해설${i ? ' (계속)' : ''}</div><div class="sol">${D.Q.slice(i, i + per).map((q) => `<div class="s"><b class="n">${q.n}</b>${q.sol.map((l) => `<div>${tex(l)}</div>`).join('')}<span class="a">답 ${tex(q.ans)}</span></div>`).join('')}</div></div>`);
}

const fonts = ['katex/dist/katex.min.css', '@fontsource/nanum-gothic/400.css', '@fontsource/nanum-gothic/700.css', '@fontsource/nanum-gothic/800.css']
  .map((f) => `<link rel="stylesheet" href="file://${path.join(NM, f)}">`).join('');
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>${D.META.title}</title>${fonts}<style>${css}</style></head><body>${pages.map((p, i) => `<div class="page">${head(i + 1)}${p}</div>`).join('')}</body></html>`;

(async () => {
  const hp = OUT.replace(/\.pdf$/, '.html');
  fs.writeFileSync(hp, html);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage();
  await p.goto('file://' + hp, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  if (TEACHER) await p.evaluate(() => {
    for (const s of document.querySelectorAll('.spot')) {
      let z = 1;
      while (s.scrollHeight > s.clientHeight + 1 && z > 0.72) { z -= 0.04; s.style.fontSize = (9.5 * z) + 'pt'; s.querySelectorAll('.tsol').forEach((t) => t.style.fontSize = (8.8 * z) + 'pt'); }
    }
  });
  const over = await p.evaluate(() => [...document.querySelectorAll('.spot')].filter((s) => s.scrollHeight > s.clientHeight + 1).map((s) => s.querySelector('.no').textContent));
  if (over.length) console.log('넘침', over);
  const sol = await p.evaluate(() => [...document.querySelectorAll('.sol')].some((s) => s.scrollWidth > s.clientWidth + 2));
  if (sol) console.log('해설 넘침');
  await p.pdf({ path: OUT, printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('ok', OUT);
})();
