> Offenes WLAN; BLE-UART ohne PIN in den zusätzlichen Testprofilen. Alte Kopplungen bei Bedarf am Handy entfernen. Details: https://github.com/Pietwars/HaldenFunk/blob/main/docs/OFFENER_ZUGANG.md

# HaldenFunk für @BOARD@

Version @VERSION@ (Commit @COMMIT@) · Quelle: https://github.com/Pietwars/HaldenFunk

> ⚠️ Kein zertifiziertes Notrufsystem. In Lebensgefahr immer **112** wählen. Diese Version ist auf echter Hardware **nicht abgenommen** (die gleiche Basis lief bei DisAHRsterRadio auf einem LILYGO T3 V1.6.1; T-Deck Plus und T-Watch S3 sind neu und noch nicht auf Hardware geprüft).

## 1. Zuerst die Antenne!

**Antenne anschrauben, bevor das Board Strom bekommt.** Ohne Antenne kann der Funkchip beim Senden beschädigt werden.

## 2. Erstinstallation (alles auf einmal)

1. Board per USB-Datenkabel an den Rechner (Chrome oder Edge am PC/Mac, nicht iPhone).
2. https://espressif.github.io/esptool-js/ öffnen, Baudrate 921600 (bei Problemen 115200), **Connect** und den Port wählen.
   - T-Deck Plus: Wird kein Port gefunden, den **Trackball** gedrückt halten und einschalten (bzw. Reset), dann loslassen.
   - T-Watch S3: USB-C neu einstecken; bei ausgeschalteter Uhr kurz die Seitentaste drücken.
3. Bei **Flash Address** `0x0` eintragen und `HaldenFunk-@ZIP@-factory.bin` wählen.
4. Optional zuerst **Erase Flash** (löscht alles, auch gespeicherte Aushänge und Einstellungen).
5. **Program** und warten, bis „Leaving…“ erscheint. Dann **RST** drücken oder kurz vom Strom trennen.

Die factory-Datei enthält Bootloader (@BOOT@), Partitionstabelle (0x8000), boot_app0 (0xe000), Firmware (0x10000) und Weboberfläche/Karten als LittleFS (0x200000).

## 3. Verbinden

Auf T-Deck Plus und T-Watch S3 bleibt das Display in dieser Version **dunkel** (noch kein Display-Treiber) – das Gerät läuft trotzdem; die Bedienung erfolgt komplett über das WLAN im Browser. Die serielle Ausgabe (USB, 115200 Baud) zeigt den Start.

Am Handy das WLAN `HaldenFunk-XXXXXX` auswählen und verbinden (höchstens 4 Handys). Bei „Kein Internet“ verbunden bleiben, dann `http://192.168.4.1` oder `http://haldenfunk.local` öffnen. Achtung: offenes, unverschlüsseltes WLAN – jede Person in Reichweite kann mitlesen und senden. Telnet ist entfernt; Konfiguration erfolgt über USB. BLE-UART ohne PIN ist in den zusätzlichen `*-ble`-Testprofilen verfügbar; deren abweichende Partitionierung beachten.

## 4. Update (nur Firmware)

Für ein Firmware-Update **nur `teile/firmware.bin` an Adresse `0x10000`** flashen – **nicht** die factory-Datei, sonst werden Weboberfläche, gespeicherte Aushänge (Schwarzes Brett) und Einstellungen im Dateisystem überschrieben.

Nur wenn sich Weboberfläche oder Karten geändert haben: zusätzlich `teile/littlefs.bin` an `0x200000` (löscht die gespeicherten Aushänge auf diesem Gerät).

## 5. Dateien prüfen

`SHA256SUMS` enthält die Prüfsummen. Linux/Mac: `sha256sum -c SHA256SUMS`, Windows: `certutil -hashfile Datei SHA256`.

| Datei | Adresse |
|---|---|
| `HaldenFunk-@ZIP@-factory.bin` | 0x0 (komplett) |
| `teile/bootloader.bin` | @BOOT@ |
| `teile/partitions.bin` | 0x8000 |
| `teile/boot_app0.bin` | 0xe000 |
| `teile/firmware.bin` | 0x10000 |
| `teile/littlefs.bin` | 0x200000 |

Kartendaten: © OpenStreetMap-Mitwirkende, ODbL 1.0. Grundlage: sudomesh/disaster-radio (GPLv3/AGPLv3).

