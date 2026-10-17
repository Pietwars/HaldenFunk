#!/usr/bin/env python3
"""DisAHRsterRadio / HaldenFunk Solarbox – parametrisches Gehäuse (CadQuery).
Material: Gehäuse/Deckel/Schlitten/Halter PETG, Dichtung + USB-Stopfen TPU 95A.
Aufruf: venv/bin/python cad/solarbox.py  -> stl/*.stl
Alle Maße in mm. Koordinaten Unterteil: Z=0 Außenboden (liegt an der Wand), +Y = oben (montiert).
"""
import math, os, sys
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stl')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

# ---------- Parameter ----------
IX, IY, IZ = 124.0, 96.0, 46.0      # Innenraum (B x H x T)
WALL, FLOOR = 3.0, 3.0              # Wand / Boden
R_IN = 2.0                          # Innenradius Ecken
FL = 11.0                           # Randbreite ab Innenwand (Flansch für Dichtung + Schrauben)
FL_H, FL_CH = 11.0, 8.0             # Flanschhöhe, 45°-Fase darunter (stützfrei druckbar)
G_OFF, G_W, G_D = 2.8, 2.2, 2.0     # Nut: Mitte ab Innenwand, Breite, Tiefe
GASKET_W, GASKET_H = 1.6, 1.9       # Dichtschnur (TPU), ~26 % Verpressung durch Feder
TONGUE_W, TONGUE_H = 1.4, 0.6       # Feder am Deckel
SCREW_OFF, PILOT_D, CLEAR_D = 7.5, 2.6, 3.4   # M3-Schrauben (selbstschneidend / Durchgang)
LID_T = 4.0
SKIRT_T, SKIRT_H, SKIRT_GAP = 1.6, 3.0, 0.4
# Akkuhalter MPD BK-18650-PC6 (Reichelt): 77,7 x 59,69 x 21,45
HOLD = (77.7, 59.69, 21.45); HOLD_C = (-21.0, 0.0)
# Soldered CN3791-Board 54 x 38 (hochkant)
MPPT = (38.0, 54.0); MPPT_C = (43.0, 0.0)
# T3-S3 V1.3 Leiterplatte lt. LilyGO-DXF: 27,25 x 64,59
PCB = (27.3, 64.6, 1.6); SLED_X = -21.0
PILLAR_H = 25.0                      # Schlittenauflage über Bodenoberkante
SLED_T, RAIL_H = 3.0, 5.5           # Schlittenplatte, Auflagehöhe Platine (Bauteile Unterseite!)
PCB_Y0 = -IY/2 + 1.5                # USB-Ende 1,5 mm vor Innenwand unten
USB_SLOT = (14.0, 9.0, 3.0)         # Öffnung USB-C (B x H, Radius)
GLAND_D = 12.3                      # M12x1,5 Kabelverschraubung / Druckausgleich
SMA_D = 6.6                         # SMA-Einbaubuchse 1/4"-36
TAB = (24.0, 16.0, 5.0)             # Wandlaschen

OX, OY = IX + 2*WALL, IY + 2*WALL
FX, FY = IX + 2*FL, IY + 2*FL
H = FLOOR + IZ

def rrect(w, h, r, z0, z1):
    return (cq.Workplane('XY').workplane(offset=z0).sketch().rect(w, h).vertices().fillet(r)
            .finalize().extrude(z1 - z0))

def ring(off_a, off_b, z0, z1):  # Ring zwischen zwei Offsets der Innenkontur
    a = rrect(IX + 2*off_b, IY + 2*off_b, R_IN + off_b, z0, z1)
    b = rrect(IX + 2*off_a, IY + 2*off_a, R_IN + off_a, z0 - 0.01, z1 + 0.01)
    return a.cut(b)

def screw_pts():
    x, y = IX/2 + SCREW_OFF, IY/2 + SCREW_OFF
    return [(-x, -y), (x, -y), (x, y), (-x, y), (0, -y), (0, y)]

def usb_z():
    return FLOOR + PILLAR_H + SLED_T + RAIL_H + PCB[2] + 1.6   # Buchsenmitte ~1,6 mm über PCB-Oberseite (geschätzt)

