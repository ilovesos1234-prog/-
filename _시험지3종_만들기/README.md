# 시험지 3종 만들기 (클라우드용)

학교 시험지 PDF 하나로 3종(시험지 B4 · 손풀이 A4 · 분석표 A4)을 PDF로 만든다.
시험지는 「채수학 B4 시험지 틀」(2026.09.19)을 따른다.

```
npm i katex@0.16.11 @fontsource/nanum-myeongjo@5.0.13 @fontsource/nanum-gothic@5.0.13 @fontsource/nanum-pen-script@5.0.12
node build.js data_김천고_2026_1기말.js <출력폴더>
```

- `build.js` — 세 가지를 짜는 곳(학교와 상관없음)
- `data_○○.js` — 학교마다 문항·선택지·풀이·단원·난이도·배점·그림·총평
