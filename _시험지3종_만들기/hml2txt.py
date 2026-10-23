import sys, re, base64, os
import xml.etree.ElementTree as ET
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
root = ET.parse(src).getroot()
# images
for b in root.iter('BINDATA'):
    fmt = 'png'
    open(os.path.join(outdir, f"bin{b.get('Id')}.{fmt}"), 'wb').write(base64.b64decode(b.text or ''))
def walk(e, buf):
    t = e.tag
    if t == 'CHAR':
        buf.append(e.text or '')
        for c in e: walk(c, buf); buf.append(c.tail or '') if c.tail else None
        return
    if t == 'EQUATION':
        sc = e.find('SCRIPT')
        buf.append(' ⟦' + (sc.text or '').strip() + '⟧ ')
        return
    if t == 'PICTURE' or t == 'IMAGE':
        img = e.find('.//IMAGE')
        if img is not None: buf.append(f" [그림 bin{img.get('BinItem')}] ")
        return
    if t == 'P':
        sub = []
        for c in e: walk(c, sub)
        s = ''.join(sub).strip()
        if s: buf.append('\n' + s)
        return
    if t == 'TAB': buf.append(' '); return
    for c in e: walk(c, buf)
buf = []
walk(root.find('BODY'), buf)
print(''.join(buf))
