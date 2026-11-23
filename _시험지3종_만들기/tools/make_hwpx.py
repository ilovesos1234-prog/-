# 학교 시험지 skeleton.json → 편집 가능한 한글 HWPX (B4, 2단, 한글 수식 객체)
# 사용: python3 make_hwpx.py <시험 폴더> <out.hwpx>
#   <시험 폴더>/skeleton.json  : meta + Q[ {n, pt, type 객/서, q, ch[5], imgs, imgW} ]
#   <시험 폴더>/x/BinData/<id>.png|jpg : 그림
# 만든 뒤 자동 검사: XML 파싱, zip 순서/mimetype, 그림 참조, 수식 스크립트 왕복(heq.py, 있으면)
# 패키징 방식은 ../mkhwpx.py 와 같음 (mimetype 무압축 첫 항목 + 나머지 deflate).
import sys, os, re, json, glob, html, zipfile, difflib
from html.parser import HTMLParser
from xml.sax.saxutils import escape
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hwpx_eq import conv as tex2heq

HEQ = os.environ.get('HEQ', '/tmp/claude-0/-home-user/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/w_n31/bin/heq.py')

# ---------------- 쪽 설정 (HWPUNIT, 1mm = 283.465) ----------------
MM = 283.465
PAGE_W, PAGE_H = 72852, 103180          # B4 257 x 364 mm
ML = MR = 4252                           # 15mm
MT = 3969                                # 14mm
MB = 2268; MF = 2268; MH = 0
GAP = 2268                               # 단 간격 8mm
TEXT_W = PAGE_W - ML - MR                # 64348
COL_W = (TEXT_W - GAP) // 2              # 31040
IND = 1800                               # 문항 번호 내어쓰기
FONT_PT = 10
LINE = 160                               # 줄 간격 %
EM = FONT_PT * 100                       # 10pt 글자 한 칸 = 1000

NS = ('xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
      'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
      'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
      'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
      'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" '
      'xmlns:opf="http://www.idpf.org/2007/opf/" xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
      'xmlns:epub="http://www.idpf.org/2007/ops" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"')
XMLDECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
CIRC = '①②③④⑤'


def X(s): return escape(s, {'"': '&quot;'})


# ======================= header.xml (스타일 표) =======================
FONTS = [('함초롬바탕', 'FCAT_GOTHIC', 6, 4), ('함초롬돋움', 'FCAT_GOTHIC', 6, 4), ('한컴바탕', 'FCAT_MYUNGJO', 6, 4)]
F_BODY, F_GOTHIC = 0, 1
LANGS = ['HANGUL', 'LATIN', 'HANJA', 'JAPANESE', 'OTHER', 'SYMBOL', 'USER']


class Styles:
    def __init__(s):
        s.cp = {}; s.pp = {}; s.tp = {(): 0}; s.bf = {}
        s.BF_NONE = s.border()                       # 1: 테두리 없음 (쪽/표 바깥)
        s.BF_CHAR = s.border()                       # 2: 글자 기본
        s.BF_BOX = s.border(all_='SOLID')            # 보기 상자/표 칸
        s.BF_HEAD = s.border(bottom=('SOLID', '0.5 mm'))
        s.BF_NAME = s.border(all_='SOLID', bottom=('SOLID', '0.5 mm'))
        s.BF_TH = s.border(all_='SOLID', fill='#EDEDED')
        s.char()                                     # 0: 본문 10pt
        s.para()                                     # 0: 기본 문단

    def border(s, all_='NONE', bottom=None, fill=None):
        k = (all_, bottom, fill)
        if k not in s.bf: s.bf[k] = len(s.bf) + 1
        return s.bf[k]

    def char(s, size=FONT_PT, bold=False, under=False, italic=False, boxed=False, font=F_BODY, color='#000000'):
        k = (size, bold, under, italic, boxed, font, color)
        if k not in s.cp: s.cp[k] = len(s.cp)
        return s.cp[k]

    def tabs(s, items):
        k = tuple(items)
        if k not in s.tp: s.tp[k] = len(s.tp)
        return s.tp[k]

    def para(s, align='JUSTIFY', intent=0, left=0, prev=0, next=0, line=LINE, tabs=(), keep=False, keeplines=False):
        k = (align, intent, left, prev, next, line, s.tabs(tabs), keep, keeplines)
        if k not in s.pp: s.pp[k] = len(s.pp)
        return s.pp[k]

    def xml(s):
        o = [XMLDECL, '<hh:head %s version="1.2" secCnt="1">' % NS,
             '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/><hh:refList>']
        o.append('<hh:fontfaces itemCnt="7">')
        for lg in LANGS:
            o.append('<hh:fontface lang="%s" fontCnt="%d">' % (lg, len(FONTS)))
            for i, (f, fam, w, pr) in enumerate(FONTS):
                o.append('<hh:font id="%d" face="%s" type="TTF" isEmbedded="0"><hh:typeInfo familyType="%s" weight="%d" proportion="%d" '
                         'contrast="0" strokeVariation="1" armStyle="1" letterform="1" midline="1" xHeight="1"/></hh:font>' % (i, f, fam, w, pr))
            o.append('</hh:fontface>')
        o.append('</hh:fontfaces>')
        o.append('<hh:borderFills itemCnt="%d">' % len(s.bf))
        for (all_, bottom, fill), i in sorted(s.bf.items(), key=lambda x: x[1]):
            def ln(tag, t, w='0.12 mm'): return '<hh:%s type="%s" width="%s" color="#000000"/>' % (tag, t, w if t != 'NONE' else '0.1 mm')
            b = bottom or (all_, '0.12 mm')
            o.append('<hh:borderFill id="%d" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
                     '<hh:slash type="NONE" Crooked="0" isCounter="0"/><hh:backSlash type="NONE" Crooked="0" isCounter="0"/>' % i
                     + ln('leftBorder', all_) + ln('rightBorder', all_) + ln('topBorder', all_) + ln('bottomBorder', b[0], b[1])
                     + '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>'
                     + ('<hc:fillBrush><hc:winBrush faceColor="%s" hatchColor="#999999" alpha="0"/></hc:fillBrush>' % fill if fill else '')
                     + '</hh:borderFill>')
        o.append('</hh:borderFills>')
        o.append('<hh:charProperties itemCnt="%d">' % len(s.cp))
        for (size, bold, under, italic, boxed, font, color), i in sorted(s.cp.items(), key=lambda x: x[1]):
            fr = ' '.join('%s="%d"' % (l.lower(), font) for l in LANGS)
            o.append('<hh:charPr id="%d" height="%d" textColor="%s" shadeColor="none" useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="%d">'
                     '<hh:fontRef %s/><hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
                     '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
                     '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
                     '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
                     % (i, int(size * 100), color, s.BF_BOX if boxed else s.BF_CHAR, fr)
                     + ('<hh:italic/>' if italic else '') + ('<hh:bold/>' if bold else '')
                     + ('<hh:underline type="BOTTOM" shape="SOLID" color="#000000"/>' if under else '')
                     + '</hh:charPr>')
        o.append('</hh:charProperties>')
        o.append('<hh:tabProperties itemCnt="%d">' % len(s.tp))
        for items, i in sorted(s.tp.items(), key=lambda x: x[1]):
            if not items: o.append('<hh:tabPr id="%d" autoTabLeft="0" autoTabRight="0"/>' % i); continue
            o.append('<hh:tabPr id="%d" autoTabLeft="0" autoTabRight="0">' % i + ''.join(
                '<hh:tabItem pos="%d" type="%s" leader="NONE"/>' % (p, t) for p, t in items) + '</hh:tabPr>')
        o.append('</hh:tabProperties>')
        o.append('<hh:numberings itemCnt="1"><hh:numbering id="1" start="0">' + ''.join(
            '<hh:paraHead start="1" level="%d" align="LEFT" useInstWidth="1" autoIndent="1" widthAdjust="0" textOffsetType="PERCENT" '
            'textOffset="50" numFormat="DIGIT" charPrIDRef="4294967295" checkable="0">^%d.</hh:paraHead>' % (l, l) for l in range(1, 8))
            + '</hh:numbering></hh:numberings>')
        o.append('<hh:paraProperties itemCnt="%d">' % len(s.pp))
        for (align, intent, left, prev, next, line, tp, keep, keeplines), i in sorted(s.pp.items(), key=lambda x: x[1]):
            o.append('<hh:paraPr id="%d" tabPrIDRef="%d" condense="0" fontLineHeight="0" snapToGrid="0" suppressLineNumbers="0" checked="0">'
                     '<hh:align horizontal="%s" vertical="BASELINE"/><hh:heading type="NONE" idRef="0" level="0"/>'
                     '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD" widowOrphan="0" keepWithNext="%d" keepLines="%d" pageBreakBefore="0" lineWrap="BREAK"/>'
                     '<hh:autoSpacing eAsianEng="0" eAsianNum="0"/><hh:margin><hc:intent value="%d" unit="HWPUNIT"/><hc:left value="%d" unit="HWPUNIT"/>'
                     '<hc:right value="0" unit="HWPUNIT"/><hc:prev value="%d" unit="HWPUNIT"/><hc:next value="%d" unit="HWPUNIT"/></hh:margin>'
                     '<hh:lineSpacing type="PERCENT" value="%d" unit="HWPUNIT"/>'
                     '<hh:border borderFillIDRef="%d" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" connect="0" ignoreMargin="0"/></hh:paraPr>'
                     % (i, tp, align, int(keep), int(keeplines), intent, left, prev, next, line, s.BF_CHAR))
        o.append('</hh:paraProperties>')
        o.append('<hh:styles itemCnt="1"><hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0" charPrIDRef="0" '
                 'nextStyleIDRef="0" langID="1042" lockForm="0"/></hh:styles>')
        o.append('</hh:refList><hh:compatibleDocument targetProgram="HWP201X"><hh:layoutCompatibility/></hh:compatibleDocument>'
                 '<hh:docOption><hh:linkinfo path="" pageInherit="0" footnoteInherit="0"/></hh:docOption>'
                 '<hh:trackchageConfig flags="56"/></hh:head>')
        return ''.join(o)


