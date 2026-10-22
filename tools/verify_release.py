#!/usr/bin/env python3
"""Prüft Release-Pakete vor der Veröffentlichung. Bricht ab, wenn eine Datei fehlt oder eine Prüfsumme nicht stimmt.

Aufruf: verify_release.py <Ordner> <Präfix> <Version> <fs-Datei> <Board> [<Board> …]
z. B.   verify_release.py dist DisAHRsterRadio 0.1.1-alpha littlefs.bin t3s3 t3-v161 heltec-v2
"""
import hashlib, json, sys, zipfile
from pathlib import Path
d, prefix, version, fs, *boards = sys.argv[1:]
errors = []
for b in boards:
    name = f'{prefix}-{version}-{b}'
    z = Path(d) / f'{name}.zip'
    if not z.is_file():
        errors.append(f'{z.name}: fehlt'); continue
    with zipfile.ZipFile(z) as zf:
        files = {n[len(name) + 1:]: n for n in zf.namelist() if n.startswith(name + '/') and not n.endswith('/')}
        need = [f'{name}-factory.bin', 'ANLEITUNG.md', 'SHA256SUMS', 'teile/bootloader.bin', 'teile/partitions.bin',
                'teile/boot_app0.bin', 'teile/firmware.bin', f'teile/{fs}']
        if b == 'tdeck-standalone':
            need += ['debug/firmware.elf', 'debug/firmware.map', 'debug/build.json', 'TDECK-BEDIENUNG.md']
        for n in need:
            if n not in files: errors.append(f'{z.name}: {n} fehlt')
            elif zf.getinfo(files[n]).file_size == 0: errors.append(f'{z.name}: {n} ist leer')
        if 'SHA256SUMS' in files:
            sums = zf.read(files['SHA256SUMS']).decode().split('\n')
            listed = set()
            for line in filter(None, sums):
                h, f = line.split(None, 1); f = f.lstrip('*'); listed.add(f)
                if f not in files: errors.append(f'{z.name}: {f} steht in SHA256SUMS, fehlt aber')
                elif hashlib.sha256(zf.read(files[f])).hexdigest() != h: errors.append(f'{z.name}: Prüfsumme von {f} falsch')
            for n in need:
                if n.endswith('.bin') and n not in listed: errors.append(f'{z.name}: {n} fehlt in SHA256SUMS')
        if 'ANLEITUNG.md' in files and version not in zf.read(files['ANLEITUNG.md']).decode('utf-8'):
            errors.append(f'{z.name}: ANLEITUNG.md nennt die Version {version} nicht')
        if b == 'tdeck-standalone' and all(n in files for n in ('debug/firmware.elf','debug/build.json','teile/firmware.bin')):
            digest=hashlib.sha256(zf.read(files['debug/firmware.elf'])).hexdigest()
            info=json.loads(zf.read(files['debug/build.json']))
            if digest != zf.read(files['teile/firmware.bin'])[176:208].hex() or digest != info['elf_sha256']:
                errors.append(f'{z.name}: ELF passt nicht zur Firmware')
            if info['environment'] != 'tdeck-standalone':
                errors.append(f'{z.name}: falsches Standalone-Buildprofil')
    print(f'{z.name}: {len(files)} Dateien geprüft')
if errors:
    print('\n'.join('FEHLER: ' + e for e in errors)); sys.exit(1)
print(f'Alle {len(boards)} Pakete vollständig, Prüfsummen stimmen.')
