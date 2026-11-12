const pl = require('./pl.js');
const R = String.raw;
const samp = (f, a, b, n = 120) => Array.from({ length: n + 1 }, (_, i) => { const x = a + (b - a) * i / n; return [x, f(x)]; });
const flip = (a) => a.map(([x, y]) => [y, x]);
const RED = '#D33', BLUE = '#1f6fe0';

// 222: f(g(x))
const gTri = pl({ x: [-0.3, 3.4], y: [-0.4, 3.4], w: 180, h: 150, s: [{ pts: [[0, 0], [1.5, 3], [3, 0]] }], guide: [[0, 1, 2.5, 1], [0.5, 0, 0.5, 1], [2.5, 0, 2.5, 1], [1.5, 0, 1.5, 3]],
  dots: [[0.5, 1, RED], [2.5, 1, RED], [1.5, 3, RED]], xt: [[0.5, '1/2'], [1.5, '3/2'], [2.5, '5/2'], [3, '3']], yt: [[1, '1'], [3, '3']],
  lab: [[0.05, 0.45, 'i)', RED], [0.6, 2.1, 'ii)', RED], [2.05, 2.1, 'iii)', RED], [2.7, 0.75, 'iv)', RED], [1.9, 3.2, 'y=g(x)']] });
const fBent = pl({ x: [-0.3, 3.4], y: [-0.4, 3.4], w: 180, h: 150, s: [{ pts: [[0, 0], [1, 2], [3, 3]] }], guide: [[0, 2, 1, 2], [1, 0, 1, 2]], xt: [[1, '1'], [3, '3']], yt: [[2, '2'], [3, '3']], lab: [[1.8, 3.2, 'y=f(x)']] });
const fgG = pl({ x: [-0.3, 3.4], y: [-0.4, 3.4], w: 230, h: 165, s: [{ pts: [[0, 0], [0.5, 2], [1.5, 3], [2.5, 2], [3, 0]], hl: 1 }],
  guide: [[0.5, 0, 0.5, 2], [1.5, 0, 1.5, 3], [2.5, 0, 2.5, 2], [0, 2, 2.5, 2], [0, 3, 1.5, 3]], dots: [[0.5, 2, RED], [1.5, 3, RED], [2.5, 2, RED]],
  xt: [[0.5, '1/2'], [1.5, '3/2'], [2.5, '5/2'], [3, '3']], yt: [[2, '2'], [3, '3']], lab: [[1.8, 3.25, 'y=f(g(x))']] });

// 223~224: f(x)=x^2+1 (x<0), 1-x (x>=0)
const f3 = (x) => (x < 0 ? x * x + 1 : 1 - x);
const f3G = pl({ x: [-1.6, 2], y: [-1.4, 3], w: 180, h: 150, s: [{ pts: samp(f3, -1.4, 0) }, { pts: samp(f3, 0, 1.9) }], dots: [[0, 1, RED], [1, 0, RED]], xt: [[1, '1']], yt: [[1, '1']], lab: [[0.25, 1.6, 'y=f(x)']] });
const ff3 = (x) => f3(f3(x));
const ff3G = pl({ x: [-1.6, 2], y: [-1.6, 2.6], w: 200, h: 165, s: [{ pts: samp(ff3, -1.25, 0), hl: 1 }, { pts: samp(ff3, 0, 1), hl: 1 }, { pts: samp(ff3, 1, 2.2), hl: 1 }],
  guide: [[1, 0, 1, 1], [0, 1, 1, 1]], xt: [[1, '1']], yt: [[1, '1']], dots: [[1, 1, RED]], lab: [[-1.5, 2.2, 'y=(f∘f)(x)', RED]] });

