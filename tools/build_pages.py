#!/usr/bin/env python3
"""Baut die Live-Demo (GitHub Pages): Weboberflaeche im Demo-Modus, Karten entpackt, Hinweisbanner."""
import gzip,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=dict(l.split('=',1) for l in (ROOT/'VERSION').read_text().split()).get('VERSION')  # zentrale Versionsquelle
SRC=ROOT/'web/static'; OUT=Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'_site')
if OUT.exists(): shutil.rmtree(OUT)
shutil.copytree(SRC,OUT)
for gz in (OUT/'map').glob('*.json.gz'):
    (OUT/'map'/gz.name[:-3]).write_bytes(gzip.decompress(gz.read_bytes()))
html=(OUT/'index.html').read_text(encoding='utf-8')
force='<script>if(!/demo/.test(location.search))location.replace("?demo=1"+location.hash)</script>'
banner=('<div style="background:#c87533;color:#1a0f08;text-align:center;'
        'font:600 13px/16px system-ui,sans-serif;padding:6px 8px;height:28px;box-sizing:border-box;white-space:nowrap;overflow:hidden">Demo '+VERSION+' – simulierte Daten · '
        '<a style="color:#1a0f08" href="https://github.com/Pietwars/HaldenFunk">Quellcode &amp; Firmware</a> · '
        '<a style="color:#1a0f08" href="flyer/HaldenFunk-Flyer-digital.pdf">Flyer</a></div>')
html=html.replace('<head>','<head>'+force,1)
i=html.index('<body'); j=html.index('>',i)+1
html=html[:j]+banner+html[j:]
(OUT/'index.html').write_text(html,encoding='utf-8')
if (ROOT/'docs/flyer').is_dir(): shutil.copytree(ROOT/'docs/flyer',OUT/'flyer')
(OUT/'.nojekyll').write_text('')
print('Demo gebaut:',OUT)
