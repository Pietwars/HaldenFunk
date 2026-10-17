#ifdef HAS_BLE
#include "BleUartClient.h"
#include "settings/settings.h"
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include "OpenUart.h"
#include <atomic>

/** Comment out to stop debug output */
// #define DEBUG_OUT

/** Service UUID for Uart */
#define UART_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
/** Characteristic UUID for receiver */
#define RX_UUID "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
/** Characteristic UUID for transmitter */
#define TX_UUID "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

/** Characteristic for BLE-UART TX */
BLECharacteristic *pCharacteristicUartTX;
/** Characteristic for BLE-UART RX */
BLECharacteristic *pCharacteristicUartRX;
/** Descriptor for the BLE-UART TX characteristic */
BLEDescriptor *txDescriptor;
/** BLE Advertiser */
BLEAdvertising *pAdvertising;
/** BLE Service for WiFi*/
BLEService *wifiService;
/** BLE Service for Uart*/
BLEService *uartService;
/** BLE Server */
BLEServer *pServer;

/** Flag if device is connected */
std::atomic_bool deviceConnected{false};

/** Flag if we already registered on the server */
std::atomic_bool notifEnabled{false};

/** Unique device name */
char apName[32] = {};

// BT callbacks enqueue bounded frames; all routing and history replay stay on loop().
struct UartFrame { size_t len; uint8_t data[233]; };
QueueHandle_t rxQueue = nullptr, txQueue = nullptr;

extern BleUartClient ble_client;
void (*connectCallback)(BleUartClient *);

void BleUartClient::receive(struct Datagram datagram, size_t len)
{
  if (!txQueue || !deviceConnected || !notifEnabled || len <= DATAGRAM_HEADER || len-DATAGRAM_HEADER > sizeof(datagram.message)) return;
  UartFrame f{}; f.len=len-DATAGRAM_HEADER;
  if(f.len>sizeof(f.data)) return;
  memcpy(f.data,datagram.message,f.len);
  xQueueSend(txQueue,&f,0); // bounded queue; never stall LoRa/WLAN for a slow phone
}

void BleUartClient::handleData(void *data, size_t len)
{
#ifdef DEBUG_OUT
  char debug[len] = {'\0'};
  memcpy(debug, data, len);
  Serial.println("BLE: Received raw data");
  for (int idx = 0; idx < len; idx++)
  {
  	Serial.printf("%02X ", debug[idx]);
  }
  Serial.println("");
#endif

  if (!disaster::validPublicUart(static_cast<const uint8_t*>(data),len)) return;
  char *msg = (char *)data;
  // UART messaging only; no UI switching/restart or console commands over BLE.
  if (msg[3] != '|' || (msg[2] != 'c' && msg[2] != 'b')) return;

  struct Datagram datagram = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
  memset(datagram.message, 0, 233);
  datagram.type = msg[2];
  memcpy(&datagram.message, data, len);

#ifdef DEBUG_OUT
  Serial.printf("BLE::handleData %s len %d type %c\n", msg, len, datagram.type);
#endif

  server->transmit(this, datagram, len + DATAGRAM_HEADER);
}

/**
 * Callbacks for client connection and disconnection
 */
class MyServerCallbacks : public BLEServerCallbacks
{
  void onConnect(BLEServer *pServer)
  {
#ifdef DEBUG_OUT
    Serial.println("BLE client connected");
#endif
    // MTU is negotiated by the phone, never assume a 260-byte peer MTU.
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer)
  {
#ifdef DEBUG_OUT
    Serial.println("BLE client disconnected");
#endif
    deviceConnected = false;
    notifEnabled = false;
    if(rxQueue)xQueueReset(rxQueue);
    if(txQueue)xQueueReset(txQueue);
    pAdvertising->start();
  }
};

/**
 * Callbacks for BLE client read/write requests
 * on BLE UART characteristic
 */
class UartTxCbHandler : public BLECharacteristicCallbacks
{
  void onWrite(BLECharacteristic *pCharacteristic)
  {
    const auto value=pCharacteristic->getValue();
    if(!rxQueue || !disaster::validPublicUart(reinterpret_cast<const uint8_t*>(value.c_str()),value.length())) return;
    UartFrame f{};f.len=value.length();memcpy(f.data,value.c_str(),f.len);
    xQueueSend(rxQueue,&f,0);
  };
};

class DescriptorCallbacks : public BLEDescriptorCallbacks
{
  void onWrite(BLEDescriptor *pDescriptor)
  {
    if (pDescriptor->getLength() < 2) return;
    uint8_t *descrValue = pDescriptor->getValue();
    if (descrValue[0] & (1 << 0))
    {
#ifdef DEBUG_OUT
      Serial.println("Notifications enabled");
#endif
      notifEnabled = true;
    }
    else
    {
#ifdef DEBUG_OUT
      Serial.println("Notifications disabled");
#endif
      notifEnabled = false;
    }
  };
};