// 225: |x-2|
const f4 = (x) => Math.abs(x - 2);
const g225a = pl({ x: [-1, 5.5], y: [-2.6, 3.4], w: 210, h: 170, s: [{ pts: samp((x) => f4(x) - 2, -0.8, 5.2), c: '#bbb', w: 1 }, { pts: samp((x) => Math.abs(f4(x) - 2), -0.8, 5.2), c: RED, w: 2.2 }],
  xt: [[2, '2'], [4, '4']], yt: [[2, '2']], lab: [[3.3, 2.6, 'y=(f∘f)(x)', RED]] });
const g225b = pl({ x: [-3, 7.5], y: [-2.6, 3.2], w: 240, h: 170, s: [{ pts: samp((x) => Math.abs(f4(x) - 2) - 2, -2.8, 7.3), c: '#bbb', w: 1 }, { pts: samp((x) => Math.abs(Math.abs(f4(x) - 2) - 2), -2.8, 7.3), c: RED, w: 2.2 }],
  xt: [[-2, '-2'], [2, '2'], [4, '4'], [6, '6']], yt: [[2, '2']], lab: [[4.3, 2.7, 'y=(f∘f∘f)(x)', RED]] });

// 227: f(f(x))=x
const tri = [[0, 0], [1, 2], [2, 0]];
const g227 = pl({ x: [-0.3, 2.5], y: [-0.3, 2.5], w: 200, h: 180, s: [{ pts: tri }, { pts: flip(tri), c: RED }, { pts: [[0, 0], [2.3, 2.3]], c: '#bbb', w: 1, dash: 1 }],
  dots: [[0, 0], [0.8, 1.6], [4 / 3, 4 / 3], [1.6, 0.8]], xt: [[1, '1'], [2, '2']], yt: [[1, '1'], [2, '2']],
  lab: [[1.05, 2.15, 'y=f(x)'], [2.02, 1.05, 'x=f(y)', RED], [2.0, 2.35, 'y=x', '#999']] });

// 230: 교점 0/1/2개
const mini = (c, n) => pl({ x: [-0.15, 2.2], y: [-0.15, 2.2], w: 120, h: 110, s: [{ pts: samp((x) => x * x + c, 0, Math.sqrt(2.2 - c)) }, { pts: flip(samp((x) => x * x + c, 0, Math.sqrt(2.2 - c))), c: RED }],
  dots: n === 0 ? [] : n === 1 ? [[0.5, 0.5]] : [[(1 - Math.sqrt(0.6)) / 2, (1 - Math.sqrt(0.6)) / 2], [(1 + Math.sqrt(0.6)) / 2, (1 + Math.sqrt(0.6)) / 2]], lab: [[1.25, 0.35, n + '개', '#111', 12]] });
const dec = samp((x) => 1 - x * x, 0, 1);
const p = (Math.sqrt(5) - 1) / 2;
const g230 = pl({ x: [-0.3, 1.4], y: [-0.3, 1.4], w: 190, h: 170, s: [{ pts: dec }, { pts: flip(dec), c: RED }, { pts: [[-0.2, -0.2], [1.25, 1.25]], c: '#bbb', w: 1, dash: 1 }, { pts: [[0, 1], [1, 0]], c: '#bbb', w: 1 }],
  dots: [[0, 1], [p, p], [1, 0]], lab: [[0.08, 1.2, 'y=f(x)'], [0.95, 0.25, 'y=f⁻¹(x)', RED], [1.12, 1.3, 'y=x', '#999'], [0.62, 0.55, '기울기 −1', '#888', 9.5]] });

// 232
const f6 = (x) => (x < 1 ? -x / 2 + 1.5 : -1.5 * x * x + 2.5 * x);
const a6 = samp(f6, -1.6, 1), b6 = samp(f6, 1, 2.3);
const g232 = pl({ x: [-2, 3], y: [-2, 3], w: 210, h: 200, s: [{ pts: a6 }, { pts: b6 }, { pts: flip(a6), c: RED }, { pts: flip(b6), c: RED }, { pts: [[-1.8, -1.8], [2.8, 2.8]], c: '#bbb', w: 1, dash: 1 }],
  dots: [[1, 1], [-1, 2], [2, -1]], xt: [[-1, '-1'], [1, '1'], [2, '2']], yt: [[2, '2'], [-1, '-1']], lab: [[-1.9, 2.5, 'y=f(x)'], [1.8, -1.6, 'y=f⁻¹(x)', RED]] });

