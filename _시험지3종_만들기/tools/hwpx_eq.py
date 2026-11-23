# KaTeX/LaTeX (시험지 skeleton.json의 $...$) → 한글(Hancom) 수식 스크립트 변환기
# make_hwpx.py 에서 사용.  conv(latex) -> (script, metrics)
#   metrics = (width_em, ascent_em, descent_em) : 수식 상자 크기 추정치 (baseUnit 배수)
# 한글 수식 문법은 실제 한글이 저장한 hwpx 스크립트(상_01.hwpx, g1_*.hwpx 등)를 따름:
#   {a} over {b}, sqrt {x}, root {n} of {x}, LEFT ( .. RIGHT ), x ^{2}, 18 ^{circ},
#   rm {A} it, bar {AB}, cases {.. # ..}, LEFT { .. RIGHT }, <=, >=, !=, +-, times, div ...
import re

TOK = re.compile(r'\\[A-Za-z]+\*?|\\.|[{}^_&\[\]]|\s+|[0-9]+(?:\.[0-9]+)?|[A-Za-z]|.', re.S)

# 단순 치환 기호: latex 명령 -> (한글 토큰, 폭em)
SYM = {
    'times': ('times', .8), 'div': ('div', .8), 'pm': ('+-', .8), 'mp': ('-+', .8),
    'cdot': ('cdot', .4), 'cdots': ('cdots', 1.0), 'ldots': ('ldots', 1.0), 'dots': ('cdots', 1.0),
    'vdots': ('vdots', .4), 'ddots': ('ddots', 1.0),
    'le': ('<=', .8), 'leq': ('<=', .8), 'leqslant': ('<=', .8), 'ge': ('>=', .8), 'geq': ('>=', .8), 'geqslant': ('>=', .8),
    'lt': ('<', .8), 'gt': ('>', .8), 'ne': ('!=', .8), 'neq': ('!=', .8),
    'approx': ('approx', .8), 'equiv': ('equiv', .8), 'sim': ('sim', .8), 'simeq': ('simeq', .8), 'cong': ('cong', .8),
    'pi': ('pi', .6), 'alpha': ('alpha', .6), 'beta': ('beta', .6), 'gamma': ('gamma', .6), 'delta': ('delta', .6),
    'epsilon': ('epsilon', .5), 'varepsilon': ('epsilon', .5), 'theta': ('theta', .55), 'lambda': ('lambda', .6), 'mu': ('mu', .6),
    'sigma': ('sigma', .6), 'omega': ('omega', .7), 'phi': ('phi', .6), 'varphi': ('phi', .6), 'rho': ('rho', .55), 'tau': ('tau', .5),
    'Omega': ('OMEGA', .75), 'Delta': ('DELTA', .75), 'Pi': ('PI', .75), 'Sigma': ('SIGMA', .75), 'Gamma': ('GAMMA', .7),
    'Theta': ('THETA', .75), 'Lambda': ('LAMBDA', .75), 'Phi': ('PHI', .75),
    'angle': ('angle', .8), 'triangle': ('triangle', .8), 'circ': ('circ', .5),
    'infty': ('inf', .9), 'in': ('in', .8), 'notin': ('notin', .8), 'ni': ('owns', .8),
    'subset': ('subset', .8), 'subseteq': ('subseteq', .8), 'supset': ('supset', .8), 'supseteq': ('supseteq', .8),
    'cup': ('cup', .8), 'cap': ('cap', .8), 'emptyset': ('EMPTYSET', .7), 'varnothing': ('EMPTYSET', .7),
    'therefore': ('therefore', .8), 'because': ('because', .8), 'perp': ('bot', .8), 'parallel': ('parallel', .6),
    'to': ('->', 1.0), 'rightarrow': ('->', 1.0), 'leftarrow': ('<-', 1.0), 'Rightarrow': ('RARROW', 1.0),
    'Leftarrow': ('LARROW', 1.0), 'Leftrightarrow': ('LRARROW', 1.2), 'iff': ('LRARROW', 1.2), 'leftrightarrow': ('lrarrow', 1.2),
    'longrightarrow': ('->', 1.2), 'implies': ('RARROW', 1.0),
    'square': ('□', .9), 'Box': ('□', .9), 'blacksquare': ('■', .9), 'star': ('star', .7), 'prime': ("'", .3),
    'mid': ('|', .5), 'vert': ('|', .3), '|': ('||', .4), 'langle': ('〈', .5), 'rangle': ('〉', .5),
    'llbracket': ('⟦', .5), 'rrbracket': ('⟧', .5), 'frown': ('⌒', .8), 'neg': ('¬', .6), 'lnot': ('¬', .6),
    'forall': ('forall', .6), 'exists': ('exist', .6), 'cdotp': ('cdot', .4), 'bullet': ('bullet', .4),
    'sin': ('sin', 1.3), 'cos': ('cos', 1.4), 'tan': ('tan', 1.4), 'cot': ('cot', 1.4), 'sec': ('sec', 1.4), 'csc': ('csc', 1.4),
    'log': ('log', 1.4), 'ln': ('ln', .9), 'exp': ('exp', 1.4), 'lim': ('lim', 1.3), 'max': ('max', 1.6), 'min': ('min', 1.5),
    'sum': ('sum', 1.0), 'int': ('int', .6), 'prod': ('prod', 1.0),
    # 간격
    ',': ('`', .17), ':': ('`', .2), ';': ('~', .28), ' ': ('~', .28), 'quad': ('~~', .6), 'qquad': ('~~~~', 1.2), '!': ('', 0),
    '%': ('%', .8), '&': ('&', .7), '$': ('$', .5), '_': ('_', .5), '#': ('#', .5),
}
IGNORE = {'displaystyle', 'textstyle', 'scriptstyle', 'limits', 'nolimits', 'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr',
          'Bigl', 'Bigr', 'biggl', 'biggr', 'left.', 'nobreak', 'allowbreak'}
