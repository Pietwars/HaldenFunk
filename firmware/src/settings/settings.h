#include <Arduino.h>
#include <Preferences.h>
#include <nvs_flash.h>

void getSettings(void);
void saveUsername(String newUserName);
void saveUI(bool useBLE);
void saveTxPower(int txPower);
void saveLoraFrq(int loraFrq);
void saveSpreadingFactor(int spreadFactor);
void saveDutyCycle(double dutyCycle);
void saveInterval(long interval);
void saveGPS(long period);
void saveRadioPreset(int preset);

extern String username;
extern bool useBLE;
extern int txPower;
extern int loraFrq;
extern int spreadingFactor;
extern double dutyCycle;
extern long routeInterval;
extern long beaconPeriod;
extern int radioPreset; // Index in RADIO_PRESETS (RadioPresets.h)
