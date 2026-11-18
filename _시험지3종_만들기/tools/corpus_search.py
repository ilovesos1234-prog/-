# 채수학 개념서 문제 검색: python3 corpus_search.py "<문제 글>" [--book 중3-2] [-k 8]
import json,re,math,os,collections,argparse
ap=argparse.ArgumentParser(); ap.add_argument('q'); ap.add_argument('--book',default=''); ap.add_argument('-k',type=int,default=8)
a=ap.parse_args()
C=json.load(open(os.path.join(os.environ.get('CS_DATA','/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/corpus'),'corpus.json')))
def norm(s): return re.sub(r'\s+','',re.sub(r'[\$\\{}]|dfrac|overline|angle|circ|times','',s))
def grams(s):
    s=norm(s); return collections.Counter(s[i:i+2] for i in range(len(s)-1))
q=grams(a.q); qn=math.sqrt(sum(v*v for v in q.values())) or 1
res=[]
for i,c in enumerate(C):
    if a.book and a.book not in c['book']: continue
    g=grams(c['text']+' '+' '.join(c['ch'][:5])); n=math.sqrt(sum(v*v for v in g.values())) or 1
    res.append((sum(v*g[k] for k,v in q.items() if k in g)/qn/n,i))
for sc,i in sorted(res,reverse=True)[:a.k]:
    c=C[i]; print(f"[{sc:.2f}] id={i} | {c['book']} p.{c['page']} {c['step']} #{c['no']} ({c['tag']})\n      {c['text'][:160]}  {' '.join(c['ch'][:5])[:80]}{'  [그림]' if c['fig'] else ''}")
