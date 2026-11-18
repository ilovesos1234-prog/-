// 일반 좌표 그래프: o={x:[a,b], y:[c,d], w,h, s:[{f|pts, c, w, hl, dash}], dots:[[x,y,c]], lab:[[x,y,t,c]], xt:[[x,t]], yt:[[y,t]]}
function pl(o) {
  const W = o.w || 200, H = o.h || 160, P = 14;
  const X = (x) => P + (x - o.x[0]) / (o.x[1] - o.x[0]) * (W - 2 * P), Y = (y) => H - P - (y - o.y[0]) / (o.y[1] - o.y[0]) * (H - 2 * P);
  let s = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Nanum Gothic" font-size="10.5">`;
  s += `<line x1="${P - 6}" y1="${Y(0)}" x2="${W - 4}" y2="${Y(0)}" stroke="#222"/><path d="M${W - 4} ${Y(0)} l-6 -3 v6z" fill="#222"/>`;
  s += `<line x1="${X(0)}" y1="${H - 4}" x2="${X(0)}" y2="4" stroke="#222"/><path d="M${X(0)} 4 l-3 6 h6z" fill="#222"/>`;
  for (const [x, t] of o.xt || []) s += `<text x="${X(x)}" y="${Y(0) + 13}" text-anchor="middle">${t}</text>`;
  for (const [y, t] of o.yt || []) s += `<text x="${X(0) - 4}" y="${Y(y) + 4}" text-anchor="end">${t}</text>`;
  for (const b of o.box || []) s += `<rect x="${X(b[0])}" y="${Y(b[3])}" width="${X(b[2]) - X(b[0])}" height="${Y(b[1]) - Y(b[3])}" fill="${b[4] || '#F8DCDC'}" opacity=".8"/>`;
  for (const g of o.guide || []) s += `<line x1="${X(g[0])}" y1="${Y(g[1])}" x2="${X(g[2])}" y2="${Y(g[3])}" stroke="#bbb" stroke-dasharray="2 2"/>`;
  for (const se of o.s) {
    let pts = se.pts;
    if (se.f) { pts = []; const [a, b] = se.r || o.x; for (let i = 0; i <= 160; i++) { const x = a + (b - a) * i / 160, y = se.f(x); if (y >= o.y[0] - 1 && y <= o.y[1] + 1) pts.push([x, y]); } }
    const d = pts.map((p) => X(p[0]).toFixed(1) + ',' + Y(p[1]).toFixed(1)).join(' ');
    if (se.hl) s += `<polyline points="${d}" fill="none" stroke="#9BE27A" stroke-width="7" stroke-linecap="round" opacity=".8"/>`;
    s += `<polyline points="${d}" fill="none" stroke="${se.c || '#111'}" stroke-width="${se.w || 1.6}" ${se.dash ? 'stroke-dasharray="4 3"' : ''}/>`;
  }
  for (const p of o.dots || []) s += `<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="2.8" fill="${p[2] || '#1f6fe0'}"/>`;
  for (const l of o.lab || []) s += `<text x="${X(l[0])}" y="${Y(l[1])}" fill="${l[3] || '#111'}" font-size="${l[4] || 10.5}">${l[2]}</text>`;
  return s + `<defs><clipPath id="c"><rect width="${W}" height="${H}"/></clipPath></defs></svg>`;
}
module.exports = pl;