ACCENT = {'overline': 'bar', 'bar': 'bar', 'overrightarrow': 'vec', 'vec': 'vec', 'overleftrightarrow': 'dyad',
          'widehat': 'hat', 'hat': 'hat', 'dot': 'dot', 'ddot': 'ddot', 'underline': 'under', 'tilde': 'tilde',
          'widetilde': 'tilde', 'boxed': 'box', 'fbox': 'box'}
FRAC = {'frac', 'dfrac', 'tfrac', 'cfrac'}
TEXT = {'text', 'textrm', 'mbox', 'textnormal', 'hbox', 'textbf'}
FONT = {'mathrm': 'rm', 'rm': 'rm', 'operatorname': 'rm', 'mathbf': 'bold', 'bf': 'bold', 'boldsymbol': 'bold',
        'mathit': 'it', 'mathsf': 'rm', 'mathcal': 'rm'}
DELIM = {'(': '(', ')': ')', '[': '[', ']': ']', '|': '|', '.': '.', '\\{': '{', '\\}': '}', '\\lbrace': '{', '\\rbrace': '}',
         '\\langle': '<', '\\rangle': '>', '\\|': '||', '\\vert': '|', '\\Vert': '||', '\\lvert': '|', '\\rvert': '|',
         '<': '<', '>': '>', '/': '/', '\\lfloor': '[', '\\rfloor': ']', '\\lceil': '[', '\\rceil': ']'}

PEND = '\x01'   # rm 뒤 'it' 복원 표시 (후처리)


class M:  # 수식 상자 크기 (em)
    __slots__ = ('w', 'a', 'd')

    def __init__(s, w=0., a=.96, d=.11): s.w, s.a, s.d = w, a, d

    def add(s, o): s.w += o.w; s.a = max(s.a, o.a); s.d = max(s.d, o.d); return s


def single_group(sc):
    """sc 가 { ... } 한 덩어리인가"""
    if not (sc.startswith('{') and sc.endswith('}')): return False
    d = 0
    for i, c in enumerate(sc):
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0 and i != len(sc) - 1: return False
    return True


def G(sc):
    """중괄호로 한 번만 감싸기"""
    sc = sc.strip()
    while single_group(sc) and single_group(sc[1:-1].strip()): sc = sc[1:-1].strip()
    return sc if single_group(sc) else '{' + sc + '}'


