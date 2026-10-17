#include <Layer1_RadioLib.h>

static volatile bool _dioFlag = false;
static volatile bool _transmitFlag = false;
uint32_t Layer1Class::_holdUntil = 0;

Layer1Class::Layer1Class(L1Radio *lora, int mode, int cs, int reset, int dio, uint8_t sf,
                         float frequency, int power, float bandwidth, float tcxo, uint8_t cr, float dutyLimit)
: _LoRa(lora), _mode(mode), _csPin(cs), _resetPin(reset), _DIOPin(dio), _spreadingFactor(sf),
  _loraFrequency(frequency), _txPower(power), _loraInitialized(0), _spiFrequency(2000000),
  _bandwidth(bandwidth), _tcxo(tcxo), _codingRate(cr), _dutyLimit(dutyLimit),
  _slotStart(0), _slotIdx(0), _lastAirtimeMs(0), _deferred(0), _blocked(false), _hasPending(false)
{
    if (_txPower > L1_MAX_DBM) _txPower = L1_MAX_DBM; // nie ueber Chipgrenze
    memset(_slots, 0, sizeof(_slots));
    txBuffer = new packetBuffer();
    rxBuffer = new packetBuffer();
}

#if defined(ESP32)
IRAM_ATTR
#endif
void Layer1Class::setFlag(void) { _dioFlag = true; }

int Layer1Class::init() {
#if defined(RL_SX1262)
    int state = _LoRa->begin(_loraFrequency, _bandwidth, _spreadingFactor, _codingRate,
                             RADIOLIB_SX126X_SYNC_WORD_PRIVATE, _txPower, 8, _tcxo, false);
    if (state == RADIOLIB_ERR_NONE) {
        _LoRa->setDio2AsRfSwitch(true);
        _LoRa->setCurrentLimit(140);          // PA-Strombegrenzung (mA)
        _LoRa->setRxBoostedGainMode(true);    // bessere Empfindlichkeit (+~2 dB, etwas mehr Strom)
        _LoRa->setCRC(2);
        _LoRa->explicitHeader();
        _LoRa->autoLDRO();                    // Low-Data-Rate-Optimierung automatisch (SF11/12 @ BW125)
    }
#else
    int state = _LoRa->begin(_loraFrequency, _bandwidth, _spreadingFactor, _codingRate,
                             RADIOLIB_SX127X_SYNC_WORD, _txPower, 8, 0);
    if (state == RADIOLIB_ERR_NONE) {
        _LoRa->setCurrentLimit(120);          // OCP (mA), PA_BOOST bis 20 dBm
        _LoRa->setCRC(true);
        _LoRa->explicitHeader();
        _LoRa->autoLDRO();
    }
#endif
    Serial.printf("Layer1::init(): RadioLib state = %d (%.3f MHz, BW %.1f, SF%d, CR4/%d, %d dBm)\r\n",
                  state, _loraFrequency, _bandwidth, _spreadingFactor, _codingRate, _txPower);
    if (state != RADIOLIB_ERR_NONE) return 0;
    _LoRa->setPacketReceivedAction(Layer1Class::setFlag);
    if (_LoRa->startReceive() != RADIOLIB_ERR_NONE) return 0;
    _slotStart = millis();
    _loraInitialized = 1;
    return 1;
}

void Layer1Class::setTxPower(int p) {
    if (p > L1_MAX_DBM) p = L1_MAX_DBM;
    if (_LoRa->setOutputPower(p) == RADIOLIB_ERR_NONE) _txPower = p;
}

void Layer1Class::setSpreadingFactor(uint8_t sf) {
    if (_LoRa->setSpreadingFactor(sf) == RADIOLIB_ERR_NONE) _spreadingFactor = sf;
    _LoRa->startReceive();
}

uint32_t Layer1Class::timeOnAirMs(size_t len) {
    return (uint32_t)((_LoRa->getTimeOnAir(len) + 999) / 1000); // RadioLib liefert Mikrosekunden
}

void Layer1Class::rollSlots() {
    uint32_t now = millis();
    while (now - _slotStart >= L1_AIRTIME_SLOT_MS) {
        _slotStart += L1_AIRTIME_SLOT_MS;
        _slotIdx = (_slotIdx + 1) % L1_AIRTIME_SLOTS;
        _slots[_slotIdx] = 0;
    }
}

uint32_t Layer1Class::airtimeUsedMs() {
    rollSlots();
    uint32_t s = 0;
    for (int i = 0; i < L1_AIRTIME_SLOTS; i++) s += _slots[i];
    return s;
}

int Layer1Class::sendPacket(char *data, size_t len) {
    _transmitFlag = true;
    int state = _LoRa->startTransmit((uint8_t *)data, len);
    if (state == RADIOLIB_ERR_NONE) return 0;
    _transmitFlag = false;
    _LoRa->startReceive();
    if (state == RADIOLIB_ERR_PACKET_TOO_LONG) return 1;
    if (state == RADIOLIB_ERR_TX_TIMEOUT) return 2;
    return 3;
}

int Layer1Class::transmit() {
    if (_transmitFlag) return 0; // laufende Aussendung abwarten
    if ((int32_t)(millis() - _holdUntil) < 0) return 0; // Sendepause (WLAN-Start)
    if (!_hasPending) {
        _pending = txBuffer->read();
        if (_pending.length <= 0) return 0;
        _hasPending = true;
    }
    uint32_t toa = timeOnAirMs(_pending.length);
    // Sendezeitgrenze des Teilbands (gleitende Stunde): Paket zurueckhalten statt senden
    if (airtimeUsedMs() + toa > airtimeBudgetMs()) {
        if (!_blocked) { _deferred++; Serial.printf("[DUTY] Sendezeitgrenze erreicht, Paket wartet\r\n"); }
        _blocked = true;
        return 0;
    }
    _blocked = false;
    _hasPending = false;
    if (sendPacket(_pending.data, _pending.length) != 0) return 0;
    _slots[_slotIdx] += toa;
    _lastAirtimeMs = toa;
    return _pending.length;
}

int Layer1Class::receive() {
    if (!_dioFlag) return 0;
    _dioFlag = false;
    if (_transmitFlag) {
        _transmitFlag = false;
        _LoRa->finishTransmit();
        _LoRa->startReceive();
        return 0;
    }
    int ret;
    size_t len = _LoRa->getPacketLength();
    if (len == 0 || len > sizeof(((BufferEntry *)0)->data)) { _LoRa->startReceive(); return -2; }
    uint8_t data[256];
    int state = _LoRa->readData(data, len);
    if (state == RADIOLIB_ERR_NONE) {
        BufferEntry entry;
        memcpy(&entry.data[0], data, len);
        entry.length = len;
        rxBuffer->write(entry);
        ret = len;
    } else if (state == RADIOLIB_ERR_CRC_MISMATCH) ret = -1;
    else ret = -2;
    _LoRa->startReceive();
    return ret;
}
