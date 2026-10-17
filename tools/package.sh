#!/usr/bin/env bash
# Erzeugt flashbare Pakete je Board: factory.bin (ab 0x0) + Einzelteile + SHA256SUMS + ANLEITUNG.md
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$ROOT/dist}
FW=$ROOT/firmware
ESPTOOL=${ESPTOOL:-"python3 -m esptool"}
BOOTAPP0=$(find ~/.platformio/packages/framework-arduinoespressif32 -name boot_app0.bin | head -1)
VERSION=$(python3 "$ROOT/tools/version.py" --get)   # zentrale Versionsquelle: Datei VERSION
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unbekannt)
mkdir -p "$OUT"
declare -A CHIP=([t3s3-sx1262]=esp32s3 [t3-v161-sx1276]=esp32 [heltec-v2-sx1276]=esp32)
declare -A BOOT=([t3s3-sx1262]=0x0 [t3-v161-sx1276]=0x1000 [heltec-v2-sx1276]=0x1000)
declare -A NAME=([t3s3-sx1262]="LILYGO T3-S3 (SX1262)" [t3-v161-sx1276]="LILYGO T3 V1.6.1 (SX1276)" [heltec-v2-sx1276]="Heltec WiFi LoRa 32 V2 (SX1276)")
declare -A ZIP=([t3s3-sx1262]=t3s3 [t3-v161-sx1276]=t3-v161 [heltec-v2-sx1276]=heltec-v2)
for env in t3s3-sx1262 t3-v161-sx1276 heltec-v2-sx1276; do
  # buildfs und der Firmware-Build leeren jeweils das Build-Verzeichnis -> Ergebnisse nach jedem Schritt sichern
  B=$FW/.pio/build/$env; D=$OUT/HaldenFunk-${ZIP[$env]}; T=$D/teile; rm -rf "$D"; mkdir -p "$T"
  (cd $FW && pio run -e $env) >/dev/null; cp $B/bootloader.bin $B/partitions.bin $B/firmware.bin "$T/"
  (cd $FW && pio run -e $env -t buildfs) >/dev/null; cp $B/littlefs.bin "$T/"; cp "$BOOTAPP0" "$T/boot_app0.bin"
  $ESPTOOL --chip ${CHIP[$env]} merge-bin -o "$D/HaldenFunk-${ZIP[$env]}-factory.bin" --flash-mode keep --flash-freq keep --flash-size 4MB \
    ${BOOT[$env]} $T/bootloader.bin 0x8000 $T/partitions.bin 0xe000 "$BOOTAPP0" 0x10000 $T/firmware.bin 0x200000 $T/littlefs.bin >/dev/null
  sed -e "s/@BOARD@/${NAME[$env]}/g" -e "s/@ZIP@/${ZIP[$env]}/g" -e "s/@CHIP@/${CHIP[$env]}/g" -e "s/@BOOT@/${BOOT[$env]}/g" \
      -e "s/@VERSION@/$VERSION/g" -e "s/@COMMIT@/$COMMIT/g" "$ROOT/tools/ANLEITUNG.template.md" > "$D/ANLEITUNG.md"
  (cd "$D" && sha256sum HaldenFunk-${ZIP[$env]}-factory.bin teile/*.bin > SHA256SUMS)
  rm -f "$OUT/HaldenFunk-${ZIP[$env]}.zip"; (cd "$OUT" && python3 -m zipfile -c "HaldenFunk-${ZIP[$env]}.zip" "HaldenFunk-${ZIP[$env]}")
  echo "$env -> $OUT/HaldenFunk-${ZIP[$env]}.zip"
done
