# -*- coding: utf-8 -*-
"""우리 시험 데이터(skeleton.json + sol.json + x/BinData) → 채수학 B4 편집가능 시험지(hwpx).

사용:  python3 make_b4_hwpx.py <시험 폴더> <out.hwpx>

채쌤 PC 도구(tools/g3/g3lib.py · hwpxlib.py, 구글 드라이브 '편집가능' 폴더에서 받은 것)를
**고치지 않고** 그대로 불러 쓴다. 이 파일은 우리 데이터를 g3lib 의 P[n] 블록 형식으로 옮기고,
g3lib 이 기대하는 몇 가지(표 위치·로고·문항 높이)를 바깥에서 채워 줄 뿐이다.

  g3lib 블록:  ('p', [T(..), E(..), ...])      본문/선택지 한 문단 (① 로 시작하면 선택지)
              ('box', [[parts], [parts], ...])  <보기> 상자
              ('cropimg', 파일이름, 너비mm)      그림 (CROP 폴더 기준)
  UNIT[n]   = 유형 알약 글자 (sol.json 의 tp)  →  "01 [채수학 X 유형]"

한글이 없는 곳이라 '한글로 재고 다시 앉히기'(_수식크기_고치기 · _문항높이_재기)는 못 한다.
  * 수식 치수: _수식크기표.json 에서 찾고(띄어쓰기·중괄호 차이는 맞춰서), 없으면 g3lib.estw 어림값.
  * 문항 높이: _문항높이표.json 에 이 시험이 없으므로 est_height() 로 어림해 g3lib.HTAB 에 넣는다
    (경신중·경산중 실측값으로 맞춘 계수, 아래 CAL_*).
"""
import io, json, math, os, re, shutil, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
G3 = os.path.join(HERE, "g3")
sys.path.insert(0, HERE)
sys.path.insert(0, G3)

import g3lib            # noqa: E402  (채쌤 도구 — 고치지 않는다)
import hwpxlib          # noqa: E402
from g3lib import T, E  # noqa: E402
from hwpx_eq import conv as tex2heq   # noqa: E402  우리 KaTeX → 한글 수식 변환기
from make_hwpx import parse_q         # noqa: E402  우리 q(HTML+$..$) 파서

MM = hwpxlib.MM
CIRC = "①②③④⑤⑥⑦⑧⑨⑩"


# ───────────────────────── g3lib 설정 (바깥에서) ─────────────────────────
def _jload(name):
    f = os.path.join(G3, name)
    return json.load(io.open(f, encoding="utf-8")) if os.path.exists(f) else {}


# g3lib 은 표를 '편집가능/..' 에서 찾는다. 우리는 tools/g3 에 두었으므로 직접 넣어 준다.
g3lib.EQTAB = _jload("_수식크기표.json")
g3lib.HTAB = _jload("_문항높이표.json")
g3lib.CHW = _jload("_글자폭표.json") or g3lib.CHW
g3lib.LOGO2 = os.path.join(G3, "logo_trim.png")
g3lib.CHAR_IMG = os.path.join(G3, "채쌤_푯말.png")
g3lib.PAPER = "B4"            # 2026-09-19 확정 틀
g3lib.HEAD_INLINE = True      # 번호 옆에 유형 알약
g3lib.FIG_NATURAL = True
g3lib.use_paper("B4")         # AVAIL·CPH·K 등을 B4 값으로 (높이 어림에 필요)

# ---- 꼬리말 (2026.11 원장님 확정): 모든 쪽 맨 아래 "수학하는 방법을 가르칩니다!!! 채수학교습소 010-8677-2263" ----
# g3lib.build_exam 은 d.set_footer("채수학교습소 · 채미정T", "B4 · ☎ …") 를 부른다. g3lib 은 고치지 않고
# hwpxlib.Doc.set_footer 를 감싸서 글자만 바꾼다 (왼쪽 칸: 문구+교습소·전화, 가운데: 쪽 번호, 오른쪽: 시험 이름·종이).
FOOT_LEFT = "수학하는 방법을 가르칩니다!!! 채수학교습소 010-8677-2263"
FOOT_RIGHT = {"text": "B4"}
_orig_set_footer = hwpxlib.Doc.set_footer
FOOT_SPLIT = (0.74, 0.08)      # 왼쪽 칸이 문구 한 줄(11.5pt 약 116mm)을 다 담도록 넓힌다 (원래 0.42/0.16/0.42)