# ---------- Unterteil ----------
def unterteil():
    body = rrect(OX, OY, R_IN + WALL, 0, H)
    z_fl = H - FL_H
    fl = rrect(FX, FY, 4.0, z_fl, H)
    s1 = cq.Sketch().rect(OX, OY).vertices().fillet(R_IN + WALL)
    s2 = cq.Sketch().rect(FX, FY).vertices().fillet(4.0).moved(cq.Location(cq.Vector(0, 0, FL_CH)))
    ch = cq.Workplane('XY').workplane(offset=z_fl - FL_CH).placeSketch(s1, s2).loft()
    b = body.union(fl).union(ch)
    # Wandlaschen (Boden-Ebene, außerhalb des Dichtraums)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx*(IX/2 - 20), sy*(OY/2 + TAB[1]/2 - 2)
            t = rrect(TAB[0], TAB[1] + 4, 3, 0, TAB[2]).translate((cx, cy, 0))
            b = b.union(t)
            # Langloch Ø5,3 für Spax 4,5 / M5
            slot = (cq.Workplane('XY').center(cx, cy + sy*1.5).slot2D(9, 5.3, 0).extrude(TAB[2] + 1))
            b = b.cut(slot)
    # Innenraum
    b = b.cut(rrect(IX, IY, R_IN, FLOOR, H + 1))
    # Dichtungsnut
    b = b.cut(ring(G_OFF - G_W/2, G_OFF + G_W/2, H - G_D, H + 0.1))
    # Schraublöcher (selbstschneidend M3, Ø2,6, 11 tief)
    for (x, y) in screw_pts():
        b = b.cut(cq.Workplane('XY').workplane(offset=H - 11).center(x, y).circle(PILOT_D/2).extrude(12))
    # Schlitten-Säulen
    for x in (SLED_X - 15, SLED_X + 15):
        for y in (-IY/2 + 7, IY/2 - 10):
            p = cq.Workplane('XY').workplane(offset=FLOOR - 0.1).center(x, y).circle(4.0).extrude(PILLAR_H + 0.1)
            p = p.cut(cq.Workplane('XY').workplane(offset=FLOOR + PILLAR_H - 10).center(x, y).circle(PILOT_D/2).extrude(11))
            b = b.union(p)
    # Akkuhalter-Rahmen: 4 Eckwinkel (3 hoch) + 2 Kabelbinderbrücken
    hx, hy = HOLD[0]/2 + 0.5, HOLD[1]/2 + 0.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = HOLD_C[0] + sx*(hx + 1), HOLD_C[1] + sy*(hy + 1)
            l1 = cq.Workplane('XY').workplane(offset=FLOOR - 0.1).center(cx - sx*4, cy).rect(10, 2).extrude(3.1)
            l2 = cq.Workplane('XY').workplane(offset=FLOOR - 0.1).center(cx, cy - sy*4).rect(2, 10).extrude(3.1)
            b = b.union(l1).union(l2)
    def bridge(cx, cy, along_x=False):
        w, d = (8, 4) if not along_x else (4, 8)
        blk = cq.Workplane('XY').workplane(offset=FLOOR - 0.1).center(cx, cy).rect(w, d).extrude(4.6)
        tun = (cq.Workplane('YZ' if not along_x else 'XZ').workplane(offset=(cx if not along_x else -cy))
               .center(cy if not along_x else cx, FLOOR + 1.6).rect(5.2 if False else 3.2, 2.2).extrude(10, both=True))
        return blk.cut(tun)
    for y in (-18, 18):
        b = b.union(bridge(HOLD_C[0] - hx - 4.5, y)).union(bridge(HOLD_C[0] + hx + 4.5, y))
    # CN3791: 4 Kabelbinderbrücken
    for x in (MPPT_C[0] - MPPT[0]/2 - 4, MPPT_C[0] + MPPT[0]/2 + 4):
        for y in (-14, 14):
            if abs(x) + 4 < IX/2:
                b = b.union(bridge(x, y))
    # Wanddurchbrüche
    yb, yt = -OY/2, OY/2
    uz = usb_z()
    usb = (cq.Workplane('XZ').workplane(offset=OY/2 - WALL - 1).center(SLED_X, uz)
           .sketch().rect(USB_SLOT[0], USB_SLOT[1]).vertices().fillet(USB_SLOT[2]).finalize().extrude(WALL + 2))
    b = b.cut(usb)
    for x in (8.0, 43.0):   # Kabelverschraubung Solar + Druckausgleich
        b = b.cut(cq.Workplane('XZ').workplane(offset=OY/2 - WALL - 1).center(x, FLOOR + 13).circle(GLAND_D/2).extrude(WALL + 2))
    b = b.cut(cq.Workplane('XZ').workplane(offset=-(OY/2 - WALL - 1)).center(SLED_X, FLOOR + 30).circle(SMA_D/2).extrude(-(WALL + 2)))
    # Tropfkante-Markierung "OBEN" innen am Boden (vertieft 0,6)
    b = b.cut(cq.Workplane('XY').workplane(offset=FLOOR - 0.6).center(43, 34).text('OBEN ^', 5, 1, font='DejaVu Sans', fontPath=FONT, kind='bold', combine=False))
    return b