# ======================= 본문 HTML-ish 파서 =======================
MATH_RE = re.compile(r'\$([^$]*)\$')
PH = re.compile('\ue000(\\d+)\ue001')


def brace_bal(m): return len(re.findall(r'\\\{|\\lbrace\b', m)) - len(re.findall(r'\\\}|\\rbrace\b', m))


def merge_split_sets(q):
    """$\\{a \\mid b$ 이고 $c\\}$ 처럼 집합 괄호가 $ 사이에 걸쳐 끊긴 경우 하나의 수식으로 합침 (중간 글은 \\text)"""
    parts = re.split(r'(\$[^$]*\$)', q)
    out = []; i = 0
    while i < len(parts):
        p = parts[i]
        if p.startswith('$') and p.endswith('$') and len(p) >= 2 and brace_bal(p) > 0:
            acc = p[1:-1]; bal = brace_bal(p); j = i + 1; ok = False
            while j < len(parts) and j <= i + 8:
                t = parts[j]
                if t.startswith('$') and t.endswith('$') and len(t) >= 2:
                    acc += t[1:-1]; bal += brace_bal(t)
                    if bal <= 0: ok = True; break
                else:
                    if '<' in t or len(t) > 40: break
                    if t: acc += r'\text{%s}' % t
                j += 1
            if ok:
                out.append('$' + acc + '$'); i = j + 1; continue
        out.append(p); i += 1
    return ''.join(out)


def style_of(attrs):
    return (dict(attrs).get('style') or '').replace(' ', '').lower()


