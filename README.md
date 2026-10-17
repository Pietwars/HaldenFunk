# HaldenFunk

> **Aktueller Stand:** offenes WLAN `HaldenFunk-XXXXXX` → `http://192.168.4.1` bzw. `http://haldenfunk.local` – einfach verbinden, nichts eingeben. Zusätzliche `*-ble`-Testprofile bieten BLE-UART ohne PIN. [Zugang, Update und Abnahme](docs/OFFENER_ZUGANG.md).


**Glück Auf – Mesh fürs Mansfelder Land**

**🔴 Live-Demo (simulierte Daten, kein Gerät nötig): https://pietwars.github.io/HaldenFunk/**

![HaldenFunk – Halden, Förderturm und Funkwellen](docs/images/haldenfunk-header.jpg)

**Version 0.1.1-alpha** (Vorabversion) · [Release v0.1.1-alpha mit Firmware](https://github.com/Pietwars/HaldenFunk/releases/tag/v0.1.1-alpha) · disaster-radio/LoRaLayer2 + RadioLib 7 · 868 MHz · **Flyer (A5):** [Druck-PDF mit QR-Codes](docs/flyer/HaldenFunk-Flyer.pdf) · [Digital-PDF mit klickbaren Links](docs/flyer/HaldenFunk-Flyer-digital.pdf) · [Änderungen](CHANGELOG.md)

**Offline-Chat über LoRa-Mesh für Sangerhausen, das Mansfelder Land, die Goldene Aue und den Harzrand.** Ein Gerät spannt ein eigenes WLAN auf, man verbindet sich mit dem Handy und schreibt im Browser. Die Nachrichten laufen per LoRa von Gerät zu Gerät weiter – ganz ohne Internet, Strom aus der Steckdose oder Mobilfunk. Ideale Standorte für Knoten: Halden, Fördertürme, Kirchtürme, Dächer am Harzrand.

HaldenFunk ist die **Regionalvariante von [Pietwars/DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio)** (ein modernisierter Fork von [sudomesh/disaster-radio](https://github.com/sudomesh/disaster-radio), **ohne MeshCore**). Technik und Funkprotokoll sind identisch – HaldenFunk-Geräte verstehen sich mit DisAHRsterRadio-Geräten auf gleicher Frequenz. Neu sind Name, Gestaltung, Ortsliste und Karten.

> ⚠️ **Wichtig:** HaldenFunk ist **kein zertifiziertes Notrufsystem** und ersetzt keine Behörden-Kommunikation. In Lebensgefahr immer **112** wählen, wenn irgendwie möglich.

<!-- projektfamilie:start (in allen fünf Repositorys identisch; erzeugt mit DisasterMesh/tools/projektfamilie.py) -->
### Projektfamilie DisAHRsterRadio / HaldenFunk

| Repository | Inhalt | Funk | Version | Demo · Download · Flyer |
|---|---|---|---|---|
| [Pietwars/DisasterMesh](https://github.com/Pietwars/DisasterMesh) | Original-Repo: MeshCore 1.18 mit der großen Weboberfläche MeshAhrtal, Karten, Werkzeuge, Doku (Ahrtal) | MeshCore | 0.9.0-alpha | [Live-Demo](https://pietwars.github.io/DisasterMesh/demo/) · [Release v0.9.0-alpha](https://github.com/Pietwars/DisasterMesh/releases/tag/v0.9.0-alpha) · Flyer [Druck](https://pietwars.github.io/DisasterMesh/flyer/DisasterMesh-Flyer.pdf) / [digital](https://pietwars.github.io/DisasterMesh/flyer/DisasterMesh-Flyer-digital.pdf) |
| [Pietwars/DisAHRsterRadio-MeshCore](https://github.com/Pietwars/DisAHRsterRadio-MeshCore) | MeshCore 1.18 mit kompakter MeshAhrtal-Oberfläche per WLAN plus Bluetooth für die MeshCore-App, 105 Geräte (Ahrtal) | MeshCore | 0.9.0-alpha | [Live-Demo](https://pietwars.github.io/DisAHRsterRadio-MeshCore/) · [Release v0.9.0-alpha](https://github.com/Pietwars/DisAHRsterRadio-MeshCore/releases/tag/v0.9.0-alpha) · Flyer [Druck](https://pietwars.github.io/DisAHRsterRadio-MeshCore/flyer/DisAHRsterRadio-MeshCore-Flyer.pdf) / [digital](https://pietwars.github.io/DisAHRsterRadio-MeshCore/flyer/DisAHRsterRadio-MeshCore-Flyer-digital.pdf) |
| [Pietwars/DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio) | Ohne MeshCore: modernisiertes disaster-radio (LoRaLayer2, RadioLib) mit kompakter MeshAhrtal-Oberfläche (Ahrtal) | LoRaLayer2 | 0.1.1-alpha | [Live-Demo](https://pietwars.github.io/DisAHRsterRadio/) · [Release v0.1.1-alpha](https://github.com/Pietwars/DisAHRsterRadio/releases/tag/v0.1.1-alpha) · Flyer [Druck](https://pietwars.github.io/DisAHRsterRadio/flyer/DisAHRsterRadio-Flyer.pdf) / [digital](https://pietwars.github.io/DisAHRsterRadio/flyer/DisAHRsterRadio-Flyer-digital.pdf) |
| [Pietwars/HaldenFunk](https://github.com/Pietwars/HaldenFunk) | Regionalvariante von DisAHRsterRadio für Sangerhausen / Mansfelder Land, ohne MeshCore | LoRaLayer2 | 0.1.1-alpha | [Live-Demo](https://pietwars.github.io/HaldenFunk/) · [Release v0.1.1-alpha](https://github.com/Pietwars/HaldenFunk/releases/tag/v0.1.1-alpha) · Flyer [Druck](https://pietwars.github.io/HaldenFunk/flyer/HaldenFunk-Flyer.pdf) / [digital](https://pietwars.github.io/HaldenFunk/flyer/HaldenFunk-Flyer-digital.pdf) |
| [Pietwars/HaldenFunk-MeshCore](https://github.com/Pietwars/HaldenFunk-MeshCore) | Regionalvariante von DisAHRsterRadio-MeshCore für das Mansfelder Land: MeshCore 1.18, WLAN + Bluetooth, Gerätematrix | MeshCore | 0.1.1-alpha | [Live-Demo](https://pietwars.github.io/HaldenFunk-MeshCore/) · [Release v0.1.0-alpha](https://github.com/Pietwars/HaldenFunk-MeshCore/releases/tag/v0.1.0-alpha) · Flyer [Druck](https://pietwars.github.io/HaldenFunk-MeshCore/flyer/HaldenFunk-MeshCore-Flyer.pdf) / [digital](https://pietwars.github.io/HaldenFunk-MeshCore/flyer/HaldenFunk-MeshCore-Flyer-digital.pdf) |

Gleiche Spalte **Funk** = Geräte können miteinander funken (gleiches Funkprofil vorausgesetzt). MeshCore- und LoRaLayer2-Varianten verstehen sich **nicht**.

**Namen:** **DisAHRsterRadio** = Projekt und Marke (WLAN `DisAHRsterRadio-XXXXXX`) · **MeshAhrtal** = die Weboberfläche im Handy-Browser · **DisasterMesh** = das Original-Repository · **HaldenFunk** = Regionalvariante fürs Mansfelder Land (WLAN `HaldenFunk-XXXXXX`).

Haupt-Boards: LILYGO T3-S3 V1.3, LILYGO T3 V1.6.1 (TTGO), Heltec WiFi LoRa 32 V2 – alle 868 MHz; Hardware-Abnahme steht aus (bisher lief nur LILYGO T3 V1.6.1 mit DisAHRsterRadio beim Nutzer). Druck-Flyer haben QR-Codes, digitale Flyer klickbare Links. Alle Demos sind simuliert.

> ⚠️ Prototyp, kein zertifiziertes Notrufsystem. **Im Notfall immer 112.**
<!-- projektfamilie:end -->

## Ehrlicher Stand (Oktober 2026)

| Punkt | Stand |
|---|---|
| Firmware baut für alle 3 Boards | ✅ CI „Firmware-Build“ (4 Profile inkl. Heltec-Alternative); Pakete im Release |
| Auf echter Hardware getestet | ❌ HaldenFunk selbst noch nicht; die gleiche Basis lief bei DisAHRsterRadio auf einem LILYGO T3 V1.6.1 |
| Funkverbindung zwischen zwei Geräten | ❓ ungetestet |
| Kompatibel mit DisAHRsterRadio | ✅ gleiches Protokoll und gleiche Standardfrequenz |
| Kompatibel mit MeshCore/Meshtastic | ❌ nein |

## Unterstützte Boards

| PlatformIO-Env | Board | Funkchip | Paket im Release |
|---|---|---|---|
| `t3s3-sx1262` | LILYGO T3-S3 | SX1262 | `HaldenFunk-t3s3.zip` |
| `t3-v161-sx1276` | LILYGO / TTGO T3 V1.6.1 | SX1276 | `HaldenFunk-t3-v161.zip` |
| `heltec-v2-sx1276` | Heltec WiFi LoRa 32 V2 | SX1276 | `HaldenFunk-heltec-v2.zip` |
| `heltec-v2-sx1276-wifi11` | Heltec WiFi LoRa 32 V2, WLAN mit 11 statt 8,5 dBm (falls das WLAN zu schwach ist) | SX1276 | – (nur CI-Artefakt / selbst bauen) |

Jedes ZIP enthält `factory.bin` (ab Adresse 0x0), die Einzelteile, `SHA256SUMS` und eine `ANLEITUNG.md` (Flashen im Browser mit esptool-js). Paketnamen oben wie im Release v0.1.1-alpha; künftige Releases (Workflow „Release“ bei jedem Tag `v*`) heißen `HaldenFunk-<Version>-<Board>.zip`.

## Funkprofile (868 MHz, Deutschland)

Alle Profile liegen vollständig im SRD-Teilband **869,4–869,65 MHz** (ETSI EN 300 220 / BNetzA-Allgemeinzuteilung): **max. 500 mW ERP, 10 % Sendezeit**. Die Firmware führt Buch über die Sendezeit der letzten Stunde (RadioLib `getTimeOnAir`) und **hält Pakete zurück**, sobald das 10-%-Budget (360 s/h) erreicht ist. Sendeleistung bleibt bei 14 dBm (Standard, nie über Chipgrenze 22 dBm SX1262 / 20 dBm SX1276).

> ⚠️ **Alle Geräte eines Netzes müssen dasselbe Funkprofil nutzen**, sonst hören sie sich nicht. Auswahl im Reiter **Gerät → Funkprofil** (gespeichert im NVS, Neustart) oder seriell `/set preset N`.

> ℹ️ Die Funkprofile sind auf `main`, aber **noch nicht im Release v0.1.1-alpha**. Die Release-Firmware 0.1.1-alpha funkt fest mit 869,525 MHz, 125 kHz, SF9, CR 4/5 (entspricht Profil 2 „Mittel“). Wer Release- und `main`-Geräte mischt, stellt die neueren Geräte auf „Mittel“.

| Nr. | Profil | Frequenz | Bandbreite | SF | CR | Sendezeit je 100-Byte-Nachricht | max. Nachrichten/h (10 %) | Reichweite ↔ Tempo |
|---|---|---|---|---|---|---|---|---|
| 0 | **EU Narrow (Standard)** | 869,618 MHz | 62,5 kHz | 8 | 4/8 | ca. 0,94 s | ca. 385 | ausgewogen, störfest (MeshCore-Standard „EU/UK Narrow“) |
| 1 | Nah/Schnell | 869,525 MHz | 250 kHz | 7 | 4/5 | ca. 0,09 s | ca. 4100 | kurze Reichweite, sehr schnell |
| 2 | Mittel (bisheriger Standard) | 869,525 MHz | 125 kHz | 9 | 4/5 | ca. 0,55 s | ca. 650 | mittel; kompatibel zu Geräten mit alter Firmware |
| 3 | Fern | 869,525 MHz | 125 kHz | 12 | 4/8 | ca. 5,9 s | ca. 60 | größte Reichweite, sehr langsam (LDRO automatisch) |
| 4 | LongFast-ähnlich | 869,525 MHz | 250 kHz | 11 | 4/5 | ca. 0,94 s | ca. 380 | wie Meshtastic „LongFast“ EU; trotzdem nicht Meshtastic-kompatibel |

<img src="docs/images/funktion-funkprofil.jpg" width="230" alt="Funkprofil-Auswahl im Gerät-Reiter">

Sendezeiten berechnet mit expliziter Kopfzeile, CRC, 8 Symbolen Präambel. Funkeinstellungen: Syncword unverändert (privat), CRC an, explizite Kopfzeile, Low-Data-Rate-Optimierung automatisch, SX1262 mit „boosted RX gain“, TCXO 1,8 V (T3-S3), Strombegrenzung 140 mA (SX1262) / 120 mA (SX1276). `/api/info` liefert `preset`, `presetName`, `freq`, `bw`, `sf`, `cr`, `airtimeMs`, `airtimeBudgetMs`, `airtimePct`, `txDeferred`; `/api/presets` listet alle Profile, `POST /api/preset` (`preset=N`) speichert und startet neu.

## Weboberfläche

| Chat | Schnellmeldung | Brett |
|---|---|---|
| <img src="docs/images/funktion-chat.jpg" width="230" alt="Chat"> | <img src="docs/images/funktion-quick.jpg" width="230" alt="Schnellmeldung"> | <img src="docs/images/funktion-board.jpg" width="230" alt="Brett"> |
| **Karte** | **Standort** | **Gerät** |
| <img src="docs/images/funktion-map.jpg" width="230" alt="Karte"> | <img src="docs/images/funktion-loc.jpg" width="230" alt="Standort"> | <img src="docs/images/funktion-info.jpg" width="230" alt="Gerät"> |

<img src="docs/images/funktion-desktop.jpg" width="700" alt="Desktop-Ansicht">

(Aufnahmen der [Live-Demo](https://pietwars.github.io/HaldenFunk/), Stand 0.1.1-alpha; alle Daten simuliert.)

- **Gestaltung:** Kupfer und Anthrazit, Spitzkegelhalden, Förderturm als Mesh-Knoten, Funkwellen. Das Hintergrundbild ist eine eigene, mit Python/PIL erzeugte Grafik (`tools/make_bg.py`), keine Fotos
- **Chat** an alle in Funkreichweite, **Schnellmeldungen** (Trinkwasser, Strom, Medikamente, Verletzt, Evakuierung, „Mir geht es gut“, Angebote)
- **Schwarzes Brett** mit Weitergabe über mehrere Geräte (LittleFS, max. 30 Aushänge, Ablaufzeit 6 h – 7 Tage)
- **Standort:** GPS des Telefons oder Ortsliste – Sangerhausen, Hohe Linde, Wallhausen, Kyffhäuser-Denkmal, Kelbra, Roßla, Allstedt, Lutherstadt Eisleben, Mansfeld, Hettstedt, Wippra, Stolberg (Harzrand)
- **Offline-Karten** (zusammen ca. 223 KB gzip im LittleFS, Übersicht 90 KB): Mansfelder Land · Goldene Aue (Übersicht), Sangerhausen, Lutherstadt Eisleben, Mansfeld · Hettstedt, Kelbra · Roßla · Kyffhäuser. Halden (braun) und Schächte (kupfer) werden hervorgehoben. Erzeugt mit `tools/make_map_osm.py` aus OpenStreetMap, Datenstand 17.10.2026, danach verkleinert mit `tools/shrink_maps.py` (Linien vereinfacht, Koordinaten gerastert, kleine Wald-/Wasserflächen und kurze Wegstücke weggelassen; Orte, Halden und Schächte vollständig) – gleiche Kartendateien wie in [HaldenFunk-MeshCore](https://github.com/Pietwars/HaldenFunk-MeshCore)
- Geräteinfo über `GET /api/info`, Demo lokal mit `web/static/index.html?demo=1`

## Erste Schritte

**Am einfachsten:** passendes ZIP aus dem [Release](https://github.com/Pietwars/HaldenFunk/releases/tag/v0.1.1-alpha) laden und nach `ANLEITUNG.md` flashen.

Selbst bauen:

```bash
pip install platformio
cd firmware
pio run -e t3s3-sx1262 -t upload      # Firmware
pio run -e t3s3-sx1262 -t uploadfs    # Weboberfläche (LittleFS)
pio device monitor                     # zeigt WLAN-Name und offenen Zugang
```

Dann mit dem offenen WLAN `HaldenFunk-XXXXXX` verbinden und `http://192.168.4.1` öffnen. Betreiberkonsole nur über USB; Telnet ist deaktiviert.

Standard-Funkprofil (aktueller Stand `main`): **EU Narrow** – 869,618 MHz, 62,5 kHz, SF8, CR 4/8, 14 dBm; weitere Profile siehe [Funkprofile](#funkprofile-868-mhz-deutschland). Release-Firmware 0.1.1-alpha: 869,525 MHz, 125 kHz, SF9, CR 4/5.

## Gemeinsamer Kern mit DisAHRsterRadio

HaldenFunk wird nicht als zweite Kopie gepflegt: Alle Kern-Dateien (Firmware, Web-Oberfläche, Werkzeuge, Workflows) entsprechen exakt [DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio) in der Revision aus `region/CORE` plus dem regionalen Overlay `region/overlay.patch`. CI prüft das bei jedem Build (`python3 tools/core_sync.py --check`). Neuen Kern übernehmen: `python3 tools/core_sync.py --update`. Details: [docs/KERN_UND_REGION.md](docs/KERN_UND_REGION.md).

## Bekannte Grenzen

- Nicht auf Hardware getestet; Pinbelegungen von DisAHRsterRadio übernommen
- Chat nur Einzelsprung (LoRaLayer2 leitet Broadcasts nicht weiter); nur das Brett wird über mehrere Geräte weitergereicht
- Keine Verschlüsselung/Signatur – alle auf der Frequenz können mitlesen und Namen fälschen
- Karten ohne Navigation und ohne Gebäude in der Übersicht
- Weitere Grenzen wie bei [DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio#bekannte-grenzen--offene-arbeit)

## Lizenz, Quellen und Danksagung

- Grundlage: [sudomesh/disaster-radio](https://github.com/sudomesh/disaster-radio) und [sudomesh/LoRaLayer2](https://github.com/sudomesh/LoRaLayer2) – vielen Dank an Sudo Mesh. Git-Historie bleibt erhalten, Original-README: [README.upstream.md](README.upstream.md)
- `firmware/`: GPLv3 und AGPLv3 (dual, wie upstream); `web/`: AGPLv3
- **Kartendaten:** © OpenStreetMap-Mitwirkende, [ODbL 1.0](web/static/map/ODbL-1.0.txt)
- **Bilder:** Hintergrund, Kopfbild und Icon sind eigene, programmatisch erzeugte Grafiken (`tools/make_bg.py`). Es werden keine Fotos von Wikimedia Commons oder anderen Quellen verwendet

