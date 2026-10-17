#ifndef CONFIG_H
#define CONFIG_H

// Zugangsdaten fuer optionalen WLAN-Client-Modus (nicht committen)
#if __has_include("secrets.h")
#include "secrets.h"
#endif

#define DAR_VERSION "0.1.0-alpha"
#define CLOCK_SPEED 240

// EU868 Standard: 869.525 MHz (Teilband g3, 10 % Duty-Cycle), 125 kHz, SF9, 14 dBm
#define LORA_DEFAULT_FREQ_MHZ 869.525f

#ifndef STARTUP_STAGGER_MS
#define STARTUP_STAGGER_MS 150
#endif

#ifndef LORA_TCXO
#define LORA_TCXO 0.0f
#endif

/* ---------- LILYGO T3-S3 (SX1262) ---------- */
#ifdef LILYGO_T3S3_SX1262
#define BOARD_NAME "LILYGO T3-S3 SX1262"
#define LORA_SCK 5
#define LORA_MISO 3
#define LORA_MOSI 6
#define LORA_CS 7
#define LORA_RST 8
#define LORA_IRQ 33   // DIO1
#define LORA_BUSY 34
#undef LORA_TCXO
#define LORA_TCXO 1.8f
#define OLED_SDA 18
#define OLED_SCL 17
#undef OLED_RST
#define OLED_RST NOT_A_PIN
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define SD_SCK 14
#define SD_MISO 2
#define SD_MOSI 11
#define SD_CS 13
#endif

/* ---------- LILYGO T3 V1.6.1 (SX1276) ---------- */
#ifdef LILYGO_T3_V161
#define BOARD_NAME "LILYGO T3 V1.6.1 SX1276"
#define LORA_SCK 5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_CS 18
#define LORA_RST 23
#define LORA_IRQ 26   // DIO0
#define LORA_BUSY RADIOLIB_NC
#define OLED_SDA 21
#define OLED_SCL 22
#undef OLED_RST
#define OLED_RST NOT_A_PIN
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define SD_SCK 14
#define SD_MISO 2
#define SD_MOSI 15
#define SD_CS 13
#endif

/* ---------- Heltec WiFi LoRa 32 V2 (SX1276) ---------- */
#ifdef HELTEC_V2
#define BOARD_NAME "Heltec WiFi LoRa 32 V2"
#define LORA_SCK 5
#define LORA_MISO 19
#define LORA_MOSI 27
#define LORA_CS 18
#define LORA_RST 14
#define LORA_IRQ 26   // DIO0
#define LORA_BUSY RADIOLIB_NC
#define OLED_SDA 4
#define OLED_SCL 15
#define OLED_RST 16
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define VEXT_PIN 21   // Vext (OLED-Versorgung), LOW = an
// Brownout-Gegenmassnahmen: reduzierte WLAN-Sendeleistung, laengere Startstaffelung
#ifdef HELTEC_WIFI_11DBM
#define WIFI_TX_POWER WIFI_POWER_11dBm
#else
#define WIFI_TX_POWER WIFI_POWER_8_5dBm
#endif
#undef STARTUP_STAGGER_MS
#define STARTUP_STAGGER_MS 600
#define DISABLE_BROWNOUT      // Brownout-Detektor frueh abschalten
#define WIFI_LATE             // WLAN erst nach LoRa/Display starten
#define WIFI_LATE_DELAY_MS 2000
#endif

#ifndef BOARD_NAME
#error "Kein Board definiert (LILYGO_T3S3_SX1262, LILYGO_T3_V161, HELTEC_V2)"
#endif

#ifndef SD_CS
#define SD_CS 13
#endif

#if defined(CONFIG_IDF_TARGET_ESP32S3)
#define VSPI_OR_FSPI FSPI
#else
#define VSPI_OR_FSPI VSPI
#endif

#endif
