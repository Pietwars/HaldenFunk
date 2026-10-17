#!/usr/bin/env python3
"""Zentrale Versionsquelle ist die Datei VERSION im Repository-Wurzelordner.

  python3 tools/version.py          schreibt alle abgeleiteten Stellen (UI-Fußzeile, Demo, Firmwarekennung, README …)
  python3 tools/version.py --check  prüft nur und bricht mit Fehler ab, wenn eine Stelle abweicht (läuft in CI)
  python3 tools/version.py --get    gibt die Version aus (für Skripte/Workflows)

Neue Version: nur VERSION ändern, dann dieses Skript ohne Argumente ausführen.
"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load():
    d = {}
    for line in (ROOT / 'VERSION').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            k, v = line.split('=', 1); d[k.strip()] = v.strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?', d.get('VERSION', '')):
        sys.exit('VERSION: ungültige oder fehlende Zeile VERSION=x.y.z[-zusatz]')
    return d

def run(rules, argv):
    vals = load()
    if '--get' in argv:
        print(vals[argv[argv.index('--get') + 1]] if len(argv) > argv.index('--get') + 1 else vals['VERSION']); return 0
    check = '--check' in argv
    bad = 0
    for path, pattern, repl, *opt in rules:
        p = ROOT / path
        if not p.exists():
            print(f'FEHLT: {path}'); bad += 1; continue
        text = p.read_text(encoding='utf-8')
        r = repl
        for k, v in vals.items(): r = r.replace('@' + k + '@', v)
        new, n = re.subn(pattern, r, text, flags=re.M)
        if n < (opt[0] if opt else 1):
            print(f'MUSTER NICHT GEFUNDEN: {path}: {pattern}'); bad += 1; continue
        if new != text:
            if check:
                old_lines = set(text.splitlines())
                for line in new.splitlines():
                    if line not in old_lines: print(f'ABWEICHUNG {path}: erwartet …{line.strip()[:160]}')
                bad += 1
            else:
                p.write_text(new, encoding='utf-8', newline='\n'); print(f'aktualisiert: {path}')
    if check:
        print('Versionen stimmen überein:' if not bad else 'Versionsprüfung fehlgeschlagen:', vals.get('VERSION'))
        if bad: print('Behebung: python3 tools/version.py ausführen und Ergebnis committen.')
    return 1 if bad else 0

ROW = r'^(\| \[Pietwars/HaldenFunk\]\(https://github\.com/Pietwars/HaldenFunk\) \| [^|]+ \| [^|]+ \| )[^|]+( \|)'
RULES = [
    ('firmware/config.h', r'^(#define DAR_VERSION ")[^"]+(")', r'\g<1>@VERSION@\g<2>'),
    ('web/static/index.html', r'(<p class="muted" id="uiver">Weboberfläche HaldenFunk )[^<]+(</p>)', r'\g<1>@VERSION@\g<2>'),
    ('web/static/index.html', r"(d=DEMO\?\{name:'HaldenFunk',version:')[^']+(')", r'\g<1>@VERSION@\g<2>'),
    ('README.md', r'^(\*\*Version )[^*]+(\*\*)', r'\g<1>@VERSION@\g<2>'),
    ('README.md', r'(HaldenFunk/\), Stand )[^;]+(; alle Daten simuliert)', r'\g<1>@VERSION@\g<2>'),
    ('README.md', ROW, r'\g<1>@VERSION@\g<2>'),
]

if __name__ == '__main__':
    sys.exit(run(RULES, sys.argv[1:]))
