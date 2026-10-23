"""2027 대구광역시 교습소 탁상달력 수정 스크립트.

1) 회원 교습소 명단 페이지 추가
2) 표지 부제: '세무·행정'을 마지막으로 이동
3) 1~12월 달력 속지를 2025년 달력 모양으로 새로 그림 (month_page)
   - 범례 순서: 교과 | 예체능 | 학교시험 | 법정의무교육 | 세무·행정 | 공휴일
   - 2월·8월 '대구 태권도 …' 일정 삭제, 2월 21일 '정월대보름' 추가
4) 표지: 작은 달력 대신 12작품을 4x3으로 (2025년 표지처럼)
5) 4쪽 2026년 12월, 5쪽 2027년 한눈에 보기(AKAS 워터마크), 6쪽부터 달마다 작품·달력
6) 2쪽 회원 명단, 3쪽 연혁(HISTORY), 주요 사항 안내는 맨 뒤
7) 표지 로고를 연합회 공식 로고(akas_logo.png)로 바꾸고 영문을 'Daegu Association of Private Tutoring Centers'로 수정

사용법: python3 build_calendar.py 원본.pdf 결과.pdf 폰트폴더
"""
import io
import re
import sys

import pypdf
from pypdf.generic import DecodedStreamObject, NameObject
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

SRC, OUT, FONT_DIR = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------------------------------------------------------------- 회원 명단
MEMBERS = [
    ("수성구", [
        ("수학", ["에듀모아G+수학", "초이스수학", "겨자씨수학|범어동", "매쓰피아수학|범어동",
                "범어수학|범어동", "세은수학|범어동", "이상호수학|범어동", "채수학|범어동",
                "깊이있는수학|상동", "서강수학|수성동1가", "MATH21수학|수성동4가", "SKY수학|황금동"]),
        ("영어", ["삼성영어", "느티나무영어|만촌동", "이큐영어|만촌동", "베이뷰영어|범어동",
                "헤럴드시스템영어|범어동", "더잉글리쉬리딩영어|수성동1가", "더자람영어|욱수동"]),
        ("국어 · 논술", ["형설국어", "맥독서논술|범물동", "성쌤국어|범물동", "라온글국어|범어동",
                     "서샘국어|범어동", "심비국어|범어동", "장서국어|범어동", "글빛김박사논술|신매동",
                     "리딩오션중동독서논술|중동", "라온하제밝은미래국어|황금동",
                     "정혜란집중력한자|황금동", "짱짱한장쌤국어|황금동"]),
        ("과학", ["사이언스베슬과학|범어동", "최재형과학|범어동"]),
        ("미술", ["아이꿈미술|만촌동", "몽아트미술|수성동4가"]),
        ("음악", ["이레바이올린", "이레플룻", "정음악|범어동", "레가토바이올린음악|수성동1가",
                "로뎀피아노|지산동"]),
        ("그 외", ["부쿠의온라인진로|신매동", "캐슬컴퓨터|황금동"]),
    ]),
    ("달서구", [
        ("수학", ["예스셈수학", "코치수학|대곡동", "에스수학|본동", "The(더)쎈수학|상인동",
                "개벽수학|송현동", "공부의신수학|월성동", "빨간펜수학의달인수학|월성동",
                "유레카수학|진천동", "초이스수학|진천동", "더블유수학|호산동"]),
        ("영어", ["미래엔영어덕인초영어", "분석영어|대천동", "티파니영어|도원동", "삼성영어|본리동",
                "드림하이영어|상인동", "유니라잇영어|유천동", "링키영어이곡점영어|이곡동",
                "제이즈잉글리쉬영어|이곡동"]),
        ("국어 · 논술", ["나무와숲국어논술|도원동", "정인국어|상인동", "한우리국어|용산동",
                     "황경희논술|월성동", "글힘논술|유천동"]),
        ("과학", ["안은숙과학|도원동", "통과학|유천동"]),
        ("미술", ["아이꿈미술|상인동", "아트스튜디오오티미술|월성동", "더샤미술|이곡동",
                "아트&하트진천미술|진천동"]),
        ("음악", ["봄음악|두류동", "계명피아노|송현동", "옴니보이스보컬|진천동"]),
        ("그 외", ["한비베트남어|이곡동"]),
    ]),
    ("북구", [
        ("수학", ["엘스마트해법수학|고성동1가", "에이플러스수학|관음동", "위드(with)수학|구암동",
                "온누리수학|노원동3가", "더함수학|동천동", "현(HYUN)수학|매천동",
                "수학의결수학|복현동", "수학의달인럭키읍내수학|읍내동", "챔프수학|침산동",
                "정쌤클래스수학|태전동"]),
        ("영어", ["하이어영어", "더(The)채움영어|태전동", "뮤엠강북이진캐스빌영어|태전동",
                "모모영어|팔달동"]),
        ("미술", ["레핀미술|사수동"]),
        ("음악", ["계명피아노|관음동"]),
        ("그 외", ["좋은소리웅변|구암동"]),
    ]),
    ("동구", [
        ("수학", ["새론미래엔수학|각산동", "e해법수학|율하동", "이쌤지묘수학|지묘동",
                "해오름수학|지묘동"]),
        ("영어", ["3030리즈영어|신암동", "아이(i)스콜라영어|신천동"]),
        ("국어 · 논술", ["리딩오션동대구초독서논술|신암동"]),
        ("음악", ["환희피아노", "에덴피아노|효목동"]),
        ("그 외", ["예스컴퓨터|율하동"]),
    ]),
    ("달성군", [
        ("수학", ["HS수학|구지면", "이선생공부수학|논공읍", "김쌤e해법수학|다사읍",
                "키메수학|다사읍", "옹기수학|화원읍"]),
        ("영어", ["프랜잉글리시영어|구지면", "권미진영어|다사읍", "리딩드리북클럽영어|유가읍"]),
        ("국어 · 논술", ["리드인독서국어|다사읍"]),
    ]),
    ("중구", [
        ("수학", ["함께하는수학|대신동"]),
        ("국어 · 논술", ["리딩히스토리독서논술|대신동"]),
        ("미술", ["율아트미술|대신동"]),
        ("음악", ["모리터국악|남산동"]),
    ]),
    ("남구", [
        ("수학", ["엘리트수학|이천동"]),
        ("영어", ["뮤엠영선영어|대명동", "영탑영어|봉덕동"]),
    ]),
    ("서구", [
        ("수학", ["큰이룸수학|평리동"]),
        ("영어", ["하이클래스영어|비산동"]),
        ("국어 · 논술", ["봄날국어|평리동"]),
    ]),
    ("군위군", [
        ("음악", ["이레피아노|군위읍"]),
    ]),
]

