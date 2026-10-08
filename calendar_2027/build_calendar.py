"""2027 대구광역시 교습소 탁상달력 수정 스크립트.

1) 2쪽에 회원 교습소 명단 페이지 추가
2) 표지 부제: '세무·행정'을 마지막으로 이동
3) 1~12월 범례: '세무·행정' <-> '학교시험' 자리 바꾸기
4) 2월·8월 주요 일정에서 '대구 태권도 …' 항목 삭제

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
    c.drawRightString(802.205, 22, "사)한국교습소총연합회 대구광역시지회  ·  회원 교습소")
    c.showPage()
    c.save()
    buf.seek(0)
    return pypdf.PdfReader(buf).pages[0]


# ---------------------------------------------------------------- 기존 쪽 수정
LEGEND_SEP = b"  |  "
ITEM4_RE = re.compile(  # 주요 일정 4번 항목(동그라미 + 숫자 + 글)
    rb"[.\d]+ [.\d]+ [.\d]+ rg\nn\n546\.2 474\.5 m\n.*?\(4\) Tj T\* ET\n"
    rb"[.\d]+ [.\d]+ [.\d]+ rg\nBT 1 0 0 1 553 471\.5 Tm (/F\S+ 9\.5 Tf 11\.4 TL) (\(.*?\)) Tj T\* ET\n",
    re.S)
ITEM3_TEXT_RE = re.compile(rb"(BT 1 0 0 1 553 487 Tm /F\S+ 9\.5 Tf 11\.4 TL )(\(.*?\)) Tj")
TAEKWONDO = b"(\\004\\005 \\270\\271\\272 "  # '대구 태권도 ' 글자 코드


def set_content(writer, page, data):
    s = DecodedStreamObject()
    s.set_data(data)
    page[NameObject("/Contents")] = writer._add_object(s)


def swap_legend(data):
    def fix(m):
        parts = m.group(1).split(LEGEND_SEP)
        assert len(parts) == 6, parts
        parts[2], parts[4] = parts[4], parts[2]  # 세무·행정 <-> 학교시험
        return b"(" + LEGEND_SEP.join(parts) + b") Tj"
    new, n = re.subn(rb"\(([^()\n]*  \|  [^()\n]*)\) Tj", fix, data)
    assert n == 1, n
    return new


def remove_taekwondo(data):
    m4 = ITEM4_RE.search(data)
    m3 = ITEM3_TEXT_RE.search(data)
    assert m4 and m3
    if m3.group(2).startswith(TAEKWONDO):
        # 2월: 3번이 태권도 -> 4번 글을 3번 자리로 올리고 4번 삭제
        data = data[:m3.start(2)] + m4.group(2) + data[m3.end(2):]
        m4 = ITEM4_RE.search(data)
    else:
        # 8월: 4번이 태권도 -> 4번 삭제
        assert m4.group(2).startswith(TAEKWONDO)
    return data[:m4.start()] + data[m4.end():]


def main():
    register_fonts()
    reader = pypdf.PdfReader(SRC)
    writer = pypdf.PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    pages = writer.pages

    # 표지 부제: 월별 주요 일정 · 법정의무교육 · 세무·행정 안내
    cover = pages[0].get_contents().get_data()
    old = (b"(\\001\\002 \\003\\004 \\005\\006 \\007 \\010\\011\\007\\012\\006 \\007 "
           b"\\013\\006\\014\\011\\015\\016 \\017\\020)")
    new = (b"(\\001\\002 \\003\\004 \\005\\006 \\007 \\013\\006\\014\\011\\015\\016 \\007 "
           b"\\010\\011\\007\\012\\006 \\017\\020)")
    assert cover.count(old) == 1
    set_content(writer, pages[0], cover.replace(old, new))

    for month in range(1, 13):
        page = pages[month]
        data = swap_legend(page.get_contents().get_data())
        if month in (2, 8):
            data = remove_taekwondo(data)
        set_content(writer, page, data)

    writer.insert_page(member_page(), 1)
    writer.add_metadata(reader.metadata)
    with open(OUT, "wb") as f:
        writer.write(f)


main()