def chw(c):
    if re.match(r'[0-9]', c): return .5
    if re.match(r'[A-Za-z]', c): return .55
    if c in '+-=<>': return .8
    if c in ',.;:': return .3
    if c in '()[]|': return .35
    if ord(c) > 0x2e80: return 1.0
    return .6


class P:
    def __init__(s, src):
        s.t = [x for x in TOK.findall(src)]
        s.i = 0
        s.warn = []
        s.env = []

    # ---- 토큰 이동
    def peek(s, k=0):
        j = s.i
        while j < len(s.t) and s.t[j].isspace(): j += 1
        while k > 0 and j < len(s.t):
            j += 1
            while j < len(s.t) and s.t[j].isspace(): j += 1
            k -= 1
        return s.t[j] if j < len(s.t) else None

    def nx(s):
        while s.i < len(s.t) and s.t[s.i].isspace(): s.i += 1
        if s.i >= len(s.t): return None
        s.i += 1
        return s.t[s.i - 1]

    def raw_group(s):  # \text{...} 내용을 그대로
        if s.peek() != '{':
            t = s.nx(); return t or ''
        s.nx(); depth = 1; out = ''
        while s.i < len(s.t):
            t = s.t[s.i]; s.i += 1
            if t == '{': depth += 1
            elif t == '}':
                depth -= 1
                if depth == 0: break
            out += t
        return out

    # ---- 인자: 한글 스크립트 문자열(중괄호 없이) + 크기
    def arg(s):
        p = s.peek()
        if p is None: return '', M()
        if p == '{':
            s.nx(); sc, m = s.seq({'}'}); s.nx(); return sc, m
        if p.startswith('\\'):
            # 명령 하나를 인자로 (예: ^\circ, \frac12 는 드묾)
            return s.item()
        if re.fullmatch(r'[0-9.]+', p) and len(p) > 1:  # \frac12, x^23 → 한 글자만
            j = s.i
            while s.t[j].isspace(): j += 1
            s.t[j:j + 1] = [p[0], p[1:]]
            p = p[0]
        s.nx()
        return s.atom_char(p)

    def atom_char(s, t):
        if t in ('<', '>'): return t, M(.8)
        if re.fullmatch(r'[0-9.]+', t): return t, M(.5 * len(t))
        if t == '"': return "'", M(.3)
        if t in '#~`': return '', M()
        return t, M(sum(chw(c) for c in t))

    def find_close_brace(s):
        """현재 위치 이후 같은 깊이에서 \\} 가 있는지"""
        depth = 0; lev = 0
        for j in range(s.i, len(s.t)):
            t = s.t[j]
            if t == '{': depth += 1
            elif t == '}':
                depth -= 1
                if depth < 0: return False
            elif t == '\\{' and depth == 0: lev += 1
            elif t == '\\}' and depth == 0:
                if lev == 0: return True
                lev -= 1
            elif t in ('\\end', '\\right') and depth == 0 and t == '\\end': return False
        return False

    # ---- 시퀀스
    def seq(s, stops):
        out = []; m = M(0)
        while True:
            p = s.peek()
            if p is None or p in stops: break
            sc, mm = s.item()
            if sc == '' and mm.w == 0: continue
            if sc in ('^', '_'): continue
            out.append(sc); m.add(mm)
        # x ^{2} 처리는 item에서 위첨자를 직전 원소에 붙이는 대신 독립 토큰으로 출력(한글이 그렇게 씀)
        return ' '.join(x for x in out if x != ''), m

    def item(s):
        t = s.nx()
        if t is None: return '', M()
        if t == '{':
            sc, m = s.seq({'}'}); s.nx()
            return (G(sc) if sc else ''), m
        if t == '}': return '', M()
        if t in ('^', '_'):
            sc, m = s.arg()
            if sc == 'circ': return '^{circ}', M(.4, 1.25, .1)
            small = M(m.w * .7, .45 + (m.a + m.d) * .7 if t == '^' else .6, .1 if t == '^' else .25 + (m.a + m.d) * .6)
            if t == '^': small = M(m.w * .7, max(1.3, .4 + m.a * .7 + m.d * .7 + .2), .1)
            else: small = M(m.w * .7, .9, max(.35, .2 + (m.a + m.d) * .7 - .3))
            return t + G(sc), small
        if t == '&':
            if s.env: return '~~~', M(1.)
            return '~', M(.3)
        if t == '\\\\':
            if s.env: return '#', M()
            return '~', M(.3)
        if not t.startswith('\\') or len(t) == 1:
            if t in ('[', ']'): return t, M(.35)
            return s.atom_char(t)
        name = t[1:]
        # ---- 구조 명령
        if name in FRAC:
            a, ma = s.arg(); b, mb = s.arg()
            ha, hb = ma.a + ma.d, mb.a + mb.d
            return '{%s over %s}' % (G(a), G(b)), M(max(ma.w, mb.w) + .3, ha + .58, hb - .26 + .0)
        if name == 'sqrt':
            if s.peek() == '[':
                s.nx(); n, mn = s.seq({']'}); s.nx()
                x, mx = s.arg()
                return 'root %s of %s' % (G(n), G(x)), M(mx.w + .9 + mn.w * .6, mx.a + .2, mx.d + .1)
            x, mx = s.arg()
            return 'sqrt %s' % G(x), M(mx.w + .9, mx.a + .17, mx.d + .08)
        if name == 'left':
            d = s.nx() or '.'
            dl = DELIM.get(d, d.lstrip('\\'))
            inner, mi = s.seq({'\\right'})
            if s.peek() == '\\right':
                s.nx(); e = s.nx() or '.'
                dr = DELIM.get(e, e.lstrip('\\'))
            else:
                dr = '.'
            return 'LEFT %s %s RIGHT %s' % (dl, inner, dr), M(mi.w + .8, mi.a + .05, mi.d + .05)
        if name == 'right':  # 짝 없는 \right
            d = s.nx() or '.'
            return DELIM.get(d, d.lstrip('\\')) if d != '.' else '', M(.35)
        if name == 'middle':
            d = s.nx() or '|'
            return DELIM.get(d, d.lstrip('\\')), M(.4)
        if name in ('{', 'lbrace'):
            if s.find_close_brace():
                inner, mi = s.seq({'\\}', '\\rbrace'}); s.nx()
                return 'LEFT { %s RIGHT }' % inner, M(mi.w + .8, mi.a + .05, mi.d + .05)
            s.warn.append('unmatched \\{')
            return 'lbrace', M(.5)
        if name in ('}', 'rbrace'):
            s.warn.append('unmatched \\}')
            return 'rbrace', M(.5)
        if name == 'begin':
            env = s.raw_group()
            if env in ('array',):
                s.raw_group()
            s.env.append(env)
            rows = []; cur = []; m = M(0); rowm = []
            while True:
                p = s.peek()
                if p is None: break
                if p == '\\end':
                    s.nx(); s.raw_group(); break
                if p == '\\\\':
                    s.nx(); rows.append(cur); cur = []; continue
                if p == '&':
                    s.nx(); cur.append(None); continue
                sc, mm = s.seq({'\\\\', '&', '\\end'})
                cur.append((sc, mm))
            if cur: rows.append(cur)
            s.env.pop()
            out_rows = []; wmax = 0; hsum = 0
            for r in rows:
                parts = []; w = 0; a = .96; dd = .11
                for c in r:
                    if c is None:
                        parts.append('&' if env not in ('cases', 'dcases', 'rcases', 'aligned', 'align', 'align*', 'gathered', 'split') else '~~~')
                        w += 1.
                    else:
                        parts.append(c[0]); w += c[1].w; a = max(a, c[1].a); dd = max(dd, c[1].d)
                parts = [p for p in parts if p]
                out_rows.append(' '.join(parts)); wmax = max(wmax, w); hsum += a + dd + .25
            body = ' # '.join(out_rows)
            if env in ('cases', 'dcases'):
                return 'cases {%s}' % body, M(wmax + 1., hsum / 2 + .3, hsum / 2)
            if env in ('pmatrix', 'bmatrix', 'matrix', 'vmatrix'):
                kw = {'pmatrix': 'pmatrix', 'bmatrix': 'bmatrix', 'matrix': 'matrix', 'vmatrix': 'dmatrix'}[env]
                return '%s {%s}' % (kw, body), M(wmax + 1., hsum / 2 + .3, hsum / 2)
            return 'pile {%s}' % body, M(wmax, hsum / 2 + .3, hsum / 2)
        if name == 'end':
            s.raw_group(); return '', M()
        if name in TEXT:
            txt = s.raw_group().replace('"', "'")
            txt = re.sub(r'\\[,;: ]', ' ', txt).replace('\\', '')
            if not txt.strip(): return '~', M(.3)
            return '"%s"' % txt, M(sum(chw(c) if c != ' ' else .3 for c in txt))
        if name in FONT:
            x, mx = s.arg()
            kw = FONT[name]
            if kw == 'it': return 'it %s' % G(x), mx
            return '%s %s%s' % (kw, G(x), PEND), mx
        if name in ACCENT:
            x, mx = s.arg()
            kw = ACCENT[name]
            if kw == 'box': return 'box %s' % G(x), M(mx.w + .5, mx.a + .15, mx.d + .15)
            if kw == 'under': return 'under %s' % G(x), M(mx.w, mx.a, mx.d + .15)
            return '%s %s' % (kw, G(x)), M(mx.w + .05, mx.a + .3, mx.d)
        if name in ('overset', 'stackrel'):
            a, ma = s.arg(); b, mb = s.arg()
            if a.strip() in ('⌒', 'frown'):
                return 'arch %s' % G(b), M(mb.w + .1, mb.a + .35, mb.d)
            return '%s atop %s' % (G(a), G(b)), M(max(ma.w, mb.w), mb.a + ma.a + ma.d, mb.d)
        if name == 'underset':
            a, ma = s.arg(); b, mb = s.arg()
            return '%s atop %s' % (G(b), G(a)), M(max(ma.w, mb.w), mb.a, mb.d + ma.a + ma.d)
        if name == 'not':
            p = s.peek()
            if p in ('\\in',): s.nx(); return 'notin', M(.8)
            if p in ('=',): s.nx(); return '!=', M(.8)
            if p and p.startswith('\\') and p[1:] in SYM:
                s.nx(); return 'not ' + SYM[p[1:]][0], M(.8)
            return '', M()
        if name in ('color', 'textcolor'):
            s.raw_group()
            return '', M()
        if name in ('phantom', 'hphantom', 'vphantom'):
            s.raw_group(); return '~', M(.3)
        if name in IGNORE: return '', M()
        if name in SYM:
            sc, w = SYM[name]
            return sc, M(w)
        s.warn.append('unknown \\' + name)
        return name, M(.55 * len(name))


