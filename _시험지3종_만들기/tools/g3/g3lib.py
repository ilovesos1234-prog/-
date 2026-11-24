# -*- coding: utf-8 -*-
"""고3 9월 모평 편집가능 시험지 공용 빌더. 공통/확통/미적/기하 공용."""
import io, json, os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from hwpxlib import Doc, MM
from PIL import Image

SC = os.path.dirname(__file__)
CROP = os.path.join(SC, "g3fig")
LOGO2 = os.path.join(SC, "..", "..", "1차시", "도형PNG", "logo_trim.png")
OUTDIR = SC
PAPER = "B4"          # 2026-09-19 확정 틀. A4 로 만들려면 데이터 파일에서 g3lib.PAPER = "A4"
BODY_H = 74550
COLW = 25512
CW_MM = 82
K = 1.0               # 글자 크기 비율(A4 기준) — 자리·여백을 같이 키우는 데 쓴다


def use_paper(name):
    """종이를 바꾸고 그에 맞춰 자리 값들을 다시 잡는다."""
    global PAPER, BODY_H, COLW, CW_MM, K, AVAIL, CPH, SPW, FIG_SCALE, MINGAP, PROBGAP, NATGAP
    import hwpxlib
    PAPER = name
    hwpxlib.PAPER = name
    BODY_H = hwpxlib.body_h()
    COLW = hwpxlib.body_w() // 2
    CPH = dict(hwpxlib.cps())
    K = CPH[14] / 900.0
    CW_MM = int(COLW / MM * 0.91)
    lm, rm = hwpxlib.PIND[name]
    AVAIL = COLW - int(600 * K) * 2 - 200 - lm - rm
    SPW = CHW.get(" ", 0.203) * CPH[14]
    FIG_SCALE = K                      # 그림 속 글씨(9pt)를 본문 크기로
    MINGAP = int(700 * K)
    PROBGAP = int(PROBGAP_MM * MM)      # 문항 사이 최소 여백
    # 아무것도 안 넣었을 때 저절로 생기는 틈(문항 끝 빈 줄) — 재어 본 값에서 비례로
    NATGAP = int(2835 * (CPH[0] * hwpxlib.LINESP[name]) / (1100.0 * 165))

# ---- 실측 표 (있으면 어림짐작 대신 쓴다) ----
def _load(name):
    f = os.path.join(SC, "..", name)
    if os.path.exists(f):
        return json.load(io.open(f, encoding="utf-8"))
    return {}

EQTAB = _load("_수식크기표.json")    # 수식 → [폭, 높이, 밑선]  (한글이 잰 값)
HTAB = _load("_문항높이표.json")     # 학교 → {문항번호: 높이}    (PDF 에서 잰 값)
MAXPERCOL = 2                        # 한 단에 최대 몇 문제 (한 쪽 = 두 단 = 4문제)
PROBGAP_MM = 22                      # 한 단 안에서 문항 사이 최소 여백(mm) — 학교 원본이 19mm
CHOICE_PAD = 0                       # 선택지 칸 위아래 여유(한글이 무시함)
CHAR_IMG = os.path.join(SC, "채쌤_푯말.png")   # 푯말 든 채쌤 (_푯말만들기.py 로 만든다)
CHAR_MAX_MM = 67                     # 마지막 쪽 빈자리에 넣는 캐릭터 최대 높이
CHAR_MIN_MM = 45                     # 빈자리가 이보다 좁으면 안 넣는다
CHAR_WORD = "<수고했어요>"             # 캐릭터 아래 글귀
CHAR_BOTTOM_MM = 17                  # 글귀 아래로 남길 자리
HEAD_INLINE = True                   # 번호 옆에 유형 (2026-09-19 확정)
CHOICE_ROW = 780                     # 선택지 줄 높이 여유 — 원본 줄간격(32pt)에 맞춘 값
HALF_TOL_MM = 20                     # 아래 문항이 한가운데보다 내려갈 수 있는 한도
MAXGAP_MM = 70                       # 이보다 큰 구멍이 생기면 높이 맞추기를 포기한다
PROBGAP = int(PROBGAP_MM * MM)
NATGAP = 2835
FIG_NATURAL = True                   # TikZ 그림을 제 크기로 (글씨 = 본문 크기)
FIG_DPI = 900                        # tikzfig.DPI 와 같아야 한다
FIG_SCALE = 1.0                      # 더 키우고 싶으면 1.1, 1.2 …
FILL_SLACK = 1500                    # 단을 채울 때 남겨 두는 여유
CHW = _load("_글자폭표.json")        # 글자 → 글자크기 대비 폭   (PDF 에서 잰 값)
CPH = {16: 100, 0: 1000, 1: 1050, 2: 2600, 3: 1000, 4: 1050, 5: 2000, 6: 1100, 7: 900,
       8: 2000, 9: 1000, 10: 1100, 11: 950, 12: 1350, 13: 1000, 14: 900, 15: 700}
