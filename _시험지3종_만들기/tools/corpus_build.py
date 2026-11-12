# 채수학 개념서 문제편 HTML → corpus.json(검색용) + corpus_html.json(원본 HTML) + book.css
# 사용: python3 corpus_build.py <html폴더> <출력폴더>
import glob,json,os,sys
from bs4 import BeautifulSoup
src,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
out=[];htm=[];css=''
for f in sorted(glob.glob(os.path.join(src,'*.html'))):
    book=os.path.basename(f).replace('채수학_개념서 문제편_','').replace('_본문.html','')
    soup=BeautifulSoup(open(f,encoding='utf-8').read(),'html.parser')
    if not css and soup.select_one('style'): css=soup.select_one('style').get_text()
    for pg in soup.select('section.page'):
        chap=pg.select_one('.chap').get_text(strip=True) if pg.select_one('.chap') else ''
        st=pg.select_one('.band .st'); tt=pg.select_one('.band .tt')
        step=((st.get_text(strip=True) if st else '')+' '+(tt.get_text(strip=True) if tt else '')).strip()
        pn=pg.select_one('.pn'); pn=''.join(ch for ch in pn.get_text() if ch.isdigit()) if pn else ''
        for q in pg.select('div.q'):
            qn=q.select_one('.qn'); qt=q.select_one('.qt')
            if not qn or not qt: continue
            tag=q.select_one('.tag')
            ch=[c.get_text(' ',strip=True) for c in q.select('.chs span')]
            rec={'book':book,'chap':chap,'step':step,'page':pn,'no':qn.get_text(strip=True),
                 'tag':tag.get_text(strip=True) if tag else '','text':qt.get_text(' ',strip=True),'ch':ch,'fig':bool(q.select('.fgw'))}
            for x in q.select('.wk'): x.decompose()
            for x in q.select('.tag'): x.decompose()
            if q.has_attr('style'): del q['style']
            out.append(rec); htm.append(str(q))
json.dump(out,open(os.path.join(dst,'corpus.json'),'w'),ensure_ascii=False)
json.dump(htm,open(os.path.join(dst,'corpus_html.json'),'w'),ensure_ascii=False)
open(os.path.join(dst,'book.css'),'w').write(css)
import collections; print(len(out),collections.Counter(o['book'] for o in out))
