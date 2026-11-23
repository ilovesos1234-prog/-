# -*- coding: utf-8 -*-
"""Reusable HWPX (OWPML 2011) builder — verified to open in the user's Hangul.
Supports editable text paragraphs and embedded raster images (반반 방식)."""
import zipfile, os

MM = 283.465  # HWPUNIT per mm

# ---- 종이·글자 크기 (2026-09-19 B4 판 추가) ----
PAPER = "A4"
PAPERS = {   # 종이별 크기와 여백 (한글 단위 = 1/100 pt)
    "A4": dict(w=59528, h=84188, lr=4252, tb=2268, hd=1134, ft=3968),   # 210 x 297
    "B4": dict(w=72850, h=103182, lr=5102, tb=2268, hd=1134, ft=3968),  # 257 x 364
}
LINESP = {"A4": 200, "B4": 165}          # 줄 간격 %
PIND = {"A4": (1700, 1900), "B4": (2170, 2430)}   # 본문 문단 좌·우 여백
EQBASE = {"A4": 1000, "B4": 1100}        # 수식 기준 크기
# 글자 크기표 (14번이 본문)
CPS = {
    "A4": {0: 1000, 1: 1050, 2: 2600, 3: 1000, 4: 1050, 5: 2000, 6: 1100, 7: 900,
           8: 2000, 9: 1000, 10: 1100, 11: 950, 12: 1350, 13: 1000, 14: 900, 15: 700, 16: 100},
    # B4 = 학교 원본에 맞춤: 본문 11.5pt, 수식 11pt, 줄간격 165%
    "B4": {0: 1100, 1: 1350, 2: 3300, 3: 1300, 4: 1350, 5: 2550, 6: 1400, 7: 1150,
           8: 2550, 9: 1300, 10: 1400, 11: 1200, 12: 1750, 13: 1300, 14: 1150, 15: 900, 16: 100},
}


def paper():
    return PAPERS[PAPER]


def body_w():
    q = paper(); return q["w"] - 2 * q["lr"]


def body_h():
    q = paper(); return q["h"] - 2 * q["tb"] - q["hd"] - q["ft"]


def cps():
    return CPS[PAPER]


def eqbase():
    return EQBASE[PAPER]


def pagepr():
    q = paper()
    return ('<hp:pagePr landscape="WIDELY" width="%d" height="%d" gutterType="LEFT_ONLY">'
            '<hp:margin header="%d" footer="%d" gutter="0" left="%d" right="%d" top="%d" bottom="%d"/>'
            '</hp:pagePr>') % (q["w"], q["h"], q["hd"], q["ft"], q["lr"], q["lr"], q["tb"], q["tb"])


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

NS = ('xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
      'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
      'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
      'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
      'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
      'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
      'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
      'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
      'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
      'xmlns:dc="http://purl.org/dc/elements/1.1/" '
      'xmlns:opf="http://www.idpf.org/2007/opf/" '
      'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
      'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" '
      'xmlns:epub="http://www.idpf.org/2007/ops" '
      'xmlns:config="http://www.hancom.co.kr/hwpml/2011/configuration"')

SECPR = (
'<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" '
'tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">'
'<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0" strtnum="0"/>'
'<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
'<hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" '
'fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>'
'<hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>'
'{PAGEPR}'
'<hp:footNotePr>'
'<hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
'<hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>'
'<hp:noteSpacing betweenNotes="850" belowLine="567" aboveLine="567"/>'
'<hp:numbering type="CONTINUOUS" newNum="1"/>'
'<hp:placement place="EACH_COLUMN" beneathText="0"/>'
'</hp:footNotePr>'
'<hp:endNotePr>'
'<hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>'
'<hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>'
'<hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>'
'<hp:numbering type="CONTINUOUS" newNum="1"/>'
'<hp:placement place="END_OF_DOCUMENT" beneathText="0"/>'
'</hp:endNotePr>'
'<hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
'<hp:pageBorderFill type="EVEN" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
'<hp:pageBorderFill type="ODD" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER"><hp:offset left="1417" right="1417" top="1417" bottom="1417"/></hp:pageBorderFill>'
'</hp:secPr>'
)

HEAD_NS = NS

