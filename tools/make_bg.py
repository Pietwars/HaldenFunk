#!/usr/bin/env python3
"""HaldenFunk: erzeugt das Hintergrundbild (Halden, Förderturm als Mesh-Knoten, Funkwellen) und das Icon. Eigenes Werk (CC0)."""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'static')
W, H, S = 1083, 722, 2
w, h = W*S, H*S
random.seed(7)
img = Image.new('RGB', (w, h))
d = ImageDraw.Draw(img)
top, mid, bot = (14,16,20), (46,34,30), (120,64,36)   # Anthrazit -> Kupferglut am Horizont
for y in range(h):
    t = y/h
    c = [int(top[i]+(mid[i]-top[i])*min(1,t/0.55)) for i in range(3)] if t < .55 else [int(mid[i]+(bot[i]-mid[i])*((t-.55)/.45)) for i in range(3)]
    d.line([(0,y),(w,y)], fill=tuple(c))
for _ in range(260):  # Sterne
    x, y = random.randrange(w), random.randrange(int(h*.5)); r = random.choice([1,1,2,2,3])
    d.ellipse([x,y,x+r,y+r], fill=(230,220,200))
glow = Image.new('L', (w,h), 0); gd = ImageDraw.Draw(glow)
gd.ellipse([w*.15,h*.55,w*.85,h*1.25], fill=150); glow = glow.filter(ImageFilter.GaussianBlur(160))
img = Image.composite(Image.new('RGB',(w,h),(196,110,58)), img, glow)
d = ImageDraw.Draw(img)
def heap(cx, base, hw, ht, col, flat=0):   # Spitzkegelhalde (Hohe Linde, Wimmelburg …) bzw. Flachhalde
    pts = [(cx-hw, base)]
    for i in range(41):
        t = i/40; x = cx-hw+2*hw*t
        y = base-ht*(1-abs(2*t-1))**1.05 if not flat else base-ht*min(1,(1-abs(2*t-1))*3)
        pts.append((x, y+random.uniform(-2,2)))
    pts.append((cx+hw, base)); d.polygon(pts, fill=col)
far, nearc = (58,44,42), (30,26,28)
heap(w*.12, h*.86, 230, 300, far); heap(w*.86, h*.86, 260, 360, far); heap(w*.62, h*.88, 360, 120, far, flat=1)
heap(w*.30, h*.92, 330, 470, nearc)   # große Spitzkegelhalde
heap(w*.97, h*.93, 240, 250, nearc)
d.rectangle([0,h*.88,w,h], fill=(22,20,22))
for x in range(0, w, 6):
    d.line([(x,h*.88),(x,h*.88-random.uniform(0,10))], fill=(22,20,22), width=3)
# Förderturm (Doppelbock-Strebengerüst) als Mesh-Knoten
cx, base = w*.66, h*.885; tw, th = 110, 520
cu, cud = (205,121,68), (150,82,46)
def L(a,b,wd=9,c=cu): d.line([a,b], fill=c, width=wd)
lf, rf, tl, tr = (cx-tw,base), (cx+tw,base), (cx-38,base-th), (cx+38,base-th)
L(lf,tl,12); L(rf,tr,12)
for i in range(1,8):
    t0, t1 = (i-1)/7, i/7
    p = lambda a,b,t:(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
    L(p(lf,tl,t0), p(rf,tr,t1), 5, cud); L(p(rf,tr,t0), p(lf,tl,t1), 5, cud); L(p(lf,tl,t1), p(rf,tr,t1), 5, cud)
L((cx+tw*2.4, base), (cx+30, base-th*.82), 11)  # Strebe
d.rectangle([cx-230, base-150, cx-60, base], fill=(40,32,30)); d.rectangle([cx-215, base-210, cx-150, base-150], fill=(40,32,30))
for k in range(4): d.rectangle([cx-215+k*40, base-115, cx-195+k*40, base-85], fill=(230,170,90))
for sx in (-1,1):  # Seilscheiben
    c0 = (cx+sx*32, base-th-6); d.ellipse([c0[0]-48,c0[1]-48,c0[0]+48,c0[1]+48], outline=cu, width=9)
    for a in range(0,360,45): L(c0,(c0[0]+44*math.cos(math.radians(a)), c0[1]+44*math.sin(math.radians(a))),4)
ant = (cx, base-th-60); L((cx,base-th),ant,6,(240,170,100)); d.ellipse([ant[0]-14,ant[1]-14,ant[0]+14,ant[1]+14], fill=(255,190,110))
wav = Image.new('RGBA',(w,h)); wd = ImageDraw.Draw(wav)   # Funkwellen
for i,r in enumerate(range(90, 640, 95)):
    a = max(30, 200-i*30); wd.arc([ant[0]-r,ant[1]-r,ant[0]+r,ant[1]+r], 200, 340, fill=(232,150,86,a), width=10)
# weitere Knoten auf den Halden, Mesh-Linien
nodes = [(w*.30, h*.92-470), (w*.86, h*.86-360), (w*.12, h*.86-300), ant]
for a in nodes:
    for b in nodes:
        if a < b: wd.line([a,b], fill=(232,150,86,70), width=4)
for n in nodes[:3]:
    wd.ellipse([n[0]-12,n[1]-12,n[0]+12,n[1]+12], fill=(255,190,110,255))
    for r in (40,75): wd.arc([n[0]-r,n[1]-r,n[0]+r,n[1]+r], 210, 330, fill=(232,150,86,120), width=6)
wav = wav.filter(ImageFilter.GaussianBlur(1.2)); img.paste(wav, (0,0), wav)
img = img.resize((W,H), Image.LANCZOS)
img.save(os.path.join(OUT,'bg.jpg'), quality=82, optimize=True, progressive=True); img.save(os.path.join(OUT,'bg.webp'), quality=78)
ic = Image.new('RGBA',(256,256),(30,26,28,255)); id_ = ImageDraw.Draw(ic)
id_.polygon([(10,236),(90,90),(170,236)], fill=(70,52,46)); id_.polygon([(120,236),(190,150),(250,236)], fill=(70,52,46))
id_.line([(150,236),(170,80)], fill=cu, width=10); id_.line([(210,236),(186,80)], fill=cu, width=10); id_.line([(158,170),(204,170)], fill=cu, width=7)
id_.ellipse([166,48,192,74], fill=(255,190,110))
for r in (30,52,74): id_.arc([179-r,61-r,179+r,61+r], 200, 340, fill=(232,150,86), width=7)
ic.resize((64,64), Image.LANCZOS).save(os.path.join(OUT,'icon.png'))
print('ok')