bool oldStatus = false;

void BleUartClient::loop(void)
{
  UartFrame received{};
  if(rxQueue && xQueueReceive(rxQueue,&received,0)==pdTRUE) handleData(received.data,received.len);
  static UartFrame sending{}; static size_t offset=0; static uint32_t last=0;
  if(!deviceConnected || !notifEnabled) { sending.len=0;offset=0;if(txQueue)xQueueReset(txQueue); }
  else if(txQueue && uint32_t(millis()-last)>=20) {
    if(!sending.len && xQueueReceive(txQueue,&sending,0)==pdTRUE) offset=0;
    if(sending.len) {
      const uint16_t mtu=pServer->getPeerMTU(pServer->getConnId());
      const size_t chunk=disaster::uartChunkSize(mtu,sending.len-offset);
      pCharacteristicUartTX->setValue(sending.data+offset,chunk);pCharacteristicUartTX->notify();
      offset+=chunk;last=millis();if(offset==sending.len){sending.len=0;offset=0;}
    }
  }
  if (notifEnabled && !oldStatus)
  {
    oldStatus = true;
    if (!username.isEmpty())
    {
      Datagram nameDatagram;
      nameDatagram.type = 'u';
      int msgLen = sprintf((char *)nameDatagram.message, "00u|%s", username.c_str());
      receive(nameDatagram, msgLen + DATAGRAM_HEADER);
    }
    if (history)
    {
      history->replay(&ble_client);
    }
  }
  if (!notifEnabled && oldStatus)
  {
    oldStatus = false;
  }
}

void BleUartClient::startServer(void (*callback)(BleUartClient *))
{
  connectCallback = callback;

  init();
  if(rxQueue && txQueue && connectCallback) connectCallback(&ble_client);
}

void BleUartClient::init()
{
  rxQueue=xQueueCreate(4,sizeof(UartFrame));txQueue=xQueueCreate(8,sizeof(UartFrame));
  if(!rxQueue || !txQueue) { Serial.println("[BLE] Kein RAM fuer BLE-UART; WLAN bleibt aktiv"); return; }
  uint64_t uniqueId = ESP.getEfuseMac();
  // Using ESP32 MAC (48 bytes only, so upper 2 bytes will be 0)
  snprintf(apName, sizeof(apName), "HaldenFunk-%02X%02X%02X%02X%02X%02X",
          (uint8_t)(uniqueId), (uint8_t)(uniqueId >> 8),
          (uint8_t)(uniqueId >> 16), (uint8_t)(uniqueId >> 24),
          (uint8_t)(uniqueId >> 32), (uint8_t)(uniqueId >> 40));
#ifdef DEBUG_OUT
  Serial.printf("Device name: %s\n", apName);
#endif

  // Initialize BLE and set output power
  BLEDevice::init(apName);
  // Default GATT permissions are open: no pairing PIN or configuration service.
  BLEDevice::setMTU(260);
  BLEDevice::setPower(ESP_PWR_LVL_P7);

#ifdef DEBUG_OUT
  BLEAddress thisAddress = BLEDevice::getAddress();
  Serial.printf("BLE address: %s\n", thisAddress.toString().c_str());
#endif

  // Create BLE Server
  pServer = BLEDevice::createServer();

  // Set server callbacks
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the UART BLE Service
  uartService = pServer->createService(UART_UUID);

  // Create a BLE Characteristic
  pCharacteristicUartTX = uartService->createCharacteristic(
      TX_UUID,
      BLECharacteristic::PROPERTY_NOTIFY |
          BLECharacteristic::PROPERTY_READ);

  pCharacteristicUartTX->addDescriptor(new BLE2902());

  // Register callback for notification enabled
  pCharacteristicUartTX->setNotifyProperty(true);

  pCharacteristicUartRX = uartService->createCharacteristic(
      RX_UUID,
      BLECharacteristic::PROPERTY_WRITE);

  pCharacteristicUartRX->setCallbacks(new UartTxCbHandler());

  txDescriptor = pCharacteristicUartTX->getDescriptorByUUID("2902");
  if (txDescriptor != NULL)
  {
    txDescriptor->setCallbacks(new DescriptorCallbacks());
  }

  // Start the service
  uartService->start();

  // Start advertising
  pAdvertising = pServer->getAdvertising();
  pAdvertising->addServiceUUID(UART_UUID);
  pAdvertising->start();
}

#endif