# 2026-09-11 확정 공용틀의 학교급 색 (main, dark, 연바탕, 연선, 아주 연한 바탕, 꼬리말 글자)
# 능인중 중2 편집가능본(공용틀 적용본)의 색 자리를 그대로 따른다.
PALETTES = {
    "초": ("#2F6BA8", "#255789", "#EAF1F8", "#C3D7E9", "#F9FBFD", "#1E4870"),
    "중": ("#2E6B4F", "#245641", "#E8F0EC", "#BFD6C9", "#FAFCFB", "#1F4A37"),
    "고": ("#7A4A2A", "#5F3920", "#F3ECE4", "#DCC7B2", "#FCFAF7", "#4E2F1A"),
}
LEVEL = "중"          # 만드는 쪽(g3lib)에서 학년 글자로 바꿔 준다


def build_header():
    MAIN, DARK, LIGHT, LINE, PALE, FOOT = PALETTES.get(LEVEL, PALETTES["중"])
    LANGS = ["HANGUL", "LATIN", "HANJA", "JAPANESE", "OTHER", "SYMBOL", "USER"]
    def fontface(lang):
        # 수식 제외 모든 글자 = 한컴 윤고딕 740 (id0=id1 동일)
        f = ('<hh:font id="%d" face="한컴 윤고딕 740" type="TTF" isEmbedded="0">'
             '<hh:typeInfo familyType="FCAT_GOTHIC" weight="0" proportion="0" contrast="0" '
             'strokeVariation="1" armStyle="0" letterform="0" midline="0" xHeight="0"/></hh:font>')
        return ('<hh:fontface lang="%s" fontCnt="2">%s%s</hh:fontface>') % (lang, f % 0, f % 1)
    fontfaces = '<hh:fontfaces itemCnt="7">%s</hh:fontfaces>' % "".join(fontface(l) for l in LANGS)

    def bside(t):
        return 'type="%s" width="0.12 mm" color="#000000"' % t
    def bf(idn, borders, fill=None):
        bt = "SOLID" if borders else "NONE"
        fx = ('<hc:fillBrush><hc:winBrush faceColor="%s" hatchColor="#999999" alpha="0"/></hc:fillBrush>' % fill) if fill else ""
        return ('<hh:borderFill id="%d" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
                '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
                '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
                '<hh:leftBorder %s/><hh:rightBorder %s/><hh:topBorder %s/><hh:bottomBorder %s/>'
                '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>%s</hh:borderFill>'
                ) % (idn, bside(bt), bside(bt), bside(bt), bside(bt), fx)
    # id 6: only a right border (the 2-column center divider)
    bf6 = ('<hh:borderFill id="6" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
           '<hh:slash type="NONE" Crooked="0" isCounter="0"/>'
           '<hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
           '<hh:leftBorder type="NONE" width="0.1 mm" color="#000000"/>'
           '<hh:rightBorder type="SOLID" width="0.12 mm" color="#000000"/>'
           '<hh:topBorder type="NONE" width="0.1 mm" color="#000000"/>'
           '<hh:bottomBorder type="NONE" width="0.1 mm" color="#000000"/>'
           '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/></hh:borderFill>')
    # id 7: header box — light navy border all sides + soft navy fill
    def bf_box(idn, bcol, fill, kind="SOLID", wd="0.4 mm"):
        return ('<hh:borderFill id="%d" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">'
                '<hh:slash type="NONE" Crooked="0" isCounter="0"/><hh:backSlash type="NONE" Crooked="0" isCounter="0"/>'
                '<hh:leftBorder type="%s" width="%s" color="%s"/>'
                '<hh:rightBorder type="%s" width="%s" color="%s"/>'
                '<hh:topBorder type="%s" width="%s" color="%s"/>'
                '<hh:bottomBorder type="%s" width="%s" color="%s"/>'
                '<hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>'
                '<hc:fillBrush><hc:winBrush faceColor="%s" hatchColor="#999999" alpha="0"/></hc:fillBrush>'
                '</hh:borderFill>') % ((idn,) + (kind, wd, bcol) * 4 + (fill,))
    # 공용틀: 머리 상자는 테두리·채움 없음, 문항 번호는 흰 바탕·테두리 없음
    bf7 = bf_box(7, LINE, "#FFFFFF", kind="NONE")    # header box
    bf8 = bf_box(8, DARK, "#FFFFFF", kind="NONE")    # number (흰 바탕)
    # id 9: dashed border + near-white fill (intro / pill boxes)
    bf9 = bf_box(9, LINE, PALE, kind="DASH", wd="0.2 mm")
    # id 10: pill — solid light border + white fill, rounded look approximated
    bf10 = bf_box(10, LINE, "#FFFFFF")
    # id 11: score pill — cream fill
    bf11 = bf_box(11, "#EAD9A6", "#FBF3DD")
    # id 12: 유형 태그 알약 — 연파랑 채움 + 연한 테두리
    bf12 = bf_box(12, LINE, LIGHT)
    # id 13: 회색 테두리 상자(안내용) — 흰 채움
    bf13 = bf_box(13, "#AAAAAA", "#FFFFFF")
    borderfills = ('<hh:borderFills itemCnt="13">' + bf(1, False) + bf(2, False) + bf(3, True)
                   + bf(4, True, MAIN) + bf(5, True, LIGHT) + bf6 + bf7 + bf8 + bf9 + bf10 + bf11 + bf12 + bf13
                   + '</hh:borderFills>')

    def cp(idn, height, bold=False, color="#000000", font=0):
        b = "<hh:bold/>" if bold else ""
        fr = ('<hh:fontRef hangul="%d" latin="%d" hanja="%d" japanese="%d" other="%d" symbol="%d" user="%d"/>'
              % (font, font, font, font, font, font, font))
        return ('<hh:charPr id="%d" height="%d" textColor="%s" shadeColor="none" useFontSpace="0" '
                'useKerning="0" symMark="NONE" borderFillIDRef="2">'
                '%s'
                '<hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
                '<hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>'
                '<hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>'
                '<hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>%s</hh:charPr>'
                ) % (idn, height, color, fr, b)
    S = cps()
    charprops = ('<hh:charProperties itemCnt="17">'
                 + cp(0, S[0]) + cp(1, S[1], True) + cp(2, S[2], True) + cp(3, S[3], True)
                 + cp(4, S[4]) + cp(5, S[5], True) + cp(6, S[6], True) + cp(7, S[7], font=1)
                 + cp(8, S[8], True, DARK, font=1)   # 제목 20pt 네이비 볼드(고딕)
                 + cp(9, S[9], False, DARK, font=1)  # info navy (고딕)
                 + cp(10, S[10], True, "#1A1A1A", font=1)   # 문항 번호 검정 볼드 (고딕)
                 + cp(11, S[11], True, FOOT, font=1)    # footer brand (고딕)
                 + cp(12, S[12], True, DARK, font=1)   # compact title navy bold (고딕)
                 + cp(13, S[13], True, "#8B95A1", font=1)   # 유형 라벨(회색 고딕 볼드)
                 + cp(14, S[14])                             # 문제 본문 9pt(명조, 수식보다 1pt 작게)
                 + cp(15, S[15], True, DARK, font=1)    # 유형 태그 7pt(고딕 네이비, 알약 배경 위)
                 + cp(16, S[16])                        # 자리 맞추기용 아주 작은 글자(1pt)
                 + '</hh:charProperties>')

    tabprops = '<hh:tabProperties itemCnt="1"><hh:tabPr id="0" autoTabLeft="0" autoTabRight="0"/></hh:tabProperties>'
    heads = "".join('<hh:paraHead start="1" level="%d" align="LEFT" useInstWidth="1" autoIndent="1" '
                    'widthAdjust="0" textOffsetType="PERCENT" textOffset="50" numFormat="DIGIT" '
                    'charPrIDRef="4294967295" checkable="0">^%d.</hh:paraHead>' % (l, l) for l in range(1, 8))
    numberings = '<hh:numberings itemCnt="1"><hh:numbering id="1" start="0">%s</hh:numbering></hh:numberings>' % heads

    def pp(idn, align, left=0, right=0):
        return ('<hh:paraPr id="%d" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="0" '
                'suppressLineNumbers="0" checked="0">'
                '<hh:align horizontal="%s" vertical="BASELINE"/>'
                '<hh:heading type="NONE" idRef="0" level="0"/>'
                '<hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="BREAK_WORD" widowOrphan="0" '
                'keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>'
                '<hh:autoSpacing eAsianEng="0" eAsianNum="0"/>'
                '<hh:margin><hc:intent value="0" unit="HWPUNIT"/><hc:left value="%d" unit="HWPUNIT"/>'
                '<hc:right value="%d" unit="HWPUNIT"/><hc:prev value="0" unit="HWPUNIT"/>'
                '<hc:next value="0" unit="HWPUNIT"/></hh:margin>'
                '<hh:lineSpacing type="PERCENT" value="LINESP" unit="HWPUNIT"/>'
                '<hh:border borderFillIDRef="2" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" '
                'connect="0" ignoreMargin="0"/></hh:paraPr>'
                ).replace("LINESP", str(LINESP[PAPER])) % (idn, align, left, right)
    paraprops = ('<hh:paraProperties itemCnt="7">' + pp(0, "CENTER") + pp(1, "CENTER") + pp(2, "CENTER")
                 + pp(3, "RIGHT") + pp(4, "LEFT") + pp(5, "LEFT", PIND[PAPER][0])
                 + pp(6, "LEFT", PIND[PAPER][0], PIND[PAPER][1]) + '</hh:paraProperties>')
    styles = ('<hh:styles itemCnt="1"><hh:style id="0" type="PARA" name="바탕글" engName="Normal" '
              'paraPrIDRef="0" charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0"/></hh:styles>')

    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<hh:head %s version="1.31" secCnt="1">'
            '<hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>'
            '<hh:refList>' + fontfaces + borderfills + charprops + tabprops + numberings + paraprops + styles +
            '</hh:refList>'
            '<hh:compatibleDocument targetProgram="HWP201X"><hh:layoutCompatibility/></hh:compatibleDocument>'
            '<hh:docOption><hh:linkinfo path="" pageInherit="0" footnoteInherit="0"/></hh:docOption>'
            '</hh:head>') % HEAD_NS


