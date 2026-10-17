# Changelog – HaldenFunk

## Unveröffentlicht · 17.10.2026

- **Zentrale Version:** Datei `VERSION` ist die einzige Quelle; `tools/version.py` schreibt `DAR_VERSION`, die neue Fußzeile „Weboberfläche HaldenFunk …“ im Gerät-Reiter, Demo-Gerätedaten und README; `--check` + `tests/version.test.py` in CI. `package.sh` und Demo-Banner lesen `VERSION`.
- Projektfamilie: gemeinsame Tabelle mit allen fünf Repositorys.
- **Automatische Releases:** Workflow `release.yml` baut bei jedem Tag `v*` alle drei Boards, packt `…-factory.bin`, `teile/`, `SHA256SUMS` und deutsche `ANLEITUNG.md`, prüft alles (`tools/verify_release.py`, Abbruch bei fehlender Datei) und veröffentlicht eine Vorabversion mit Text aus diesem CHANGELOG. Probelauf im Pull Request. Paketnamen jetzt mit Version: `HaldenFunk-<Version>-<Board>.zip`.
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
