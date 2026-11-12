// 채수학 시리즈 표지 (흑백) → PDF + PNG
const fs=require('fs'),path=require('path');
const NM='/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/build/node_modules';
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const C=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const out=process.argv[3];
const html=`<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/400.css"><link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/700.css"><link rel="stylesheet" href="file://${NM}/@fontsource/nanum-gothic/800.css">
<style>@page{size:210mm 297mm;margin:0}*{box-sizing:border-box;margin:0;padding:0}
body{width:210mm;height:297mm;font-family:'Nanum Gothic';color:#111;background:#fff;position:relative;overflow:hidden}
.top{height:22mm;background:#111;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 14mm}
.top b{font-size:17pt;font-weight:800;letter-spacing:1px}.top span{font-size:9pt}
.pill{position:absolute;top:42mm;left:14mm;display:flex;align-items:center;gap:4mm;font-size:10pt;color:#555}
.pill b{background:#111;color:#fff;border-radius:99px;padding:1.6mm 6mm;font-size:11pt;font-weight:800}
.t1{position:absolute;top:70mm;left:14mm;font-size:22pt;font-weight:800;color:#333}
.t2{position:absolute;top:86mm;left:14mm;font-size:38pt;font-weight:800;letter-spacing:-1px}
.t3{position:absolute;top:110mm;left:14mm;font-size:22pt;font-weight:800;color:#333}
.bar{position:absolute;top:127mm;left:14mm;right:14mm;height:2.4mm;background:#111}
.kind{position:absolute;top:134mm;left:14mm;display:flex;gap:2.5mm}
.kind span{border:1.2px solid #111;border-radius:2mm;padding:1.2mm 4mm;font-size:10.5pt;font-weight:700}
.kind span.on{background:#111;color:#fff}
.motto{position:absolute;top:186mm;left:14mm;font-size:14pt;font-weight:800}
.sub{position:absolute;top:197mm;left:14mm;font-size:9pt;color:#666}
.hr{position:absolute;top:207mm;left:14mm;width:80mm;border-top:1px solid #bbb}
.fig{position:absolute;top:150mm;right:14mm;width:82mm;height:82mm}
.info{position:absolute;top:214mm;left:14mm;font-size:9.5pt;color:#444;line-height:1.7;width:90mm}
.sign{position:absolute;top:247mm;left:14mm;right:14mm;display:flex;gap:12mm;font-size:10pt;font-weight:700}
.sign div{flex:1;display:flex;align-items:flex-end;gap:3mm}.sign i{flex:1;border-bottom:1px solid #111;height:5mm}
.foot{position:absolute;bottom:10mm;left:14mm;right:14mm;border-top:1.5px solid #111;padding-top:3mm;display:flex;justify-content:space-between;font-size:8.5pt}
.foot b{font-weight:800}
</style></head><body>
<div class="top"><b>채수학</b><span>생각이 다른 수학</span></div>
<div class="pill"><b>${C.year}</b>${C.pill}</div>
<div class="t1">${C.t1}</div><div class="t2">${C.t2}</div><div class="t3">${C.t3}</div>
<div class="bar"></div>
<div class="kind">${C.kinds.map(k=>`<span class="${k.on?'on':''}">${k.n}</span>`).join('')}</div>
<svg class="fig" viewBox="0 0 200 200"><circle cx="100" cy="100" r="92" fill="none" stroke="#999" stroke-width="1.6"/>
<polygon points="100,8 20,146 180,146" fill="none" stroke="#111" stroke-width="3.2"/><line x1="100" y1="8" x2="100" y2="146" stroke="#666" stroke-width="2.4" stroke-dasharray="6 4"/>
<circle cx="100" cy="8" r="4" fill="#111"/><circle cx="20" cy="146" r="4" fill="#111"/><circle cx="180" cy="146" r="4" fill="#111"/></svg>
<div class="motto">수학하는 방법을 가르칩니다</div><div class="sub">문제를 읽고, 생각하고, 끝까지 풀어내는 힘</div><div class="hr"></div>
<div class="info">${C.info}</div>
<div class="sign"><div>이름<i></i></div><div>점수<i></i></div></div>
<div class="foot"><span><b>채수학교습소</b> &nbsp;|&nbsp; 수학하는 방법을 가르칩니다</span><span>☎ 010-8677-2263</span></div>
</body></html>`;
(async()=>{fs.writeFileSync(out+'.html',html);const b=await chromium.launch();const p=await b.newPage({viewport:{width:794,height:1123},deviceScaleFactor:2.5});
await p.goto('file://'+out+'.html',{waitUntil:'networkidle'});await p.pdf({path:out+'.pdf',width:'210mm',height:'297mm',printBackground:true});
await p.screenshot({path:out+'.png',fullPage:false});await b.close();console.log('ok',out)})();