# ---------- Deckel ----------
def deckel(brand=None):
    # Oberseite bei Z=LID_T (außen), Unterseite Z=0 liegt auf dem Flansch
    d = rrect(FX, FY, 4.0, 0, LID_T)
    sk_o = rrect(FX + 2*(SKIRT_GAP + SKIRT_T), FY + 2*(SKIRT_GAP + SKIRT_T), 4 + SKIRT_GAP + SKIRT_T, -SKIRT_H, LID_T)
    sk_i = rrect(FX + 2*SKIRT_GAP, FY + 2*SKIRT_GAP, 4 + SKIRT_GAP, -SKIRT_H - 1, LID_T - 0.01)
    d = d.union(sk_o.cut(sk_i))
    d = d.union(ring(G_OFF - TONGUE_W/2, G_OFF + TONGUE_W/2, -TONGUE_H, 0.01))
    for (x, y) in screw_pts():
        d = d.cut(cq.Workplane('XY').workplane(offset=-1).center(x, y).circle(CLEAR_D/2).extrude(LID_T + 2))
        d = d.cut(cq.Workplane('XY').workplane(offset=LID_T - 1.2).center(x, y).circle(3.3).extrude(2))  # Kopfsenkung flach
    if brand:
        d = d.cut(branding(brand))
    return d

def _arc(cx, cy, r, w, a0, a1, z0, h):
    ann = cq.Workplane('XY').workplane(offset=z0).center(cx, cy).circle(r + w/2).circle(r - w/2).extrude(h)
    R = r + w
    pts = [(cx, cy)] + [(cx + R*1.5*math.cos(math.radians(a)), cy + R*1.5*math.sin(math.radians(a))) for a in (a0, (a0 + a1)/2, a1)]
    wedge = cq.Workplane('XY').workplane(offset=z0 - 0.1).polyline(pts).close().extrude(h + 0.2)
    return ann.intersect(wedge)

def _poly(pts, z0, h):
    return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(h)

def _bar(p, q, w, z0, h):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1); a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return (cq.Workplane('XY').workplane(offset=z0).center((x1 + x2)/2, (y1 + y2)/2)
            .transformed(rotate=(0, 0, a)).rect(L + w, w).extrude(h))

def _text(t, size, x, y, z0, h, max_x=None):
    max_x = FX/2 - 7 if max_x is None else max_x
    while True:
        w = (cq.Workplane('XY').workplane(offset=z0).center(x, y)
             .text(t, size, h, font='DejaVu Sans', fontPath=FONT, kind='bold', halign='left', valign='center', combine=False))
        if w.val().BoundingBox().xmax <= max_x or size < 3: return w
        size *= 0.95

