# 표지 PNG 한 장을 A4 전면 그림으로 넣은 HWPX 만들기: python3 mkhwpx.py <png> <out.hwpx> <제목>
import sys,os,re,shutil,zipfile
from PIL import Image
T='/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad/dgd/x'
png,out,title=sys.argv[1:4]
W,H=59528,84188  # A4 (hwpunit)
iw,ih=Image.open(png).size
s=open(T+'/Contents/section0.xml',encoding='utf-8').read()
head=s[:s.find('<hp:p ')]
sec=s[s.find('<hp:secPr'):s.find('</hp:secPr>')+len('</hp:secPr>')]
sec=re.sub(r'<hp:pagePr [^>]*>','<hp:pagePr landscape="WIDELY" width="%d" height="%d" gutterType="LEFT_ONLY">'%(W,H),sec)
sec=re.sub(r'<hp:margin [^/]*/>','<hp:margin header="0" footer="0" gutter="0" left="0" right="0" top="0" bottom="0"/>',sec)
pic=f'''<hp:pic id="100" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" instid="101" reverse="0"><hp:offset x="0" y="0"/><hp:orgSz width="{W}" height="{H}"/><hp:curSz width="{W}" height="{H}"/><hp:flip horizontal="0" vertical="0"/><hp:rotationInfo angle="0" centerX="{W//2}" centerY="{H//2}" rotateimage="1"/><hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:scaMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/><hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo><hc:img binaryItemIDRef="image1" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/><hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="{W}" y="0"/><hc:pt2 x="{W}" y="{H}"/><hc:pt3 x="0" y="{H}"/></hp:imgRect><hp:imgClip left="0" right="{iw*75}" top="0" bottom="{ih*75}"/><hp:inMargin left="0" right="0" top="0" bottom="0"/><hp:imgDim dimwidth="{iw*75}" dimheight="{ih*75}"/><hp:effects/><hp:sz width="{W}" widthRelTo="ABSOLUTE" height="{H}" heightRelTo="ABSOLUTE" protect="0"/><hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="0" allowOverlap="1" holdAnchorAndSO="0" vertRelTo="PAPER" horzRelTo="PAPER" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:shapeComment>채수학 표지</hp:shapeComment></hp:pic>'''
body=f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="0">{sec}<hp:ctrl><hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/></hp:ctrl></hp:run><hp:run charPrIDRef="0">{pic}<hp:t/></hp:run></hp:p></hs:sec>'
tmp=out+'.d'; shutil.rmtree(tmp,ignore_errors=True); shutil.copytree(T,tmp)
shutil.rmtree(tmp+'/BinData'); os.makedirs(tmp+'/BinData'); shutil.copy(png,tmp+'/BinData/cover.png')
open(tmp+'/Contents/section0.xml','w',encoding='utf-8').write(head+body)
h=open(tmp+'/Contents/content.hpf',encoding='utf-8').read()
h=re.sub(r'<opf:item id="image\d+"[^>]*/>','',h)
h=h.replace('<opf:item id="settings"','<opf:item id="image1" href="BinData/cover.png" media-type="image/png" isEmbeded="1"/><opf:item id="settings"')
h=re.sub(r'<opf:title>.*?</opf:title>','<opf:title>'+title+'</opf:title>',h)
open(tmp+'/Contents/content.hpf','w',encoding='utf-8').write(h)
hd=open(tmp+'/Contents/header.xml',encoding='utf-8').read()
print('header binItems:',re.findall(r'<hh:binData[^>]*>',hd)[:3], hd.count('binItem'))
if os.path.isdir(tmp+'/Preview'): Image.open(png).convert('RGB').resize((iw//4,ih//4)).save(tmp+'/Preview/PrvImage.png')
if os.path.exists(out): os.remove(out)
z=zipfile.ZipFile(out,'w'); z.write(tmp+'/mimetype','mimetype',compress_type=zipfile.ZIP_STORED)
for r,_,fs in os.walk(tmp):
    for f in fs:
        p=os.path.join(r,f); a=os.path.relpath(p,tmp)
        if a!='mimetype': z.write(p,a,compress_type=zipfile.ZIP_DEFLATED)
z.close(); shutil.rmtree(tmp); print('ok',out)
