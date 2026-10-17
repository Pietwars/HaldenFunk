// DisAHRsterRadio/HaldenFunk: Funkprofile fuer 868 MHz in Deutschland
// (ETSI EN 300 220 / BNetzA SRD-Allgemeinzuteilung, Teilband 869,4-869,65 MHz:
//  max. 500 mW ERP, 10 % Sendezeit). Alle Profile liegen vollstaendig in diesem Teilband:
//  62,5 kHz auf 869,618 MHz (869,587-869,649), 125/250 kHz auf 869,525 MHz (869,400-869,650).
// Alle Knoten eines Netzes muessen dasselbe Profil verwenden.
#ifndef RADIO_PRESETS_H
#define RADIO_PRESETS_H
#include <stdint.h>

struct RadioPreset {
    const char *id;
    const char *name;
    float freqMHz;
    float bwKHz;
    uint8_t sf;
    uint8_t cr;          // Nenner der Coderate (5..8 => 4/5..4/8)
    float dutyLimit;     // erlaubter Sendezeitanteil im Teilband (0.10 = 10 %)
    uint8_t maxErpDbm;   // Grenze des Teilbands (27 dBm = 500 mW ERP)
};

static const RadioPreset RADIO_PRESETS[] = {
    {"eu-narrow", "EU Narrow (Standard)",        869.618f,  62.5f,  8, 8, 0.10f, 27},
    {"nah",       "Nah/Schnell",                 869.525f, 250.0f,  7, 5, 0.10f, 27},
    {"mittel",    "Mittel (bisheriger Standard)", 869.525f, 125.0f,  9, 5, 0.10f, 27},
    {"fern",      "Fern",                        869.525f, 125.0f, 12, 8, 0.10f, 27},
    {"longfast",  "LongFast-aehnlich",           869.525f, 250.0f, 11, 5, 0.10f, 27},
};
static const int RADIO_PRESET_COUNT = sizeof(RADIO_PRESETS) / sizeof(RADIO_PRESETS[0]);
static const int RADIO_PRESET_DEFAULT = 0;

static inline const RadioPreset &getRadioPreset(int i) {
    return RADIO_PRESETS[(i >= 0 && i < RADIO_PRESET_COUNT) ? i : RADIO_PRESET_DEFAULT];
}
#endif