def branding(brand):
    D = 0.8; z0 = LID_T - D
    if brand == 'haldenfunk':
        ix, iy = -FX/2 + 26, 4
        icon = _poly([(ix - 20, iy - 18), (ix - 2, iy + 6), (ix + 4, iy - 2), (ix + 4, iy - 18)], z0, D + 0.1)  # Halde
        for (p, q) in [((ix + 6, iy - 18), (ix + 12, iy + 12)), ((ix + 18, iy - 18), (ix + 12, iy + 12)),
                       ((ix + 7.5, iy - 10), (ix + 16.5, iy - 10)), ((ix + 9, iy - 2), (ix + 15, iy - 2)),
                       ((ix + 15, iy - 18), (ix + 24, iy - 2))]:
            icon = icon.union(_bar(p, q, 1.6, z0, D + 0.1))
        icon = icon.union(cq.Workplane('XY').workplane(offset=z0).center(ix + 12, iy + 13).circle(3.4).circle(2.0).extrude(D + 0.1))
        for i, r in enumerate((7, 11.5, 16)):
            icon = icon.union(_arc(ix + 12, iy + 13, r, 1.5, 35, 145, z0, D + 0.1))
        t1 = _text('HaldenFunk', 13, ix + 30, iy + 8, z0, D + 0.1)
        t2 = _text('Glück Auf · Solar-Knoten', 5.2, ix + 30.5, iy - 8, z0, D + 0.1)
        t3 = _text('Mansfelder Land', 5.2, ix + 30.5, iy - 16, z0, D + 0.1)
        return icon.union(t1).union(t2).union(t3)
    if brand == 'disahrsterradio':
        ix, iy = -FX/2 + 24, 2
        icon = _poly([(ix - 17, iy - 16), (ix - 6, iy + 2), (ix, iy - 6), (ix + 7, iy + 6), (ix + 17, iy - 16)], z0, D + 0.1)
        icon = icon.cut(_poly([(ix - 4, iy - 17), (ix + 1, iy - 11), (ix - 2, iy - 7), (ix + 3, iy - 3),
                               (ix + 4.6, iy - 4.2), (ix + 0.8, iy - 7.3), (ix + 3.6, iy - 11), (ix - 1.4, iy - 17)], z0 - 0.1, D + 0.4))  # Ahr
        icon = icon.union(cq.Workplane('XY').workplane(offset=z0).center(ix + 10, iy + 14).circle(4).extrude(D + 0.1))
        for r in (8, 12.5):
            icon = icon.union(_arc(ix + 10, iy + 14, r, 1.5, 95, 200, z0, D + 0.1))
        t1 = _text('DisAHRsterRadio', 10.5, ix + 22, iy + 8, z0, D + 0.1)
        t2 = _text('LoRa-Funknetz fürs Ahrtal', 5.2, ix + 22.5, iy - 6, z0, D + 0.1)
        t3 = _text('Solar-Knoten', 5.2, ix + 22.5, iy - 14, z0, D + 0.1)
        return icon.union(t1).union(t2).union(t3)
    raise ValueError(brand)

# ---------- Dichtung (TPU) ----------
def dichtung():
    return ring(G_OFF - GASKET_W/2, G_OFF + GASKET_W/2, 0, GASKET_H)

# ---------- USB-C-Stopfen (TPU) mit Halteband ----------
def usb_stopfen():
    w, h, r = USB_SLOT
    plug = (cq.Workplane('XY').sketch().rect(w + 0.3, h + 0.3).vertices().fillet(r).finalize().extrude(WALL - 0.4)
            .translate((0, 0, 1.5)))
    rib = (cq.Workplane('XY').workplane(offset=1.5 + WALL - 0.4).sketch().rect(w + 0.9, h + 0.9).vertices().fillet(r + 0.3)
           .finalize().extrude(0.8))   # Rastwulst hinter der Wand
    tip = (cq.Workplane('XY').workplane(offset=1.5 + WALL + 0.4).sketch().rect(w - 0.4, h - 0.4).vertices().fillet(r - 0.2)
           .finalize().extrude(1.6))
    hollow = (cq.Workplane('XY').workplane(offset=2.5).sketch().rect(w - 4, h - 4).vertices().fillet(1.5).finalize().extrude(10))
    fl = cq.Workplane('XY').sketch().rect(w + 6, h + 6).vertices().fillet(r + 2).finalize().extrude(1.5)
    p = fl.union(plug).union(rib).union(tip).cut(hollow)
    strap = cq.Workplane('XY').center(-(w + 6)/2 - 15, 0).rect(32, 4).extrude(1.2)
    eye = cq.Workplane('XY').center(-(w + 6)/2 - 37, 0).circle(9).circle(6.2).extrude(1.2)   # Öse über M12-Verschraubung
    tab = cq.Workplane('XY').center((w + 6)/2 + 3, 0).rect(8, 6).extrude(1.5)              # Griffnase
    return p.union(strap).union(eye).union(tab)

# ---------- Platinen-Schlitten (PETG) ----------
def schlitten():
    L = (IY/2 - 10) - (-IY/2 + 7) + 12
    y0 = (-IY/2 + 7) - 6
    s = cq.Workplane('XY').center(0, y0 + L/2).rect(40, L).extrude(SLED_T)
    for x in (-15, 15):
        for y in (-IY/2 + 7, IY/2 - 10):
            s = s.cut(cq.Workplane('XY').center(x, y).circle(CLEAR_D/2).extrude(SLED_T + 1))
    # Auflageleisten unter den PCB-Längskanten + Anschlag am Antennenende
    py0 = PCB_Y0; py1 = PCB_Y0 + PCB[1]
    for sx in (-1, 1):
        x_in = sx*(PCB[0]/2 - 1.2)
        rail = cq.Workplane('XY').workplane(offset=SLED_T).center(sx*(PCB[0]/2 + 0.2), (py0 + py1)/2).rect(3.2, PCB[1] - 4).extrude(RAIL_H)
        lip = cq.Workplane('XY').workplane(offset=SLED_T).center(sx*(PCB[0]/2 + 1.8 + 0.3), (py0 + py1)/2).rect(1.6, PCB[1] - 4).extrude(RAIL_H + PCB[2] + 1.0)
        s = s.union(rail).union(lip)
    # Kabelbinder-Schlitze (Niederhalter)
    for y in (py0 + 14, py1 - 14):
        for sx in (-1, 1):
            s = s.cut(cq.Workplane('XY').center(sx*(PCB[0]/2 + 6), y).rect(2.2, 4.2).extrude(SLED_T + 1))
    s = s.cut(cq.Workplane('XY').center(0, (py0 + py1)/2).rect(14, 30).extrude(SLED_T + 1))  # Belüftung/Kabeldurchführung
    return s