# ---- 유형 알약의 "채수학  X  " 머리 빼기 (2026.11 원장님: 모든 곳에서 뺀다) ----
# g3lib.type_pill / head_row 가 글자 앞에 "채수학  X  " 를 붙이고 그 길이로 알약 너비를 잡는다.
# g3lib 은 고치지 않고 Doc._tbl_in_p 를 감싸서, 그 글자를 빼고 알약 너비를 같은 식(글자수×700K+1500K)으로 다시 잡는다.
PILL_PREFIX = "채수학  X  "
_orig_tbl_in_p = hwpxlib.Doc._tbl_in_p


def _pill_w(txt, cap):
    K = g3lib.K
    return min(int(len(txt) * 700 * K) + int(1500 * K), cap)


def _tbl_in_p(self, rows, widths, row_h, *a, **kw):
    try:
        if len(rows) == 1:
            cells = rows[0]
            hit = [i for i, c in enumerate(cells)
                   if len(c) == 1 and c[0][0] == 'p' and isinstance(c[0][1], str) and c[0][1].startswith(PILL_PREFIX)]
            if hit:
                i = hit[0]
                old = cells[i][0][1]; new = old[len(PILL_PREFIX):]
                cells = list(cells); cells[i] = [(cells[i][0][0], new) + tuple(cells[i][0][2:])]
                widths = list(widths)
                if len(widths) == 1:            # type_pill: 알약 하나
                    widths[0] = min(widths[0], _pill_w(new, widths[0]))
                elif len(widths) == 3 and i == 1:  # head_row: [번호, 알약, 빈칸] — 줄 전체 너비는 그대로
                    tot = sum(widths); pw = min(widths[1], _pill_w(new, widths[1]))
                    widths = [widths[0], pw, tot - widths[0] - pw]
                rows = [cells]
    except Exception:
        pass
    return _orig_tbl_in_p(self, rows, widths, row_h, *a, **kw)


hwpxlib.Doc._tbl_in_p = _tbl_in_p


def _set_footer(self, left, right, charpr=7):
    """hwpxlib.Doc.set_footer 와 같은 3칸 꼬리말 — 글자와 칸 너비만 바꾼다."""
    _orig_set_footer(self, FOOT_LEFT, FOOT_RIGHT["text"], charpr)
    W = hwpxlib.body_w()
    o1 = int(W * 0.42); o3 = int(W * 0.42); o2 = W - o1 - o3
    n1 = int(W * FOOT_SPLIT[0]); n2 = int(W * FOOT_SPLIT[1]); n3 = W - n1 - n2
    x = self.footer_xml_str
    for col, (ow, nw) in enumerate(((o1, n1), (o2, n2), (o3, n3))):
        x = x.replace('<hp:cellAddr colAddr="%d" rowAddr="0"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
                      '<hp:cellSz width="%d" height="1400"/>' % (col, ow),
                      '<hp:cellAddr colAddr="%d" rowAddr="0"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
                      '<hp:cellSz width="%d" height="1400"/>' % (col, nw))
    # 칸 안 글자 폭(textWidth)도 함께
    parts = x.split('<hp:tc ')
    for k, nw in zip(range(1, 4), (n1, n2, n3)):
        parts[k] = re.sub(r'textWidth="\d+"', 'textWidth="%d"' % max(nw - 300, 500), parts[k], count=1)
    self.footer_xml_str = '<hp:tc '.join(parts)


hwpxlib.Doc.set_footer = _set_footer


def exam_title(t):
    """'2026 강북중 3학년 2학기 기말' → '… 기말시험' (PDF 시험지 제목과 같게)."""
    t = str(t).strip()
    return t + "시험" if re.search(r"(중간|기말)$", t) else t

