const fs=require('fs');const B='/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/build/node_modules/';
const {chromium}=require('playwright');
const idx=JSON.parse(fs.readFileSync('/home/user/chaemath-app/exams/index.json'));const D=idx.items;
const G=['중1','중2','중3','고1','고2','고3'];const T=[[1,'중간'],[1,'기말'],[2,'중간'],[2,'기말']];
const years=[...new Set(D.map(x=>x.year))].sort((a,b)=>b-a);
const sub=s=>s==='확률과통계'?'확률과 통계':s;
const ko=(a,b)=>a.localeCompare(b,'ko');
const F=B+'@fontsource/nanum-gothic/files/nanum-gothic-korean-';
let css=[400,700,800].map(w=>`@font-face{font-family:NG;font-weight:${w};src:url(file://${F}${w}-normal.woff2)}`).join('');
css+=`@page{size:A4;margin:14mm 12mm}body{font-family:NG;color:#111;font-size:9.5pt;margin:0}
h1{font-size:22pt;font-weight:800;margin:0 0 4px}.sub{color:#555;margin-bottom:14px}
table{border-collapse:collapse;width:100%;margin:8px 0 16px}th,td{border:1px solid #999;padding:5px 6px;text-align:center}th{background:#eee}
td.t{font-weight:800;background:#f6f6f6}.tot{font-weight:800}
.sec{page-break-before:always}.sec h2{font-size:15pt;font-weight:800;border-bottom:3px solid #111;padding-bottom:4px;margin:0 0 6px}
.sec h2 span{font-size:10pt;font-weight:400;color:#555;margin-left:8px}
.g{margin:8px 0 2px;font-weight:800;font-size:10.5pt;background:#eee;padding:3px 6px;border-left:5px solid #111}.g span{font-weight:400;color:#555;font-size:9pt}
.ls{columns:4;column-gap:10px;font-size:9pt;line-height:1.5;padding:2px 4px}.ls div{break-inside:avoid}
.ls small{color:#666}`;
let h=`<h1>채수학 기출방 시험지 목록</h1><div class="sub">기준일 ${idx.updated} · 전체 ${D.length}개 (시험지·풀이·분석표 3종 모두 있음)</div>`;
h+=`<table><tr><th>년도·학기</th>${G.map(g=>`<th>${g}</th>`).join('')}<th>합계</th></tr>`;
const secs=[];
for(const y of years)for(const [t,e] of T){const L=D.filter(x=>x.year===y&&x.term===t&&x.exam===e);if(!L.length)continue;secs.push([y,t,e,L]);
 h+=`<tr><td class="t">${y} ${t}학기 ${e}</td>${G.map(g=>`<td>${L.filter(x=>x.grade===g).length||'-'}</td>`).join('')}<td class="tot">${L.length}</td></tr>`;}
h+=`<tr><td class="t">합계</td>${G.map(g=>`<td class="tot">${D.filter(x=>x.grade===g).length}</td>`).join('')}<td class="tot">${D.length}</td></tr></table>`;
h+=`<div class="sub">※ 다음 쪽부터 년도 → 학기(1학기 중간·기말, 2학기 중간·기말) → 학년 순으로 학교 이름을 가나다순으로 정리했습니다. 고등학교는 괄호 안에 과목을 적었습니다.</div>`;
for(const [y,t,e,L] of secs){h+=`<div class="sec"><h2>${y}년 ${t}학기 ${e}고사<span>총 ${L.length}개</span></h2>`;
 for(const g of G){const M=L.filter(x=>x.grade===g).sort((a,b)=>ko(a.school,b.school)||ko(a.subj||'',b.subj||''));if(!M.length)continue;
  h+=`<div class="g">${g} <span>${M.length}개</span></div><div class="ls">${M.map(x=>`<div>${x.school}${x.subj?` <small>(${sub(x.subj)})</small>`:''}</div>`).join('')}</div>`;}
 h+='</div>';}
const html=`<!doctype html><meta charset=utf-8><style>${css}</style>${h}`;fs.writeFileSync('list.html',html);
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.cwd()+'/list.html');await p.evaluate(()=>document.fonts.ready);
await p.pdf({path:process.argv[2],format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#777"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',margin:{top:'14mm',bottom:'14mm',left:'12mm',right:'12mm'}});await b.close();console.log('OK')})();
