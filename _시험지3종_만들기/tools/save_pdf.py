# 사용: python3 -I save_pdf.py <pdf> <폴더이름> [원래제목]
import sys,os,shutil,subprocess
S=os.environ.get('WS','/tmp/claude-0/-home-user--/84d60132-5d48-57e1-a9e4-40c41bc5565d/scratchpad'); name=sys.argv[2]
out=os.path.join(S,'school',name); os.makedirs(out+'/x/BinData',exist_ok=True)
shutil.copy(sys.argv[1],out+'/src.pdf'); open(out+'/src_title.txt','w').write(sys.argv[3] if len(sys.argv)>3 else os.path.basename(sys.argv[1]))
subprocess.run(['pdftoppm','-r','110','-png',out+'/src.pdf',out+'/page'],check=True,stderr=subprocess.DEVNULL)
print(name,'pages',len([f for f in os.listdir(out) if f.startswith('page')]))