# ---- 수식 크기표: 띄어쓰기·한 글자 중괄호만 다른 것도 찾게 한다 ----
def _norm(s):
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"([\^_])\{([^{}])\}", r"\1\2", s)     # x^{2} == x^2
    s = re.sub(r"\{([^{}])\}", r"\1", s)               # {1}over{2} == 1over2
    return s


_NIDX = {}
for _k, _v in g3lib.EQTAB.items():
    _b, _, _sc = _k.partition("|") if re.match(r"^\d+\|", _k) else ("1000", "", _k)
    _NIDX.setdefault((_b, _norm(_sc)), _v)
_orig_eqlook = g3lib.eqlook
STAT = {"eq": 0, "eq_hit": 0, "eq_nhit": 0}


def _eqlook(script):
    v = _orig_eqlook(script)
    if v is None:
        v = _NIDX.get((str(hwpxlib.eqbase()), _norm(script)))
    return v


g3lib.eqlook = _eqlook          # E()·estw()·Evar() 가 모듈 전역 이름으로 부르므로 이것만 바꾸면 된다


# ───────────────────────── 수식 변환 (KaTeX → 한글) ─────────────────────────
# 한글 수식 예약어: 점 이름(대문자 여러 글자)이 이것과 겹치면 글자가 기호로 바뀌어 사라진다(경신중 18번 ∠DEG).
RESERVED = {"DEG", "PI", "INF", "INFTY", "ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA", "SIGMA", "THETA",
            "LAMBDA", "PHI", "PSI", "XI", "MU", "NU", "ETA", "RHO", "TAU", "CHI", "ZETA", "KAPPA", "IOTA",
            "EPSILON", "UPSILON", "OMICRON", "LEFT", "RIGHT", "OVER", "SQRT", "ROOT", "BAR", "VEC", "DOT",
            "SUM", "INT", "LIM", "LOG", "LN", "SIN", "COS", "TAN", "ANGLE", "CDOT", "TIMES", "DIV", "OR", "AND",
            "IN", "NOT", "TO", "IT", "RM", "BOLD", "BOX", "ARCH", "HAT", "ACUTE", "GRAVE", "CHECK", "TILDE",
            "MATRIX", "CASES", "PILE", "ATOP", "OF", "EXIST", "FORALL", "PROD", "UNION", "INTER", "LARROW",
            "RARROW", "LRARROW", "EMPTYSET", "AA", "BB", "CC", "DD", "EE", "FF", "GG", "HH", "II", "JJ",
            "KK", "LL", "MM", "NN", "OO", "PP", "QQ", "RR", "SS", "TT", "UU", "VV", "WW", "XX", "YY", "ZZ"}
_RES_SORTED = sorted(RESERVED, key=len, reverse=True)


def _split_caps(tok):
    """대문자 점 이름에 예약어가 들어 있으면 낱글자로 쪼갠다 — DEG → D E G."""
    up = tok.upper()
    if any(r in up for r in _RES_SORTED if len(r) <= len(tok)):
        return " ".join(tok)
    return tok


def guard_reserved(sc):
    """스크립트 안의 (따옴표 밖) 대문자 덩어리와 "따옴표" 속 대문자 이름을 지킨다. pi 는 소문자 그대로."""
    out = []
    for i, seg in enumerate(re.split(r'("[^"]*")', sc)):
        if i % 2 == 1:                                    # "ABC" → rm {A B C}  (예약어 걱정 없는 꼴)
            body = seg[1:-1]
            if re.fullmatch(r"[A-Z]{2,}", body) and _split_caps(body) != body:
                seg = "rm {%s}" % " ".join(body)
            out.append(seg)
            continue
        seg = re.sub(r"(?<![A-Za-z])[A-Z]{2,}(?![A-Za-z])",
                     lambda m: m.group(0) if m.group(0) in ("PI", "OMEGA", "DELTA", "SIGMA", "GAMMA", "THETA",
                                                            "LAMBDA", "PHI", "EMPTYSET", "LEFT", "RIGHT",
                                                            "RARROW", "LARROW", "LRARROW")
                     else _split_caps(m.group(0)), seg)
        seg = seg.replace("π", " pi ")
        out.append(seg)
    return re.sub(r"\s+", " ", "".join(out)).strip()