module.exports = R`
<div class="card"><div class="h"><span class="k">응용</span>같은 방법으로 $f(g(x))$의 그래프 그리기</div><div class="b">
<div class="src" style="margin:0">원본 222쪽</div>
<div class="row">${gTri}${fBent}</div>
$g(x)$가 $f$의 꺾이는 $x$값 $1$이 되는 곳: $g(x)=1$ → $x=\dfrac12,\ \dfrac52$ / $g$가 꺾이는 곳: $x=\dfrac32$
<div class="step"><span class="c">i) $0\le x<\frac12$</span><span>$g:0\to1$ ⇒ $f:0\to2$ &nbsp; $f(g(x))=2(2x)=4x$</span></div>
<div class="step"><span class="c">ii) $\frac12\le x<\frac32$</span><span>$g:1\to3$ ⇒ $f:2\to3$ &nbsp; $f(g(x))=\frac12(2x)+\frac32=x+\frac32$</span></div>
<div class="step"><span class="c">iii) $\frac32\le x<\frac52$</span><span>$g:3\to1$ ⇒ $f:3\to2$ &nbsp; $f(g(x))=\frac12(-2x+6)+\frac32=-x+\frac92$</span></div>
<div class="step"><span class="c">iv) $\frac52\le x\le3$</span><span>$g:1\to0$ ⇒ $f:2\to0$ &nbsp; $f(g(x))=2(-2x+6)=-4x+12$</span></div>
<div class="row" style="justify-content:center">${fgG}</div>
<div class="tip"><b>강사 TIP</b> 직선과 직선의 합성은 그냥 <b>양 끝점을 연결</b>하면 된다. 끝점 $(0,0)$, $\left(\frac12,2\right)$, $\left(\frac32,3\right)$, $\left(\frac52,2\right)$, $(3,0)$만 찍게 하자.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 3</span>곡선이 섞인 합성: $y=(f\circ f)(x)$의 그래프</div><div class="b">
<div class="src" style="margin:0">원본 223~224쪽</div>
$f(x)=\begin{cases}x^2+1 & (x<0)\\ 1-x & (x\ge0)\end{cases}$일 때, $y=(f\circ f)(x)$의 그래프를 그려 보자.
<div class="row">${f3G}<div style="flex:1;min-width:70mm">기준이 되는 점<br>· $f(x)$의 <b>식이 바뀌는 지점</b>: $x=0$<br>· $f(x)=0$ <b>인 지점</b>: $x=1$ &nbsp;(안쪽 $f$의 값이 바깥 $f$의 경계 $0$을 지나는 곳)</div></div>
<b style="color:#17777a">풀이 1) 그래프로 (끝점 + 모양)</b><br>
· $x<0$: $f(x)$는 $\infty\to1$로 <b>가파르다가 완만해지며</b> 감소 → 바깥 $f$는 $1-x$ 식 → $y$는 $-\infty\to0$, 역시 가파르다가 완만<br>
· $0\le x<1$: $f(x):1\to0$ → $1-x$ 식 → $y:0\to1$ (직선)<br>
· $x\ge1$: $f(x):0\to-\infty$ → $x^2+1$ 식 → $y:1\to\infty$ (곡선)
<div class="row" style="justify-content:center">${ff3G}</div>
<b style="color:#17777a">풀이 2) 서술형 답안용</b>
<div class="step"><span class="c">i) $x<0$</span><span>$f(x)=x^2+1>0$ ⇒ $(f\circ f)(x)=1-(x^2+1)=-x^2$</span></div>
<div class="step"><span class="c">ii) $0\le x<1$</span><span>$f(x)=1-x>0$ ⇒ $(f\circ f)(x)=1-(1-x)=x$</span></div>
<div class="step"><span class="c">iii) $x\ge1$</span><span>$f(x)=1-x\le0$ ⇒ $(f\circ f)(x)=(1-x)^2+1$</span></div>
<div class="tip"><b>강사 TIP</b> 곡선이면 끝점만 잇지 말고 <b>'가파르다가 완만해짐'</b> 같은 모양(볼록성)까지 함께 옮겨야 한다. $x=1$에서 iii)의 식에 $f(1)=0$을 넣으면 $0^2+1=1$, ii)의 끝값도 $1$이라 이어진다는 것을 확인시키자.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 4</span>$f(x)=|x-2|$일 때 $y=(f\circ f)(x)$, $y=(f\circ f\circ f)(x)$</div><div class="b">
<div class="src" style="margin:0">원본 225쪽</div>
$f(x)=|x-2|=\begin{cases}x-2 & (x\ge2)\\ 2-x & (x<2)\end{cases}$ — 어느 쪽으로 주어지든 <b>하나의 함수</b>라는 것을 캐치해야 한다.<br>
$f(f(x))=|f(x)-2|$ → $f(x)$의 그래프를 $y$축 방향으로 $-2$만큼 이동한 다음 <b>절댓값을 씌우면(접어 올리면)</b> 된다.
<div class="row" style="justify-content:center">${g225a}${g225b}</div>
$(f\circ f\circ f)(x)=|(f\circ f)(x)-2|$ → $y=(f\circ f)(x)$의 그래프를 2만큼 내린 다음 접어 올린다. 꼭짓점: $(-2,0),(0,2),(2,0),(4,2),(6,0)$
<div class="tip"><b>강사 TIP</b> '내리고 → 접어 올리기'를 반복할 때마다 W자의 봉우리가 늘어난다. $(f\circ f\circ f)(x)=k$의 실근 개수 문제로 바로 연결된다.</div>
</div></div>

<h2>합성함수와 방정식</h2>
<div class="card"><div class="h"><span class="k">유형</span>$(f\circ f)(x)=f(x)$의 해의 개수</div><div class="b">
<div class="src" style="margin:0">원본 226쪽</div>
<div class="step"><span class="c">풀이 1</span><span>$y=(f\circ f)(x)$와 $y=f(x)$의 그래프를 각각 그려서 교점 찾기</span></div>
<div class="step"><span class="c">풀이 2</span><span>$f(x)=t$로 치환 → $f(t)=t$를 만족하는 $t$를 찾은 다음, $f(x)=t$를 만족하는 $x$ 찾기</span></div>
<div style="margin-top:2mm"><b>[예제]</b> $f(f(x))=4-f(x)$의 해를 구하시오.</div>
$f(x)=t$로 치환 → $f(t)=4-t$ ⇒ 직선 $y=4-t$와 $y=f(t)$의 교점 $t$를 찾고 → $f(x)=t$를 푼다.
<div class="tip"><b>강사 TIP</b> 치환하면 '두 번 푸는 문제'가 된다. 1단계에서 $t$가 여러 개 나오면 2단계에서 <b>$t$마다 따로</b> 해의 개수를 세서 더한다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 5</span>$f(f(x))=x$의 해</div><div class="b">
<div class="src" style="margin:0">원본 227~228쪽</div>
<div class="step"><span class="c">풀이 1</span><span>$y=(f\circ f)(x)$와 $y=x$의 그래프를 그려서 교점 찾기</span></div>
<div class="step"><span class="c">풀이 2</span><span>$y=f(x)$와 $x=f(y)$를 연립하면 된다. ($y=f(x)$를 $x=f(y)$에 대입하면 $x=f(f(x))$)<br><span style="color:#D33">$x=f(y)$는 함수일 수도 있고 아닐 수도 있음 — $y=f(x)$를 $y=x$에 대칭시킨 것</span></span></div>
<div class="row"><div>${g227}</div><div style="flex:1;min-width:60mm">예를 들어 $f$가 $(0,0),(1,2),(2,0)$을 잇는 꺾은선이라면<br>교점: $(0,0)$, $\left(\frac45,\frac85\right)$, $\left(\frac43,\frac43\right)$, $\left(\frac85,\frac45\right)$<br>⇒ $f(f(x))=x$의 해는 $x=0,\ \frac45,\ \frac43,\ \frac85$ → <b>4개</b><br><span style="font-size:9pt;color:#555">확인: $f\left(\frac45\right)=\frac85$, $f\left(\frac85\right)=\frac45$</span></div></div>
<div style="margin-top:2mm"><b>[예제]</b> $(f\circ f\circ f)(x)=x$ → $y=f(x)$와 $x=f(f(y))$를 연립: $y=(f\circ f)(x)$의 그래프를 그린 다음 그걸 $y=x$에 대칭시키고, $y=f(x)$와의 교점을 찾으면 된다.</div>
<div class="tip"><b>강사 TIP</b> 풀이 2의 장점은 $y=x$ 위에 있지 않은 교점(서로 짝인 점 $(a,b)$, $(b,a)$)까지 한 번에 보인다는 것. 풀이 1로만 하면 $f\circ f$를 정확히 그려야 해서 시간이 걸린다.</div>
</div></div>

<h2>역함수</h2>
<div class="card"><div class="h"><span class="k">개념</span>역함수 $f^{-1}$와 성질</div><div class="b">
<div class="src" style="margin:0">원본 229쪽</div>
$f:X\to Y$, &nbsp;$f^{-1}:Y\to X$ &nbsp;(화살표 방향을 거꾸로)<br>
<b>I. 역함수의 성질</b>
<ol><li>$f\circ f^{-1}=I$, $f^{-1}\circ f=I$</li>
<li>$(f^{-1})^{-1}=f$</li>
<li><b style="color:#D33">★</b> $y=f(x)$와 $y=f^{-1}(x)$의 그래프는 직선 $y=x$에 대하여 대칭</li>
<li><b style="color:#D33">★</b> $f(a)=b$이면 $f^{-1}(b)=a$</li></ol>
<div class="wrong"><b>✘ $f\circ f^{-1}=f^{-1}\circ f$라고 생각하면 절대 안 됨!</b><br>
$f:\{1,2,3,4\}\to\{a,b,c,d\}$일 때 $f\circ f^{-1}$은 $\{a,b,c,d\}\to\{a,b,c,d\}$인 항등함수, $f^{-1}\circ f$는 $\{1,2,3,4\}\to\{1,2,3,4\}$인 항등함수 → 정의역이 달라 같은 함수가 아님</div>
</div></div>

<div class="card"><div class="h"><span class="k">개념</span>II. $y=f(x)$와 $y=f^{-1}(x)$의 교점</div><div class="b">
<div class="src" style="margin:0">원본 230쪽</div>
교점은 생길 수도 있고 안 생길 수도 있다. (예: 이차함수를 반 자른 것과 무리함수는 역함수 관계)
<div class="row" style="justify-content:center">${mini(0.5, 0)}${mini(0.25, 1)}${mini(0.1, 2)}</div>
· 역함수가 존재하려면 <b>일대일대응</b>이어야 한다.<br>
· "교점이 존재할 때 이 교점은 무조건 $y=x$ 위에 있다" → <b style="color:#D33">거짓</b>
<div class="row"><div>${g230}</div><div style="flex:1;min-width:60mm"><b>반례</b> 감소하는 이차함수(반쪽)와 무리함수<br>$y=x$ 위의 교점 1개 + $y=x$에 대칭인 교점 2개 $(0,1)$, $(1,0)$<br>→ 두 점을 이은 직선의 기울기 $-1$</div></div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 6</span>$f(x)=\sqrt{ax+b}$와 $f^{-1}(x)$의 교점이 $(1,4)$일 때 $a,b$</div><div class="b">
<div class="src" style="margin:0">원본 231쪽</div>
<b>핵심 원리</b>
<div class="step"><span class="c">$y=x$ 위</span><span>$f(\alpha)=\alpha$이면 $f^{-1}(\alpha)=\alpha$</span></div>
<div class="step"><span class="c">$y=x$ 밖</span><span>교점이 $(a,b)$이면 $f(a)=b\Rightarrow f^{-1}(b)=a$, $f^{-1}(a)=b\Rightarrow f(b)=a$<br>즉 <span class="hl1">$(a,b)$</span>를 교점으로 가지면 반드시 <span class="hl1">$(b,a)$</span>도 교점 (두 점을 이은 직선의 기울기 $-1$)</span></div>
· 교점이 $y=x$ 위에 없다면 <b>증가함수는 아님</b> (기울기 $-1$인 두 점을 지나므로)<br>
· 반대로, <b>증가함수이고 교점이 존재한다면 교점은 반드시 $y=x$ 위</b>에 있다.
<div class="ok"><b style="color:#2e8b57">결론) $f(x)$와 $f^{-1}(x)$의 교점을 구하는 문제</b><br>i) 증가함수 → $f(x)=x$ 풀기<br>ii) 감소함수 → ① $f(x)=x$ 풀기 ② 두 교점이 $y=x$에 대칭인 경우가 있는지 확인하기</div>
<b>풀이</b> $(1,4)$는 $y=x$ 위에 있지 않으므로 $(4,1)$도 교점 (이 경우 교점은 3개)<br>
$f(1)=4$: $\sqrt{a+b}=4\Rightarrow a+b=16$, &nbsp; $f(4)=1$: $\sqrt{4a+b}=1\Rightarrow 4a+b=1$<br>
$\therefore a=-5,\ b=21$ &nbsp; (감소함수 ✓)
<br><span class="ans">답 $a=-5,\ b=21$</span>
</div></div>

<div class="card"><div class="h"><span class="k">예제 7</span>연속함수와 역함수의 교점 3개</div><div class="b">
<div class="src" style="margin:0">원본 232쪽</div>
$f(x)=\begin{cases}ax+b & (x<1)\\ cx^2+\frac52x & (x\ge1)\end{cases}$가 연속<span style="color:#D33">(=끊기지 않고 한붓그리기가 가능한 함수)</span>이고, $f(x)$와 $f^{-1}(x)$의 교점이 3개, 교점의 $x$좌표가 $-1,1,2$이다. $a,b,c$를 구하시오.
<div class="row"><div>${g232}</div><div style="flex:1;min-width:65mm">
역함수를 가지므로 증가 or 감소함수<br>
· 증가함수라면 교점이 모두 $y=x$ 위 → $(-1,-1),(1,1),(2,2)$<br>&nbsp;&nbsp;$f(1)=1$이면 $c=-\frac32$, $f(2)=2$이면 $c=-\frac34$ → 모순, 존재하지 않음<br>
· ∴ <b>감소함수</b>: $-1,1,2$ 중 가운데 값이 $y=x$ 위의 점<br>&nbsp;&nbsp;교점은 $(1,1)$, $(-1,2)$, $(2,-1)$<br>
$f(1)=c+\frac52=1\Rightarrow c=-\frac32$ &nbsp;(확인 $f(2)=-6+5=-1$ ✓)<br>
$f(-1)=-a+b=2$, 연속: $a+b=1$ ⇒ $a=-\frac12,\ b=\frac32$
</div></div>
<span class="ans">답 $a=-\frac12,\ b=\frac32,\ c=-\frac32$</span>
<div class="tip"><b>강사 TIP</b> 감소함수에서 $y=x$ 밖의 교점은 짝 $(p,q)$, $(q,p)$로 생기므로 $x$좌표 3개 중 <b>가운데 값</b>이 $y=x$ 위의 점, 양 끝 값이 서로 짝이다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 8</span>$y=f(3x+1)$의 역함수를 $g(x)$로 표시</div><div class="b">
<div class="src" style="margin:0">원본 233쪽</div>
$y=f(x)$의 역함수가 $g(x)$이다. $y=f(3x+1)$의 역함수를 $g(x)$로 표시하여라.
<div style="margin-top:2mm"><b style="color:#17777a">풀이 1)</b> $y=f(3x+1)$에 어떤 함수를 합성했을 때 $x$가 나와야 한다. 구하려는 역함수를 ★라 하면</div>
$f(3\bigstar+1)=x$ → 양변에 $f^{-1}=g$를 걸면 $3\bigstar+1=g(x)$ → $\bigstar=\dfrac13\{g(x)-1\}$
<div style="margin-top:2mm"><b style="color:#17777a">풀이 2) 빨리 푸는 방법</b> — $x$, $y$를 서로 바꾸면 $x=f(3y+1)$ → 양변에 $g$: $g(x)=3y+1$ → 정리하면 $y=\dfrac{g(x)-1}{3}$</div>
<span class="ans">답 $y=\dfrac13\{g(x)-1\}$</span>
<div class="wrong"><b>✘ 자주 하는 실수</b> &nbsp; $g(3x+1)$로 쓰기 — 안쪽 $3x+1$은 $f$보다 <b>먼저</b> 적용되므로 역함수에서는 <b>나중에</b> 풀어야 한다.</div>
</div></div>

<h2 style="break-before:page">정답 한눈에</h2>
<div class="card"><div class="b"><table style="width:100%;border-collapse:collapse;font-size:9.5pt">
<tr style="background:#eaf7f7"><th style="padding:1.5mm;text-align:left">예제</th><th style="text-align:left">내용</th><th style="text-align:left">답</th><th>원본</th></tr>
<tr><td>1</td><td>$g\circ f$가 정의되는 $(f,g)$ 개수</td><td>$3360$</td><td>218~219</td></tr>
<tr><td>2</td><td>$g(f(x))$ 그래프</td><td>꺾이는 점 $\left(\frac34,3\right),(1,2)$</td><td>220~222</td></tr>
<tr><td>응용</td><td>$f(g(x))$ 그래프</td><td>$\left(\frac12,2\right),\left(\frac32,3\right),\left(\frac52,2\right)$</td><td>222</td></tr>
<tr><td>3</td><td>곡선 포함 $f\circ f$</td><td>$-x^2,\ x,\ (1-x)^2+1$</td><td>223~224</td></tr>
<tr><td>4</td><td>$|x-2|$의 반복 합성</td><td>내리고 접어 올리기</td><td>225</td></tr>
<tr><td>5</td><td>$f(f(x))=x$</td><td>$y=f(x)$, $x=f(y)$ 연립</td><td>227~228</td></tr>
<tr><td>6</td><td>$\sqrt{ax+b}$, 교점 $(1,4)$</td><td>$a=-5,\ b=21$</td><td>231</td></tr>
<tr><td>7</td><td>교점 $x$좌표 $-1,1,2$</td><td>$a=-\frac12,\ b=\frac32,\ c=-\frac32$</td><td>232</td></tr>
<tr><td>8</td><td>$f(3x+1)$의 역함수</td><td>$\frac13\{g(x)-1\}$</td><td>233</td></tr>
</table>
<div style="font-size:8.5pt;color:#8B95A1;margin-top:2mm">※ 예제 3·5·6·7·8의 답과 예제 5의 구체적 그래프는 원본 풀이를 따라 채수학에서 계산해 채웠습니다.</div>
</div></div>
`;
