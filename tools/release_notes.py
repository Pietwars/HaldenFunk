#!/usr/bin/env python3
"""Release-Text aus CHANGELOG.md (Abschnitt der Version) + feste Hinweise. Aufruf: release_notes.py <Version> <Repo> <Präfix> <Board=Name> …"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
version, repo, prefix, *boards = sys.argv[1:]
log = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
m = re.search(r'^## [^\n]*?v?' + re.escape(version) + r'\b[^\n]*\n(.*?)(?=^## |\Z)', log, re.S | re.M)
body = m.group(1).strip() if m else '(Kein eigener CHANGELOG-Abschnitt für diese Version gefunden.)'
rows = '\n'.join(f'| {n} | `{prefix}-{version}-{b}.zip` |' for b, n in (x.split('=', 1) for x in boards))
print(f"""> ⚠️ **Kein zertifiziertes Notrufsystem.** In Lebensgefahr immer **112** wählen. {'Vorabversion. ' if '-' in version else ''}T-Deck Standalone: Start, Bedienung, Tastatur, Trackball, Touch und Hilfefunktionen vom Nutzer bestätigt. GPS/Karte im Freien und umfassende Funk-/Dauertests stehen noch aus. Keine pauschale Hardwareabnahme anderer Boards.

## Änderungen
{body}

## Pakete
| Board | Datei |
|---|---|
{rows}

Jedes Paket enthält `…-factory.bin` (komplett an **0x0** flashen, z. B. mit https://espressif.github.io/esptool-js/), die Einzelteile unter `teile/`, `SHA256SUMS` und eine deutsche `ANLEITUNG.md`. **Antenne zuerst anschrauben!** Update ohne Datenverlust: nur `teile/firmware.bin` an 0x10000.

Automatisch gebaut vom Workflow „Release“ aus dem Tag `v{version}` ({repo}); vor der Veröffentlichung auf Vollständigkeit und Prüfsummen geprüft.""")
