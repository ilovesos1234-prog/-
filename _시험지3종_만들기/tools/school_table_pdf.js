const fs=require('fs');const {chromium}=require('playwright');
const T=JSON.parse(fs.readFileSync('tab.json'));const F='/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/build/node_modules/@fontsource/nanum-gothic/files/nanum-gothic-korean-';
let css=[400,700,800].map(w=>`@font-face{font-family:NG;font-weight:${w};src:url(file://${F}${w}-normal.woff2)}`).join('')+`
body{font-family:NG;margin:0;font-size:8.5pt}h1{font-size:17pt;margin:0 0 2px}.sub{color:#555;margin-bottom:8px;font-size:9pt}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #aaa;padding:2px 3px;text-align:center}
thead th{background:#e8e8e8;font-weight:800}thead{display:table-header-group}tr{break-inside:avoid}
td.s{text-align:left;font-weight:700}td.h{background:#dbe9f6;font-weight:700}td.y{font-size:7.5pt;color:#333}
tr.sep td{background:#333;color:#fff;font-weight:800;text-align:left;padding:4px 6px}th.yr{border-bottom:2px solid #111}`;
const C=T.cols;const yrs=[];for(const c of C){const l=yrs[yrs.length-1];if(l&&l[0]===c[0])l[1]++;else yrs.push([c[0],1]);}
let h=`<h1>기출방 학교별 시험지 표</h1><div class="sub">기준일 ${T.updated} · 학교 ${T.data.length}곳 · 시험지 ${T.n}개 &nbsp;|&nbsp; 칸 안 숫자 = 그 시험이 있는 <b>학년</b> (예: 1·3 → 1학년, 3학년)</div>`;
h+=`<table><thead><tr><th rowspan=2>학교</th><th rowspan=2>있는 년도</th>${yrs.map(([y,n])=>`<th class=yr colspan=${n}>${y}</th>`).join('')}<th rowspan=2>합계</th></tr><tr>${C.map(c=>`<th>${c[1]}학기<br>${c[2]}</th>`).join('')}</tr></thead><tbody>`;
let last='';for(const r of T.data){if(r[1]!==last){last=r[1];h+=`<tr class=sep><td colspan=${C.length+3}>${r[1]} (${T.data.filter(x=>x[1]===last).length}곳)</td></tr>`;}
 h+=`<tr><td class=s>${r[0]}</td><td class=y>${r[2]}</td>${r.slice(3,3+C.length).map(v=>v?`<td class=h>${v}</td>`:'<td></td>').join('')}<td>${r[3+C.length]}</td></tr>`;}
h+='</tbody></table>';fs.writeFileSync('t.html',`<!doctype html><meta charset=utf-8><style>${css}</style>${h}`);
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.cwd()+'/t.html');await p.evaluate(()=>document.fonts.ready);
await p.pdf({path:process.argv[2],format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#777"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',margin:{top:'10mm',bottom:'12mm',left:'8mm',right:'8mm'}});await b.close();console.log('OK')})();
