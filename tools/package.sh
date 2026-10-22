#!/usr/bin/env bash
# Erzeugt flashbare Pakete je Board: factory.bin (ab 0x0) + Einzelteile + SHA256SUMS + ANLEITUNG.md
# Aufruf: tools/package.sh [Ausgabeordner]   (Boards einschränken: ENVS="tdeck-sx1262" tools/package.sh)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$ROOT/dist}
FW=$ROOT/firmware
NAMEPREFIX=${NAMEPREFIX:-HaldenFunk}
ESPTOOL=${ESPTOOL:-"python3 -m esptool"}
VERSION=$(python3 "$ROOT/tools/version.py" --get)   # zentrale Versionsquelle: Datei VERSION
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unbekannt)
ENVS=${ENVS:-"tdeck-standalone tdeck-sx1262 twatch-s3-sx1262"}
mkdir -p "$OUT"
declare -A CHIP=([tdeck-standalone]=esp32s3 [tdeck-sx1262]=esp32s3 [tdeck-screen-test]=esp32s3 [twatch-s3-sx1262]=esp32s3 [t3s3-sx1262]=esp32s3 [t3-v161-sx1276]=esp32 [heltec-v2-sx1276]=esp32)
declare -A BOOT=([tdeck-standalone]=0x0 [tdeck-sx1262]=0x0 [tdeck-screen-test]=0x0 [twatch-s3-sx1262]=0x0 [t3s3-sx1262]=0x0 [t3-v161-sx1276]=0x1000 [heltec-v2-sx1276]=0x1000)
declare -A FLASH=([tdeck-standalone]=16MB [tdeck-sx1262]=16MB [tdeck-screen-test]=16MB [twatch-s3-sx1262]=16MB [t3s3-sx1262]=4MB [t3-v161-sx1276]=4MB [heltec-v2-sx1276]=4MB)
declare -A NAME=([tdeck-standalone]="LILYGO T-Deck Plus Standalone (Display und Touch)" [tdeck-sx1262]="LILYGO T-Deck Plus (SX1262)" [tdeck-screen-test]="LILYGO T-Deck Plus (Display-Test)" [twatch-s3-sx1262]="LILYGO T-Watch S3 (SX1262)" [t3s3-sx1262]="LILYGO T3-S3 (SX1262)" [t3-v161-sx1276]="LILYGO T3 V1.6.1 (SX1276)" [heltec-v2-sx1276]="Heltec WiFi LoRa 32 V2 (SX1276)")
declare -A ZIP=([tdeck-standalone]=tdeck-standalone [tdeck-sx1262]=tdeck [tdeck-screen-test]=tdeck-screen-test [twatch-s3-sx1262]=twatch-s3 [t3s3-sx1262]=t3s3 [t3-v161-sx1276]=t3-v161 [heltec-v2-sx1276]=heltec-v2)
for env in $ENVS; do
  # buildfs und der Firmware-Build leeren jeweils das Build-Verzeichnis -> Ergebnisse nach jedem Schritt sichern
  Z=$VERSION-${ZIP[$env]}; P=$NAMEPREFIX-$Z
  B=$FW/.pio/build/$env; D=$OUT/$P; T=$D/teile; rm -rf "$D"; mkdir -p "$T"
  (cd $FW && pio run -e $env) >/dev/null; cp $B/bootloader.bin $B/partitions.bin $B/firmware.bin "$T/"
  if [[ "$env" = tdeck-screen-test || "$env" = tdeck-standalone ]]; then
    python3 "$ROOT/tools/tdeck_debug.py" "$B" "$D/debug"
  fi
  (cd $FW && pio run -e $env -t buildfs) >/dev/null; cp $B/littlefs.bin "$T/"
  BOOTAPP0=$(find ~/.platformio/packages/ -path '*framework-arduinoespressif32*' -name boot_app0.bin | head -1)
  cp "$BOOTAPP0" "$T/boot_app0.bin"
  $ESPTOOL --chip ${CHIP[$env]} merge-bin -o "$D/$P-factory.bin" --flash-mode keep --flash-freq keep --flash-size ${FLASH[$env]} \
    ${BOOT[$env]} $T/bootloader.bin 0x8000 $T/partitions.bin 0xe000 $T/boot_app0.bin 0x10000 $T/firmware.bin 0x200000 $T/littlefs.bin >/dev/null
  sed -e "s/@BOARD@/${NAME[$env]}/g" -e "s/@ZIP@/$Z/g" -e "s/@CHIP@/${CHIP[$env]}/g" -e "s/@BOOT@/${BOOT[$env]}/g" \
      -e "s/@PACKAGE@/$P/g" -e "s/@VERSION@/$VERSION/g" -e "s/@COMMIT@/$COMMIT/g" "$ROOT/tools/ANLEITUNG.template.md" > "$D/ANLEITUNG.md"
  (cd "$D" && sha256sum $P-factory.bin teile/*.bin > SHA256SUMS)
  if [[ "$env" = tdeck-screen-test || "$env" = tdeck-standalone ]]; then
    cp "$ROOT/docs/TDECK_DISPLAY_RECOVERY.md" "$D/TDECK-BEDIENUNG.md"
    (cd "$D" && sha256sum debug/* TDECK-BEDIENUNG.md >> SHA256SUMS)
  fi
  rm -f "$OUT/$P.zip"; (cd "$OUT" && python3 -m zipfile -c "$P.zip" "$P")
  echo "$env -> $OUT/$P.zip"
done
