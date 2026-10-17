#!/usr/bin/env python3
"""HaldenFunk: Offline-Karten fuer die Weboberflaeche direkt aus OpenStreetMap (Overpass API, ODbL 1.0).
Gleiches kompaktes Format wie tools/make_map.py:
{"name","attr","bbox","view","l":[[art,x0,y0,dx,dy,...]],"p":[[art,name,x,y]]}, Koordinaten in 1e-5 Grad."""
import json, gzip, os, sys, time, urllib.request, urllib.parse
API = os.environ.get('OVERPASS', 'https://maps.mail.ru/osm/tools/overpass/api/interpreter')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'static', 'map')
MAJOR = 'motorway|trunk|primary|secondary|tertiary|motorway_link|trunk_link|primary_link|secondary_link'
POI = {'pharmacy':'apo','hospital':'med','doctors':'med','clinic':'med','fire_station':'fw','police':'pol',
       'drinking_water':'h2o','water_point':'h2o','shelter':'sh','townhall':'amt','school':'sch'}
def q(v): return int(round(v * 1e5))
def query(bb, detail):
    s, w, n, e = bb; b = f'({s},{w},{n},{e})'
    roads = f'way[highway~"^({MAJOR}|residential|unclassified|living_street|pedestrian)$"]{b};' if detail else f'way[highway~"^({MAJOR})$"]{b};'
    extra = (f'way[highway~"^(track|path|footway)$"]{b};' if detail else '')
    places = 'city|town|village|suburb|hamlet' if detail else 'city|town|village'
    return f'''[out:json][timeout:180];(
{roads}{extra}way[railway=rail]{b};' + (f'way[waterway~"^(river|stream|canal)$"]{b};' if detail else f'way[waterway~"^(river|canal)$"]{b};') + f'way[natural=water]{b};
way[landuse=forest]{b};way[natural=wood]{b};way[man_made=spoil_heap]{b};way[landuse=landfill]{b};
node[place~"^({places})$"]{b};node[amenity~"^(pharmacy|hospital|doctors|clinic|fire_station|police|townhall|drinking_water)$"]{b};
node[man_made=mineshaft]{b};node[man_made=spoil_heap]{b};node[natural=peak][name]{b};);out geom qt;'''
def kind(t):
    h = t.get('highway')
    if h:
        if h.split('_')[0] in ('motorway','trunk','primary','secondary','tertiary'): return 'h'
        if h in ('track','path','footway'): return 'f'
        return 'r'
    if t.get('railway'): return 'rw'
    w = t.get('waterway')
    if w == 'river': return 'w'
    if w: return 's'
    if t.get('natural') == 'water': return 'wa'
    if t.get('man_made') == 'spoil_heap' or t.get('landuse') == 'landfill': return 'v'   # Halde (braun dargestellt)
    if t.get('landuse') == 'forest' or t.get('natural') == 'wood': return 'wd'
    return None
def conv(key, name, bb, detail):
    data = urllib.parse.urlencode({'data': query(bb, detail)}).encode()
    for i in range(4):
        try:
            d = json.load(urllib.request.urlopen(API, data, timeout=300)); break
        except Exception as ex:
            print('retry', key, ex); time.sleep(10)
    else: sys.exit('Overpass fehlgeschlagen')
    L, P = [], []
    for el in d['elements']:
        t = el.get('tags', {})
        if el['type'] == 'node':
            if 'place' in t: k = 'pl:' + t['place']
            elif t.get('amenity') in POI: k = POI[t['amenity']]
            elif t.get('man_made') == 'mineshaft': k = 'sch'  # Schacht
            elif t.get('man_made') == 'spoil_heap' or t.get('natural') == 'peak': k = 'pl:hamlet'
            else: continue
            if t.get('man_made') == 'mineshaft': k = 'shaft'
            P.append([k, t.get('name', ''), q(el['lon']), q(el['lat'])]); continue
        k = kind(t); g = el.get('geometry')
        if not k or not g or len(g) < 2: continue
        row, px, py = [k], 0, 0
        for i, pt in enumerate(g):
            X, Y = q(pt['lon']), q(pt['lat'])
            if i and X == px and Y == py: continue
            row += [X, Y] if i == 0 else [X - px, Y - py]; px, py = X, Y
        L.append(row)
    s, w, n, e = bb
    out = {'name': name, 'attr': '© OpenStreetMap-Mitwirkende · ODbL 1.0', 'bbox': [w, s, e, n], 'view': [w, s, e, n], 'l': L, 'p': P}
    raw = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()
    os.makedirs(OUT, exist_ok=True)
    with gzip.open(os.path.join(OUT, key + '.json.gz'), 'wb', 9) as z: z.write(raw)
    print(f'{key}: {len(L)} Linien, {len(P)} Punkte, {len(raw)//1024} KB roh')
MAPS = [
 ('mansfelder-land', 'Mansfelder Land · Goldene Aue (Übersicht)', (51.36, 10.98, 51.68, 11.62), False),
 ('sangerhausen', 'Sangerhausen (Detail)', (51.45, 11.26, 51.50, 11.35), True),
 ('eisleben', 'Lutherstadt Eisleben (Detail)', (51.51, 11.51, 51.55, 11.58), True),
 ('mansfeld-hettstedt', 'Mansfeld · Hettstedt', (51.57, 11.42, 51.67, 11.55), True),
 ('kelbra-kyffhaeuser', 'Kelbra · Roßla · Kyffhäuser', (51.40, 10.97, 51.48, 11.12), True),
]
if __name__ == '__main__':
    sel = sys.argv[1:]
    for m in MAPS:
        if not sel or m[0] in sel: conv(*m); time.sleep(5)