WARN = []


def eq(latex):
    sc, _m, w = tex2heq(latex)
    if w:
        WARN.append("%s → %s" % (latex, w))
    sc = guard_reserved(sc)
    STAT["eq"] += 1
    if _orig_eqlook(sc) is not None:
        STAT["eq_hit"] += 1
    elif _eqlook(sc) is not None:
        STAT["eq_nhit"] += 1
    return sc


def inl_to_parts(inl):
    """parse_q 의 인라인 목록 → g3lib 조각 [T(..), E(..)]."""
    parts = []
    for x in inl:
        if x[0] == "t":
            if x[1]:
                parts.append(T(x[1]))
        elif x[0] == "eq":
            sc = eq(x[1])
            if sc:
                parts.append(E(sc))
    return parts


def blocks_to_g3(blocks):
    """parse_q 블록 → g3lib 블록. 표는 g3lib 에 없으므로 칸을 띄어 쓴 <보기> 상자로 근사한다."""
    out = []
    for b in blocks:
        if b[0] == "p":
            parts = inl_to_parts(b[1])
            if parts:
                out.append(("p", parts))
        elif b[0] == "box":
            lines = []
            for bb in b[1]:
                if bb[0] == "p":
                    pp = inl_to_parts(bb[1])
                    if pp:
                        lines.append(pp)
                elif bb[0] == "table":
                    lines += table_lines(bb)
            if lines:
                out.append(("box", lines))
        elif b[0] == "table":
            lines = table_lines(b)
            if lines:
                out.append(("box", lines))
    return out


def table_lines(tb):
    lines = []
    for row in tb[1]:
        parts = []
        for k, cell in enumerate(row):
            if k:
                parts.append(T("    "))
            for bb in cell["blocks"]:
                if bb[0] == "p":
                    parts += inl_to_parts(bb[1])
        if parts:
            lines.append(parts)
    return lines


# ───────────────────────── 문항 높이 어림 ─────────────────────────
# _문항높이_재기.py(한글 PDF 실측)를 못 돌리므로 g3lib 이 쓰는 것과 같은 자리 값으로 어림한다.
# 계수는 경신중 중3·경산중 중3(그림 없는 문항) 실측 높이에 맞춘 값 — calibrate() 참고.
CAL_A, CAL_B = 0.888, 666     # 39문항 맞춤, 평균 오차 약 1300 (4.6 mm)


def _lh(cp=14):
    return g3lib.CPH[cp] * hwpxlib.LINESP["B4"] / 100.0


def _para_h(parts, avail=None):
    avail = avail or g3lib.AVAIL
    ex = g3lib.expand(parts)
    w = g3lib.pwidth(ex)
    n = max(1, int(math.ceil(w / float(avail))))
    tall = [q[2][1] for q in ex if q[0] == "eq" and q[2][1] > 1500]
    h = n * _lh()
    for th in tall[:n]:                          # 키 큰 수식이 든 줄은 그만큼 늘어난다
        h += max(0, th + g3lib.CPH[14] * 0.65 - _lh())
    return h


def est_items(blks):
    """g3lib 블록 목록(P[n]) → 어림 높이(한글 단위), 번호 줄 포함."""
    K = g3lib.K
    h = int(1150 * K) + int(140 * K)             # 번호+알약 줄
    i = 0
    while i < len(blks):
        b = blks[i]
        if g3lib.is_choice(b):
            items = []
            while i < len(blks) and g3lib.is_choice(blks[i]):
                items += g3lib.choice_items(blks[i]); i += 1
            ex = [g3lib.expand(x) for x in items]
            ncol = g3lib.plan_cols([g3lib.pwidth(x) for x in ex])
            if ncol == 1:
                h += sum(_para_h(x) for x in items)
            else:
                maxh = 900
                for it in ex:
                    for q in it:
                        if q[0] == "eq":
                            maxh = max(maxh, q[2][1])
                rows = int(math.ceil(len(items) / float(ncol)))
                h += rows * max(maxh + int(g3lib.CHOICE_ROW * K), _lh())
            nxt = None
        else:
            if b[0] == "p":
                h += _para_h(b[1])
            elif b[0] == "box":
                h += int(500 * K) + 2 * _lh(15)
                h += sum(_para_h(ln, g3lib.AVAIL - int(900 * K)) for ln in b[1])
            elif b[0] in ("cropimg", "fig"):
                h += b[3] if len(b) > 3 else 0      # 그림 높이는 아래에서 넣어 둔다
            i += 1
            nxt = blks[i][0] if i < len(blks) else None
            if b[0] == "box" or nxt == "box":
                h += _lh(0)
        # 문항 끝 빈 줄은 넣지 않는다 — 실측표도 글자 끝까지만 재고, g3lib 이 NATGAP 으로 따로 셈한다
    return int(CAL_A * h + CAL_B)