def _fix_pending(sc):
    """rm {..} 다음에 오는 첫 실제 토큰 앞에 'it' 삽입 (위·아래첨자는 건너뜀)"""
    if PEND not in sc: return sc
    out = []; i = 0; pend = False; n = len(sc)
    while i < n:
        c = sc[i]
        if c == PEND:
            pend = True; i += 1; continue
        if pend:
            if c.isspace() or c == '}':
                out.append(c); i += 1; continue
            if c in '^_' and i + 1 < n:
                # 첨자 그룹 통째로 복사
                j = i + 1
                while j < n and sc[j].isspace(): j += 1
                if j < n and sc[j] == '{':
                    depth = 0; k = j
                    while k < n:
                        if sc[k] == '{': depth += 1
                        elif sc[k] == '}':
                            depth -= 1
                            if depth == 0: break
                        k += 1
                    out.append(sc[i:k + 1].replace(PEND, '')); i = k + 1; continue
            if sc.startswith('rm ', i) or sc.startswith('#', i):
                pend = False
            else:
                out.append('it '); pend = False
        out.append(c); i += 1
    return ''.join(out)


def conv(latex):
    """LaTeX -> (한글 수식 스크립트, M, warnings)"""
    p = P(latex)
    parts = []; m = M(0)
    while p.peek() is not None:
        sc, mm = p.item()
        if sc: parts.append(sc); m.add(mm)
    sc = ' '.join(parts)
    sc = _fix_pending(sc)
    sc = re.sub(r'\s+', ' ', sc).strip()
    if m.w == 0: m.w = .3
    return sc, m, p.warn


if __name__ == '__main__':
    import sys
    for l in sys.stdin:
        sc, m, w = conv(l.rstrip('\n'))
        print(sc, '   #', round(m.w, 2), round(m.a, 2), round(m.d, 2), w if w else '')