SUBJECT_COLOR = {
    "수학": "#1B2F55", "영어": "#B8892B", "국어 · 논술": "#2F7A4F", "과학": "#2F6DB5",
    "미술": "#8A5A2B", "음악": "#6E4FA3", "그 외": "#6B7B88",
}

# 달력 본문과 같은 색
GREEN = HexColor("#17483B")
GREEN2 = HexColor("#1E5A49")
GRAY = HexColor("#727F7A")
LIGHTGRAY = HexColor("#8FA89C")
LINE = HexColor("#B9CAC2")
INK = HexColor("#26342F")
PALE = HexColor("#EAF4EF")
CARD = HexColor("#F7FAF8")
DONG = HexColor("#9AA8A2")
GOLD = HexColor("#C9A23F")


def register_fonts():
    for name, file in [("NG", "NanumGothic-Regular.ttf"), ("NGB", "NanumGothic-Bold.ttf"),
                       ("NGEB", "NanumGothic-ExtraBold.ttf")]:
        pdfmetrics.registerFont(TTFont(name, f"{FONT_DIR}/{file}"))
    # 한자(丁未年)용
    pdfmetrics.registerFont(TTFont("NSKR", f"{FONT_DIR}/NotoSansKR.ttf"))


def member_page():
    W, H = 841.8898, 595.2756
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # 왼쪽 위 초록 상자 (월 표시 상자와 같은 자리)
    c.setFillColor(GREEN)
    c.roundRect(39.685, 488, 128, 70, 11, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("NGEB", 21)
    c.drawCentredString(103.685, 527, "회원")
    c.drawCentredString(103.685, 502, "교습소")

    c.setFillColor(GREEN2)
    c.setFont("NGEB", 18)
    c.drawString(185.685, 534, "우리 동네 교습소")
    c.setFillColor(GRAY)
    c.setFont("NGB", 10.5)
    c.drawString(185.685, 512, "정회원 122곳  |  구  |  동  |  과목별")
    # 과목 색 범례
    x = 185.685
    c.setFont("NG", 8.5)
    for subj, col in SUBJECT_COLOR.items():
        c.setFillColor(HexColor(col))
        c.roundRect(x, 490.5, 7, 7, 1.5, stroke=0, fill=1)
        c.setFillColor(GRAY)
        c.drawString(x + 10, 491.5, subj)
        x += 10 + c.stringWidth(subj, "NG", 8.5) + 12

    # 오른쪽 안내 상자
    c.setFillColor(PALE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(520, 488, 282.205, 72, 7, stroke=1, fill=1)
    c.setFillColor(GREEN2)
    c.setFont("NGB", 10.5)
    c.drawString(534, 541, "회원 교습소 명단 안내")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(534, 534, 788.205, 534)
    c.setFillColor(INK)
    c.setFont("NG", 8.3)
    c.drawString(534, 519, "이름 뒤의 「교습소」와 원장님 성함 · 연락처는 줄였습니다.")
    c.drawString(534, 506, "작은 회색 글씨는 동(읍·면) 이름입니다.")
    c.drawString(534, 493, "바뀐 내용이 있으면 연합회(053-281-0011)로 알려 주세요.")

    # ---- 본문: 5단으로 흘려 넣기
    cols, gap = 5, 9
    left, right = 39.685, 802.205
    top, bottom = 476, 34
    cw = (right - left - gap * (cols - 1)) / cols
    HEAD_H, CAT_H, ROW_H, CARD_PAD, CARD_GAP = 20, 11.6, 9.9, 5, 6

    # 그릴 줄 목록 만들기
    blocks = []
    for district, cats in MEMBERS:
        count = sum(len(v) for _, v in cats)
        rows = []
        for i, (subj, names) in enumerate(cats):
            rows.append(("cat", subj, i > 0))
            rows.extend(("name", n, subj) for n in names)
        blocks.append((district, count, rows))

    def row_h(r):
        return (CAT_H + (2 if r[2] else 0)) if r[0] == "cat" else ROW_H

    col, y = 0, top
    for district, count, rows in blocks:
        pending = list(rows)
        cont = False
        while pending:
            avail = y - bottom - HEAD_H - CARD_PAD * 2
            take, used = [], 0
            for r in pending:
                h = row_h(r)
                if used + h > avail:
                    break
                take.append(r)
                used += h
            # 과목 제목만 단 끝에 남지 않게
            while take and take[-1][0] == "cat":
                used -= row_h(take.pop())
            if len(take) < 3 and col < cols - 1 and y < top:
                col, y = col + 1, top
                continue
            pending = pending[len(take):]
            card_h = HEAD_H + used + CARD_PAD * 2
            x0 = left + col * (cw + gap)
            c.setFillColor(CARD)
            c.setStrokeColor(LINE)
            c.setLineWidth(0.7)
            c.roundRect(x0, y - card_h, cw, card_h, 5, stroke=1, fill=1)
            # 구 이름
            c.setFillColor(GREEN)
            c.setFont("NGEB", 10.5)
            c.drawString(x0 + 8, y - 15, district + (" (계속)" if cont else ""))
            if not cont:
                c.setFillColor(GOLD)
                c.setFont("NGB", 9)
                c.drawRightString(x0 + cw - 8, y - 15, f"{count}곳")
            c.setStrokeColor(GOLD)
            c.setLineWidth(0.8)
            c.line(x0 + 8, y - 20, x0 + cw - 8, y - 20)
            yy = y - HEAD_H - CARD_PAD
            for r in take:
                if r[0] == "cat":
                    if r[2]:
                        yy -= 2
                    yy -= CAT_H
                    c.setFillColor(HexColor(SUBJECT_COLOR[r[1]]))
                    c.rect(x0 + 8, yy + 1, 2.2, 7.5, stroke=0, fill=1)
                    c.setFont("NGB", 7.8)
                    c.drawString(x0 + 14, yy + 2, r[1])
                else:
                    yy -= ROW_H
                    name, _, dong = r[1].partition("|")
                    c.setFillColor(INK)
                    c.setFont("NG", 7.6)
                    c.drawString(x0 + 14, yy + 2, name)
                    if dong:
                        nx = x0 + 14 + c.stringWidth(name, "NG", 7.6) + 3
                        c.setFillColor(DONG)
                        c.setFont("NG", 6.2)
                        c.drawString(nx, yy + 2, dong)
            y -= card_h + CARD_GAP
            if pending:
                col, y, cont = col + 1, top, True
                if col >= cols:
                    raise SystemExit("명단이 한 쪽에 다 들어가지 않습니다")

    # 바닥글 (달력 다른 쪽과 같은 형식)
    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 6.5)
    c.drawString(39.685, 22, "※ 2026년 9월 정회원 명단 기준입니다. 동 이름은 교습소 위치이며 바뀔 수 있습니다.")
    c.drawRightString(802.205, 22, "사)한국교습소총연합회 대구광역시지회 ")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


# ---------------------------------------------------------------- 표지 수정
def set_content(writer, page, data):
    s = DecodedStreamObject()
    s.set_data(data)
    page[NameObject("/Contents")] = writer._add_object(s)


LOGO = __file__.rsplit("/", 1)[0] + "/akas_logo.png" if "/" in __file__ else "akas_logo.png"
# 표지의 옛 AKAS 그림(타원 안 막대 + AKAS 글자) 부분
OLD_LOGO_RE = re.compile(rb"q\nn 289\.0264 147 m .*?\(AKAS\) Tj T\* ET\nQ\n", re.S)


def cover_logo():
    """표지의 옛 로고 자리에 공식 로고 그림을 놓는다."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(841.8898, 595.2756))
    h = 38
    w = h * 1362 / 734  # 그림 가로세로 비율 유지
    c.drawImage(LOGO, 256.0264 - w / 2, 147 - h / 2, w, h, mask="auto")
    c.setFillColor(HexColor("#26342F"))
    c.setFont("Times-Italic", 11)
    c.drawString(304.0264, 133.5, "Daegu Association of Private Tutoring Centers")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


HERE = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
PAGE_W, PAGE_H = 841.8898, 595.2756
# 달마다 들어갈 작품 정보 (학생 이름 · 학년 · 교습소). 비어 있으면 안내 문구만 연하게 표시
# 값: (작품 제목, 학생 이름 · 학교 학년)
ARTWORK_INFO = {m: None for m in range(1, 13)}
ARTWORK_INFO.update({
    1: ("무지개 문어와 친구들", "노연서 · 대청초 3학년"),
    2: ("전통문화 탐방", "박하진 · 와룡초 4학년"),
    3: ("맛있는 손가락 꼬깔콘", "정하연 · 롯데가야유치원 7세"),
    4: ("자연은 내친구", "노이준 · 6세"),
    5: ("하리보디자인", "변초아 · 대청초 6학년"),
    6: ("행복한 하굣길", "권현정 · 월암초 6학년"),
    7: ("강아지와 함께하는 목욕놀이", "구하윤 · 월암중 1학년"),
    8: ("친구들과 행복한시간", "이용준 · 와룡초 4학년"),
    9: ("상상의 바다", "황지우 · 성당초 3학년"),
    10: ("별빛 부엉이", "홍하윤 · 대청초 6학년"),
    11: ("바닷속이야기", "이채민 · 사수초 4학년"),
    12: ("걱정마세요, 행복한 왕자님", "손은서 · 사수초 2학년"),
})


def artwork_path(month):
    return f"{HERE}/artworks/{month:02d}.jpg"


_SHARP = {}


def sharp_image(month):
    """작품 사진을 또렷하게: 윤곽 선명하게(언샤프 마스크) + 대비·채도 살짝 올림."""
    from PIL import Image, ImageEnhance, ImageFilter
    if month not in _SHARP:
        im = Image.open(artwork_path(month)).convert("RGB")
        im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=110, threshold=2))
        im = ImageEnhance.Contrast(im).enhance(1.06)
        im = ImageEnhance.Color(im).enhance(1.06)
        _SHARP[month] = im
    return _SHARP[month]


def sharp_reader(month):
    from reportlab.lib.utils import ImageReader
    out = io.BytesIO()
    sharp_image(month).save(out, "JPEG", quality=90)
    out.seek(0)
    return ImageReader(out)


def thumb(month, w, h):
    """작품을 w:h 비율로 가운데를 잘라 작은 그림으로 만든다 (표지 모자이크용)."""
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    im = sharp_image(month).copy()
    iw, ih = im.size
    if iw / ih > w / h:
        nw = ih * w / h
        im = im.crop(((iw - nw) / 2, 0, (iw + nw) / 2, ih))
    else:
        nh = iw * h / w
        im = im.crop((0, (ih - nh) / 2, iw, (ih + nh) / 2))
    im.thumbnail((int(w * 5), int(h * 5)))  # 인쇄용 약 360dpi
    out = io.BytesIO()
    im.save(out, "JPEG", quality=85)
    out.seek(0)
    return ImageReader(out)


def cover_watermark():
    """표지 작은 달력들 가운데에 AKAS 로고를 옅게 깐다."""
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    im = Image.open(LOGO).convert("RGBA")
    r, g, b, a = im.split()
    a = a.point(lambda v: int(v * 0.07))  # 투명도 7%
    im = Image.merge("RGBA", (r, g, b, a))
    out = io.BytesIO()
    im.save(out, "PNG")
    out.seek(0)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    w = 440
    h = w * im.size[1] / im.size[0]
    c.drawImage(ImageReader(out), (PAGE_W - w) / 2, 322 - h / 2, w, h, mask="auto")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


def artwork_page(month):
    """그 달 달력 앞에 들어가는 작품 쪽."""
    from PIL import Image
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # 위쪽 제목
    c.setFillColor(GREEN)
    c.roundRect(39.685, 543, 66, 30, 7, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("NGEB", 16)
    c.drawCentredString(72.685, 552, f"{month}월")
    c.setFillColor(GREEN2)
    c.setFont("NGEB", 13)
    c.drawString(116, 553, "이달의 작품")
    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 8.5)
    c.drawRightString(802.205, 553, "2027 대구광역시 교습소 탁상달력")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(39.685, 535, 802.205, 535)

    # 작품 (비율 유지, 가운데)
    box_x, box_y, box_w, box_h = 39.685, 70, 762.52, 452
    iw, ih = sharp_image(month).size
    scale = min(box_w / iw, box_h / ih)
    w, h = iw * scale, ih * scale
    x, y = box_x + (box_w - w) / 2, box_y + (box_h - h) / 2
    c.setFillColor(HexColor("#E3EBE7"))
    c.rect(x + 2.5, y - 2.5, w, h, stroke=0, fill=1)  # 옅은 그림자
    c.drawImage(sharp_reader(month), x, y, w, h)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, stroke=1, fill=0)

    # 작품 정보
    info = ARTWORK_INFO[month]
    if info:
        title, who = f"「{info[0]}」", info[1]
        tw = c.stringWidth(title, "NGB", 11)
        ww = c.stringWidth(who, "NG", 9)
        x = (PAGE_W - (tw + 12 + ww)) / 2
        c.setFillColor(GREEN2)
        c.setFont("NGB", 11)
        c.drawString(x, 48, title)
        c.setFillColor(GRAY)
        c.setFont("NG", 9)
        c.drawString(x + tw + 12, 48, who)
    else:
        c.setFillColor(HexColor("#C2CEC8"))
        c.setFont("NG", 9)
        c.drawCentredString(PAGE_W / 2, 48, "작품 정보 (학생 이름 · 학년 · 교습소)")
    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 6.5)
    c.drawRightString(802.205, 22, f"사)한국교습소총연합회 대구광역시지회  ·  2027 · {month:02d}")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


# 달마다 주요 일정(✓)과 날짜 칸 글씨
# 글씨 종류: holiday 공휴일(빨강) · term 절기·명절(갈색) · admin 세무·행정(초록)
# off: 일요일이 아닌데 빨간 날(공휴일·연휴·대체공휴일)
MONTHS = {
    1: {
        "items": ['겨울방학 특강', '신학기 수업계획·교재 준비', '상반기 콩쿠르·공모전 준비', '사업장현황신고 자료 준비'],
        "labels": {1: [('신정', 'holiday')], 5: [('소한', 'term')], 20: [('대한', 'term')]},
        "off": [1],
    },
    2: {
        "items": ['2/10 면세사업자 사업장현황신고', '신학기 반편성·시간표 확정', '법정의무교육 연간계획 확인'],
        "labels": {4: [('입춘', 'term')], 6: [('설 연휴', 'holiday')], 7: [('설날', 'holiday')], 8: [('설 연휴', 'holiday')], 9: [('대체공휴일', 'holiday')], 10: [('사업장현황신고', 'admin')], 19: [('우수', 'term')], 21: [('정월대보름', 'term')]},
        "off": [6, 8, 9],
    },
    3: {
        "items": ['신학기 개학·학력평가', '1학기 내신·중간고사 대비 시작', '봄 예체능 대회·공모전 준비', '학교별 학사일정 확인'],
        "labels": {1: [('삼일절', 'holiday')], 6: [('경칩', 'term')], 21: [('춘분', 'term')]},
        "off": [1],
    },
    4: {
        "items": ['1학기 중간고사 집중 대비', '학교별 시험일정 확인', '종합소득세 신고·납부 준비(5/31까지)', '봄 예체능 대회·공모전 시즌'],
        "labels": {5: [('청명', 'term')], 20: [('곡우', 'term')]},
        "off": [],
    },
    5: {
        "items": ['대구 교습소 정기연수(예정)', '중간고사 분석·학부모 상담', '기말고사 대비 시작', '종합소득세 신고·납부'],
        "labels": {1: [('노동절', 'holiday')], 3: [('대체공휴일', 'holiday')], 5: [('어린이날', 'holiday')], 6: [('입하', 'term')], 13: [('부처님오신날', 'holiday')], 21: [('소만', 'term')], 31: [('종합소득세 기한', 'admin')]},
        "off": [1, 3, 5, 13],
    },
    6: {
        "items": ['수능 모의평가', '1학기 기말고사 집중 대비', '여름방학 특강 모집', '상반기 예체능 대회 일정 확인'],
        "labels": {6: [('현충일', 'holiday'), ('망종', 'term')], 21: [('하지', 'term')]},
        "off": [],
    },
    7: {
        "items": ['1학기 성적분석·상담', '여름방학 특강·2학기 선행', '예체능 여름방학 특강', '상반기 장부·증빙자료 점검'],
        "labels": {7: [('소서', 'term')], 17: [('제헌절', 'holiday')], 19: [('대체공휴일', 'holiday')], 23: [('대서', 'term')]},
        "off": [17, 19],
    },
    8: {
        "items": ['2학기 개학·반편성·시간표 조정', '2학기 중간고사 선행', '하반기 예체능 대회 준비'],
        "labels": {8: [('입추', 'term')], 15: [('광복절', 'holiday')], 16: [('대체공휴일', 'holiday')], 23: [('처서', 'term')]},
        "off": [16],
    },
    9: {
        "items": ['수능 모의평가', '2학기 중간고사 집중 대비', '법정의무교육 이수기간 시작(9~12월)', '가을 콩쿠르·공모전 시즌'],
        "labels": {8: [('백로', 'term')], 14: [('추석 연휴', 'holiday')], 15: [('추석', 'holiday')], 16: [('추석 연휴', 'holiday')], 23: [('추분', 'term')]},
        "off": [14, 15, 16],
    },
    10: {
        "items": ['전국연합학력평가', '중간고사 분석·기말고사 대비 시작', '법정의무교육 이수·점검', '가을 예체능 행사 일정 확인'],
        "labels": {3: [('개천절', 'holiday')], 4: [('대체공휴일', 'holiday')], 8: [('한로', 'term')], 9: [('한글날', 'holiday')], 11: [('대체공휴일', 'holiday')], 23: [('상강', 'term')]},
        "off": [4, 9, 11],
    },
    11: {
        "items": ['대학수학능력시험', '2학기 기말고사 집중 대비', '예비중·예비고·겨울특강 모집', '법정의무교육 이수·점검'],
        "labels": {7: [('입동', 'term')], 22: [('소설', 'term')]},
        "off": [],
    },
    12: {
        "items": ['교습소 원장님 작품전시회', '기말고사 분석·학부모 상담', '겨울방학 특강·다음 학년도 반편성', '법정의무교육 최종 이수 점검'],
        "labels": {7: [('대설', 'term')], 22: [('동지', 'term')], 25: [('성탄절', 'holiday')], 27: [('대체공휴일', 'holiday')]},
        "off": [25, 27],
    },
}


# ---------------------------------------------------------------- 월별 속지 (2025년 달력 모양)
MONTH_EN = ["", "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]
WEEK = [("일요일", "Sunday"), ("월요일", "Monday"), ("화요일", "Tuesday"),
        ("수요일", "Wednesday"), ("목요일", "Thursday"), ("금요일", "Friday"),
        ("토요일", "Saturday")]
RED = HexColor("#BB3E45")
BLUE = HexColor("#355C9A")
WEEKDAY_BAR = HexColor("#A7B1AC")
BIG_NUM = HexColor("#9FB3A9")
LABEL_COLOR = {"holiday": RED, "term": HexColor("#9A6A24"), "admin": GREEN2}
LEGEND = "교과  |  예체능  |  학교시험  |  법정의무교육  |  세무·행정  |  공휴일"


def lunar_mark(year, month, day):
    """음력 1일·15일이면 '음M.D' 글씨를 돌려준다 (2025년 달력처럼)."""
    from korean_lunar_calendar import KoreanLunarCalendar
    cal = KoreanLunarCalendar()
    cal.setSolarDate(year, month, day)
    if cal.lunarDay in (1, 15) and not cal.isIntercalation:
        return f"음{cal.lunarMonth}.{cal.lunarDay}"
    return ""


def mini_month(c, year, month, x, y, w, h):
    """날짜 칸 안에 들어가는 지난달·다음달 작은 달력. (x, y)는 칸의 왼쪽 위."""
    import calendar as pycal
    c.setFillColor(INK)
    c.setFont("NG", 7)
    c.drawString(x + 6, y - 12, MONTH_EN[month])
    c.drawRightString(x + w - 6, y - 12, f"{month} / {year}")
    cw = (w - 12) / 7
    c.setFont("NG", 4.3)
    for i, en in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]):
        c.setFillColor(RED if i == 0 else BLUE if i == 6 else GRAY)
        c.drawCentredString(x + 6 + cw * (i + 0.5), y - 20, en)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(x + 6, y - 22.5, x + w - 6, y - 22.5)
    first = (pycal.monthrange(year, month)[0] + 1) % 7  # 일요일=0
    days = pycal.monthrange(year, month)[1]
    rh = min(7.6, (h - 28) / 6)
    c.setFont("NG", 5.3)
    for d in range(1, days + 1):
        i = first + d - 1
        col, row = i % 7, i // 7
        c.setFillColor(RED if col == 0 else BLUE if col == 6 else INK)
        c.drawCentredString(x + 6 + cw * (col + 0.5), y - 29 - row * rh, str(d))


def month_page(month, year=2027, data=None, art=True):
    import calendar as pycal
    data = data or MONTHS[month]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    L, R = 30, PAGE_W - 30

    # 머리 부분 (맨 위 40pt는 스프링 자리로 비움)
    c.setFillColor(BIG_NUM)
    c.setFont("NGEB", 64)
    c.drawString(L + 4, 482, f"{month:02d}")
    nx = L + 4 + c.stringWidth(f"{month:02d}", "NGEB", 64) + 10
    c.setFillColor(GRAY)
    c.setFont("NG", 20)
    c.drawString(nx, 512, str(year))
    c.setFillColor(GREEN2)
    c.setFont("NGB", 20)
    c.drawString(nx + c.stringWidth(f"{year} ", "NG", 20), 512, MONTH_EN[month])
    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 7.5)
    c.drawString(nx, 497, "사)한국교습소총연합회 대구광역시지회")
    c.setFillColor(GRAY)
    c.setFont("NG", 7)
    c.drawString(nx, 484, LEGEND)

    # 이달의 주요 일정 (✓ 표시, 두 줄씩 두 칸)
    ix = 372
    c.setFont("NGB", 9)
    for i, item in enumerate(data["items"]):
        col, row = i // 2, i % 2
        x = ix + col * 140
        y = 516 - row * 19
        c.setStrokeColor(RED)
        c.setLineWidth(1.1)
        c.circle(x + 3.5, y + 3, 3.6, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(x + 1.8, y + 3.1)
        p.lineTo(x + 3.2, y + 1.6)
        p.lineTo(x + 5.4, y + 4.6)
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(INK)
        size = 9
        while c.stringWidth(item, "NGB", size) > 124 and size > 6.5:
            size -= 0.25
        c.setFont("NGB", size)
        c.drawString(x + 11, y, item)
    if data["items"]:
        c.setFillColor(LIGHTGRAY)
        c.setFont("NG", 6.8)
        c.drawString(ix, 478, f"{month}월 교습소 주요 일정")

    # 오른쪽 위 그 달의 작품
    if art:
        aw, ah = 128, 84
        ax, ay = R - aw, 470
        c.drawImage(thumb(month, aw, ah), ax, ay, aw, ah)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.rect(ax, ay, aw, ah, stroke=1, fill=0)

    # 요일 줄
    cw = (R - L) / 7
    bar_y, bar_h = 440, 22
    for i, (ko, en) in enumerate(WEEK):
        c.setFillColor(RED if i == 0 else BLUE if i == 6 else WEEKDAY_BAR)
        c.rect(L + i * cw + (0 if i == 0 else 0.6), bar_y, cw - (0 if i in (0, 6) else 0.6), bar_h,
               stroke=0, fill=1)
        kw = c.stringWidth(ko, "NGB", 9.5)
        ew = c.stringWidth(en, "NG", 8)
        sx = L + i * cw + (cw - kw - 4 - ew) / 2
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("NGB", 9.5)
        c.drawString(sx, bar_y + 7.3, ko)
        c.setFillColor(HexColor("#FFFFFF") if i in (0, 6) else HexColor("#EEF2F0"))
        c.setFont("NG", 8)
        c.drawString(sx + kw + 4, bar_y + 7.3, en)

    # 날짜 칸
    first = (pycal.monthrange(year, month)[0] + 1) % 7  # 일요일=0
    days = pycal.monthrange(year, month)[1]
    rows = (first + days + 6) // 7
    top, bottom = bar_y, 36
    rh = (top - bottom) / rows
    trailing = rows * 7 - first - days
    for r in range(rows):
        y = top - r * rh
        c.setStrokeColor(HexColor("#D5DDD9"))
        c.setLineWidth(0.6)
        if r:
            c.line(L, y, R, y)
        for i in range(1, 7):  # 칸 위쪽에 짧은 세로선
            c.line(L + i * cw, y - 1, L + i * cw, y - 20)
    c.setLineWidth(0.6)
    c.line(L, bottom, R, bottom)

    for d in range(1, days + 1):
        i = first + d - 1
        col, row = i % 7, i // 7
        x = L + col * cw + 8
        y = top - row * rh - 20
        red = col == 0 or d in data["off"]
        c.setFillColor(RED if red else BLUE if col == 6 else INK)
        c.setFont("NG", 17)
        c.drawString(x, y, str(d))
        lx = x + c.stringWidth(str(d), "NG", 17) + 4
        ly = y + 1
        texts = []
        lunar = lunar_mark(year, month, d)
        if lunar:
            texts.append((lunar, GRAY))
        for t, kind in data["labels"].get(d, []):
            texts.append((t, LABEL_COLOR[kind]))
        for j, (t, col_) in enumerate(texts):
            c.setFillColor(col_)
            c.setFont("NGB" if col_ is not GRAY else "NG", 7)
            if j == 0:
                c.drawString(lx, ly, t)
            else:
                c.drawString(x, y - 11 * j, t)

    # 지난달·다음달 작은 달력: 앞쪽 빈칸에 지난달, 뒤쪽 빈칸에 다음달 (모자라면 한쪽에 둘 다)
    prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_m = (year + 1, 1) if month == 12 else (year, month + 1)
    def cell(idx):
        return L + (idx % 7) * cw, top - (idx // 7) * rh
    if first >= 1 and trailing >= 1:
        spots = [0, rows * 7 - 1]
    elif first >= 2:
        spots = [0, 1]
    else:
        spots = [rows * 7 - 2, rows * 7 - 1]
    for (yy, mm), idx in zip((prev_m, next_m), spots):
        x, y = cell(idx)
        mini_month(c, yy, mm, x + 2, y - 2, cw - 4, rh - 4)

    # 바닥글
    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 6.5)
    c.drawString(L, 20, "※ 학교 시험·대회·공모전·심사 일정은 변경될 수 있습니다. "
                        "세무·의무교육은 사업자 유형과 종사자 현황에 따라 적용사항을 확인하세요.")
    c.drawRightString(R, 20, f"사)한국교습소총연합회 대구광역시지회  ·  {year} · {month:02d}")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


# 2쪽: 지난해 12월 (2025년 달력처럼 일정·작품 없이 날짜만)
DEC_2026 = {
    "items": [],
    "labels": {7: [("대설", "term")], 22: [("동지", "term")], 25: [("성탄절", "holiday")]},
    "off": [25],
}


def year_page():
    """3쪽: 2027년 한눈에 보기 (12달 작은 달력) + AKAS 워터마크."""
    import calendar as pycal
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    tw = c.stringWidth("2027", "NGEB", 34)
    c.setFillColor(GRAY)
    c.setFont("NSKR", 12)
    lw = c.stringWidth("정미년(丁未年)  ", "NSKR", 12)
    x0 = (PAGE_W - lw - tw) / 2
    c.drawString(x0, 508, "정미년(丁未年)")
    c.setFillColor(BIG_NUM)
    c.setFont("NGEB", 34)
    c.drawString(x0 + lw, 504, "2027")

    cols, rows = 4, 3
    L, R, top, bottom = 70, PAGE_W - 70, 482, 40
    gw = (R - L) / cols
    gh = (top - bottom) / rows
    for m in range(1, 13):
        col, row = (m - 1) % cols, (m - 1) // cols
        x = L + col * gw + 14
        y = top - row * gh
        w = gw - 28
        cw = w / 7
        c.setFillColor(INK)
        num, en = f"{m} ", MONTH_EN[m]
        nw = c.stringWidth(num, "NGB", 11) + c.stringWidth(en, "NG", 10)
        c.setFont("NGB", 11)
        c.drawString(x + (w - nw) / 2, y - 12, num)
        c.setFont("NG", 10)
        c.drawString(x + (w - nw) / 2 + c.stringWidth(num, "NGB", 11), y - 12, en)
        c.setStrokeColor(GRAY)
        c.setLineWidth(0.5)
        c.line(x, y - 17, x + w, y - 17)
        c.setFont("NGB", 7.5)
        for i, d in enumerate("SMTWTFS"):
            c.setFillColor(RED if i == 0 else BLUE if i == 6 else INK)
            c.drawCentredString(x + cw * (i + 0.5), y - 27, d)
        c.line(x, y - 31, x + w, y - 31)
        first = (pycal.monthrange(2027, m)[0] + 1) % 7
        c.setFont("NG", 8.5)
        for d in range(1, pycal.monthrange(2027, m)[1] + 1):
            i = first + d - 1
            cc, rr = i % 7, i // 7
            red = cc == 0 or d in MONTHS[m]["off"]
            c.setFillColor(RED if red else BLUE if cc == 6 else INK)
            c.drawCentredString(x + cw * (cc + 0.5), y - 43 - rr * 12.5, str(d))
    c.showPage()
    c.save()
    buf.seek(0)
    page = pypdf.PdfReader(buf).pages[0]
    page.merge_page(cover_watermark())
    return page


# 3쪽 연혁: (연도, 내용) 순서대로. 비어 있으면 안내 문구만 표시
HISTORY = []


def history_page():
    """3쪽: 사)한국교습소총연합회 대구광역시지회 연혁."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.roundRect(39.685, 488, 128, 70, 11, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("NGEB", 24)
    c.drawCentredString(103.685, 514, "연혁")
    c.setFillColor(GREEN2)
    c.setFont("NGEB", 18)
    c.drawString(185.685, 534, "함께 걸어온 길")
    c.setFillColor(GRAY)
    c.setFont("NGB", 10.5)
    c.drawString(185.685, 512, "사)한국교습소총연합회 대구광역시지회")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(39.685, 470, 802.205, 470)

    if not HISTORY:
        c.setFillColor(HexColor("#C2CEC8"))
        c.setFont("NG", 11)
        c.drawCentredString(PAGE_W / 2, 280, "연혁 내용이 들어갈 자리입니다")
    else:
        # 세로 시간선 + 연도 + 내용 (많으면 두 단)
        per_col = 18
        cols = 1 if len(HISTORY) <= per_col else 2
        col_w = (802.205 - 60) / cols
        for i, (year, text) in enumerate(HISTORY):
            col, row = i // per_col, i % per_col
            x = 60 + col * col_w
            y = 448 - row * 22.5
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            if row:
                c.line(x + 52, y + 3.5 + 22.5, x + 52, y + 3.5)
            c.setFillColor(GOLD)
            c.circle(x + 52, y + 3.5, 3, stroke=0, fill=1)
            c.setFillColor(GREEN2)
            c.setFont("NGB", 10.5)
            c.drawRightString(x + 42, y, str(year))
            c.setFillColor(INK)
            c.setFont("NG", 9.5)
            c.drawString(x + 64, y, text)

    c.setFillColor(LIGHTGRAY)
    c.setFont("NG", 6.5)
    c.drawRightString(802.205, 22, "사)한국교습소총연합회 대구광역시지회  ·  연혁")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