SPW = CHW.get(" ", 0.203) * 900      # 본문 9pt 빈칸 한 칸의 폭
# 본문 칸에서 글이 실제로 놓이는 가로 (칸 너비 − 칸 여백 − 문단 여백)
AVAIL = COLW - 600 * 2 - 200 - 1700 - 1900
MINGAP = 700                          # 원번호 사이 최소 틈

_KW = ("matrix|cases|left|right|over|sqrt|root|bar|times|div|cdot|"
       "alpha|beta|gamma|theta|pi|infty|lim|sum|int|sin|cos|tan|log|ln|"
       "vec|angle|overline|rightarrow|leftarrow|geq|leq|neq|<=|>=|!=|<|>")

def eqlook(script):
    """수식 크기표에서 찾기 — 기준 크기(baseUnit)마다 따로 쌓는다."""
    import hwpxlib
    b = hwpxlib.eqbase()
    v = EQTAB.get("%d|%s" % (b, script))
    if v is None and b == 1000:
        v = EQTAB.get(script)          # 예전에 쌓아 둔 것(10pt)
    return v


def estw(script):
    v = eqlook(script)
    if v:                                   # 한글이 직접 잰 값이 있으면 그걸 쓴다
        return v[0], v[1], (2 if v[1] > 1700 else 1)
    is_mat = "matrix" in script or "cases" in script
    tall = is_mat or "over" in script or "sqrt" in script or "root" in script or "int" in script or "sum" in script or "lim" in script
    vis = re.sub(_KW, "x", script)
    vis = re.sub(r"[{}&#^_~`\\]", "", vis).replace(" ", "")
    n = max(len(vis), 2)
    if is_mat:
        return 2600 + n * 300, 2500, 2
    w = 700 + int(n * 640)
    return w, (1250 if tall else (1050 if "^" in script else 850)), (2 if tall else 1)

def T(s): return ('t', s, 14)
def E(script):
    v = eqlook(script)
    if v:
        return ('eq', script, (v[0], v[1], v[2]))
    w, h, _ = estw(script); return ('eq', script, (w, h))

_LAT = re.compile(r'[A-Za-z]+')
UNITS = {"cm", "mm", "km", "m", "kg", "g", "s"}
def Evar(tok):
    v = eqlook(tok)
    if v:
        return ('eq', tok, (v[0], v[1], v[2]))
    return ('eq', tok, (360 + len(tok) * 500, 850))
def expand(parts):
    # 변수(소문자 한 글자)만 이탤릭 수식개체로. 점이름(대문자)·여러 글자·단위는 일반 글자.
    out = []
    for p in parts:
        if p[0] != 't':
            out.append(p); continue
        s = p[1]; last = 0
        for m in _LAT.finditer(s):
            tok = m.group(0)
            if m.start() > last: out.append(('t', s[last:m.start()], 14))
            unit = tok in UNITS and re.search(r"\d\s?$", s[:m.start()])   # 1.5 m, 390 m 같은 단위는 글자 그대로
            if len(tok) == 1 and tok.islower() and not unit:
                out.append(Evar(tok))
            else:
                out.append(('t', tok, 14))
            last = m.end()
        if last < len(s): out.append(('t', s[last:], 14))
    return out


CIRC = "①②③④⑤⑥⑦⑧⑨⑩"


def pwidth(parts):
    """expand() 를 거친 조각들이 차지하는 가로 폭(한글 단위)."""
    w = 0.0
    for p in parts:
        if p[0] == 't':
            h = CPH.get(p[2], 900)
            w += sum(CHW.get(c, 0.95) for c in p[1]) * h
        elif p[0] == 'eq':
            w += p[2][0]
    return int(w)


