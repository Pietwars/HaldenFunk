# Changelog – HaldenFunk

## Unveröffentlicht – offener Zugang

- **Offenes WLAN:** `HaldenFunk-XXXXXX` ohne Zugangsdaten (höchstens 4 Handys), ein früher gespeicherter AP-Schlüssel wird beim Start aus dem NVS gelöscht; seriell/OLED zeigen „offen“. WLAN bleibt auch bei früher gespeicherter BLE-only-Einstellung aktiv.
- Telnet-Konsole entfernt, Betreiberkonfiguration nur über USB.
- Zusätzliche Testprofile `*-ble`: WLAN plus BLE-UART ohne PIN (Partitionierung `huge_app.csv`; nicht MeshCore-App-kompatibel).
- Kern auf DisAHRsterRadio `main` (offenes WLAN, #12/#13) per `tools/core_sync.py` aktualisiert; Overlay deutlich kleiner (Funkprofile jetzt im Kern).
- Doku, Flash-Anleitung und Flyer ohne Zugangsdaten-Hinweise. Hardwareabnahme steht aus.

## Unveröffentlicht · 17.10.2026

- **Gemeinsamer Kern:** HaldenFunk = DisAHRsterRadio (`region/CORE`, aktuell 0.1.1-alpha) + `region/overlay.patch`; regionale Dateien in `region/own.txt`. `tools/core_sync.py` (`--check`, `--update`, `--make-patch`), CI-Schritt „Kern-Abgleich“, Doku `docs/KERN_UND_REGION.md`. Dabei aus dem Kern übernommen: Kartenprüfung `tests/maps.test.py` und der Workflow `build.yml`.
- Flyer-Generator `tools/flyer/flyer.py` (HTML + headless Chrome, QR-Codes mit python-qrcode; Konfiguration `tools/flyer/flyer.json` mit HaldenFunk-Farbschema, Version aus `VERSION`). Flyer 0.1.1-alpha damit neu erzeugt (Druck-PDF mit QR zu Download und Demo, Digital-PDF mit klickbaren Links).
- **Funkprofile für 868 MHz (17.10.2026):** neuer Standard **EU Narrow 869,618 MHz, 62,5 kHz, SF8, CR 4/8** (vorher 869,525 MHz, 125 kHz, SF9, CR 4/5 – jetzt Profil „Mittel“). Wählbar: Nah/Schnell (BW 250, SF7), Mittel (BW 125, SF9), Fern (BW 125, SF12, CR 4/8), LongFast-ähnlich (BW 250, SF11), alle im Teilband 869,4–869,65 MHz. Auswahl im Gerät-Reiter (NVS, Neustart), `/set preset N`, `GET /api/presets`, `POST /api/preset`. **Achtung:** Geräte mit älterer Firmware funken auf „Mittel“ – entweder alle aktualisieren oder alle auf „Mittel“ stellen.
- **Sendezeit-Buchführung:** gleitende Stunde (60 × 1 min) aus RadioLib `getTimeOnAir()`, Pakete warten, wenn das 10-%-Budget erreicht ist; ersetzt die feste Airtime-Formel (SF/BW125/CR5) in `LoRaLayer2.cpp`. `/api/info` und Gerät-Reiter zeigen Profil, Bandbreite, Coderate, Sendezeit der letzten Stunde und zurückgehaltene Pakete.
- **Funkchip-Einstellungen:** Coderate aus Profil, CRC an, explizite Kopfzeile, LDRO automatisch, SX1262 boosted RX gain, Strombegrenzung 140 mA (SX1262) / 120 mA (SX1276), Sendeleistung auf Chipgrenze begrenzt (Standard 14 dBm unverändert). RadioLib 7.8.1 (aktuell). `/set sf` und `/set lorafrq` sind durch `/set preset` ersetzt.
- **Zentrale Version:** Datei `VERSION` ist die einzige Quelle; `tools/version.py` schreibt `DAR_VERSION`, die neue Fußzeile „Weboberfläche HaldenFunk …“ im Gerät-Reiter, Demo-Gerätedaten und README; `--check` + `tests/version.test.py` in CI. `package.sh` und Demo-Banner lesen `VERSION`.
- Projektfamilie: gemeinsame Tabelle mit allen fünf Repositorys.
- **Automatische Releases:** Workflow `release.yml` baut bei jedem Tag `v*` alle drei Boards, packt `…-factory.bin`, `teile/`, `SHA256SUMS` und deutsche `ANLEITUNG.md`, prüft alles (`tools/verify_release.py`, Abbruch bei fehlender Datei) und veröffentlicht eine Vorabversion mit Text aus diesem CHANGELOG. Probelauf im Pull Request. Paketnamen jetzt mit Version: `HaldenFunk-<Version>-<Board>.zip`.
- **Freier Speicher (Heap):** `/api/info` liefert `heap`, `minHeap`, `maxBlock`, `heapWarn` (40 KB); Gerät-Reiter zeigt KB-Werte, unter der Schwelle rot mit ⚠, Aktualisierung alle 10 s; seriell alle 30 s `[HEAP] …` mit Warnung.
- **Feste Versionen:** pioarduino `55.03.312-1` statt `stable`, Bibliotheken exakt (AsyncTCP 3.5.0, ESPAsyncWebServer 3.12.1, RadioLib 7.8.1, OLED 4.6.2, TinyGPSPlus 1.1.0, ArduinoJson 7.4.3), CI mit `platformio==6.2.0`, `esptool==5.6.0`.

## v0.1.1-alpha – 17.10.2026 (Vorabversion)

- **Offline-Karten verkleinert** (`tools/shrink_maps.py`, gleiche Dateien wie HaldenFunk-MeshCore): Linien vereinfacht (Douglas-Peucker), Koordinaten gerastert, auf den Kartenausschnitt zugeschnitten, kleine Wald-/Wasserflächen und kurze Wegstücke weggelassen; Orte, Halden und Schächte vollständig. Alle Karten 633 KB → 223 KB, Übersicht Mansfelder Land 335 KB → 90 KB – mehr Platz im LittleFS (u. a. für das Schwarze Brett), schnelleres Laden im Browser.
- Live-Demo und Vorschaubild der Karte aktualisiert; Firmwarekennung `0.1.1-alpha`.
- Release-Pakete enthalten je Board `factory.bin`, `teile/firmware.bin`, `teile/littlefs.bin` (Weboberfläche + Karten), Bootloader, Partitionstabelle, `boot_app0.bin`, `SHA256SUMS` und `ANLEITUNG.md` (CI-Artefakt enthält jetzt firmware.bin und littlefs.bin, PR #1).

## v0.1.0-alpha – 17.10.2026 (Vorabversion)

Erste Version der Regionalvariante von [DisAHRsterRadio](https://github.com/Pietwars/DisAHRsterRadio) für Sangerhausen und das Mansfelder Land.

- Name **HaldenFunk**, Motto „Glück Auf – Mesh fürs Mansfelder Land“
- Weboberfläche im Regionalstil: Kupfer- und Anthrazittöne, ganzseitiges Hintergrundbild (Spitzkegelhalden, Förderturm als Mesh-Knoten, Funkwellen; selbst erzeugt mit `tools/make_bg.py`), neues Icon
- Ortsliste: Sangerhausen, Hohe Linde, Wallhausen, Kyffhäuser-Denkmal, Kelbra, Roßla, Allstedt, Lutherstadt Eisleben, Mansfeld, Hettstedt, Wippra und Stolberg (Harzrand)
- Fünf neue Offline-Karten aus OpenStreetMap (`tools/make_map_osm.py`, Overpass): Mansfelder Land/Goldene Aue (Übersicht), Sangerhausen, Eisleben, Mansfeld · Hettstedt, Kelbra · Roßla · Kyffhäuser; Halden und Schächte werden hervorgehoben
- WLAN `HaldenFunk-XXXXXX` mit geräteindividuellem Zufallspasswort (gleicher Mechanismus wie DisAHRsterRadio), mDNS `haldenfunk.local`
- Fehler behoben: CSS-Selektor `#map` traf den Abschnitt statt der Karte (`#cv`), dadurch war die Karte verschoben und zu groß gezeichnet
- Live-Demo auf GitHub Pages mit Beispieldaten aus der Region
- Flyer A5: Druck-PDF mit QR-Codes und Digital-PDF mit klickbaren Links
- Firmware-Pakete für LILYGO T3-S3 (SX1262), LILYGO/TTGO T3 V1.6.1 (SX1276) und Heltec WiFi LoRa 32 V2 (SX1276)

Funktechnische Basis unverändert gegenüber DisAHRsterRadio 0.1.1-dev (disaster-radio/LoRaLayer2, RadioLib 7, pioarduino, LittleFS). Nicht auf echter Hardware getestet.
