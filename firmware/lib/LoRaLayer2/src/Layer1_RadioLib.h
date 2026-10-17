// DisAHRsterRadio: vereinheitlichte RadioLib-Layer1 (ersetzt Layer1_LoRa/Layer1_SX1276/Layer1_SX126x
// aus sudomesh/LoRaLayer2). Unterstuetzt SX1276 (RL_SX1276) und SX1262 (RL_SX1262), RadioLib >= 7.
// Funkprofile siehe RadioPresets.h; Sendezeit-Buchfuehrung (gleitende Stunde) mit getTimeOnAir().
#ifndef LAYER1_RADIOLIB_H
#define LAYER1_RADIOLIB_H
#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>
#include <packetBuffer.h>
#include <RadioPresets.h>

#if defined(RL_SX1262)
typedef SX1262 L1Radio;
#define L1_MAX_DBM 22
#elif defined(RL_SX1276)
typedef SX1276 L1Radio;
#define L1_MAX_DBM 20
#else
#error "RL_SX1262 oder RL_SX1276 definieren"
#endif

#define L1_AIRTIME_SLOTS 60          // 60 x 1 min = gleitende Stunde
#define L1_AIRTIME_SLOT_MS 60000UL

class Layer1Class {
public:
    Layer1Class(L1Radio *lora, int mode, int cs, int reset, int dio, uint8_t sf = 8,
                float frequency = 869.618, int power = 14, float bandwidth = 62.5, float tcxo = 0.0,
                uint8_t cr = 8, float dutyLimit = 0.10f);
    static int getTime() { return millis(); }
    int spreadingFactor() { return _spreadingFactor; }
    int loraInitialized() { return _loraInitialized; }
    int loraCSPin() { return _csPin; }
    int resetPin() { return _resetPin; }
    int DIOPin() { return _DIOPin; }
    long spiFrequency() { return _spiFrequency; }
    float loraFrequency() { return _loraFrequency; }
    float bandwidth() { return _bandwidth; }
    int codingRate() { return _codingRate; }
    int txPower() { return _txPower; }
    void setTxPower(int p);
    // LoRa-Senden fuer ms Millisekunden zurueckhalten (z. B. waehrend WLAN-Start)
    static void holdTx(uint32_t ms) { _holdUntil = millis() + ms; }
    static uint32_t _holdUntil;
    void setSpreadingFactor(uint8_t sf);
    // Sendezeit (ms) eines Pakets dieser Laenge mit den aktuellen Funkparametern
    uint32_t timeOnAirMs(size_t len);
    uint32_t lastAirtimeMs() { return _lastAirtimeMs; }
    uint32_t airtimeUsedMs();                       // Summe der letzten Stunde
    uint32_t airtimeBudgetMs() { return (uint32_t)(_dutyLimit * 3600000.0f); }
    float dutyLimit() { return _dutyLimit; }
    uint32_t deferredCount() { return _deferred; }  // wegen Sendezeitgrenze zurueckgehaltene Versuche
    bool txBlocked() { return _blocked; }
    packetBuffer *txBuffer;
    packetBuffer *rxBuffer;
    int init();
    int transmit();
    int receive();
private:
    static void setFlag(void);
    int sendPacket(char *data, size_t len);
    void rollSlots();
    L1Radio *_LoRa;
    int _mode, _csPin, _resetPin, _DIOPin;
    uint8_t _spreadingFactor;
    float _loraFrequency;
    int _txPower;
    int _loraInitialized;
    long _spiFrequency;
    float _bandwidth;
    float _tcxo;
    uint8_t _codingRate;
    float _dutyLimit;
    uint32_t _slots[L1_AIRTIME_SLOTS];
    uint32_t _slotStart;
    int _slotIdx;
    uint32_t _lastAirtimeMs;
    uint32_t _deferred;
    bool _blocked;
    BufferEntry _pending;
    bool _hasPending;
};
#endif