class QParser(HTMLParser):
    """q 문자열 → 블록 목록
       블록: ('p', inl, align) | ('box', blocks) | ('table', rows, border)
       inl : ('t', text, (bold, under, italic, boxed)) | ('eq', latex)"""
    KNOWN = {'b', 'strong', 'u', 'i', 'em', 'span', 'br', 'div', 'p', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'sup', 'sub', 'font', 'center'}

    def __init__(s, maths):
        super().__init__(convert_charrefs=True)
        s.maths = maths
        s.root = {'kind': 'root', 'blocks': [], 'cur': [], 'align': ['JUSTIFY']}
        s.stack = [s.root]
        s.bold = s.under = s.italic = s.boxed = 0
        s.spans = []; s.divs = []
        s.tables = []

    @property
    def c(s): return s.stack[-1]

    def flush(s):
        c = s.c
        if c['kind'] in ('table',): c['cur'] = []; return
        inl = c['cur']
        if any((x[0] == 'eq') or x[1].strip() for x in inl):
            c['blocks'].append(('p', inl, c['align'][-1]))
        c['cur'] = []

    def handle_starttag(s, tag, attrs):
        st = style_of(attrs)
        if tag in ('b', 'strong'): s.bold += 1
        elif tag == 'u': s.under += 1
        elif tag in ('i', 'em'): s.italic += 1
        elif tag == 'span':
            bx = 'border' in st; s.spans.append(bx); s.boxed += bx
        elif tag == 'br': s.flush()
        elif tag in ('div', 'p', 'center'):
            s.flush()
            if 'border' in st and 'border:0' not in st and 'border:none' not in st:
                box = {'kind': 'box', 'blocks': [], 'cur': [], 'align': ['JUSTIFY']}
                s.stack.append(box); s.divs.append('box')
            else:
                al = 'CENTER' if ('text-align:center' in st or tag == 'center') else s.c['align'][-1]
                s.c['align'].append(al); s.divs.append('div')
        elif tag == 'table':
            s.flush()
            a = dict(attrs)
            border = (a.get('border') not in (None, '0')) or 'border' in st.replace('border-collapse', '')
            t = {'kind': 'table', 'rows': [], 'border': border, 'blocks': None, 'cur': [], 'align': ['CENTER']}
            s.stack.append(t); s.tables.append(t)
        elif tag == 'tr':
            if s.tables:
                while s.c['kind'] == 'cell': s.end_cell()
                s.tables[-1]['rows'].append([])
        elif tag in ('td', 'th'):
            if not s.tables: return
            while s.c['kind'] == 'cell': s.end_cell()
            t = s.tables[-1]
            if not t['rows']: t['rows'].append([])
            if 'border' in st: t['border'] = True
            a = dict(attrs)
            al = 'CENTER' if ('text-align:center' in st or tag == 'th' or 'text-align' not in st) else 'LEFT'
            if 'text-align:left' in st: al = 'LEFT'
            cell = {'kind': 'cell', 'blocks': [], 'cur': [], 'align': [al], 'th': tag == 'th',
                    'colspan': int(a.get('colspan') or 1), 'rowspan': int(a.get('rowspan') or 1)}
            t['rows'][-1].append(cell); s.stack.append(cell)
            if tag == 'th': s.bold += 1

    def end_cell(s):
        s.flush()
        cell = s.stack.pop()
        if cell.get('th'): s.bold = max(0, s.bold - 1)

    def handle_endtag(s, tag):
        if tag in ('b', 'strong'): s.bold = max(0, s.bold - 1)
        elif tag == 'u': s.under = max(0, s.under - 1)
        elif tag in ('i', 'em'): s.italic = max(0, s.italic - 1)
        elif tag == 'span':
            if s.spans: s.boxed -= s.spans.pop()
        elif tag in ('div', 'p', 'center'):
            if not s.divs: return
            k = s.divs.pop()
            s.flush()
            if k == 'box':
                while s.c['kind'] == 'cell': s.end_cell()
                box = s.stack.pop()
                if box['kind'] == 'box' and box['blocks']: s.c['blocks'].append(('box', box['blocks']))
            else:
                if len(s.c['align']) > 1: s.c['align'].pop()
        elif tag in ('td', 'th'):
            if s.c['kind'] == 'cell': s.end_cell()
        elif tag == 'table':
            if not s.tables: return
            while s.c['kind'] == 'cell': s.end_cell()
            t = s.tables.pop()
            if s.c is t: s.stack.pop()
            rows = [r for r in t['rows'] if r]
            if rows: s.c['blocks'].append(('table', rows, t['border']))

    def handle_data(s, d):
        if s.c['kind'] == 'table': return          # 표 안 칸 밖 공백
        d = d.replace('\xa0', ' ').replace('\u2003', '  ')
        d = re.sub(r'[ \t\r\n]+', ' ', d)
        sty = (s.bold > 0, s.under > 0, s.italic > 0, s.boxed > 0)
        pos = 0
        for m in PH.finditer(d):
            if m.start() > pos: s.c['cur'].append(('t', d[pos:m.start()], sty))
            s.c['cur'].append(('eq', s.maths[int(m.group(1))]))
            pos = m.end()
        if pos < len(d): s.c['cur'].append(('t', d[pos:], sty))

    def done(s):
        while len(s.stack) > 1:
            c = s.stack.pop()
            if c['kind'] == 'cell': continue
            if c['kind'] == 'box' and c['blocks']: s.root['blocks'].append(('box', c['blocks']))
        s.stack = [s.root]; s.flush()
        return s.root['blocks']


def parse_q(q):
    q = merge_split_sets(q or '')
    maths = []

    def rep(m): maths.append(m.group(1)); return '\ue000%d\ue001' % (len(maths) - 1)
    q2 = MATH_RE.sub(rep, q)
    # 알려진 태그가 아닌 <...> (예: <보기>, <조건>)는 글자로
    q2 = re.sub(r'<(?!/?(?:%s)\b)' % '|'.join(QParser.KNOWN), '&lt;', q2)
    p = QParser(maths); p.feed(q2); p.close()
    blocks = p.done()
    return [trim_block(b) for b in blocks]


def trim_inl(inl):
    inl = [list(x) for x in inl]
    while inl and inl[0][0] == 't' and not inl[0][1].strip(): inl.pop(0)
    while inl and inl[-1][0] == 't' and not inl[-1][1].strip(): inl.pop()
    if inl and inl[0][0] == 't': inl[0][1] = inl[0][1].lstrip()
    if inl and inl[-1][0] == 't': inl[-1][1] = inl[-1][1].rstrip()
    return [tuple(x) for x in inl]


def trim_block(b):
    if b[0] == 'p': return ('p', trim_inl(b[1]), b[2])
    if b[0] == 'box': return ('box', [trim_block(x) for x in b[1]])
    if b[0] == 'table':
        for r in b[1]:
            for c in r: c['blocks'] = [trim_block(x) for x in c['blocks']]
        return b
    return b


# ======================= 본문 XML 조립 =======================
def txt_w(t, size=FONT_PT):
    w = 0
    for ch in t:
        if ch == ' ': w += .3
        elif ord(ch) > 0x2e80: w += 1.
        elif ch in 'ilI.,;:\'|!': w += .3
        elif ch.isupper(): w += .65
        else: w += .5
    return w * size * 100


