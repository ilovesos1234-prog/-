import json,collections,sys
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment,PatternFill,Border,Side
from openpyxl.utils import get_column_letter
idx=json.load(open('/home/user/chaemath-app/exams/index.json'));D=idx['items']
cols=sorted({(x['year'],x['term'],x['exam']) for x in D},key=lambda k:(-k[0],k[1],k[2]!='중간'))
S=collections.defaultdict(lambda:collections.defaultdict(set))
for x in D: S[x['school']][(x['year'],x['term'],x['exam'])].add(int(x['grade'][1]))
kind=lambda s:'중' if s.endswith('중') or '중학' in s else '고'
gr={}
for x in D: gr[x['school']]=x['grade'][0]
rows=sorted(S,key=lambda s:(gr[s]!='중',s))
def cell(s,c):
  g=S[s].get(c); return '·'.join(map(str,sorted(g))) if g else ''
data=[]
for s in rows:
  ys=sorted({c[0] for c in S[s]},reverse=True)
  data.append([s,'중학교' if gr[s]=='중' else '고등학교',', '.join(map(str,ys))]+[cell(s,c) for c in cols]+[sum(len(v) for v in S[s].values())])
json.dump({'cols':cols,'data':data,'updated':idx['updated'],'n':len(D)},open('tab.json','w'),ensure_ascii=False)
# xlsx
wb=Workbook();ws=wb.active;ws.title='학교별'
thin=Side(style='thin',color='999999');B=Border(left=thin,right=thin,top=thin,bottom=thin)
H1=['학교','구분','있는 년도']+[str(c[0]) for c in cols]+['합계'];H2=['','','']+[f'{c[1]}학기 {c[2]}' for c in cols]+['']
ws.append(H1);ws.append(H2)
for i in (1,2,3,len(H1)): ws.merge_cells(start_row=1,start_column=i,end_row=2,end_column=i)
c0=4
while c0<4+len(cols):
  c1=c0
  while c1+1<4+len(cols) and cols[c1+1-4][0]==cols[c0-4][0]: c1+=1
  if c1>c0: ws.merge_cells(start_row=1,start_column=c0,end_row=1,end_column=c1)
  c0=c1+1
for r in data: ws.append(r)
gray=PatternFill('solid',fgColor='E8E8E8');hit=PatternFill('solid',fgColor='DDEBF7')
for row in ws.iter_rows(min_row=1,max_row=ws.max_row,max_col=len(H1)):
  for c in row:
    c.border=B;c.alignment=Alignment(horizontal='center',vertical='center')
    if c.row<=2: c.font=Font(bold=True);c.fill=gray
    elif 4<=c.column<4+len(cols) and c.value: c.fill=hit
ws.column_dimensions['A'].width=16;ws.column_dimensions['B'].width=9;ws.column_dimensions['C'].width=18
for i in range(4,len(H1)+1): ws.column_dimensions[get_column_letter(i)].width=10
ws.freeze_panes='D3';ws.auto_filter.ref=f'A2:{get_column_letter(len(H1))}{ws.max_row}'
ws2=wb.create_sheet('설명');ws2.append(['칸 안의 숫자 = 그 시험이 있는 학년 (예: 1·3 → 1학년, 3학년)']);ws2.append([f'기출방 기준일 {idx["updated"]}, 시험지 {len(D)}개, 학교 {len(data)}곳'])
wb.save(sys.argv[1]);print(len(data),cols)