# ───────────────────────── skeleton → P / UNIT ─────────────────────────
def fig_block(folder, name, w_mm):
    """그림은 '제 크기'로. 우리 그림은 TikZ 900dpi 가 아니라 원본에서 잘라 낸 PNG 이므로
    skeleton 의 imgW(원본 시험지에서의 너비, mm)가 곧 제 크기다. 단 너비를 넘으면 줄인다."""
    from PIL import Image
    path = None
    for ext in (".png", ".jpg", ".jpeg", ".PNG", ".JPG"):
        p = os.path.join(folder, "x", "BinData", name + ext)
        if os.path.exists(p):
            path = p; break
    if path is None:
        raise SystemExit("그림 없음: %s" % name)
    im = Image.open(path)
    if not w_mm:
        dpi = (im.info.get("dpi") or (150, 150))[0] or 150
        w_mm = im.width / float(dpi) * 25.4
    w_mm = min(float(w_mm), (g3lib.AVAIL - 400) / MM)
    h = int(w_mm * MM * im.height / im.width)
    return ("cropimg", os.path.basename(path), w_mm, h)


def build_P(folder):
    sk = json.load(io.open(os.path.join(folder, "skeleton.json"), encoding="utf-8"))
    solp = os.path.join(folder, "sol.json")
    sol = json.load(io.open(solp, encoding="utf-8")) if os.path.exists(solp) else {}
    meta = sk["meta"]
    P, UNIT, nums = {}, {}, []
    ns = 0
    for q in sk["Q"]:
        n = int(q["n"]); nums.append(n)
        s = sol.get(str(n)) or {}
        UNIT[n] = (s.get("tp") or q.get("sub") or q.get("unit") or "").strip()
        blks = blocks_to_g3(parse_q(q.get("q", "")))
        if not blks or blks[0][0] != "p":
            blks.insert(0, ("p", []))
        is_sub = q.get("type") == "서"
        if is_sub:                                   # 경신중 편집본처럼 "[서술형 k] …  [7점]"
            if not re.search(r"\[\s*(서술형|단답형|서답형)", q.get("q", "")):
                ns += 1
                blks[0] = ("p", [T("[서술형 %d] " % ns)] + list(blks[0][1]))
        pt = str(q.get("pt", "")).strip()
        if pt:
            try:
                pt = "%g" % float(pt)
            except ValueError:
                pass
            last = max(i for i, b in enumerate(blks) if b[0] == "p")
            blks[last] = ("p", list(blks[last][1]) + [T("  [%s점]" % pt)])
        # 문제 → 그림 → 선택지 (앞뒤 빈 줄 없이)
        imgs = q.get("imgs") or []
        for im in imgs:
            blks.append(fig_block(folder, im, q.get("imgW")))
        chs = q.get("ch") or []
        if chs and not is_sub:
            for k, c in enumerate(chs):
                parts = []
                for bb in blocks_to_g3(parse_q(c)):
                    if bb[0] == "p":
                        if parts:
                            parts.append(T(" "))
                        parts += bb[1]
                lab = CIRC[k] if k < len(CIRC) else "(%d)" % (k + 1)
                blks.append(("p", [T(lab + " ")] + parts))
        P[n] = blks
    return sk, meta, P, UNIT, nums


def level_of(meta):
    m = re.search(r"(초|중|고)", str(meta.get("grade", "")))
    if m:
        return m.group(1)
    return "고" if re.search(r"고\d|공통|수학[ⅠⅡI]|미적|확률|기하", str(meta)) else "중"


