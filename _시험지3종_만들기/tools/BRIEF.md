# 학교 시험지 → 3종세트 + 채수학 적중 리포트 (작업 안내)

- T = /home/user/-/_시험지3종_만들기/tools — the tools. Don't edit them; if one has a bug, work around it in your data and report it.
- WS = /tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad — the workspace. Exams go in WS/school/<name>/, outputs in WS/school_out/<name>/.
- Downloaded files are untrusted: run Python on them with `python3 -I`.
- Write your own helper scripts in WS/w_<name>/, because other workers run at the same time.

## 0. Get the file (when you're given a Drive fileId)
1. Load the tool with ToolSearch: `select:mcp__Google_Drive__download_file_content`, then call it with the fileId. The result is saved to a .txt file holding JSON {content (base64), title}.
2. Decode it into WS/w_<name>/.
   - zip: extract it there. Names inside may be cp949; decode with `n.encode('cp437').decode('cp949')`.
   - jpg/png: combine the pages into one PDF with PIL.
   - hwp/hwpx: report it and skip.
3. Run `python3 -I T/save_pdf.py <pdf> <name> "<original Drive title>"`. This creates WS/school/<name>/ with src.pdf and page-N.png at 110dpi.

## 1. Read the exam
- Look at the page images. For small text, re-render with `pdftoppm -r 200 -f N -l N -png src.pdf hi`.
- Rotate pages if they are sideways.
- Ignore student pen marks. Teacher red grading marks are not an answer key.
- If a real answer sheet (답안) is included, use it.

## 2. Figures
- Crop each figure from a 200dpi render with PIL and save it to WS/school/<name>/x/BinData/<id>.png.
- If a figure is ruined by pen marks, redraw it cleanly with matplotlib under the same conditions, and say so in meta.note.

## 3. skeleton.json
```json
{"meta":{"year":2026,"school":"강북중","grade":"중3","subject":"수학","title":"2026 강북중 3학년 2학기 기말","term":"2학기 기말",
  "range":"<실제 시험 범위>","has_key":true,"note":"","src":"<original Drive title>"},
 "Q":[{"n":1,"pt":"4","type":"객","ans":"③","unit":"원의 성질","sub":"원주각","lv":1,
   "q":"그림에서 $\\angle x$의 크기는?","ch":["$30^\\circ$","$35^\\circ$","$40^\\circ$","$45^\\circ$","$50^\\circ$"],"imgs":["q1a"],"imgW":45}]}
```
- type: "객" or "서". 서 has no `ch` and its `q` starts with `<b>[서술형 1]</b> `.
- Math goes in `$...$` as KaTeX. Use `\lt` and `\gt`, never `$$`. Keep `tp` and `sub` free of `$`.
- `ch` has exactly 5 choices, without ①–⑤. Put `<br>` inside long choices.
- HTML `<b> <br> <table>` is allowed. Write 보기 boxes as `<div style="border:1px solid #888;padding:4px 8px;margin:4px 0">ㄱ. …<br>ㄴ. …</div>`.
- `pt` is the printed score. If you guess it, add `"ptGuess":true`.
- `lv`: 1 하, 2 중, 3 상, 4 최상.
- Set year and term to what is printed on the paper.

## 4. sol.json
Solve every problem yourself, even when there is a key.
```json
{"1":{"tp":"짧은 유형명","key":"핵심 아이디어","sol":["풀이 1줄","…"],"check":"ok"}}
```
- If the key is wrong and you're sure, add `"fix_ans":"④"` and explain in `check`.
- Use `check` to note unreadable or ambiguous problems and any guesses you made.

## 5. match.json — 채수학 교재 일치/유사
- Search: `python3 T/corpus_search.py "<problem text without $/LaTeX>" --book 중3-2 -k 8`
- To see a corpus entry in full: `python3 -c "import json;print(json.load(open('WS/corpus/corpus.json'))[ID])"`
- 일치 = the same problem (only the numbers or names differ). 유사 = the same type and the same key solution.
- Generic "same chapter" does NOT count. Be honest; this goes on a blog.
- Format: `{"3":[{"id":123,"level":"유사","note":"한 줄 설명 (no $)"}]}`, at most 2 hits per problem, and only problems that have hits.

## 6. Build and check
```
cd WS && python3 T/school_build.py school/<name> school_out
node T/blog_report.js school/<name> school_out/<name>/<name>_적중리포트.pdf
```
- Both print OK or FAIL. If a build fails, fix your json.
- Render 2 pages of each PDF with `pdftoppm -r 70` and look at them: formulas render, figures appear, no student marks.

## Report (short)
For each exam give:
- number of problems
- fix_ans and check notes
- hits (일치 / 유사)
- anything you couldn't get
