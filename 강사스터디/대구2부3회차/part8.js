const pl = require('./pl.js');
const R = String.raw;
const samp = (f, a, b, n = 120) => Array.from({ length: n + 1 }, (_, i) => { const x = a + (b - a) * i / n; return [x, f(x)]; });
const RED = '#D33', BLUE = '#1f6fe0';

// 194 상등
const g194 = pl({ x: [-1.8, 1.8], y: [-2.2, 2.2], w: 190, h: 150, s: [{ pts: samp((x) => x ** 3, -1.3, 1.3) }, { pts: [[-1.7, -1.7], [1.7, 1.7]], c: RED }], dots: [[-1, -1], [0, 0], [1, 1]], xt: [[-1, '-1'], [1, '1']], lab: [[1.0, 2.0, 'f(x)=x³'], [1.1, 1.0, 'g(x)=x', RED]] });
// 196
const f6 = (x) => -x * x + 6 * x - 4;
const g196a = pl({ x: [-0.6, 5.2], y: [-1.5, 6], w: 200, h: 170, s: [{ pts: samp(f6, 0.2, 5) }, { pts: [[-0.4, -0.4], [5.1, 5.1]], c: RED }], guide: [[3, 0, 3, 5], [4, 0, 4, 4], [1, 0, 1, 1]], dots: [[1, 1], [4, 4]], xt: [[1, '1'], [3, '3'], [4, '4']], lab: [[4.3, 1.4, 'f(x)'], [4.3, 5.4, 'y=x', RED]] });
const g196b = pl({ x: [-0.6, 5.2], y: [-1.5, 6], w: 200, h: 170, box: [[-0.6, -1.5, 1, 1]], s: [{ pts: samp(f6, 0.2, 5) }, { pts: [[-0.4, -0.4], [5.1, 5.1]], c: RED }], guide: [[1, -1.5, 1, 1], [-0.6, 1, 1, 1]], dots: [[1, 1]], xt: [[1, '1'], [3, '3'], [4, '4']], lab: [[1.2, 0.6, 'k=1 ✔', '#2e8b57', 11]] });
const g196c = pl({ x: [-0.6, 5.2], y: [-1.5, 6], w: 200, h: 170, box: [[-0.6, -1.5, 4, 4]], s: [{ pts: samp(f6, 0.2, 5) }, { pts: [[-0.4, -0.4], [5.1, 5.1]], c: RED }], guide: [[4, -1.5, 4, 4], [-0.6, 4, 4, 4]], dots: [[3, 5, RED]], xt: [[1, '1'], [3, '3'], [4, '4']], lab: [[1.6, 5.5, '벗어나는 부분', RED, 10], [4.2, 3.4, 'k=4 ✘', RED, 11]] });
// 198
const f8 = (x) => 0.75 * (x - 2) ** 2 + 1;
const g198 = pl({ x: [-0.4, 5], y: [-0.4, 5.2], w: 210, h: 190, box: [[1, 1, 4, 4]], s: [{ pts: samp(f8, 0, 4.4) }, { pts: [[-0.3, -0.3], [4.9, 4.9]], c: RED }], guide: [[1, 0, 1, 1], [4, 0, 4, 4], [0, 4, 4, 4], [0, 1, 1, 1]], dots: [[1, 1], [4, 4], [2, 1, RED], [4 / 3, 4 / 3, '#999']], xt: [[1, '1'], [2, '2'], [4, '4']], yt: [[1, '1'], [4, '4']], lab: [[4.2, 4.95, 'y=x', RED], [0.1, 4.9, 'f(x)']] });
// 204
const g204 = pl({ x: [-2.2, 2.2], y: [-0.4, 4], w: 170, h: 130, s: [{ pts: samp((x) => 2 ** x, -2.1, 1.9), c: RED }, { pts: samp((x) => 0.5 ** x, -1.9, 2.1), c: BLUE }], dots: [[0, 1, '#111']], yt: [[1, '1']], lab: [[1.0, 3.6, '밑>1', RED], [-2.1, 3.6, '0<밑<1', BLUE]] });
// 209
const g209 = pl({ x: [-0.08, 1.15], y: [-0.08, 1.12], w: 210, h: 190, box: [[0, 0, 1, 1, '#f3f6f6']],
  s: [{ pts: [[1 / 3, 0.5], [2 / 3, 0.5]], c: RED, w: 2.4 }, { pts: [[1 / 9, 0.25], [2 / 9, 0.25]], c: RED, w: 2.4 }, { pts: [[7 / 9, 0.75], [8 / 9, 0.75]], c: '#aaa', w: 2.4, dash: 1 }],
  guide: [[1 / 3, 0, 1 / 3, 0.5], [2 / 3, 0, 2 / 3, 0.5], [1 / 9, 0, 1 / 9, 0.25], [2 / 9, 0, 2 / 9, 0.25], [0, 0.5, 1 / 3, 0.5], [0, 0.25, 1 / 9, 0.25]],
  dots: [[0, 0, '#111'], [1, 1, '#111'], [0.5, 0.5, '#111'], [2 / 13, 0.25, BLUE]], xt: [[1 / 9, '1/9'], [2 / 9, '2/9'], [1 / 3, '1/3'], [2 / 3, '2/3'], [1, '1']], yt: [[0.25, '1/4'], [0.5, '1/2'], [1, '1']], lab: [[0.52, 0.56, '(1/2, 1/2)'], [0.12, 0.31, 'f(2/13)', BLUE, 9.5]] });