def _explode(parts):
    """한 문단에 ①② 가 여러 개면 원번호 앞에서 끊어 낱개로 만든다."""
    out, cur = [], []
    for p in parts:
        if p[0] != 't':
            cur.append(p); continue
        s, last = p[1], 0
        for i, ch in enumerate(s):
            if ch in CIRC:
                head = s[last:i]
                if head.strip():
                    cur.append(('t', head, p[2]))
                if cur:
                    out.append(cur)
                cur, last = [], i
        tail = s[last:]
        if tail:
            cur.append(('t', tail, p[2]))
    if cur:
        out.append(cur)
    return out


def is_choice(blk):
    """① 으로 시작하는 선택지 블록인가."""
    if blk[0] == 'ch':
        return True
    if blk[0] == 'p':
        for p in blk[1]:
            if p[0] == 't':
                t = p[1].strip()
                return bool(t) and t[0] in CIRC
    return False


def choice_items(blk):
    if blk[0] == 'ch':
        return [[('t', x, 14)] for x in blk[1]]
    return _explode(blk[1])


def outkey():
    """문항 높이표에서 이 시험지를 찾는 열쇠 — <학기폴더>/<학교폴더>."""
    d = os.path.normpath(os.path.abspath(OUTDIR)).replace("\\", "/")
    return "/".join(d.split("/")[-2:])