# ───────────────────────── 만들기 ─────────────────────────
def build(folder, out):
    folder = os.path.abspath(folder); out = os.path.abspath(out)
    sk, meta, P, UNIT, nums = build_P(folder)
    g3lib.CROP = os.path.join(folder, "x", "BinData")
    tmp = tempfile.mkdtemp(prefix="b4_")
    code = os.path.basename(folder.rstrip("/"))
    g3lib.OUTDIR = os.path.join(tmp, "채수학", code)
    os.makedirs(g3lib.OUTDIR)
    key = g3lib.outkey() + "|" + g3lib.PAPER
    measured = key in g3lib.HTAB
    if not measured:                              # 실측 높이가 없으니 어림값을 넣어 쪽을 짠다
        g3lib.HTAB[key] = {str(n): est_items(P[n]) for n in nums}
    # 'cropimg' 에는 어림용 높이(4번째 값)가 붙어 있다 — g3lib 은 앞 세 값만 쓴다
    P = {n: [b[:3] if b[0] == "cropimg" else b for b in blks] for n, blks in P.items()}
    lev = level_of(meta)
    # g3lib 은 파일 이름의 '중3'·'고1' 글자로 학교급 색을 고른다 → 이름에 넣어 만든 뒤 옮긴다
    grade = re.search(r"[초중고]\d", str(meta.get("grade", "")))
    fname = "build (%s).hwpx" % (grade.group(0) if grade else lev + "1")
    title = exam_title(meta.get("title") or code)
    info = "날짜 ____.____      이름 ____________      점수 ________"
    path = g3lib.build_exam(P, UNIT, nums, "", fname, per_page=2, title=title, info=info)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.move(path, out)
    shutil.rmtree(tmp, ignore_errors=True)
    return out, measured, g3lib.HTAB[key]


# ───────────────────────── 검사 ─────────────────────────
def validate(out):
    import xml.dom.minidom as M
    z = zipfile.ZipFile(out)
    infos = z.infolist()
    errs = []
    if infos[0].filename != "mimetype" or infos[0].compress_type != zipfile.ZIP_STORED:
        errs.append("mimetype 이 첫 항목·무압축이 아님")
    if z.read("mimetype") != b"application/hwp+zip":
        errs.append("mimetype 내용")
    for i in infos:
        if i.filename.endswith((".xml", ".hpf")):
            try:
                M.parseString(z.read(i.filename))
            except Exception as e:
                errs.append("XML %s: %s" % (i.filename, e))
    hpf = z.read("Contents/content.hpf").decode("utf-8")
    man = dict(re.findall(r'<opf:item id="([^"]+)" href="([^"]+)"', hpf))
    sec = z.read("Contents/section0.xml").decode("utf-8")
    if FOOT_LEFT not in sec:
        errs.append("꼬리말 문구 없음")
    if "logo.png" not in hpf:
        errs.append("로고 그림 없음")
    refs = set(re.findall(r'binaryItemIDRef="([^"]+)"', sec))
    names = set(z.namelist())
    for r in refs:
        if r not in man:
            errs.append("그림 참조 %s 가 content.hpf 에 없음" % r)
        elif man[r] not in names:
            errs.append("그림 파일 없음: %s" % man[r])
    return errs, dict(files=len(names), pics=len(refs), eqs=sec.count("<hp:equation"),
                      tables=sec.count("<hp:tbl"), size=os.path.getsize(out))


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    out, measured, hs = build(sys.argv[1], sys.argv[2])
    errs, info = validate(out)
    print("문항 높이: %s" % ("_문항높이표 실측" if measured else "어림값(한글 실측 없음)"))
    print("수식 %d개 — 크기표 그대로 %d · 띄어쓰기 맞춰 %d · 나머지는 g3lib 어림"
          % (STAT["eq"], STAT["eq_hit"], STAT["eq_nhit"]))
    if WARN:
        print("변환 경고 %d건: %s" % (len(WARN), "; ".join(WARN[:5])))
    print("검사:", "OK" if not errs else errs, info)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