module.exports = R`
<div class="cover"><span class="tag">강사스터디 · 대구 2부 3회차</span><div class="no">8</div><h1>함수</h1><p>참고자료 1 · 원본 194~215쪽 정리 · 채수학 편집</p></div>

<h2>함수의 정의와 기본 용어</h2>
<div class="card"><div class="h"><span class="k">개념</span>I. 함수의 정의 · II. 함수의 상등</div><div class="b">
<div class="src" style="margin:0">원본 194쪽</div>
<b>I. 함수</b>: 정의역의 <span class="hl1"><b style="color:#D33">★</b>모든</span> 원소들이 공역의 원소에 <span class="hl1"><b style="color:#D33">★</b>하나씩</span> 대응된다.<br>
<b>II. 함수의 상등</b>: 두 함수가 같다 = 정의역, 공역이 각각 같고 대응되는 것(함숫값)이 같다.
<div class="row"><div>${g194}</div><div style="flex:1;min-width:65mm">$f(x)=x^3$, $g(x)=x$일 때 정의역을 어떻게 잡으면 두 함수가 같아질까?<br>
· 정의역을 실수 전체로 잡으면 → 서로 다른 함수<br>
· $x^3=x$의 해 $x=-1,0,1$ → 정의역을 $X=\{-1,0,1\}$로 잡으면 된다.<br>
· $X$의 부분집합인 경우도 모두 가능 (단, 공집합 $\varnothing$은 제외)</div></div>
<div class="tip"><b>강사 TIP</b> $\varnothing$을 빼는 이유: 정의역의 임의의 원소가 공역의 원소에 대응되어야 하는데 원소가 없으면 함수가 안 된다. → 가능한 정의역은 $2^3-1=7$개.</div>
</div></div>

<div class="card"><div class="h"><span class="k">개념</span>III. 기본 용어</div><div class="b">
<div class="src" style="margin:0">원본 194~196쪽</div>
<div class="step"><span class="c">1. 항등함수</span><span>정의역의 임의의 원소 $x$에 대해 $f(x)=x$인 함수</span></div>
<div class="step"><span class="c">2. 상수함수</span><span>정의역의 모든 원소가 하나로 대응되는 함수</span></div>
<div class="step"><span class="c">3. 일대일함수</span><span>정의역의 임의의 두 원소 $x_1,x_2$에 대해 $x_1\ne x_2$이면 $f(x_1)\ne f(x_2)$<br>대우명제) $f(x_1)=f(x_2)$이면 $x_1=x_2$</span></div>
<div class="step"><span class="c">4. 일대일대응</span><span>일대일함수이면서 <b>치역=공역</b><br>유한집합이라면 정의역의 원소의 개수 = 공역의 원소의 개수</span></div>
<div class="tip"><b>강사 TIP</b> 일대일함수를 증명할 때는 대우명제 '$f(x_1)=f(x_2)\Rightarrow x_1=x_2$' 쪽이 식으로 다루기 훨씬 편하다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 1</span>$X\to X$가 일대일대응이 되는 $k$</div><div class="b">
<div class="src" style="margin:0">원본 196쪽</div>
$f(x)=-x^2+6x-4$, $X$에서 $X$로의 함수가 일대일대응이 되도록 하는 $X=\{x\mid x\le k\}$일 때 $k$의 값을 구하시오.<br>
<b>풀이</b> 정의역, 치역 모두 $k$ 이하의 실수 → 그래프가 꼭짓점 $(k,k)$인 '왼쪽 아래 사각형' 안에 꽉 차야 한다 → $(k,k)$는 $y=x$ 위의 점.<br>
$-x^2+6x-4=x$ → $x^2-5x+4=0$ → $x=1,\ 4$
<div class="row" style="justify-content:center">${g196a}${g196b}${g196c}</div>
i) $k=1$: $x\le1$에서 $f$는 증가, $f(1)=1$ → 치역 $\{y\mid y\le1\}$ ✔ &nbsp; ii) $k=4$: 꼭짓점 $(3,5)$가 사각형을 벗어남 ✘
<br><span class="ans">답 $k=1$</span>
<div class="tip"><b>강사 TIP</b> $y=x$와의 교점이 여러 개 나오면 <b>꼭짓점(축 $x=3$)이 범위 안에 들어오는지</b> 반드시 확인시키자.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 2</span>$X\to Y$ 일대일대응, $Y=\{y\mid y\le 2k-1\}$</div><div class="b">
<div class="src" style="margin:0">원본 197쪽</div>
$X$에서 $Y$로의 함수가 일대일대응이 되도록 하는 $X=\{x\mid x\le k\}$, $Y=\{y\mid y\le 2k-1\}$일 때 $k$의 값을 구하시오.<br>
<b>풀이</b> 사각형의 꼭짓점이 $(k,\ 2k-1)$ → <b>$y=2x-1$과 연립</b>해서 예제 1과 같은 방법으로 풀면 된다.<br>
($f$가 예제 1과 같다면) $-k^2+6k-4=2k-1$ → $k^2-4k+3=0$ → $k=1,\ 3$ — 둘 다 축 $x=3$ 이하라 가능
<br><span class="ans">답 $k=1$ 또는 $k=3$</span> <span style="font-size:8.5pt;color:#8B95A1">※ 원본에 함수식이 없어 예제 1의 $f$로 계산</span>
</div></div>

<div class="card"><div class="h"><span class="k">예제 3</span>치역이 $X$일 때 $a,b$ (치역=공역)</div><div class="b">
<div class="src" style="margin:0">원본 198~202쪽</div>
$X$에서 $X$로의 함수 $f(x)=\dfrac34x^2-3x+4$, $X=\{x\mid a\le x\le b\}$, 치역이 $X$일 때 $a,b$를 구하시오. (단, $a<b$)<br>
<span style="color:#D33">→ 공역이 $X$이므로 '치역=공역'이라는 것!</span> 함수는 정사각형 $[a,b]\times[a,b]$에 <b>꽉 찬 모양</b>이어야 한다.
<div class="row"><div>${g198}</div><div style="flex:1;min-width:70mm">
$f(x)=\dfrac34(x-2)^2+1$, $y=x$와의 교점: $3x^2-16x+16=0$ → $x=\dfrac43,\ 4$<br>
<b>① $b$ 구하기</b> $b>4$이면 $f(b)>b$로 위로 벗어남, $b<4$이면 $f(a)$ 쪽이 $b$를 넘어 안 들어감 ⇒ $b=4$<br>
<b>② $a$ 구하기</b> — 네 가지 경우<br>
· 꼭짓점 포함(①②): 최솟값 $1$이 포함되므로 $a=1$ → $[1,4]$에서 $f(1)=\frac74\le4$ ✔<br>
· 증가(③): $(a,a),(b,b)$가 모두 $y=x$ 위 → $a=\frac43<2$라 꼭짓점이 벗어남 ✘<br>
· 감소(④): $f(a)=b,\ f(b)=a$ → $\frac34x^2-2x+4-k=0$의 두 근이 $a,b$ ($k=a+b$)<br>&nbsp;&nbsp;근과 계수: $a+b=k=\frac83$ → 대입하면 중근 → $a=b$ ✘
</div></div>
<span class="ans">답 $a=1,\ b=4$</span>
<div class="tip"><b>강사 TIP</b> '치역이 $X$' = 그래프가 정사각형에 꽉 찬다. 증가·감소·꼭짓점 포함(2가지) 네 그림을 먼저 그려 놓고 하나씩 지우는 게 핵심.</div>
</div></div>

<h2>IV. 함수방정식</h2>
<div class="card"><div class="h"><span class="k">예제 4</span>$f(x+y)=f(x)f(y)$, $f(1)\ne0$</div><div class="b">
<div class="src" style="margin:0">원본 203~205쪽</div>
<b>함수방정식</b>: 함수에 관한 관계식이 나와 있는 것. → <b>$f(0)$이나 $f(1)$을 먼저 찾고 시작하는 게 국룰!</b><br>
(1) $f(x)=\dfrac1{f(-x)}$? &nbsp;(2) $f(x-y)=\dfrac{f(x)}{f(y)}$? &nbsp;(3) 임의의 $a$에 대해 $f(a)>0$ 증명 &nbsp;(4) 일대일대응인가?
<div class="step"><span class="c">$f(0)$</span><span>$x=y=0$: $\{f(0)\}^2=f(0)$ → $0,1$ 두 개가 나옴 ✘ → $x=1,y=0$: $f(1)=f(1)f(0)$, $f(1)\ne0$이므로 <b>$f(0)=1$</b></span></div>
<div class="step"><span class="c">(1) ○</span><span>$y=-x$: $1=f(x)f(-x)$ → $f(x),f(-x)\ne0$ → $f(x)=\dfrac1{f(-x)}$</span></div>
<div class="step"><span class="c">(2) ○</span><span>$f(x-y)=f(x)f(-y)=f(x)\times\dfrac1{f(y)}$</span></div>
<div class="step"><span class="c">(3) ○</span><span>$x=y=\frac a2$: $f(a)=\left\{f\left(\frac a2\right)\right\}^2\ge0$, (1)에서 $f\ne0$ → $f(a)>0$</span></div>
<div class="step"><span class="c">(4) ✘</span><span>지수함수라 일대일대응이라고 생각하기 쉬운데 <b>아닐 수도 있음</b> — $f(x)=1$(상수함수)도 조건을 만족!</span></div>
<div class="row"><div>${g204}</div><div class="ok" style="flex:1;min-width:60mm">$f(x+y)=f(x)f(y)$를 만족하는 대표 함수: <b>지수함수</b><br>일대일대응이려면 ① 일대일함수 ② 치역=공역 → 공역을 $\{y\mid y>0\}$으로 잡으면 지수함수는 일대일대응</div></div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 5</span>$f(2x+y)=4f(x)+f(y)+xy+4$일 때 $f(6)$</div><div class="b">
<div class="src" style="margin:0">원본 206쪽</div>
<b>풀이</b> $x=y=0$: $f(0)=-1$<br>
보통 이런 문제는 <span class="hl2">$2x+y$</span>$=$<span class="hl3">$x$</span> 또는 <span class="hl2">$2x+y$</span>$=$<span style="background:#C9F2B8">$y$</span>가 되는 값을 넣어 본다. ($=y$는 $x=0$이 나와 도움이 안 됨)<br>
$2x+y=x$ → $y=-x$: $f(x)=4f(x)+f(-x)-x^2+4$ → $3f(x)+f(-x)=x^2-4$ … ①<br>
$x$ 대신 $-x$: $3f(-x)+f(x)=x^2-4$ … ② &nbsp; ①$\times3-$②: $8f(x)=2x^2-8$<br>
$f(x)=\dfrac{x^2-4}4$ → $f(6)=\dfrac{32}4=8$ &nbsp;<span style="font-size:9pt;color:#555">(원래 식에 넣으면 양변 모두 $x^2+xy+\frac{y^2}4-1$ ✔)</span>
<br><span class="ans">답 $8$</span>
<div class="wrong"><b>✘ $f(x)$가 다항함수라는 조건은 없다!</b> 이차함수라고 놓고 계수비교하면 감점 — 연립으로 구해야 한다.</div>
<div class="tip"><b>강사 TIP · 윤환형</b> $x\leftrightarrow-x$, $x\leftrightarrow\frac1x$, $x\leftrightarrow2-x$처럼 두 번 바꾸면 제자리로 돌아오는 꼴은 바꿔 넣은 식과 <b>연립방정식처럼</b> 풀면 된다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 6</span>$f(xy)\le f(x)+f(y)$, $f(x)\le x-1$ ($x>0$)</div><div class="b">
<div class="src" style="margin:0">원본 207쪽</div>
ㄱ. $f(1)=0$ &nbsp; ㄴ. $f(x)+f\left(\frac1x\right)\ge0$ &nbsp; ㄷ. $0<y<x$일 때 $f(y)<f(x)$ <span style="color:#D33">← 증가함수임을 보이라는 것</span>
<div class="step"><span class="c">ㄱ 참</span><span>부등식 문제 → $f(1)\le0$, $f(1)\ge0$을 찾는 형태! $f(x)\le x-1$에서 $f(1)\le0$, $x=y=1$: $f(1)\le2f(1)$ → $f(1)\ge0$ ∴ $f(1)=0$</span></div>
<div class="step"><span class="c">ㄴ 참</span><span>$y=\frac1x$: $f(1)\le f(x)+f\left(\frac1x\right)$ → $f(x)+f\left(\frac1x\right)\ge0$</span></div>
<div class="step"><span class="c">ㄷ 참</span><span>$0<\frac yx<1$ → $f\left(\frac yx\right)\le\frac yx-1<0$<br>$f(y)=f\left(x\times\frac yx\right)\le f(x)+f\left(\frac yx\right)$ → $f(y)-f(x)\le f\left(\frac yx\right)<0$</span></div>
<span class="ans">답 ㄱ, ㄴ, ㄷ</span>
</div></div>

<div class="card"><div class="h"><span class="k">예제 7</span>$f\left(\frac2{13}\right)$ 구하기 (단조 + 대칭 + 축소)</div><div class="b">
<div class="src" style="margin:0">원본 208~209쪽</div>
정의역이 $\{x\mid0\le x\le1\}$인 $f$가 (가) $x_1<x_2$이면 $f(x_1)\le f(x_2)$ (나) $f\left(\frac x3\right)=\frac{f(x)}2$ (다) $f(1-x)=1-f(x)$
<div class="row"><div>${g209}</div><div style="flex:1;min-width:65mm">
(다) → $\left(\frac12,\frac12\right)$ 대칭, $x=\frac12$: $f\left(\frac12\right)=\frac12$<br>
(나) $x=0$: $f(0)=0$ → (다) $f(1)=1$<br>
(나) $x=1$: $f\left(\frac13\right)=\frac12$ → (다) $f\left(\frac23\right)=\frac12$<br>
(가)에 의해 $\frac13\le x\le\frac23$에서 $f(x)=\frac12$ (상수)<br>
$\frac2{13}<\frac13$이므로 한 번 더: (나) $f\left(\frac19\right)=\frac14$, $f\left(\frac29\right)=\frac14$<br>
→ $\frac19\le x\le\frac29$에서 $f(x)=\frac14$, $\frac19<\frac2{13}<\frac29$
</div></div>
<span class="ans">답 $f\left(\frac2{13}\right)=\frac14$</span>
<div class="tip"><b>강사 TIP</b> (다)처럼 <span class="hl2">$1-x$</span>$=$<span class="hl3">$x$</span>가 되는 값($x=\frac12$)을 먼저 넣는 것이 출발점. 그 뒤 (나)로 구간을 $\frac13$씩 줄여 가며 계단을 만든다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 8</span>$f(x)+f(y)=f\left(\frac{x+y}2\right)f\left(\frac{x-y}2\right)$, $f(1)=-1$</div><div class="b">
<div class="src" style="margin:0">원본 210쪽</div>
$\{f(1)\}^2+\{f(3)\}^2+\cdots+\{f(19)\}^2$를 구하시오. → 두 문자 식을 <b>한 문자에 관한 식</b>으로 바꾸자.<br>
$x$ 대신 $x+2$, $y$ 대신 $x$: $f(x+2)+f(x)=f(x+1)f(1)=-f(x+1)$ → $f(x)+f(x+1)+f(x+2)=0$
<div class="step"><span class="c">방법 1</span><span>$x=y=1$: $2f(1)=f(1)f(0)$ → $f(0)=2$ → $f(0),f(1),f(2),\cdots=2,-1,-1,2,-1,-1,\cdots$</span></div>
<div class="step"><span class="c">방법 2</span><span>하나 증가시킨 $f(x+1)+f(x+2)+f(x+3)=0$과 빼면 $f(x+3)=f(x)$ : 주기함수</span></div>
홀수 $1,3,\cdots,19$ (10개) 중 3의 배수 $3,9,15$에서 $f=2$, 나머지 7개에서 $f=-1$<br>
$3\times4+7\times1=19$ &nbsp;<span class="ans">답 $19$</span>
<div class="tip"><b>강사 TIP</b> $f(x+y)=f(x)+f(y)+\sim$ 꼴은 두 문자 중 하나를 숫자로 ($y=1$) → $f(x+1)=f(x)+f(1)+\sim$ 처럼 <b>수열</b>로 풀 수 있다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">예제 9</span>$f(n)=3$인 100 이하의 자연수 $n$의 개수</div><div class="b">
<div class="src" style="margin:0">원본 211~212쪽</div>
$f(1)=1$, $f(n)=\begin{cases}f\left(\frac n2\right)&(n=2,4,6,\cdots)\\ f\left(\frac{n-1}2\right)+1&(n=3,5,7,\cdots)\end{cases}$
<div class="step"><span class="c">풀이 1</span><span>$f(1)=f(2)=f(4)=f(8)=\cdots=1$, $\times2+1$ 할 때마다 $+1$: $f(3)=f(5)=f(9)=2$, $f(11)=f(19)=3$ … 규칙으로 직접 세기</span></div>
<div class="step"><span class="c">풀이 2</span><span>$f(n)=1 \Leftrightarrow n=2^a$, $f(n)=2 \Leftrightarrow n=2^a+2^b$, $f(n)=3 \Leftrightarrow n=2^a+2^b+2^c$ ($a>b>c\ge0$)</span></div>
<div class="step"><span class="c">풀이 3 (진법)</span><span>$1010001_{(2)}=2^6+2^4+1$ → $f$ = <b>이진법의 1의 개수</b><br>$100<128=2^7$ → 7자리 중 1이 3개: $\,{}_7\mathrm C_3=35$ (앞자리 0 허용: $0011001_{(2)}=11001_{(2)}$)<br>100을 넘는 것 빼기: $1110000_{(2)}=112$, $1101000_{(2)}=104$ ($1100100_{(2)}=100$은 포함)</span></div>
$\,{}_7\mathrm C_3-2=33$ &nbsp;<span class="ans">답 $33$</span>
</div></div>

<h2>V. 함수의 특징</h2>
<div class="card"><div class="h"><span class="k">개념</span>1. 선대칭 · 2. 점대칭</div><div class="b">
<div class="src" style="margin:0">원본 213쪽</div>
<div class="step"><span class="c">선대칭</span><span>$f(a-x)=f(a+x)$ ⇔ 직선 $x=a$에 대칭 &nbsp; ($a=0$: $f(-x)=f(x)$, $y$축 대칭 = <b>우함수</b>)<br>$f(a-x)=f(b+x)$ ⇔ $x=\dfrac{a+b}2$에 대칭</span></div>
<div class="step"><span class="c">점대칭</span><span>$f(x)+f(2a-x)=2b$ ⇔ $\left(\dfrac{x+(2a-x)}2,\dfrac{2b}2\right)=(a,b)$에 대칭 &nbsp; ($x$ 대신 $x+a$: $f(a-x)+f(a+x)=2b$)<br>$a=b=0$: $f(-x)=-f(x)$, 원점 대칭 = <b>기함수</b><br>$f(a-x)+f(b+x)=c$ ⇔ $\left(\dfrac{a+b}2,\dfrac c2\right)$에 대칭</span></div>
<div class="tip"><b>강사 TIP</b> 괄호 안 두 식을 더해서 2로 나누면 대칭축(대칭점의 $x$좌표)이 나온다. 점대칭 식은 유리함수의 점근선의 교점을 나타내는 식이기도 하다.</div>
</div></div>

<div class="card"><div class="h"><span class="k">개념</span>3. 기함수 · 우함수</div><div class="b">
<div class="src" style="margin:0">원본 214쪽</div>
<div class="step"><span class="c">① 기×기=우</span><span>$x\times x=x^2$ / 증명: $h(-x)=f(-x)g(-x)=\{-f(x)\}\{-g(x)\}=h(x)$</span></div>
<div class="step"><span class="c">② 기×우=기</span><span></span></div>
<div class="step"><span class="c">③ $f(g(x))$</span><span>기(기)이면 기, 나머지 경우는 우</span></div>
<div class="step"><span class="c">④ 우+우=우</span><span></span></div>
<div class="step"><span class="c">⑤ 기+기=?</span><span>$x+(-x)=0$이 걸리지만 $y=0$은 기함수이면서 우함수 → $h(-x)=-f(x)-g(x)=-h(x)$ 이므로 <b>기+기=기</b></span></div>
<div class="wrong"><b>✘ 일대일대응+일대일대응도 일대일대응?</b> $f,g$가 일대일대응일 때 $\dfrac{2f(x)+g(x)}3$은 아닐 수도 있다: $f(x)=x$, $g(x)=-2x$이면 $0$ (상수함수)</div>
</div></div>

<div class="card"><div class="h"><span class="k">개념</span>4. 주기함수</div><div class="b">
<div class="src" style="margin:0">원본 215쪽</div>
· $f(x)=f(x+2)$는 2마다 반복된다는 뜻이지만 <b>주기가 반드시 2인 것은 아님</b> (1마다 반복되어도 만족)<br>
· $f(x)=f(x+p)$를 만족하는 <b>"최소의 양수"</b> $p$가 주기<br>
· $x=a$, $x=b$에 대해 대칭인 함수는 주기함수 ($a\ne b$)<br>
&nbsp;&nbsp;증명) $f(x)=f(2a-x)=f(2b-(2a-x))=f(x+(2b-2a))$ — 단, 주기가 $2b-2a$라고는 할 수 없음<br>
· $\cos x$는 $y$축, $x=\pi,2\pi,\cdots,n\pi$에 대해 대칭, $\sin x$는 평행이동하면 $\cos x$와 겹침 ⇒ 둘 다 두 개 이상의 축에 대해 선대칭이므로 주기함수
</div></div>

<h2 style="break-before:page">정답 한눈에</h2>
<div class="card"><div class="b"><table style="width:100%;border-collapse:collapse;font-size:9.5pt">
<tr style="background:#eaf7f7"><th style="padding:1.5mm;text-align:left">예제</th><th style="text-align:left">내용</th><th style="text-align:left">답</th><th>원본</th></tr>
<tr><td>1</td><td>$X\to X$ 일대일대응, $x\le k$</td><td>$k=1$</td><td>196</td></tr>
<tr><td>2</td><td>$Y=\{y\mid y\le2k-1\}$</td><td>$k=1$ 또는 $3$</td><td>197</td></tr>
<tr><td>3</td><td>치역이 $X=[a,b]$</td><td>$a=1,\ b=4$</td><td>198~202</td></tr>
<tr><td>4</td><td>$f(x+y)=f(x)f(y)$</td><td>(1)(2)(3) ○, (4) ✘</td><td>203~205</td></tr>
<tr><td>5</td><td>$f(6)$</td><td>$8$</td><td>206</td></tr>
<tr><td>6</td><td>ㄱ ㄴ ㄷ</td><td>ㄱ, ㄴ, ㄷ</td><td>207</td></tr>
<tr><td>7</td><td>$f\left(\frac2{13}\right)$</td><td>$\frac14$</td><td>208~209</td></tr>
<tr><td>8</td><td>$\{f(1)\}^2+\cdots+\{f(19)\}^2$</td><td>$19$</td><td>210</td></tr>
<tr><td>9</td><td>$f(n)=3$인 $n\le100$</td><td>$33$</td><td>211~212</td></tr>
</table>
<div style="font-size:8.5pt;color:#8B95A1;margin-top:2mm">※ 예제 2·5·8·9의 최종 값은 원본 풀이를 따라 채수학에서 계산해 채웠습니다. 예제 2는 원본에 함수식이 없어 예제 1의 함수로 계산했습니다.</div>
</div></div>
`;
