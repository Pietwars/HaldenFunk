# Firmware ab 0.9.4

- `pio run -e tdeck-standalone`: T-Deck Plus mit lokaler Oberfläche, Bootlogo, Tastatur, Trackball und kalibriertem GT911-Touch.
- `tdeck-sx1262` / `twatch-s3-sx1262`: zusätzliche WLAN-Varianten.
- `tdeck-screen-test`: Entwicklungsprofil derselben lokalen Oberfläche.

Alle verwenden LoRaLayer2. Keine Verbindung zu MeshCore-Geräten. Flash-/Bedienhilfe: [T-Deck](../docs/TDECK_DISPLAY_RECOVERY.md).


Siehe [Haupt-README](../README.md). Optionaler WLAN-Client-Modus: `secrets.example.h` nach `secrets.h` kopieren und `WIFI_SSID`/`WIFI_PASSWORD` setzen.
