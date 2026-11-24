# 학교 시험지: skeleton.json + sol.json → 데이터(.js) → build.js 3종 PDF
# 사용: python3 school_build.py <WS>/school/<폴더> <출력폴더>
import sys,json,os,glob,subprocess
from PIL import Image
d=os.path.abspath(sys.argv[1]); outroot=os.path.abspath(sys.argv[2])
REPO='/home/user/-/_시험지3종_만들기'; WS=os.environ.get('WS','/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad'); B=WS+'/build'
if not os.path.exists(B+'/build.js') or open(B+'/build.js').read()!=open(REPO+'/build.js').read():
    import shutil; shutil.copy(REPO+'/build.js',B+'/build.js')
sk=json.load(open(d+'/skeleton.json')); sol=json.load(open(d+'/sol.json')); m=sk['meta']
name=os.path.basename(d); imgdir=os.path.join(REPO,'img_school',name); os.makedirs(imgdir,exist_ok=True)
err=[]
for q in sk['Q']:
    if str(q['n']) not in sol: err.append(f"sol.json에 {q['n']}번 없음")
    if q.get('type')=='객' and len(q.get('ch',[]))!=5: err.append(f"{q['n']}번 보기 5개 아님")
    for i in q.get('imgs',[]):
        if not glob.glob(f"{d}/x/BinData/{i}.*"): err.append(f"{q['n']}번 그림 {i} 없음")
    if (q['q']+''.join(q.get('ch',[]))).count('$')%2: err.append(f"{q['n']}번 $ 짝 안 맞음")
if err: print(name,'FAIL',' / '.join(err)); sys.exit(1)
mid=m.get('grade','').startswith('중')
Q=[];checks=[]
for q in sk['Q']:
    s=sol[str(q['n'])]
    e={'n':q['n'],'pt':('%g' if mid else '%.2f')%float(q['pt']),'type':q['type'],'ans':s.get('fix_ans',q['ans']),'unit':q['unit'],'sub':q['sub'],
       'tp':s['tp'],'key':s['key'],'lv':q['lv'],'q':q['q'],'sol':s['sol'],'fin':s.get('fix_ans',q['ans'])}
    if q.get('ptGuess'): e['ptGuess']=True
    if q.get('alone'): e['alone']=True
    if 'ch' in q: e['ch']=q['ch']
    if q.get('imgs'):
        ims=[Image.open(glob.glob(f"{d}/x/BinData/{i}.*")[0]).convert('RGB') for i in q['imgs']]
        h=max(i.height for i in ims); W=sum(i.width for i in ims)+40*(len(ims)-1)
        c=Image.new('RGB',(W,h),'white'); x=0
        for i in ims: c.paste(i,(x,(h-i.height)//2)); x+=i.width+40
        c.save(f"{imgdir}/q{q['n']}.png"); e['__img']=f"q{q['n']}.png"; e['imgW']=s.get('imgW',q.get('imgW',55))
    if s.get('check','ok')!='ok': checks.append(f"{q['n']}번: {s['check']}")
    Q.append(e)
units={}
for q in Q: units[q['unit']]=units.get(q['unit'],0)+float(q['pt'])
note=f"<b>시험 범위</b> &nbsp;{m.get('range','')} · 원본 스캔을 옮겨 적고, 정답은 {'원본 답안과 대조' if m.get('has_key') else '채수학에서 직접 풀어'} 확인했다."
note+="<br><b>단원별 배점</b> &nbsp;"+', '.join(f"{k} {v:g}점" for k,v in units.items())
if m.get('note'): note+="<br>"+m['note']
if checks: note+="<br><b>검토 메모</b> &nbsp;"+' / '.join(checks)
yr=int(m.get('year',2026))
js=[f"// {m['title']} — 원본: {m.get('src','')}","const path = require('path');",
f"const IMG = path.join(__dirname, '..', 'img_school', {json.dumps(name)});",
"const META = "+json.dumps({'year':yr,'school':m['school'],'grade':m['grade'],'term':m.get('term','2학기 중간'),'subject':m['subject'],'title':m['title'],'units':m.get('range',''),'keyNote':'정답은 학교 답안과 대조 완료' if m.get('has_key') else '정답은 채수학에서 직접 풀어 확인'},ensure_ascii=False)+";",
"const Q = ["]
for e in Q:
    im=e.pop('__img',None); s=json.dumps(e,ensure_ascii=False)
    if im: s=s[:-1]+f', "img": path.join(IMG, "{im}")}}'
    js.append(s+',')
js.append('];')
js.append("META.note = () => "+json.dumps(note,ensure_ascii=False)+";")
js.append("const graphs = () => ({});\nmodule.exports = { META, Q, graphs };")
os.makedirs(REPO+'/학교시험',exist_ok=True)
df=f"{REPO}/학교시험/data_{name}.js"; open(df,'w').write('\n'.join(js)+'\n')
od=os.path.join(outroot,name); os.makedirs(od,exist_ok=True)
r=subprocess.run(['node','build.js',df,od],cwd=B,capture_output=True,text=True)
print(name,'OK' if r.returncode==0 else 'FAIL',r.stdout.strip().split('\n')[-1][:80],r.stderr[-400:] if r.returncode else '','| checks:',len(checks))
sys.exit(r.returncode)