# ---------- Solarhalter (PETG, 2 Stück je Panel) ----------
ANGLES = (30, 45, 60, 70)
def halter_wand():
    """Wandteil: Grundplatte (an Wand/Mast) + 2 Gelenkwangen. Gelenkachse = X, Achse 46 mm vor der Wand.
    Rasterlöcher r=14 um die Achse für Paneel-Neigung 30/45/60/70° (Ø4,4 Stift/M4-Schraube)."""
    base = rrect(70, 60, 4, 0, 6)
    for x in (-25, 25):
        for y in (-20, 20):
            base = base.cut(cq.Workplane('XY').center(x, y).circle(2.75).extrude(7))
            base = base.cut(cq.Workplane('XY').workplane(offset=3.5).center(x, y).circle(5).extrude(3))
    for y in (-8, 8):   # Schlitze für Schlauchschellen (Mastmontage)
        base = base.cut(cq.Workplane('XY').center(0, y).rect(24, 4).extrude(7))
    PZ = 46.0
    for sx in (-1, 1):
        x0 = sx*9.6 - 3
        lug = cq.Workplane('YZ').workplane(offset=x0).polyline([(-26, 5), (26, 5), (21, PZ), (-21, PZ)]).close().extrude(6)
        lug = lug.union(cq.Workplane('YZ').workplane(offset=x0).center(0, PZ).circle(21).extrude(6))
        base = base.union(lug)
    base = base.cut(cq.Workplane('YZ').workplane(offset=-20).center(0, PZ).circle(2.7).extrude(40))
    for t in ANGLES:
        base = base.cut(cq.Workplane('YZ').workplane(offset=-20).center(14*math.cos(math.radians(t)), PZ + 14*math.sin(math.radians(t))).circle(2.2).extrude(40))
    return base

def halter_arm():
    arm = rrect(130, 36, 4, 0, 5)
    for x in (-55, -35, 35, 55):
        arm = arm.cut(cq.Workplane('XY').center(x, 0).slot2D(16, 4.5, 90).extrude(6))
    tongue = (cq.Workplane('YZ').workplane(offset=-6.4).center(0, 5).polyline([(-16, 0), (16, 0), (8, 22), (-8, 22)]).close().extrude(12.8))
    tongue = tongue.union(cq.Workplane('YZ').workplane(offset=-6.4).center(0, 27).circle(9).extrude(12.8))
    tongue = tongue.union(cq.Workplane('YZ').workplane(offset=-6.4).center(0, 27).rect(26, 4).extrude(12.8))
    arm = arm.union(tongue)
    pv = (0, 27)
    arm = arm.cut(cq.Workplane('YZ').workplane(offset=-10).center(*pv).circle(2.7).extrude(20))
    arm = arm.cut(cq.Workplane('YZ').workplane(offset=-10).center(pv[0], pv[1] - 14).circle(2.2).extrude(20))
    return arm

def export(shape, name):
    path = os.path.join(OUT, name)
    cq.exporters.export(shape, path, tolerance=0.05, angularTolerance=0.15)
    print('STL', path)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    jobs = {
        'gehaeuse_unterteil.stl': unterteil,
        'gehaeuse_deckel.stl': lambda: deckel(None),
        'gehaeuse_deckel_haldenfunk.stl': lambda: deckel('haldenfunk'),
        'gehaeuse_deckel_disahrsterradio.stl': lambda: deckel('disahrsterradio'),
        'dichtung_tpu.stl': dichtung,
        'usb_stopfen_tpu.stl': usb_stopfen,
        'platinenschlitten.stl': schlitten,
        'solar_halter_wand.stl': halter_wand,
        'solar_halter_arm.stl': halter_arm,
    }
    for n, f in jobs.items():
        if only and not any(o in n for o in only): continue
        export(f(), n)