def plan_cols(ws):
    """원번호를 한 줄에 몇 개씩 앉힐지 — 5 → 3,2 → 2,2,1 → 하나씩.

    눈에 안 보이는 표의 칸에 하나씩 넣으므로, 가장 넓은 것이 칸에 들어가면 된다.
    """
    n = len(ws)
    cand = []
    for k in (n, (n + 1) // 2, 2, 1):
        if 0 < k <= n and k not in cand:
            cand.append(k)
    # 글자폭표가 **빈칸·쉼표를 좁게** 잡아 놓아 "① ㄱ, ㄴ" 처럼 빈칸이 여럿인
    # 선택지는 실제보다 20% 쯤 좁게 재진다. 그래서 다섯 칸에 우겨넣고는 칸끼리
    # 딱 붙어 버렸다(2026-09-20 오성중 중3 12번). 여기서만 넉넉히 보정한다 —
    # 칸 수만 달라지므로 높이·쪽수에는 영향이 없다.
    need = max(ws) * 1.15
    for k in cand:
        if need <= AVAIL // k - MINGAP:        # 칸 사이에 최소 틈은 남긴다
            return k
    return 1


def build_exam(P, UNIT, nums, subject, fname, per_page=2, sol_prefix=None, sol_mm=82, title=None, info=None):
    # 2026-09-17 공용틀 학교급 색 — 파일 이름의 '중2'·'고1' 같은 글자로 고른다(없으면 고등)
    import hwpxlib
    use_paper(PAPER)
    m = re.search(r"(초|중|고)\d", fname)
    hwpxlib.LEVEL = m.group(1) if m else "고"
    d = Doc(title=(title or ("2027 고3 9월 모의평가 수학 " + subject)))

    def add_img(path, w_mm):
        im = Image.open(path); wpx, hpx = im.width, im.height
        with open(path, "rb") as f: data = f.read()
        iid = d.add_image(os.path.basename(path), data, "image/png", wpx, hpx)
        if w_mm is None:
            # 그림 속 글씨(\small = 9pt)가 본문 글씨와 같은 크기로 나오는 '제 크기'
            # 1px = 72/FIG_DPI pt (한글 단위로는 x100)
            w = int(wpx * 7200.0 / FIG_DPI * FIG_SCALE)
        else:
            w = int(w_mm * MM)
        return (iid, w, int(w * hpx / wpx))

    def type_pill(n):
        txt = "채수학  X  " + UNIT.get(n, "")
        w = min(int(len(txt) * 700 * K) + int(1500 * K), COLW - 1000)
        st, ss = d.cell_top_margin, d.cell_side_margin
        d.cell_top_margin, d.cell_side_margin = int(70 * K), int(350 * K)
        p = d._tbl_in_p([[[('p', txt, 15, 1)]]], [w], row_h=int(1050 * K), divider=False, parapr=4, cell_bf=12)
        d.cell_top_margin, d.cell_side_margin = st, ss
        return p

    def head_row(n):
        """문항 번호와 유형 알약을 한 줄에 나란히 놓는다."""
        txt = "채수학  X  " + UNIT.get(n, "")
        inner = COLW - 2 * int(600 * K) - 200
        bw = int(2400 * K)
        pw = min(int(len(txt) * 700 * K) + int(1500 * K), inner - bw - int(600 * K))
        st, sb, ss = d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = int(70 * K), int(70 * K), int(350 * K)
        rows = [[[('p', "%02d" % n, 10, 4)], [('p', txt, 15, 4)], [('p', "", 16, 4)]]]
        xml = d._tbl_in_p(rows, [bw, pw, inner - bw - pw], row_h=int(1150 * K),
                          divider=False, parapr=4,
                          cell_bf=lambda r, c: (1, 12, 1)[c], valign="CENTER")
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = st, sb, ss
        return xml

    def choice_block(items):
        """원번호를 눈에 안 보이는 표에 나란히 앉힌다 — 자리가 어긋나지 않는다."""
        ncol = plan_cols([pwidth(x) for x in items])
        if ncol == 1:
            return [('mix', it, 6) for it in items]
        pitch = AVAIL // ncol
        maxh = 900
        for it in items:
            for q in it:
                if q[0] == 'eq':
                    maxh = max(maxh, q[2][1])
        trs = []
        for r in range(0, len(items), ncol):
            cells = [[('mix', x, 4)] for x in items[r:r + ncol]]
            while len(cells) < ncol:
                cells.append([('p', "", 14, 4)])
            trs.append(cells)
        st, sb, ss = d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin
        # 원본처럼 선택지 줄 사이가 숨 쉬도록 위아래를 띄운다
        d.cell_top_margin = d.cell_bottom_margin = int(CHOICE_PAD * K)
        d.cell_side_margin = 0
        xml = d._tbl_in_p(trs, [pitch] * ncol, row_h=maxh + int(CHOICE_ROW * K),
                          divider=False, parapr=6, cell_bf=1)
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = st, sb, ss
        return [('raw', xml)]

    SPACER_OVER = 1050          # 자리 채우는 표가 스스로 먹는 높이(재어 본 값)

    def spacer_xml(h):
        """세로로 h 만큼 자리를 비우는 눈에 안 보이는 표."""
        h -= SPACER_OVER
        if h < 300:
            return None
        st, sb, ss = d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin
        d.cell_top_margin = d.cell_bottom_margin = d.cell_side_margin = 0
        xml = d._tbl_in_p([[[('p', "", 16, 4)]]], [COLW - int(3400 * K)], row_h=h,
                          divider=False, parapr=4, cell_bf=1, noadjust=True)
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = st, sb, ss
        return xml

    def box_xml(lines):
        items = [('p', "", 15, 4)]
        items += [('mix', expand(ln), 5) for ln in lines]
        items += [('p', "", 15, 4)]
        st, sb, ss = d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = int(250*K), int(250*K), int(450*K)
        xml = d._tbl_in_p([[items]], [COLW - int(3400 * K)], row_h=1200, divider=False, parapr=5, cell_bf=3)
        d.cell_top_margin, d.cell_bottom_margin, d.cell_side_margin = st, sb, ss
        return xml

    # 빈 줄은 그림·네모상자 앞뒤와 문항 끝에만 둔다.
    # (번호↔문제, 문제↔①, ①↔② 사이는 붙여 쓴다 — 2026-09-19)
    SPACED = ('box',)      # 그림 앞뒤는 안 띄운다(문제-그림-선택지 붙임, 2026-09-19)

    def prob_items(n):
        if HEAD_INLINE:                      # 번호 옆에 유형 (2026-09-19 시험판)
            it = [('raw', head_row(n))]
        else:
            it = [('raw', type_pill(n)), ('raw', d.badge_xml(int(n)))]
        blks = list(P[n])
        i = 0
        while i < len(blks):
            blk = blks[i]
            if is_choice(blk):                 # ①②③ — 폭을 재서 한 줄에 여럿 앉힌다
                j, items = i, []
                while j < len(blks) and is_choice(blks[j]):
                    items += choice_items(blks[j]); j += 1
                it += choice_block([expand(x) for x in items])
                i = j
            elif blk[0] == 'p':
                it.append(('mix', expand(blk[1]), 6)); i += 1
            elif blk[0] == 'box':
                it.append(('raw', box_xml(blk[1]))); i += 1
            elif blk[0] == 'fig':
                w = None if FIG_NATURAL else blk[2]      # 제 크기로 넣는다
                it.append(('img', [add_img(os.path.join(CROP, blk[1]), w)], 1)); i += 1
            elif blk[0] == 'cropimg':
                w = blk[2] if len(blk) > 2 else CW_MM
                it.append(('img', [add_img(os.path.join(CROP, blk[1]), w)], 1)); i += 1
            else:
                i += 1
            # 빈 줄은 그림·네모상자 앞뒤와 문항 끝에만 (2026-09-19)
            nxt = blks[i][0] if i < len(blks) else None
            if blk[0] in SPACED or nxt in SPACED or nxt is None:
                it.append(('p', "", 0, 4))
        return it

    # ---- header ----
    d.cell_top_margin, d.cell_side_margin, d.divider_gap = int(600*K), int(600*K), int(1600*K)
    # 인쇄할 종이를 꼬리말에 적어 둔다(B4 / A4)
    tag = (PAPER + " · ") if PAPER != "A4" else ""   # B4 일 때만 종이를 적는다
    d.set_footer("채수학교습소 · 채미정T", tag + "☎ 010-8677-2263")
    im = Image.open(LOGO2); lw, lh = im.width, im.height
    with open(LOGO2, "rb") as f: ldata = f.read()
    lid = d.add_image("logo.png", ldata, "image/png", lw, lh)
    LW = int(21 * MM); LH = int(LW * lh / lw)
    _st, _ss = d.cell_top_margin, d.cell_side_margin
    d.cell_top_margin, d.cell_side_margin = int(120*K), int(300*K)
    LCW = LW + 2 * d.cell_side_margin + 400        # 로고가 칸에 넉넉히 들어가게
    INFO = info or "날짜 26.__      이름 ____________      점수 ________"
    TITLE = title or ("2027 고3 9월 모의평가 · 수학영역 " + subject)
    titlerow = d._tbl_in_p([[[('img', [(lid, LW, LH)], 1)],
                             [('p', TITLE, 8, 1)],
                             [('p', "", 0, 1)]]],
                           [LCW, COLW * 2 - 2 * LCW, LCW], row_h=LH,
                           divider=False, parapr=1, cell_bf=lambda r, c: 1)
    inforow = d._p_xml(INFO, 7, 3)
    d.cell_top_margin, d.cell_side_margin = _st, _ss
    HEADER_H, INTRO_H = LH + 2000, 1250
    d.header_box([('raw', titlerow), ('raw', inforow)], height=HEADER_H)
    d.header_box([('p', "✏  수학하는 방법을 알려줍니다!!", 15, 3)], bf=13, height=INTRO_H)

    SPACER = HEADER_H + INTRO_H
    AVAIL1 = BODY_H - SPACER
    ROWH = AVAIL1 - 3500
    # 한 단에 몇 문제를 앉힐지 — 잰 높이가 있으면 채워 넣는다(길어서 안 되는 것만 홀로)
    hs = HTAB.get(outkey() + "|" + PAPER, {}) if not sol_prefix else {}
    CAP = AVAIL1 - FILL_SLACK
    HALF = CAP // 2                # 아래 문항은 단의 한가운데에서 시작한다
    TMAX = HALF + int(HALF_TOL_MM * MM)   # 꼭 필요하면 이만큼까지 내려갈 수 있다
    cols = []
    if hs:
        i, n_all = 0, len(nums)
        while i < n_all:
            a = nums[i]
            ha = hs.get(str(a))
            if ha is None or ha > TMAX - PROBGAP:      # 너무 긴 문항은 혼자 한 단
                cols.append([a]); i += 1; continue
            hb = hs.get(str(nums[i + 1])) if i + 1 < n_all else None
            if hb is not None and hb <= CAP - TMAX:
                cols.append([a, nums[i + 1]]); i += 2
            else:
                cols.append([a]); i += 1
        print("  단 나누기:", " | ".join(",".join(str(x) for x in c) for c in cols),
              "(단 %d, 한가운데 %d)" % (CAP, HALF))
    else:
        cols = [[n] for n in nums]
    pages = [cols[i:i + per_page] for i in range(0, len(cols), per_page)]

    def sol_below(n):
        path = os.path.join(SC, "%s_%d.png" % (sol_prefix, n))
        iid_wh = add_img(path, sol_mm)
        return [('p', "", 0, 4), ('mix', [('t', "▶ 풀이", 13)], 5), ('img', [iid_wh], 1)]

    def char_tail(free):
        """마지막 쪽 빈자리에 채쌤 캐릭터를 앉힌다."""
        if not (CHAR_IMG and os.path.exists(CHAR_IMG)):
            return []
        if free < int(CHAR_MIN_MM * MM):
            return []
        im = Image.open(CHAR_IMG)
        cap_h = int(CPH[14] * 2.4) if CHAR_WORD else 0       # 글귀 한 줄
        room = free - cap_h - int(CHAR_BOTTOM_MM * MM)
        h_mm = min(room / MM, CHAR_MAX_MM)
        if h_mm < 25:
            return []
        w_mm = h_mm * im.width / im.height
        if w_mm * MM > COLW - int(2500 * K):
            w_mm = (COLW - int(2500 * K)) / MM
            h_mm = w_mm * im.height / im.width
        out = []
        pad = int(room - h_mm * MM)            # 아래쪽으로 내려 앉힌다
        sp = spacer_xml(pad)
        if sp:
            out.append(('raw', sp))
        out.append(('img', [add_img(CHAR_IMG, w_mm)], 1))
        if CHAR_WORD:
            out.append(('p', CHAR_WORD, 14, 1))
        return out

    def colcell(col, t2=None, tail=False):
        items = []
        for k, n in enumerate(col):
            if k:
                h1 = hs.get(str(col[0]))
                if t2 and h1:                 # 아래 문항 시작 높이를 두 단이 같게
                    want = t2 - h1
                else:                         # 못 맞추면 적어도 최소 여백만큼은 띄운다
                    want = PROBGAP
                sp = spacer_xml(want - NATGAP)
                if sp:
                    items.append(('raw', sp))
            items += prob_items(n)   # 문항 끝 빈 줄이 곧 문항 사이 틈
            if sol_prefix:
                items += sol_below(n)
        if tail:
            if not col:
                used = 0                       # 빈 단이면 단 전체가 캐릭터 자리
            elif hs:
                used = (t2 + hs.get(str(col[-1]), 0)) if len(col) > 1 else hs.get(str(col[0]), 0)
            else:
                used = CAP
            items += char_tail(CAP - used)
        return items or [('p', "", 0, 4)]

    for gi, pg in enumerate(pages):
        pg = pg + [[]] * (per_page - len(pg))
        # 이 쪽의 아래 문항 시작 높이 — 한가운데가 기본, 위 문항이 길면 그만큼만 내린다
        t2 = HALF
        for c in pg:
            if len(c) > 1 and hs.get(str(c[0])):
                t2 = max(t2, hs[str(c[0])] + PROBGAP)
        tail_j = -1
        if gi == len(pages) - 1:               # 마지막 쪽 — 빈 단이 있으면 거기, 없으면 마지막 단
            filled = [j for j, c in enumerate(pg) if c]
            tail_j = len(filled) if len(filled) < per_page else (filled[-1] if filled else -1)
        d.table([[colcell(c, t2, tail=(j == tail_j))
                  for j, c in enumerate(pg)]], [COLW] * per_page, row_h=ROWH,
                divider=True, pagebreak=(gi > 0), top_spacer=(SPACER if gi > 0 else 0))

    out = os.path.join(OUTDIR, fname)
    d.write(out)
    print("saved:", os.path.basename(out), os.path.getsize(out), "| pages:", len(pages), "| imgs:", len(d.images))
    return out


def units(code):
    """손풀이 원고(sol_<코드>.py)의 유형 이름을 단원 알약에 쓴다."""
    import importlib
    sys.path.insert(0, os.path.join(SC, ".."))
    m = importlib.import_module("sol_" + code)
    return {p["no"]: p["type"].split(" · ")[-1] for p in m.SOL}


def note(school, lines):
    """원본이 가려져 확인이 필요한 곳을 한 파일에 모아 적는다."""
    path = os.path.join(SC, "_확인할곳.txt")
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    # 앞뒤 빈 줄을 떼고 견주어야 같은 학교를 두 번 적지 않는다(2026-09-19)
    blocks = [b.strip("\n") for b in old.split("\n\n") if b.strip()]
    blocks = [b for b in blocks if not b.startswith("[" + school + "]")]
    if lines:
        blocks.append("[" + school + "]\n" + "\n".join("  - " + x for x in lines))
    open(path, "w", encoding="utf-8").write("\n\n".join(blocks) + "\n")