class Doc:
    def __init__(s, folder):
        s.st = Styles()
        s.folder = folder
        s.zo = 0
        s.bins = {}            # id -> (path, ext)
        s.eqs = []             # (latex, script, warnings)

    def nid(s):
        s.zo += 1; return s.zo

    # ---- 수식
    def eq(s, latex):
        sc, m, warn = tex2heq(latex)
        s.eqs.append((latex, sc, warn))
        bu = 1000
        w = max(300, int(m.w * bu)); h = max(1000, int((m.a + m.d) * bu * 1.0))
        bl = max(40, min(95, int(round(100 * m.a / max(.1, m.a + m.d)))))
        k = s.nid()
        xml = ('<hp:equation id="%d" zOrder="%d" numberingType="EQUATION" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
               'dropcapstyle="None" version="Equation Version 60" baseLine="%d" textColor="#000000" baseUnit="%d" lineMode="CHAR" font="HancomEQN">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" '
               'horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment/><hp:script>%s</hp:script></hp:equation>'
               % (7800000 + k, k, bl, bu, w, h, X(sc)))
        return xml, w, h

    # ---- 그림
    def pic(s, img_id, width):
        fs = sorted(glob.glob(os.path.join(s.folder, 'x', 'BinData', img_id + '.*')))
        if not fs: raise SystemExit('그림 없음: %s' % img_id)
        path = fs[0]; ext = path.rsplit('.', 1)[1].lower()
        s.bins[img_id] = (path, ext)
        iw, ih = Image.open(path).size
        W = int(width); H = int(width * ih / iw)
        ow, oh = iw * 75, ih * 75
        k = s.nid()
        xml = ('<hp:pic id="%d" zOrder="%d" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
               'href="" groupLevel="0" instid="%d" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="%d" height="%d"/><hp:curSz width="%d" height="%d"/>'
               '<hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/>'
               '<hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="%.6f" e2="0" e3="0" e4="0" e5="%.6f" e6="0"/>'
               '<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
               '<hc:img binaryItemIDRef="%s" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
               '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>'
               '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/><hp:inMargin left="0" right="0" top="0" bottom="0"/>'
               '<hp:imgDim dimwidth="%d" dimheight="%d"/><hp:effects/>'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" '
               'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/>'
               '<hp:shapeComment>그림입니다.</hp:shapeComment></hp:pic>'
               % (8800000 + k, k, 9800000 + k, ow, oh, W, H, W // 2, H // 2, W / ow, H / oh, X(img_id),
                  ow, ow, oh, oh, ow, oh, ow, oh, W, H))
        return xml, W, H

    # ---- 문단
    def inl_runs(s, inl, base=None):
        """inline 목록 → (runs xml, 폭 추정, 최대 높이)"""
        base = base or {}
        out = []; w = 0; hmax = 0
        for it in inl:
            if it[0] == 't':
                bold, under, italic, boxed = it[2]
                cp = s.st.char(size=base.get('size', FONT_PT), bold=bold or base.get('bold', False), under=under, italic=italic, boxed=boxed,
                               font=base.get('font', F_BODY))
                out.append('<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp, X(it[1])))
                w += txt_w(it[1], base.get('size', FONT_PT))
            elif it[0] == 'eq':
                if not it[1].strip(): continue
                xml, ew, eh = s.eq(it[1])
                out.append('<hp:run charPrIDRef="%d">%s</hp:run>' % (s.st.char(), xml))
                w += ew; hmax = max(hmax, eh)
            elif it[0] == 'tab':
                out.append('<hp:run charPrIDRef="%d"><hp:t><hp:tab width="%d" leader="0" type="%d"/></hp:t></hp:run>'
                           % (s.st.char(), it[2] if len(it) > 2 else 1000, it[1]))
                w += 1000
            elif it[0] == 'raw':
                out.append(it[1]); w += it[2]
        return ''.join(out), w, hmax

    def P(s, pp, runs):
        if not runs: runs = '<hp:run charPrIDRef="0"><hp:t/></hp:run>'
        return '<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">%s</hp:p>' % (pp, runs)

    # ---- 표
    def table(s, rows, width, border=True, bf_cell=None, cell_margin=(510, 510, 280, 280), bf_tbl=None, heights=None):
        """rows: [[{'xml':문단들, 'w':폭, 'h':높이추정, 'colspan','rowspan','bf'}]], 열 폭 자동"""
        # 격자 배치
        grid = {}; placed = []; ncol = 0
        for r, row in enumerate(rows):
            c = 0
            for cell in row:
                while (r, c) in grid: c += 1
                cs, rs = cell.get('colspan', 1), cell.get('rowspan', 1)
                for dr in range(rs):
                    for dc in range(cs): grid[(r + dr, c + dc)] = 1
                placed.append((r, c, cell)); c += cs
                ncol = max(ncol, c)
        nrow = len(rows)
        for (r, c) in grid: nrow = max(nrow, r + 1)
        # 열 폭
        need = [1200] * ncol
        for r, c, cell in placed:
            if cell.get('colspan', 1) == 1: need[c] = max(need[c], cell.get('w', 0) + cell_margin[0] + cell_margin[1] + 200)
        tot = sum(need)
        if tot > width or (rows and rows[0] and rows[0][0].get('full')):
            colw = [int(width * x / tot) for x in need]
        else:
            colw = need[:]
        colw[-1] += (width if tot > width or (rows and rows[0] and rows[0][0].get('full')) else tot) - sum(colw)
        TW = sum(colw)
        rowh = [0] * nrow
        for r, c, cell in placed:
            cw = sum(colw[c:c + cell.get('colspan', 1)]) - cell_margin[0] - cell_margin[1]
            lines = 0
            for (pw, ph) in cell.get('paras', [(cell.get('w', 0), 0)]):
                lines += max(1, -(-int(pw) // max(1000, cw))) * max(1, ph / 1100.)
            h = int(lines * EM * LINE / 100 + cell_margin[2] + cell_margin[3])
            if heights: h = max(h, heights[r])
            if cell.get('rowspan', 1) == 1: rowh[r] = max(rowh[r], h)
        rowh = [h or 1600 for h in rowh]
        k = s.nid()
        o = ['<hp:tbl id="%d" zOrder="%d" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
             'pageBreak="CELL" repeatHeader="0" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="%d" noAdjust="0">'
             '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
             '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" '
             'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/>'
             '<hp:inMargin left="%d" right="%d" top="%d" bottom="%d"/>'
             % ((31000000 + k, k, nrow, ncol, bf_tbl or s.st.BF_NONE, TW, sum(rowh)) + tuple(cell_margin))]
        byrow = {}
        for r, c, cell in placed: byrow.setdefault(r, []).append((c, cell))
        for r in range(nrow):
            o.append('<hp:tr>')
            for c, cell in byrow.get(r, []):
                cs, rs = cell.get('colspan', 1), cell.get('rowspan', 1)
                cw = sum(colw[c:c + cs]); ch = sum(rowh[r:r + rs])
                bf = cell.get('bf') or bf_cell or (s.st.BF_BOX if border else s.st.BF_NONE)
                o.append('<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="%d">'
                         '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="%s" linkListIDRef="0" linkListNextIDRef="0" '
                         'textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
                         '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="%d"/><hp:cellSz width="%d" height="%d"/>'
                         '<hp:cellMargin left="%d" right="%d" top="%d" bottom="%d"/></hp:tc>'
                         % ((bf, cell.get('valign', 'CENTER'), cell['xml'] or s.P(0, ''), c, r, cs, rs, cw, ch) + tuple(cell_margin)))
            o.append('</hp:tr>')
        o.append('</hp:tbl>')
        return ''.join(o), TW, sum(rowh)

    # ---- 블록 → 문단 XML (상자/표 안쪽 포함)
    def blocks_xml(s, blocks, width, pp_text=None, base=None):
        """width: 사용 가능한 폭. 반환 (xml, [(폭,높이)...])"""
        out = []; paras = []
        for b in blocks:
            if b[0] == 'p':
                runs, w, h = s.inl_runs(b[1], base)
                pp = pp_text if pp_text is not None else s.st.para(align=b[2] if b[2] != 'JUSTIFY' else 'LEFT', line=150)
                if b[2] == 'CENTER': pp = s.st.para(align='CENTER', line=150)
                out.append(s.P(pp, runs)); paras.append((w, h))
            elif b[0] == 'box':
                xml, tw, th = s.box(b[1], width - 200)
                out.append(s.P(s.st.para(align='LEFT', line=130), '<hp:run charPrIDRef="0">%s<hp:t/></hp:run>' % xml))
                paras.append((tw, th))
            elif b[0] == 'table':
                xml, tw, th = s.html_table(b[1], b[2], width - 200)
                out.append(s.P(s.st.para(align='CENTER', line=130), '<hp:run charPrIDRef="0">%s<hp:t/></hp:run>' % xml))
                paras.append((tw, th))
        return ''.join(out), paras

    def box(s, blocks, width):
        cm = (850, 850, 425, 425)
        xml, paras = s.blocks_xml(blocks, width - cm[0] - cm[1])
        cell = {'xml': xml, 'w': width, 'paras': paras, 'full': True, 'valign': 'TOP'}
        return s.table([[cell]], width, border=True, cell_margin=cm)

    def html_table(s, rows, border, width):
        R = []
        cm = (300, 300, 140, 140)
        for row in rows:
            rr = []
            for c in row:
                base = {'bold': True} if c.get('th') else None
                xml, paras = s.blocks_xml(c['blocks'] or [('p', [], c['align'][0])], width, base=base,
                                          pp_text=s.st.para(align=c['align'][0] if c['align'][0] != 'JUSTIFY' else 'CENTER', line=130))
                rr.append({'xml': xml, 'w': max([p[0] for p in paras] or [0]), 'paras': paras, 'colspan': c['colspan'], 'rowspan': c['rowspan'],
                           'bf': (s.st.BF_TH if (c.get('th') and border) else None)})
            R.append(rr)
        return s.table(R, width, border=border, cell_margin=cm)


# ======================= 문항 배치 =======================
def choice_layout(ws, avail):
    """보기 폭 목록 → 한 줄에 몇 개 (5, 3, 2, 1)"""
    pad = 700
    for per in (5, 3, 2):
        if max(ws) + pad <= avail / per: return per
    return 1


def build_section(d, sk, folder):
    st = d.st; meta = sk['meta']
    mid = str(meta.get('grade', '')).startswith('중')
    avail = COL_W - IND
    # 문단 모양
    PP_Q1 = st.para(align='JUSTIFY', intent=-IND, left=0, prev=0, tabs=[(COL_W - 60, 'RIGHT')], keep=True)
    PP_QC = st.para(align='JUSTIFY', left=IND, tabs=[(avail - 60, 'RIGHT')], keep=True)
    PP_OBJ = st.para(align='LEFT', left=IND, line=130, keep=True, prev=200, next=200)
    PP_FIG = st.para(align='CENTER', left=IND, line=100, keep=True, prev=200, next=200)
    PP_GAP = st.para(line=LINE)
    ch_pp = {per: st.para(align='LEFT', left=IND, line=170, keep=True,
                          tabs=[(int(avail * k / per), 'LEFT') for k in range(1, per)]) for per in (5, 3, 2, 1)}
    PP_CH_LAST = {per: st.para(align='LEFT', left=IND, line=170, next=0,
                               tabs=[(int(avail * k / per), 'LEFT') for k in range(1, per)]) for per in (5, 3, 2, 1)}
    body = []

    # ---- 1) 쪽 설정 + 1단 + 꼬리말(쪽 번호)
    secpr = ('<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" outlineShapeIDRef="1" memoShapeIDRef="0" '
             'textVerticalWidthHead="0" masterPageCnt="0"><hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>'
             '<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
             '<hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" '
             'hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
             '<hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>'
             '<hp:pagePr landscape="WIDELY" width="%d" height="%d" gutterType="LEFT_ONLY">'
             '<hp:margin header="%d" footer="%d" gutter="0" left="%d" right="%d" top="%d" bottom="%d"/></hp:pagePr>'
             '<hp:footNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
             '<hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/>'
             '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="EACH_COLUMN" beneathText="0"/></hp:footNotePr>'
             '<hp:endNotePr><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
             '<hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/><hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>'
             '<hp:numbering type="CONTINUOUS" newNum="1"/><hp:placement place="END_OF_DOCUMENT" beneathText="0"/></hp:endNotePr>'
             + ''.join('<hp:pageBorderFill type="%s" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">'
                       '<hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>' % t for t in ('BOTH', 'EVEN', 'ODD'))
             + '</hp:secPr>') % (PAGE_W, PAGE_H, MH, MF, ML, MR, MT, MB)
    cp_foot = st.char(size=9)
    footer = ('<hp:ctrl><hp:footer id="1" applyPageType="BOTH"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="BOTTOM" '
              'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="%d" hasTextRef="0" hasNumRef="0">'
              '<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="%d"><hp:t>- </hp:t>'
              '<hp:ctrl><hp:autoNum num="1" numType="PAGE"><hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar="" supscript="0"/></hp:autoNum></hp:ctrl>'
              '<hp:t> -</hp:t></hp:run></hp:p></hp:subList></hp:footer></hp:ctrl>') % (TEXT_W, MF, st.para(align='CENTER', line=100), cp_foot)
    body.append('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '<hp:run charPrIDRef="0">%s<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl></hp:run>'
                '<hp:run charPrIDRef="0">%s</hp:run>' % (st.para(line=100), secpr, footer))

    # ---- 2) 머리 줄: 제목 · 수학 | 성명 [   ] | 채수학
    title = '%s · %s' % (meta.get('title', ''), '수학')
    cp_t = st.char(size=17, bold=True)
    cp_sub = st.char(size=9, font=F_GOTHIC, color='#444444')
    cp_lab = st.char(size=10, bold=True, font=F_GOTHIC)
    cp_mark = st.char(size=15, bold=True, font=F_GOTHIC)
    pl = st.para(align='LEFT', line=120); pc = st.para(align='CENTER', line=120); pr = st.para(align='RIGHT', line=120)
    sub = ' · '.join(x for x in [meta.get('school', ''), meta.get('grade', '') + ' ' + meta.get('subject', ''), meta.get('range', '')] if x.strip())
    c1 = d.P(pl, '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp_t, X(title)))
    if sub: c1 += d.P(pl, '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (cp_sub, X(sub)))
    W2, W3, W4 = 4500, 13000, 9000
    W1 = TEXT_W - W2 - W3 - W4
    cells = [[{'xml': c1, 'w': W1, 'bf': st.BF_HEAD, 'valign': 'BOTTOM'},
              {'xml': d.P(pc, '<hp:run charPrIDRef="%d"><hp:t>성명</hp:t></hp:run>' % cp_lab), 'w': W2, 'bf': st.BF_NAME},
              {'xml': d.P(pc, ''), 'w': W3, 'bf': st.BF_NAME},
              {'xml': d.P(pr, '<hp:run charPrIDRef="%d"><hp:t>채수학</hp:t></hp:run>' % cp_mark), 'w': W4, 'bf': st.BF_HEAD, 'valign': 'BOTTOM'}]]
    # 고정 폭 표
    need_tot = W1 + W2 + W3 + W4
    for c, w in zip(cells[0], (W1, W2, W3, W4)): c['w'] = w - 1220
    tbl, _, _ = d.table(cells, need_tot, cell_margin=(510, 510, 200, 200), heights=[3400])
    body.append('</hp:p>')
    body.append(d.P(st.para(align='LEFT', line=100, next=600), '<hp:run charPrIDRef="0">%s<hp:t/></hp:run>' % tbl))

    # ---- 3) 2단 시작 (단 구분선)
    colpr = ('<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="2" sameSz="1" sameGap="%d">'
             '<hp:colLine type="SOLID" width="0.12 mm" color="#000000"/></hp:colPr></hp:ctrl>' % GAP)
    first = True
    for q in sk['Q']:
        blocks = parse_q(q.get('q', ''))
        is_sub = q.get('type') == '서'
        pt = q.get('pt', '')
        try: pts = ('%g' if mid else '%.2f') % float(pt)
        except Exception: pts = str(pt)
        head = [('t', '%s. ' % q['n'], (True, False, False, False))]
        if is_sub and '서술형' not in q.get('q', ''):
            head.append(('t', '[서술형] ', (True, False, False, False)))
        if not blocks or blocks[0][0] != 'p': blocks.insert(0, ('p', [], 'JUSTIFY'))
        blocks[0] = ('p', head + list(blocks[0][1]), blocks[0][2])
        last_p = max(i for i, b in enumerate(blocks) if b[0] == 'p')
        tail = [('tab', 1, 1000), ('t', '[%s점]' % pts, (False, False, False, False))]
        b = blocks[last_p]; blocks[last_p] = ('p', list(b[1]) + tail, b[2])
        qx = []
        for i, b in enumerate(blocks):
            if b[0] == 'p':
                runs, _, _ = d.inl_runs(b[1])
                pp = PP_Q1 if i == 0 else PP_QC
                if b[2] == 'CENTER' and i: pp = st.para(align='CENTER', left=IND, keep=True)
                qx.append([pp, runs])
            elif b[0] == 'box':
                xml, _, _ = d.box(b[1], avail - 100)
                qx.append([PP_OBJ, '<hp:run charPrIDRef="0">%s<hp:t/></hp:run>' % xml])
            elif b[0] == 'table':
                xml, _, _ = d.html_table(b[1], b[2], avail - 100)
                qx.append([st.para(align='CENTER', left=IND, line=130, keep=True, prev=200, next=200),
                           '<hp:run charPrIDRef="0">%s<hp:t/></hp:run>' % xml])
        # 그림
        imgs = q.get('imgs') or []
        if imgs:
            wmm = float(q.get('imgW') or 55)
            ws = [wmm * MM] * len(imgs)
            tot = sum(ws) + 600 * (len(imgs) - 1)
            if tot > avail - 200:
                f = (avail - 200) / tot; ws = [w * f for w in ws]
            runs = []
            for k, im in enumerate(imgs):
                xml, _, _ = d.pic(im, ws[k])
                runs.append('<hp:run charPrIDRef="0">%s%s</hp:run>' % (xml, '<hp:t>  </hp:t>' if k < len(imgs) - 1 else '<hp:t/>'))
            qx.append([PP_FIG, ''.join(runs)])
        # 보기 ①~⑤
        chs = q.get('ch') or []
        if chs and not is_sub:
            items = []
            for k, c in enumerate(chs):
                bl = parse_q(c)
                inl = []
                for bb in bl:
                    if bb[0] == 'p':
                        if inl: inl.append(('t', ' ', (False,) * 4))
                        inl += bb[1]
                inl = [('t', CIRC[k] + ' ' if k < 5 else '(%d) ' % (k + 1), (False,) * 4)] + inl
                runs, w, _ = d.inl_runs(inl)
                items.append((runs, w))
            per = choice_layout([w for _, w in items], avail)
            rows = [items[i:i + per] for i in range(0, len(items), per)]
            for ri, row in enumerate(rows):
                tabrun = '<hp:run charPrIDRef="0"><hp:t><hp:tab width="1000" leader="0" type="0"/></hp:t></hp:run>'
                runs = tabrun.join(r for r, _ in row)
                qx.append([ch_pp[per] if ri < len(rows) - 1 else PP_CH_LAST[per], runs])
        if first:
            qx[0][1] = '<hp:run charPrIDRef="0">%s</hp:run>' % colpr + qx[0][1]
            first = False
        for pp, runs in qx: body.append(d.P(pp, runs))
        # 문항 사이 / 서술형 답 쓰는 칸
        n_blank = 10 if is_sub else 2
        for _ in range(n_blank): body.append(d.P(PP_GAP, ''))
    return XMLDECL + '<hs:sec %s>' % NS + ''.join(body) + '</hs:sec>'


# ======================= 패키지 =======================
def package(d, sk, section_xml, out):
    meta = sk['meta']
    header_xml = d.st.xml()
    items = ''.join('<opf:item id="%s" href="BinData/%s.%s" media-type="image/%s" isEmbeded="1"/>'
                    % (X(i), X(i), e, 'jpg' if e in ('jpg', 'jpeg') else e) for i, (p, e) in sorted(d.bins.items()))
    hpf = (XMLDECL + '<opf:package %s version="" unique-identifier="" id=""><opf:metadata><opf:title>%s</opf:title><opf:language>ko</opf:language>'
           '<opf:meta name="creator" content="text">채수학</opf:meta><opf:meta name="subject" content="text">%s</opf:meta>'
           '<opf:meta name="description" content="text"/><opf:meta name="keyword" content="text"/></opf:metadata>'
           '<opf:manifest><opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
           '<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>'
           '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>%s</opf:manifest>'
           '<opf:spine><opf:itemref idref="header" linear="yes"/><opf:itemref idref="section0" linear="yes"/></opf:spine></opf:package>'
           % (NS, X(meta.get('title', '')), X(meta.get('subject', '')), items))
    container = (XMLDECL + '<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf">'
                 '<ocf:rootfiles><ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>'
                 '<ocf:rootfile full-path="Preview/PrvText.txt" media-type="text/plain"/>'
                 '<ocf:rootfile full-path="META-INF/container.rdf" media-type="application/rdf+xml"/></ocf:rootfiles></ocf:container>')
    rdf = (XMLDECL + '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
           '<rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" rdf:resource="Contents/header.xml"/></rdf:Description>'
           '<rdf:Description rdf:about="Contents/header.xml"><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#HeaderFile"/></rdf:Description>'
           '<rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" rdf:resource="Contents/section0.xml"/></rdf:Description>'
           '<rdf:Description rdf:about="Contents/section0.xml"><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#SectionFile"/></rdf:Description>'
           '<rdf:Description rdf:about=""><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#Document"/></rdf:Description></rdf:RDF>')
    manifest = XMLDECL + '<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"/>'
    version = (XMLDECL + '<hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" tagetApplication="WORDPROCESSOR" major="5" minor="1" '
               'micro="0" buildNumber="1" os="1" xmlVersion="1.2" application="Hancom Office Hangul" appVersion="11, 0, 0, 2129 WIN32LEWindows_8"/>')
    settings = (XMLDECL + '<ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
                'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"><ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/></ha:HWPApplicationSetting>')
    prv = '%s\n%s · %d문항\n' % (meta.get('title', ''), meta.get('range', ''), len(sk['Q']))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if os.path.exists(out): os.remove(out)
    z = zipfile.ZipFile(out, 'w')
    z.writestr(zipfile.ZipInfo('mimetype'), 'application/hwp+zip', compress_type=zipfile.ZIP_STORED)
    D = zipfile.ZIP_DEFLATED
    z.writestr('version.xml', version, compress_type=D)
    z.writestr('Contents/header.xml', header_xml, compress_type=D)
    z.writestr('Contents/section0.xml', section_xml, compress_type=D)
    z.writestr('settings.xml', settings, compress_type=D)
    for i, (p, e) in sorted(d.bins.items()):
        z.write(p, 'BinData/%s.%s' % (i, e), compress_type=D)
    z.writestr('Contents/content.hpf', hpf, compress_type=D)
    z.writestr('META-INF/container.xml', container, compress_type=D)
    z.writestr('META-INF/container.rdf', rdf, compress_type=D)
    z.writestr('META-INF/manifest.xml', manifest, compress_type=D)
    z.writestr('Preview/PrvText.txt', prv, compress_type=D)
    z.close()


# ======================= 검사 =======================
def norm_tex(s):
    s = re.sub(r'\\(dfrac|tfrac|cfrac)', r'\\frac', s)
    s = re.sub(r'\\(begin|end)\{cases\}|\bcases\b|&|\\\\', '', s)
    rep = [(r'\lt', '<'), (r'\gt', '>'), (r'\leq', r'\le'), (r'\geq', r'\ge'), (r'\neq', r'\ne'), (r'\varnothing', r'\emptyset'),
           (r'\rightarrow', r'\to'), ('\\{', '{'), ('\\}', '}'), (r'\lbrace', '{'), (r'\rbrace', '}'), (r'\mid', '|'),
           (r'^\circ', r'\circ'), (r'\infty', 'inf'), (r'\Rightarrow', '=>'), ('\\ ', '')]
    for a, b in rep: s = s.replace(a, b)
    s = re.sub(r'\\(left|right|middle|big|Big|bigl|bigr|displaystyle|limits|mathrm|operatorname|text|textrm|mathit|quad|qquad|boxed)\b', '', s)
    s = re.sub(r'\\[,;:!]', '', s)
    s = re.sub(r'[\s{}~`]', '', s)
    s = s.replace('^', '').replace('_', '')
    for a, b in CANON: s = s.replace(a, b)
    return s


# heq.py 가 모르는 한글 토큰 ↔ LaTeX 를 같은 표기로 (느슨한 비교용)
CANON = [('\\overset\\frown', '⌒'), ('arch', '⌒'), ('\\overleftrightarrow', '↔'), ('dyad', '↔'), ('\\Omega', 'Ω'), ('OMEGA', 'Ω'),
         ('\\Leftrightarrow', '⇔'), ('LRARROW', '⇔'), ('=>', '⇒'), ('RARROW', '⇒'), ('\\langle', '〈'), ('\\rangle', '〉'),
         ('\\llbracket', '⟦'), ('\\rrbracket', '⟧'), ('\\square', '□'), ('\\notin', '∉'), ('notin', '∉'), ('\\equiv', '≡'), ('equiv', '≡'),
         ('\\varnothing', '∅'), ('\\emptyset', '∅'), ('EMPTYSET', '∅'), ('\\perp', '⊥'), ('bot', '⊥'), ('\\overline', 'bar'),
         ('\\overrightarrow', 'vec'), ('root', '\\sqrt'), ('of', ''), ('lbrace', '{'), ('rbrace', '}'), ('\\dot', 'dot'),
         ('\\boxed', 'box'), ('\\fbox', 'box'), ('\\square', 'box'), ('\\to', '->'), ('\\Delta', 'Δ'), ('DELTA', 'Δ'),
         ('\\Pi', 'Π'), ('PI', 'Π'), ('\\lim', 'lim'), ('\\log', 'log'), ('\\sin', 'sin'), ('\\cos', 'cos'), ('\\tan', 'tan'),
         ('\\ln', 'ln'), ('\\sum', 'sum'), ('\\star', 'star'), ('\\parallel', 'parallel'), ('\\cot', 'cot'), ('\\sec', 'sec'),
         ('\\csc', 'csc'), ('\\gamma', 'gamma'), ('\\vdots', 'vdots'), ('\\widehat', 'hat'), ('\\exists', 'exist'),
         ('\\cong', 'cong'), ('\\simeq', 'simeq'), ('\\subseteq', 'subseteq'), ('\\frown', '⌒')]


def validate(out, d):
    errs = []; info = []
    import xml.etree.ElementTree as ET
    z = zipfile.ZipFile(out)
    infos = z.infolist()
    if infos[0].filename != 'mimetype': errs.append('mimetype 이 첫 항목이 아님')
    if infos[0].compress_type != zipfile.ZIP_STORED: errs.append('mimetype 압축됨')
    if z.read('mimetype') != b'application/hwp+zip': errs.append('mimetype 내용 틀림')
    if infos[0].extra: errs.append('mimetype extra field 있음')
    names = z.namelist()
    for need in ['META-INF/container.xml', 'META-INF/manifest.xml', 'Contents/content.hpf', 'Contents/header.xml',
                 'Contents/section0.xml', 'settings.xml', 'version.xml']:
        if need not in names: errs.append('없음: ' + need)
    trees = {}
    for n in names:
        if n.endswith(('.xml', '.hpf', '.rdf')):
            try: trees[n] = ET.fromstring(z.read(n))
            except ET.ParseError as e: errs.append('XML 오류 %s: %s' % (n, e))
    HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'; HC = '{http://www.hancom.co.kr/hwpml/2011/core}'
    HH = '{http://www.hancom.co.kr/hwpml/2011/head}'; OPF = '{http://www.idpf.org/2007/opf/}'
    sec = trees.get('Contents/section0.xml'); hd = trees.get('Contents/header.xml'); hpf = trees.get('Contents/content.hpf')
    if sec is not None and hd is not None and hpf is not None:
        man = {it.get('id'): it.get('href') for it in hpf.iter(OPF + 'item')}
        refs = [e.get('binaryItemIDRef') for e in sec.iter(HC + 'img')]
        for r in refs:
            if r not in man: errs.append('content.hpf 에 없는 그림 %s' % r)
            elif man[r] not in names: errs.append('BinData 에 없는 그림 %s' % man[r])
        for i, h in man.items():
            if h.startswith('BinData/') and i not in refs: info.append('사용 안 한 BinData %s' % h)
        ids = {t: {e.get('id') for e in hd.iter(HH + t)} for t in ('charPr', 'paraPr', 'borderFill', 'tabPr', 'style')}
        for e in sec.iter():
            for a, t in (('charPrIDRef', 'charPr'), ('paraPrIDRef', 'paraPr'), ('borderFillIDRef', 'borderFill'), ('styleIDRef', 'style')):
                v = e.get(a)
                if v is not None and v not in ids[t]: errs.append('%s=%s 정의 없음' % (a, v)); break
        for e in hd.iter():
            for a, t in (('tabPrIDRef', 'tabPr'), ('borderFillIDRef', 'borderFill'), ('paraPrIDRef', 'paraPr'), ('charPrIDRef', 'charPr')):
                v = e.get(a)
                if v is not None and v not in ids[t] and v != '4294967295': errs.append('header %s=%s 정의 없음' % (a, v))
        for tag in ('borderFills', 'charProperties', 'paraProperties', 'tabProperties', 'styles'):
            el = hd.find('.//' + HH + tag)
            if el is not None and int(el.get('itemCnt')) != len(list(el)): errs.append('%s itemCnt 틀림' % tag)
        for tbl in sec.iter(HP + 'tbl'):
            rc, cc = int(tbl.get('rowCnt')), int(tbl.get('colCnt'))
            trs = tbl.findall(HP + 'tr')
            if len(trs) != rc: errs.append('표 rowCnt 불일치')
        neq = len(list(sec.iter(HP + 'equation'))); npic = len(list(sec.iter(HP + 'pic'))); ntbl = len(list(sec.iter(HP + 'tbl')))
        info.append('수식 %d개 · 그림 %d개 · 표 %d개 · 문단 %d개' % (neq, npic, ntbl, len(list(sec.iter(HP + 'p')))))
        # 스크립트 안 중괄호 짝
        for e in sec.iter(HP + 'script'):
            t = e.text or ''
            dep = 0; bad = False
            for ch in t:
                dep += (ch == '{') - (ch == '}')
                if dep < 0: bad = True
            if dep != 0 or bad: errs.append('수식 중괄호 짝 안 맞음: %s' % t[:80])
    # 수식 왕복 검사 (heq.py: 한글 수식 → LaTeX)
    warns = [(l, sc, w) for l, sc, w in d.eqs if w]
    for l, sc, w in warns[:30]: info.append('수식 경고 %s: $%s$ -> %s' % (','.join(sorted(set(w))), l[:60], sc[:80]))
    if os.path.exists(HEQ):
        import importlib.util
        spec = importlib.util.spec_from_file_location('heq_rt', HEQ); heq = importlib.util.module_from_spec(spec); spec.loader.exec_module(heq)
        bad = []; tot = 0
        for l, sc, w in d.eqs:
            tot += 1
            try: back = heq.conv(sc)
            except Exception as e: back = '<<%s>>' % e
            a, b = norm_tex(l), norm_tex(back)
            r = difflib.SequenceMatcher(None, a, b).ratio() if (a or b) else 1.
            if r < .8: bad.append((r, l, sc, back))
        info.append('수식 왕복(heq.py) %d/%d 일치(유사도≥0.8)' % (tot - len(bad), tot))
        for r, l, sc, back in sorted(bad)[:25]:
            info.append('  왕복 차이 %.2f  $%s$\n      한글: %s\n      역변환: %s' % (r, l[:90], sc[:110], back[:110]))
    else:
        info.append('heq.py 없음 → 왕복 검사 생략 (%s)' % HEQ)
    return errs, info


def main():
    if len(sys.argv) < 3:
        print(__doc__ or 'python3 make_hwpx.py <test folder> <out.hwpx>'); sys.exit(2)
    folder, out = os.path.abspath(sys.argv[1]), sys.argv[2]
    sk = json.load(open(os.path.join(folder, 'skeleton.json'), encoding='utf-8'))
    d = Doc(folder)
    section = build_section(d, sk, folder)
    package(d, sk, section, out)
    errs, info = validate(out, d)
    for i in info: print(i)
    if errs:
        print('검사 실패 %d건:' % len(errs))
        for e in errs[:40]: print('  ', e)
        sys.exit(1)
    print('OK', os.path.abspath(out))


if __name__ == '__main__':
    main()