def cover_grid():
    """표지: 작은 달력 자리에 12작품을 4x3으로 크게 놓는다 (2025년 표지처럼)."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    gap, th = 9, 88
    tw = th * 4 / 3
    x0 = (PAGE_W - (4 * tw + 3 * gap)) / 2
    top = 462
    for m in range(1, 13):
        col, row = (m - 1) % 4, (m - 1) // 4
        x = x0 + col * (tw + gap)
        y = top - (row + 1) * th - row * gap
        c.drawImage(thumb(m, tw, th), x, y, tw, th)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.4)
        c.rect(x, y, tw, th, stroke=1, fill=0)
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


# 원본 표지의 작은 달력 12개 부분 (첫 달력 상자부터 옛 로고 앞까지)
OLD_MINI_CALS_RE = re.compile(rb"q\n\.964706 \.980392 \.972549 rg\n.*?(?=q\nn 289\.0264 147 m )", re.S)


def main():
    register_fonts()
    reader = pypdf.PdfReader(SRC)
    writer = pypdf.PdfWriter()

    # 표지 (원본 1쪽을 고쳐 씀)
    writer.add_page(reader.pages[0])
    cover_page = writer.pages[0]
    cover = cover_page.get_contents().get_data()
    # 표지 부제: 월별 주요 일정 · 법정의무교육 · 세무·행정 안내
    old = (b"(\\001\\002 \\003\\004 \\005\\006 \\007 \\010\\011\\007\\012\\006 \\007 "
           b"\\013\\006\\014\\011\\015\\016 \\017\\020)")
    new = (b"(\\001\\002 \\003\\004 \\005\\006 \\007 \\013\\006\\014\\011\\015\\016 \\007 "
           b"\\010\\011\\007\\012\\006 \\017\\020)")
    assert cover.count(old) == 1
    cover = cover.replace(old, new)
    cover, n = OLD_MINI_CALS_RE.subn(b"", cover)
    assert n == 1
    cover, n = OLD_LOGO_RE.subn(b"", cover)
    assert n == 1
    # 옛 영문(Helvetica)은 지우고, 로고와 같은 기울임 글씨로 cover_logo()에서 다시 쓴다
    eng = b"BT 1 0 0 1 304.0264 135 Tm (The  Association  of  Korea  Academic  School) Tj T* ET\n"
    assert cover.count(eng) == 1
    cover = cover.replace(eng, b"")
    set_content(writer, cover_page, cover)
    cover_page.merge_page(cover_logo())
    cover_page.merge_page(cover_grid())

    # 2쪽 회원 명단, 3쪽 연혁, 4쪽 지난해 12월, 5쪽 2027년 한눈에 보기,
    # 6쪽부터 달마다 작품(앞면)·달력(뒷면), 끝에 원본 마지막 안내 쪽
    writer.add_page(member_page())
    writer.add_page(history_page())
    writer.add_page(month_page(12, year=2026, data=DEC_2026, art=False))
    writer.add_page(year_page())
    for month in range(1, 13):
        writer.add_page(artwork_page(month))
        writer.add_page(month_page(month))
    writer.add_page(reader.pages[13])
    writer.add_metadata(reader.metadata)
    with open(OUT, "wb") as f:
        writer.write(f)


main()
