# Gemeinsamer Kern (DisAHRsterRadio) und Region (HaldenFunk)

HaldenFunk ist die Regionalvariante von [DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio).
Statt zwei Kopien von Hand zu pflegen, gilt:

**HaldenFunk = DisAHRsterRadio in einer festen Revision + regionales Overlay.**

| Datei | Bedeutung |
|---|---|
| `region/CORE` | Kern-Repository und Commit, auf dem HaldenFunk aufsetzt |
| `region/own.txt` | Muster der rein regionalen Dateien (README, CHANGELOG, VERSION, Doku, Karten, Bilder, Flyer-Inhalt …) |
| `region/overlay.patch` | alle regionalen Änderungen an Kern-Dateien (Namen, WLAN/mDNS, Farben, Orte, Kartenliste, Demo, Paketpräfix, Funkprofil …) |
| `tools/core_sync.py` | Werkzeug: prüfen, Kern aktualisieren, Overlay neu erzeugen |

Versionsnummern werden vor dem Vergleich auf `0.0.0-dev` gesetzt; die Version kommt in beiden Projekten nur aus `VERSION`.

## Befehle

    python3 tools/core_sync.py --check           # CI: jede Kern-Datei == Kern + Overlay?
    python3 tools/core_sync.py --update [REF]    # neuen Kern holen (Standard main), Overlay anwenden, region/CORE setzen
    python3 tools/core_sync.py --make-patch      # nach einer gewollten regionalen Änderung an einer Kern-Datei
    # Option: --core-dir PFAD  lokaler DisAHRsterRadio-Checkout statt Download

## Ablauf

1. **Fehlerbehebung oder neue Funktion** zuerst in DisAHRsterRadio umsetzen und mergen.
2. In HaldenFunk: `python3 tools/core_sync.py --update` → bei Konflikten `*.rej` von Hand einarbeiten,
   dann `--make-patch`.
3. Bauen/testen (`pio run`, `tests/`), committen (inkl. `region/CORE`, `region/overlay.patch`).
4. **Nur HaldenFunk betrifft es** (z. B. Text, Ort, Farbe): direkt in HaldenFunk ändern und
   `python3 tools/core_sync.py --make-patch` ausführen – sonst schlägt der CI-Schritt „Kern-Abgleich“ fehl.

## Warum so (pragmatisch)

- Kein Git-Submodul und kein Paket: Arduino/PlatformIO-Firmware, Web-Oberfläche und Werkzeuge bleiben in
  beiden Repositorys direkt baubar; Releases, Pages und Flyer funktionieren unverändert.
- Der Unterschied zwischen beiden Projekten ist jederzeit als eine lesbare Datei (`region/overlay.patch`) sichtbar.
- Drift fällt in CI sofort auf (Schritt „Kern-Abgleich“ im Workflow „Firmware-Build“, nur wenn `region/CORE` existiert –
  derselbe Workflow liegt unverändert im Kern).

Stand 17.10.2026: Kern = DisAHRsterRadio 0.1.1-alpha (`7b53e3f`). Das Overlay enthält noch das neue Funkprofil
EU Narrow (HaldenFunk #5); sobald DisAHRsterRadio #10 gemergt ist, schrumpft es nach `--update` deutlich.