class Doc:
    def __init__(self, title="문서"):
        self.title = title
        self.body = []
        self.images = []   # list of (item_id, arcname, media_type, bytes)
        self.img_px = {}   # item_id -> (w_px, h_px) natural pixel size
        self._pid = 0
        self._z = 0
        self.first = True
        self.col_count = 1
        self.col_gap = 2834   # ~10mm gap between columns
        self.header_xml_str = ""
        self.footer_xml_str = ""
        self.cell_top_margin = 283   # HWPUNIT top padding inside table cells
        self.cell_bottom_margin = 283  # HWPUNIT bottom padding inside table cells
        self.cell_side_margin = 510  # HWPUNIT left/right padding inside table cells
        self.divider_gap = 0         # extra padding around the center divider
    def pid(self):
        self._pid += 1
        return self._pid
    def zorder(self):
        self._z += 1
        return self._z

    def _first_run_extra(self):
        # secPr + colPr goes into the very first run of the document
        if self.first:
            self.first = False
            if self.col_count > 1:
                cols = "".join('<hp:col width="0" gap="%d"/>' % self.col_gap for _ in range(self.col_count))
                colpr = ('<hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="%d" sameSz="1" sameGap="%d">'
                         '%s</hp:colPr>') % (self.col_count, self.col_gap, cols)
            else:
                colpr = ('<hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/>')
            out = SECPR.replace('{PAGEPR}', pagepr()) + '<hp:ctrl>' + colpr + '</hp:ctrl>'
            if self.header_xml_str:
                out += '<hp:ctrl>' + self.header_xml_str + '</hp:ctrl>'
            if self.footer_xml_str:
                out += '<hp:ctrl>' + self.footer_xml_str + '</hp:ctrl>'
            return out
        return ""

    def para(self, text, charpr=0, parapr=4, colbreak=False, pagebreak=False):
        extra = self._first_run_extra()
        t = ("<hp:t>%s</hp:t>" % esc(text)) if text != "" else "<hp:t></hp:t>"
        run_extra = ('<hp:run charPrIDRef="%d">%s</hp:run>' % (charpr, extra)) if extra else ""
        cb = "1" if colbreak else "0"
        pb = "1" if pagebreak else "0"
        self.body.append('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="%s" columnBreak="%s" merged="0">'
                         '%s<hp:run charPrIDRef="%d">%s</hp:run></hp:p>'
                         % (self.pid(), parapr, pb, cb, run_extra, charpr, t))

    def spacer(self):
        self.para("", 0, 4)

    def add_image(self, arcname, data, media_type, w_px, h_px):
        item_id = "image%d" % (len(self.images) + 1)
        self.images.append((item_id, arcname, media_type, data))
        self.img_px[item_id] = (int(w_px), int(h_px))
        return item_id

    def _pic_xml(self, item_id, w, h):
        # w,h = display size in HWPUNIT.  Natural size = px * 75 (7200/96), matching Hangul.
        z = self.zorder()
        wpx, hpx = self.img_px.get(item_id, (int(w/75), int(h/75)))
        nw, nh = wpx * 75, hpx * 75
        return ('<hp:pic id="%d" zOrder="%d" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" '
                'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="%d" reverse="0">'
                '<hp:offset x="0" y="0"/>'
                '<hp:orgSz width="%d" height="%d"/>'
                '<hp:curSz width="0" height="0"/>'
                '<hp:flip horizontal="0" vertical="0"/>'
                '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/>'
                '<hp:renderingInfo>'
                '<hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
                '<hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
                '<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
                '</hp:renderingInfo>'
                '<hc:img binaryItemIDRef="%s" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
                '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>'
                '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/>'
                '<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
                '<hp:imgDim dimwidth="%d" dimheight="%d"/>'
                '<hp:effects/>'
                '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
                '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
                'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="CENTER" vertOffset="0" horzOffset="0"/>'
                '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
                '</hp:pic>') % (self.pid(), z, self.pid(), w, h, w//2, h//2, item_id,
                                w, w, h, h, nw, nh, nw, nh, w, h)

    def image_para(self, pics, parapr=1):
        # pics: list of (item_id, w_hwp, h_hwp) -> one centered paragraph containing them
        extra = self._first_run_extra()
        runs = ""
        if extra:
            runs += '<hp:run charPrIDRef="0">%s</hp:run>' % extra
        inner = "".join(self._pic_xml(iid, w, h) for (iid, w, h) in pics)
        runs += '<hp:run charPrIDRef="0">%s</hp:run>' % inner
        self.body.append('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         '%s</hp:p>' % (self.pid(), parapr, runs))

    # ---------- XML-returning helpers (no first-run side effects) ----------
    def _p_xml(self, text, charpr=0, parapr=4):
        t = ("<hp:t>%s</hp:t>" % esc(text)) if text != "" else "<hp:t></hp:t>"
        return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '<hp:run charPrIDRef="%d">%s</hp:run></hp:p>') % (self.pid(), parapr, charpr, t)

    def _pic_p_xml(self, pics, parapr=1):
        inner = "".join(self._pic_xml(iid, w, h) for (iid, w, h) in pics)
        return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '<hp:run charPrIDRef="0">%s</hp:run></hp:p>') % (self.pid(), parapr, inner)

    def eqn_xml(self, script, w=3000, h=1000, charpr=0, bl=85):
        # 한글 수식개체(hp:equation) — 인라인, 편집 가능. script = 한글 수식 언어.
        z = self.zorder()
        return ('<hp:equation id="%d" zOrder="%d" numberingType="EQUATION" textWrap="SQUARE" textFlow="BOTH_SIDES" '
                'lock="0" dropcapstyle="None" version="Equation Version 60" baseLine="%d" textColor="#000000" '
                'baseUnit="%d" lineMode="CHAR" font="HYhwpEQ">'
                '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
                '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
                'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="CENTER" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
                '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
                '<hp:script>%s</hp:script>'
                '</hp:equation>') % (self.pid(), z, bl, eqbase(), w, h, esc(script))

    def _mixed_p_xml(self, parts, parapr=4):
        # parts: ('t', text, charpr) | ('pic', [(iid,w,h),...]) | ('eq', script, (w,h)[, charpr])
        runs = ""
        for p in parts:
            if p[0] == 't':
                runs += '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>' % (p[2], esc(p[1]))
            elif p[0] == 'pic':
                runs += '<hp:run charPrIDRef="0">%s</hp:run>' % "".join(self._pic_xml(i, w, h) for (i, w, h) in p[1])
            elif p[0] == 'eq':
                wh = p[2]; cpr = p[3] if len(p) > 3 else 0
                bl = wh[2] if len(wh) > 2 else 85
                runs += '<hp:run charPrIDRef="%d">%s</hp:run>' % (cpr, self.eqn_xml(p[1], wh[0], wh[1], cpr, bl))
        return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '%s</hp:p>') % (self.pid(), parapr, runs)

    def _p2_xml(self, pre, pre_cp, text, text_cp, parapr=4):
        return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>'
                '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>'
                ) % (self.pid(), parapr, pre_cp, esc(pre), text_cp, esc(text))

    def _cell(self, items, w, h, borderfill, col, row, valign="TOP", lm=None, rm=None):
        if lm is None: lm = self.cell_side_margin
        if rm is None: rm = self.cell_side_margin
        paras = ""
        for it in items:
            if it[0] == 'p':
                paras += self._p_xml(it[1], it[2] if len(it) > 2 else 0, it[3] if len(it) > 3 else 4)
            elif it[0] == 'p2':
                paras += self._p2_xml(it[1], it[2], it[3], it[4], it[5] if len(it) > 5 else 4)
            elif it[0] == 'img':
                paras += self._pic_p_xml(it[1], it[2] if len(it) > 2 else 1)
            elif it[0] == 'mix':
                paras += self._mixed_p_xml(it[1], it[2] if len(it) > 2 else 4)
            elif it[0] == 'raw':
                paras += it[1]
        if not paras:
            paras = self._p_xml("", 0, 4)
        return ('<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="%d">'
                '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="%s" '
                'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="0" hasTextRef="0" hasNumRef="0">'
                '%s</hp:subList>'
                '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
                '<hp:cellSz width="%d" height="%d"/>'
                '<hp:cellMargin left="%d" right="%d" top="%d" bottom="%d"/></hp:tc>'
                ) % (borderfill, valign, max(w - lm - rm - 200, 1000), paras, col, row, w, h,
                     lm, rm, self.cell_top_margin, self.cell_bottom_margin)

    def _tbl_in_p(self, rows, widths, row_h, divider=False, parapr=1, cell_bf=None, valign="TOP", noadjust=False):
        tbl = self._tbl_xml(rows, widths, row_h, divider, tid_off=6000000, cell_bf=cell_bf, valign=valign, noadjust=noadjust)
        return ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                '<hp:run charPrIDRef="0">%s</hp:run></hp:p>') % (self.pid(), parapr, tbl)

    def badge_xml(self, num):
        # small navy box with white 2-digit number, left-aligned (like 01, 02 …)
        st, ss, tp = self.cell_top_margin, self.cell_side_margin, None
        k = cps()[14] / 900.0
        self.cell_top_margin, self.cell_side_margin = int(90 * k), int(260 * k)
        p = self._tbl_in_p([[[('p', "%02d" % num, 10, 1)]]], [int(2900 * k)], row_h=int(1550 * k),
                           divider=False, parapr=4, cell_bf=8)
        self.cell_top_margin, self.cell_side_margin = st, ss
        return p

    def _tbl_xml(self, rows, widths, row_h, divider, tid_off=3000000, top_spacer=0, cell_bf=None, valign="TOP", noadjust=False):
        ncol = len(widths); tw = sum(widths)
        nrow = len(rows) + (1 if top_spacer else 0)
        th = row_h * len(rows) + top_spacer
        tid = self.pid() + tid_off
        trs = ""
        roff = 0
        if top_spacer:
            spacer = ('<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="1">'
                      '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" '
                      'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="0" hasTextRef="0" hasNumRef="0">'
                      '%s</hp:subList>'
                      '<hp:cellAddr colAddr="0" rowAddr="0"/><hp:cellSpan colSpan="%d" rowSpan="1"/>'
                      '<hp:cellSz width="%d" height="%d"/>'
                      '<hp:cellMargin left="0" right="0" top="0" bottom="0"/></hp:tc>'
                      ) % (tw, self._p_xml("", 0, 4), ncol, tw, top_spacer)
            trs += "<hp:tr>%s</hp:tr>" % spacer
            roff = 1
        for r, row in enumerate(rows):
            cells = ""
            for c, cell in enumerate(row):
                if cell_bf is not None:
                    bf = cell_bf(r, c) if callable(cell_bf) else cell_bf
                else:
                    bf = 6 if (divider and c == 0 and ncol >= 2) else 1
                lm = rm = None
                if divider and ncol == 2:
                    if c == 0:
                        rm = self.cell_side_margin + self.divider_gap   # left cell: pad before divider
                    else:
                        lm = self.cell_side_margin + self.divider_gap   # right cell: pad after divider
                cells += self._cell(cell, widths[c], row_h, bf, c, r + roff, valign=valign, lm=lm, rm=rm)
            trs += "<hp:tr>%s</hp:tr>" % cells
        return ('<hp:tbl id="%d" zOrder="0" numberingType="NONE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" '
                'lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" rowCnt="%d" colCnt="%d" '
                'cellSpacing="0" borderFillIDRef="1" noAdjust="NOADJ">'
                '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
                '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
                'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
                '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
                '<hp:inMargin left="0" right="0" top="0" bottom="0"/>%s</hp:tbl>'
                ).replace("NOADJ", "1" if noadjust else "0") % (tid, nrow, ncol, tw, th, trs)

    def table(self, rows, widths, row_h=9000, divider=True, pagebreak=False, top_spacer=0):
        extra = self._first_run_extra()
        tbl = self._tbl_xml(rows, widths, row_h, divider, top_spacer=top_spacer)
        runs = ('<hp:run charPrIDRef="0">%s</hp:run>' % extra) if extra else ""
        runs += '<hp:run charPrIDRef="0">%s</hp:run>' % tbl
        self.body.append('<hp:p id="%d" paraPrIDRef="0" styleIDRef="0" pageBreak="%s" columnBreak="0" merged="0">'
                         '%s</hp:p>' % (self.pid(), "1" if pagebreak else "0", runs))

    def header_box(self, items, width=None, bf=7, height=100):
        if width is None:
            width = body_w()
        extra = self._first_run_extra()
        cell = self._cell(items, width, height, bf, 0, 0, valign="CENTER")
        tid = self.pid() + 5000000
        tbl = ('<hp:tbl id="%d" zOrder="0" numberingType="NONE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" '
               'lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" rowCnt="1" colCnt="1" cellSpacing="0" '
               'borderFillIDRef="1" noAdjust="0">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
               'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="0" right="0" top="0" bottom="0"/>'
               '<hp:tr>%s</hp:tr></hp:tbl>') % (tid, width, height, cell)
        runs = ('<hp:run charPrIDRef="0">%s</hp:run>' % extra) if extra else ""
        runs += '<hp:run charPrIDRef="0">%s</hp:run>' % tbl
        self.body.append('<hp:p id="%d" paraPrIDRef="1" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         '%s</hp:p>' % (self.pid(), runs))

    def set_header(self, pics, parapr=1):
        inner = "".join(self._pic_xml(iid, w, h) for (iid, w, h) in pics)
        p = ('<hp:p id="%d" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
             '<hp:run charPrIDRef="0">%s</hp:run></hp:p>') % (self.pid(), parapr, inner)
        self.header_xml_str = ('<hp:header id="%d" applyPageType="BOTH">'
            '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" '
            'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="0" hasTextRef="0" hasNumRef="0">'
            '%s</hp:subList></hp:header>') % (self.pid(), body_w(), p)

    def set_footer(self, left, right, charpr=7):
        W = body_w(); w1 = int(W * 0.42); w3 = int(W * 0.42); w2 = W - w1 - w3
        pagenum = ('<hp:p id="%d" paraPrIDRef="1" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                   '<hp:run charPrIDRef="%d"><hp:ctrl><hp:autoNum num="1" numType="PAGE">'
                   '<hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar="" supscript="0"/>'
                   '</hp:autoNum></hp:ctrl><hp:t></hp:t></hp:run></hp:p>') % (self.pid(), charpr)
        left_p = self._p_xml(left, charpr, 4)
        right_p = self._p_xml(right, charpr, 3)
        def fcell(paras, w, col):
            return ('<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" borderFillIDRef="1">'
                    '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" '
                    'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="0" hasTextRef="0" hasNumRef="0">'
                    '%s</hp:subList><hp:cellAddr colAddr="%d" rowAddr="0"/><hp:cellSpan colSpan="1" rowSpan="1"/>'
                    '<hp:cellSz width="%d" height="1400"/><hp:cellMargin left="141" right="141" top="0" bottom="0"/></hp:tc>'
                    ) % (max(w - 300, 500), paras, col, w)
        trs = '<hp:tr>%s%s%s</hp:tr>' % (fcell(left_p, w1, 0), fcell(pagenum, w2, 1), fcell(right_p, w3, 2))
        tid = self.pid() + 4000000
        tbl = ('<hp:tbl id="%d" zOrder="0" numberingType="NONE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" '
               'lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="0" rowCnt="1" colCnt="3" cellSpacing="0" '
               'borderFillIDRef="1" noAdjust="0">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="1400" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
               'vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="0" right="0" top="0" bottom="0"/>'
               '%s</hp:tbl>') % (tid, W, trs)
        fp = ('<hp:p id="%d" paraPrIDRef="4" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
              '<hp:run charPrIDRef="0">%s</hp:run></hp:p>') % (self.pid(), tbl)
        self.footer_xml_str = ('<hp:footer id="%d" applyPageType="BOTH">'
            '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="BOTTOM" '
            'linkListIDRef="0" linkListNextIDRef="0" textWidth="%d" textHeight="0" hasTextRef="0" hasNumRef="0">'
            '%s</hp:subList></hp:footer>') % (self.pid(), body_w(), fp)

    def section_xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<hs:sec %s>%s</hs:sec>') % (NS, "".join(self.body))

    def write(self, out):
        header_xml = build_header()
        section0 = self.section_xml()
        img_items = "".join('<opf:item id="%s" href="BinData/%s" media-type="%s" isEmbeded="1"/>'
                            % (iid, arc, mt) for (iid, arc, mt, _) in self.images)
        content_hpf = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<opf:package xmlns:opf="http://www.idpf.org/2007/opf/" '
            'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'version="" unique-identifier="" id="">'
            '<opf:metadata><opf:title>%s</opf:title><opf:language>ko</opf:language>'
            '<opf:meta name="creator" content="채수학"/></opf:metadata>'
            '<opf:manifest>'
            '<opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>'
            '<opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>'
            '<opf:item id="settings" href="settings.xml" media-type="application/xml"/>'
            + img_items +
            '</opf:manifest>'
            '<opf:spine><opf:itemref idref="section0" linear="yes"/></opf:spine>'
            '</opf:package>') % esc(self.title)
        container_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" '
            'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf"><ocf:rootfiles>'
            '<ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>'
            '</ocf:rootfiles></ocf:container>')
        man_imgs = "".join('<odf:file-entry full-path="BinData/%s" media-type="%s"/>' % (arc, mt)
                           for (_, arc, mt, _) in self.images)
        manifest_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" version="1.2">'
            '<odf:file-entry full-path="/" media-type="application/hwp+zip"/>'
            '<odf:file-entry full-path="version.xml" media-type="application/xml"/>'
            '<odf:file-entry full-path="Contents/header.xml" media-type="application/xml"/>'
            '<odf:file-entry full-path="Contents/section0.xml" media-type="application/xml"/>'
            '<odf:file-entry full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>'
            '<odf:file-entry full-path="settings.xml" media-type="application/xml"/>'
            + man_imgs + '</odf:manifest>')
        settings_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
            'xmlns:config="http://www.hancom.co.kr/hwpml/2011/configuration">'
            '<ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/></ha:HWPApplicationSetting>')
        version_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" '
            'tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0" os="1" '
            'xmlVersion="1.4" application="Hancom Office Hangul" appVersion="9, 1, 1, 5656"/>')
        prv = self.title

        if os.path.exists(out):
            os.remove(out)
        zf = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
        zi = zipfile.ZipInfo("mimetype"); zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, b"application/hwp+zip")
        zf.writestr("version.xml", version_xml.encode("utf-8"))
        zf.writestr("Contents/header.xml", header_xml.encode("utf-8"))
        zf.writestr("Contents/section0.xml", section0.encode("utf-8"))
        zf.writestr("Contents/content.hpf", content_hpf.encode("utf-8"))
        zf.writestr("META-INF/container.xml", container_xml.encode("utf-8"))
        zf.writestr("META-INF/manifest.xml", manifest_xml.encode("utf-8"))
        zf.writestr("settings.xml", settings_xml.encode("utf-8"))
        for (iid, arc, mt, data) in self.images:
            zf.writestr("BinData/" + arc, data)
        zf.writestr("Preview/PrvText.txt", prv.encode("utf-8"))
        zf.close()
        # validate xml well-formed
        import xml.dom.minidom as M
        for x in [section0, header_xml, content_hpf, container_xml, manifest_xml, settings_xml, version_xml]:
            M.parseString(x.encode("utf-8"))
        return out
