#include <Arduino.h>

// required for LoRa and/or AsyncSDServer libraries?
#include <FS.h>
#include <SPI.h>

#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <SD.h>
#include <LittleFS.h>
#ifdef HAS_OLED
#include <SSD1306Wire.h>
#endif
#include "config.h"
#ifdef DISABLE_BROWNOUT
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#endif
#ifdef BOARD_PMU_AXP2101
#include <Wire.h>
#include <XPowersLib.h>
XPowersAXP2101 pmu;
#endif


#include <Layer1_RadioLib.h>

#include <LoRaLayer2.h>
#include <RadioPresets.h>

// server
#include "server/DisasterRadio.h"
// client
#include "client/OLEDClient.h"
#include "client/HistoryRecord.h"
#include "client/LoRaClient.h"
#include "client/StreamClient.h"
#include "client/TCPClient.h"
#include "client/WebSocketClient.h"
#include "client/GPSClient.h"
#include "client/BoardClient.h"
#include "client/BleUartClient.h"

// middleware
#include "middleware/Console.h"
#include "middleware/HistoryReplay.h"
// history
#include "history/HistorySD.h"
#include "history/HistoryMemory.h"

#include "DisasterHistory.h"
#include "DisasterMiddleware.h"

#define MDNS_NAME_PREFIX "haldenfunk"
#define HOST_NAME "haldenfunk"
#define WIFI_AP_SSID_PREFIX "HaldenFunk-"

#define INDEX_FILE "index.html"

#ifdef HAS_OLED
SSD1306Wire display(0x3c, OLED_SDA, OLED_SCL);
#endif

#ifdef SD_SCK
SPIClass sd_card(HSPI);
#else
SPIClass sd_card(VSPI_OR_FSPI);
#endif


AsyncWebServer http_server(80);
AsyncWebSocket ws_server("/ws");

#ifdef HAS_BLE
BleUartClient ble_client;
#endif

#ifdef RL_SX1276
SX1276 lora = new Module(LORA_CS, LORA_IRQ, LORA_RST, LORA_BUSY);
  #ifdef DUAL_LORA
  SX1276 lora2 = new Module(LORA2_CS, LORA2_IRQ, LORA2_RST, LORA2_BUSY);
  #endif
#endif

#ifdef RL_SX1262
SX1262 lora = new Module(LORA_CS, LORA_IRQ, LORA_RST, LORA_BUSY);
  #ifdef DUAL_LORA
  SX1262 lora2 = new Module(LORA2_CS, LORA2_IRQ, LORA2_RST, LORA2_BUSY);
  #endif
#endif

LL2Class *LL2;

#include "settings/settings.h"

// Funkprofil aus den Einstellungen (RadioPresets.h); Frequenz/BW/SF/CR kommen nur noch von dort
const RadioPreset &activePreset() { return getRadioPreset(radioPreset); }
float loraFreqMHz() { return activePreset().freqMHz; }
Layer1Class *Layer1_main = NULL;

DisasterRadio *radio = new DisasterRadio();
DisasterHistory *history = NULL;
BoardClient *board = NULL;

int internal_clients = 0;
int clients = 0;
int routes = 0;

#define WIFI_POLL_DELAY 500
#define WIFI_POLL_TRIES 20

char nodeAddress[ADDR_LENGTH*2 + 1] = {'\0'};
char ssid[100] = {'\0'};
bool apOk = false;
uint32_t lastApRetry = 0, lastApPrint = 0;

void bootMark(const char *step)
{
  Serial.printf("[BOOT %lu ms] %s\n", (unsigned long)millis(), step);
  Serial.flush();
}

bool startSoftAP()
{
  bool ok = WiFi.softAP(ssid, nullptr, 1, false, 4);
#ifdef WIFI_TX_POWER
  WiFi.setTxPower(WIFI_TX_POWER);
#endif
  Serial.printf("[WLAN] softAP(\"%s\", Kanal 1) -> %s, TX-Leistung %d (0,25 dBm)\n", ssid, ok ? "OK" : "FEHLER",
                (int)WiFi.getTxPower());
  Serial.flush();
  return ok;
}
IPAddress ip;

bool sdInitialized = false;
bool fsInitialized = false;
bool displayInitialized = false;
bool loraInitialized = false;

void setupWiFi()
{
  Serial.println("* Initializing WiFi...");

  // get the WiFi MAC address
  uint8_t mac[6];
  WiFi.macAddress(mac);

  // format WiFi MAC address to string
  sprintf(nodeAddress, "%02x%02x%02x%02x", mac[2], mac[3], mac[4], mac[5]);

#ifdef WIFI_SSID
  Serial.printf(" --> Connecting to WiFi \"%s\"\n", WIFI_SSID);
  for (int i = 0; i < WIFI_POLL_TRIES && WiFi.status() != WL_CONNECTED; i++)
  {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(WIFI_POLL_DELAY);
  }
  if (WiFi.status() == WL_CONNECTED)
  {
    ip = WiFi.localIP();
    snprintf(ssid, sizeof(ssid), "%s", WIFI_SSID);

    Serial.print(" --> WiFi connected, IP address: ");
    Serial.println(ip);
  }
  else
  {
    Serial.println(" --> Unable to connect to WiFi");
  }
#endif

  if (WiFi.status() != WL_CONNECTED)
  {
    // format full SSID with MAC address suffix
    snprintf(ssid, sizeof(ssid), "%s%02X%02X%02X", WIFI_AP_SSID_PREFIX, mac[3], mac[4], mac[5]);

    // Open AP, also after upgrading a device with saved credentials.
    Preferences wp;
    if (wp.begin("dar-wifi", false)) { wp.remove("ap-pass"); wp.end(); }

    // start the AP
    Layer1Class::holdTx(8000); // waehrend WLAN-Start nicht per LoRa senden (Stromspitzen)
    bootMark("WiFi.mode(AP)");
    WiFi.mode(WIFI_AP);
#ifdef WIFI_TX_POWER
    WiFi.setTxPower(WIFI_TX_POWER); // Brownout-Schutz (z. B. Heltec V2)
    bootMark("WiFi.setTxPower");
#endif
    WiFi.setHostname(HOST_NAME);
    apOk = startSoftAP();

    ip = WiFi.localIP();
    ip = WiFi.softAPIP();
    Serial.printf("\n==============================\nWLAN: %s\nOffenes WLAN - kein Passwort\nBrowser: http://%s\n==============================\n",
                  ssid, ip.toString().c_str());
  }
}

void checkWiFi() {
#ifdef WIFI_SSID
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }
#endif
}

void setupMDNS()
{
  Serial.println("* Initializing mDNS responder...");
  if (MDNS.begin(MDNS_NAME_PREFIX))
  {
    Serial.println(" --> Advertising http://" MDNS_NAME_PREFIX ".local");
  }
  else
  {
    Serial.println(" --> mDNS responder failed");
  }
}

void setupSD()
{
#ifdef SD_SCK
  Serial.println("* Initializing SD card...");
  sd_card.begin(SD_SCK, SD_MISO, SD_MOSI, -1);
  if (SD.begin(SD_CS, sd_card))
  {
    sdInitialized = true;
  }
  else
  {
    Serial.println(" --> SD card not found");
  }
#endif
}

void setupFS()
{
  Serial.println("* Initializing LittleFS...");
  if (LittleFS.begin(true))
  {
    fsInitialized = true;
  }
  else
  {
    Serial.println(" --> LittleFS initializtion failed");
  }
}

bool checkFileIsReadable(FS &fs, const char *path)
{
  if (fs.exists(path))
  {
    return !!fs.open(path, "r");
  }
  return false;
}

void setupHTTPSever()
{
  Serial.println("* Initializing HTTP server...");

  if (sdInitialized && checkFileIsReadable(SD, "/" INDEX_FILE))
  {
    Serial.println(" --> Serving web application from SD card");
    http_server.serveStatic("/", SD, "/").setDefaultFile(INDEX_FILE).setCacheControl("max-age=600");
  }
  else if (fsInitialized && checkFileIsReadable(LittleFS, "/" INDEX_FILE))
  {
    Serial.println(" --> Serving web application from LittleFS");
    http_server.serveStatic("/", LittleFS, "/").setDefaultFile(INDEX_FILE);
  }
  else
  {
    Serial.println(" --> No web application found! Did you add it to the SD card or SPIFFs?");
  }

  http_server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *request) {
    char json[768];
    snprintf(json, sizeof(json),
             "{\"name\":\"HaldenFunk\",\"version\":\"%s\",\"board\":\"%s\",\"node\":\"%s\",\"ssid\":\"%s\","
             "\"lora\":%s,\"preset\":%d,\"presetId\":\"%s\",\"presetName\":\"%s\",\"freq\":%.3f,\"bw\":%.1f,\"sf\":%d,\"cr\":\"4/%d\",\"airtimeMs\":%lu,\"airtimeBudgetMs\":%lu,\"airtimePct\":%.2f,\"dutyLimitPct\":%.0f,\"txDeferred\":%lu,\"txPower\":%d,\"routes\":%d,\"clients\":%d,\"sd\":%s,\"uptime\":%lu,"
             "\"heap\":%u,\"minHeap\":%u,\"maxBlock\":%u,\"heapWarn\":%u}",
             DAR_VERSION, BOARD_NAME, nodeAddress, ssid, loraInitialized ? "true" : "false", radioPreset, activePreset().id, activePreset().name, loraFreqMHz(), activePreset().bwKHz, activePreset().sf, activePreset().cr,
             (unsigned long)(Layer1_main ? Layer1_main->airtimeUsedMs() : 0), (unsigned long)(activePreset().dutyLimit * 3600000.0f),
             Layer1_main ? Layer1_main->airtimeUsedMs() / 36000.0f : 0.0f, activePreset().dutyLimit * 100.0f, (unsigned long)(Layer1_main ? Layer1_main->deferredCount() : 0),
             txPower, routes, clients, sdInitialized ? "true" : "false", (unsigned long)(millis() / 1000),
             (unsigned)ESP.getFreeHeap(), (unsigned)ESP.getMinFreeHeap(), (unsigned)ESP.getMaxAllocHeap(), (unsigned)HEAP_WARN_BYTES);
    request->send(200, "application/json", json);
  });

  // Funkprofile auflisten / waehlen (gespeichert im NVS, wirksam nach Neustart)
  http_server.on("/api/presets", HTTP_GET, [](AsyncWebServerRequest *request) {
    String j = "[";
    for (int i = 0; i < RADIO_PRESET_COUNT; i++) {
      const RadioPreset &p = RADIO_PRESETS[i];
      char b[200];
      snprintf(b, sizeof(b), "%s{\"i\":%d,\"id\":\"%s\",\"name\":\"%s\",\"freq\":%.3f,\"bw\":%.1f,\"sf\":%d,\"cr\":%d,\"duty\":%.0f}",
               i ? "," : "", i, p.id, p.name, p.freqMHz, p.bwKHz, p.sf, p.cr, p.dutyLimit * 100.0f);
      j += b;
    }
    request->send(200, "application/json", j + "]");
  });
  http_server.on("/api/preset", HTTP_POST, [](AsyncWebServerRequest *request) {
    if (!request->hasParam("preset", true)) { request->send(400, "text/plain", "preset fehlt"); return; }
    int p = request->getParam("preset", true)->value().toInt();
    if (p < 0 || p >= RADIO_PRESET_COUNT) { request->send(400, "text/plain", "ungueltiges Profil"); return; }
    saveRadioPreset(p);
    request->send(200, "application/json", "{\"ok\":true,\"restart\":true}");
    static esp_timer_handle_t t = NULL;
    if (!t) { esp_timer_create_args_t a = {}; a.callback = [](void *) { ESP.restart(); }; a.name = "rst"; esp_timer_create(&a, &t); }
    esp_timer_start_once(t, 1500000);
  });

  http_server.on("/api/board", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "application/json", board ? board->toJson() : String("[]"));
  });

  http_server.onNotFound([](AsyncWebServerRequest *request) {
    request->send(404);
  });

  http_server.onRequestBody([](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
  });

  http_server.begin();

  MDNS.addService("http", "tcp", 80);
}

void setupHistory()
{
  Serial.println("* Initializing history...");

  if (sdInitialized)
  {
    HistorySD *history_sd_client = new HistorySD(&sd_card);
    if (history_sd_client->init())
    {
      Serial.println(" --> Storing history on SD card");
      history = history_sd_client;
    }
  }
  if (!history)
  {
    Serial.println(" --> Storing (limited) history in memory");
    history = new HistoryMemory();
  }

  radio->connect(new HistoryRecord(history));
}

struct Datagram buildDatagram(uint8_t destination[ADDR_LENGTH], uint8_t type, uint8_t* data, size_t len){
    struct Datagram datagram;
    memcpy(datagram.destination, destination, ADDR_LENGTH);
    datagram.type = 'c';
    memcpy(datagram.message, data, len);
    return datagram;
}

class WelcomeMessage : public DisasterMiddleware
{
public:
  void setup()
  {
    char data[128] = {0};
    int msgLen = 0;
    Serial.printf("WelcomeMessage username: >%s<\n", username.c_str());
    if (username.isEmpty())
    {
      msgLen = sprintf(data, "00c|Glueck Auf! Willkommen bei HaldenFunk ");
    }
    else
    {
      msgLen = snprintf(data, 127, "00c|Glueck Auf! Willkommen bei HaldenFunk >%s<", username.c_str());
    }

    struct Datagram datagram1 = buildDatagram(BROADCAST, 'i', (uint8_t *)data, msgLen);
    client->receive(datagram1, msgLen + DATAGRAM_HEADER);
    if (!sdInitialized)
    {
      msgLen = sprintf(data, "00c|Hinweis: keine SD-Karte, Verlauf nur im RAM");
      struct Datagram datagram2 = buildDatagram(BROADCAST, 'i', (uint8_t *)data, msgLen);
      client->receive(datagram2, msgLen + DATAGRAM_HEADER);
    }
    if (!loraInitialized)
    {
      msgLen = sprintf(data, "00c|WARNUNG: LoRa-Funkmodul nicht gefunden");
      struct Datagram datagram3 = buildDatagram(BROADCAST, 'i', (uint8_t *)data, msgLen);
      client->receive(datagram3, msgLen + DATAGRAM_HEADER);
    }
    client->setup();
  }
};

void setupSerial()
{
  Serial.println("* Initializing serial...");

  radio->connect(new WelcomeMessage())
      ->connect(new HistoryReplay(history))
      ->connect(new Console())
      ->connect(new StreamClient(&Serial));
}

void setupWebSocket()
{
  Serial.println("* Initializing WebSocket server...");

  http_server.addHandler(&ws_server);

  WebSocketClient::startServer(&ws_server, [](WebSocketClient *ws_client) {
    radio->connect(new WelcomeMessage())
        ->connect(new HistoryReplay(history))
        ->connect(ws_client);
  });
}

void setupLoRa()
{
  char cfgStr[MESSAGE_LENGTH];
#ifdef LORA_CS
  Serial.println("* Initializing LoRa...");
  #ifdef LOPY4
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI); //LORA_CS);
  #endif
  
  #if defined(LORA_SCK) && !defined(LOPY4)
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI);
  #endif
  pinMode(LORA_CS, OUTPUT);
  digitalWrite(LORA_CS, LOW);
  #ifdef DUAL_LORA
  pinMode(LORA2_CS, OUTPUT);
  digitalWrite(LORA2_CS, HIGH);
  #endif
  const RadioPreset &rp = activePreset();
  Layer1Class *Layer1_1 = new Layer1Class(&lora, 0, LORA_CS, LORA_RST, LORA_IRQ, rp.sf, rp.freqMHz, txPower, rp.bwKHz, LORA_TCXO, rp.cr, rp.dutyLimit);
  Layer1_main = Layer1_1;
  #ifdef DUAL_LORA
  digitalWrite(LORA_CS, HIGH);
  digitalWrite(LORA2_CS, LOW);
  Layer1Class *Layer1_2 = new Layer1Class(&lora2, 0, LORA2_CS, LORA2_RST, LORA2_IRQ, rp.sf, rp.freqMHz, txPower, rp.bwKHz, LORA_TCXO, rp.cr, rp.dutyLimit);
  digitalWrite(LORA_CS, LOW);
  digitalWrite(LORA2_CS, HIGH);
  #endif
  if(Layer1_1->init())
  {
    #ifndef DUAL_LORA
    Serial.printf(" --> Layer1 init succeeded\r\n");
    LL2 = new LL2Class(Layer1_1);
    LL2->setDutyCycle(rp.dutyLimit);
    #else
    if(Layer1_2->init()){
      Serial.printf(" --> Dual Layer1 init succeeded\r\n");
      LL2 = new LL2Class(Layer1_1, Layer1_2);
    }
    #endif
    LL2->setLocalAddress(nodeAddress);
    LL2->setInterval(routeInterval);
    LoRaClient *lora_client = new LoRaClient(LL2);
    if (lora_client->init())
    {
      Serial.printf(" --> LL2 init succeeded\r\n");
      LL2->getCurrentConfig(cfgStr);
      Serial.printf("%s", cfgStr);
      radio->connect(lora_client);
      loraInitialized = true;
      return;
    }
  }
  Serial.println(" --> Failed to initialize LoRa");
#endif
}

#define STATUS_BAR_HEIGHT 12
#define MARGIN 3

void drawStatusBar()
{
  #ifdef HAS_OLED
  if (!displayInitialized)
  {
    return;
  }

  display.setFont(ArialMT_Plain_10);

  // clear the status bar
  display.setColor(BLACK);
  display.fillRect(0, 0, OLED_WIDTH, STATUS_BAR_HEIGHT);

  // draw MAC
  display.setColor(WHITE);
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.drawString(0, 0, nodeAddress);

  String clientsString = String(clients) + "," + routes;
  String ipString = ip.toString();

  // measure client and IP width
  int widthClients = (int)display.getStringWidth(clientsString) + 1;
  int widthIP = display.getStringWidth(ipString);

  // clear space behind IP address in case the SSID was too long
  display.setColor(BLACK);
  display.fillRect(OLED_WIDTH - widthClients - MARGIN - widthIP - MARGIN, 0, OLED_WIDTH, STATUS_BAR_HEIGHT);

  // draw client count
  display.setColor(WHITE);
  display.fillRect(OLED_WIDTH - widthClients, 2, widthClients, STATUS_BAR_HEIGHT - 3);
  display.setColor(BLACK);
  display.setTextAlignment(TEXT_ALIGN_RIGHT);
  display.drawString(OLED_WIDTH, 0, clientsString);

  // draw IP address
  display.setColor(WHITE);
  display.setTextAlignment(TEXT_ALIGN_RIGHT);
  display.drawString(OLED_WIDTH - widthClients - MARGIN, 0, ipString);

  // draw divider line
  display.drawLine(0, 12, 128, 12);
  display.display();
  #endif
}

void setupDisplay()
{
#ifdef HAS_OLED
  Serial.println("* Initializing display...");
#ifdef VEXT_PIN
  pinMode(VEXT_PIN, OUTPUT);
  digitalWrite(VEXT_PIN, LOW);
  delay(50);
#endif
  if (OLED_RST != NOT_A_PIN)
  {
    pinMode(OLED_RST, OUTPUT);
    digitalWrite(OLED_RST, LOW); // set GPIO16 low to reset OLED
    delay(50);
    digitalWrite(OLED_RST, HIGH); // while OLED is running, must set GPIO16 in high
  }
  if (display.init())
  {
    displayInitialized = true;

    display.flipScreenVertically();
    display.clear();

    radio->connect(new OLEDClient(&display, 0, STATUS_BAR_HEIGHT + 1, OLED_WIDTH, OLED_HEIGHT));

    drawStatusBar();
  }
  else
  {
    Serial.println(" --> Failed to initialize the display");
  }

#endif
}

void setupGPS()
{
#ifdef GPS_SERIAL
  Serial.println("* Initializing GPS...");
  Serial1.begin(GPS_SERIAL);
  radio->connect(new GPSClient(&Serial1, beaconPeriod));
  Serial.printf(" --> GPS connected,");
  if(beaconPeriod == 0)
  {
    Serial.printf(" beacons disabled\r\n");
  }
  else
  {
    Serial.printf(" beacons enabled with period of %ldms\r\n", beaconPeriod);
  }
#endif
}

#ifdef HAS_BLE
void setupBLE(void)
{
  Serial.println("* Initializing BLE...");

  uint64_t uniqueId = ESP.getEfuseMac();

  sprintf(nodeAddress, "%02x%02x%02x%02x", (uint8_t)(uniqueId >> 16), (uint8_t)(uniqueId >> 24), (uint8_t)(uniqueId >> 32), (uint8_t)(uniqueId >> 40));

  ble_client.startServer([](BleUartClient *ble_client) {
  	radio->connect(new WelcomeMessage())
        ->connect(new HistoryReplay(history))
  		->connect(ble_client);
  });
}
#else
void setupBLE(void) { Serial.println("* BLE in diesem Build deaktiviert"); }
#endif

void setupNetwork()
{
  // Always keep the open WLAN available, even with an old saved BLE-only setting.
  bootMark("WLAN");
  setupWiFi();
  delay(STARTUP_STAGGER_MS);
  bootMark("mDNS");
  setupMDNS();
  bootMark("HTTP");
  setupHTTPSever();
  bootMark("Telnet/WebSocket");
  // No network console on an open AP. Operator configuration stays on USB.
  setupWebSocket();
#ifdef HAS_BLE
  setupBLE(); // optional combined build; never replaces WLAN
#endif
}

// Board-Versorgung vor LoRa einschalten (T-Deck: Peripherie-Pin, T-Watch S3: AXP2101-Kanäle)
void setupBoardPower()
{
#ifdef BOARD_POWER_PIN
  pinMode(BOARD_POWER_PIN, OUTPUT);
  digitalWrite(BOARD_POWER_PIN, HIGH);
#endif
#ifdef BOARD_TFT_CS
  pinMode(BOARD_TFT_CS, OUTPUT);
  digitalWrite(BOARD_TFT_CS, HIGH);
#endif
#ifdef BOARD_SD_CS
  pinMode(BOARD_SD_CS, OUTPUT);
  digitalWrite(BOARD_SD_CS, HIGH);
#endif
#ifdef BOARD_TFT_BL
  pinMode(BOARD_TFT_BL, OUTPUT);
  digitalWrite(BOARD_TFT_BL, LOW);
#endif
#ifdef BOARD_PMU_AXP2101
  if (pmu.begin(Wire, AXP2101_SLAVE_ADDRESS, BOARD_PMU_SDA, BOARD_PMU_SCL))
  {
    pmu.setALDO3Voltage(3300); pmu.enableALDO3();  // LoRa-Funkmodul
    pmu.setALDO4Voltage(3300); pmu.enableALDO4();  // LoRa (muss an bleiben)
    pmu.disableALDO2();                            // Display/Touch aus (kein Display-Treiber)
    pmu.disableBLDO2();                            // Vibrationsmotor aus
    pmu.enableBattVoltageMeasure();
    Serial.println("* AXP2101: LoRa-Versorgung an");
  }
  else
  {
    Serial.println(" --> AXP2101 nicht gefunden (LoRa ohne Versorgung)");
  }
#endif
#if defined(BOARD_POWER_PIN) || defined(BOARD_PMU_AXP2101)
  delay(20); // Versorgung stabilisieren lassen
#endif
}

void setup()
{
#ifdef DISABLE_BROWNOUT
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Brownout-Detektor aus (Heltec V2: Reset-Schleifen)
#endif
  Serial.begin(115200);
  delay(200);
  bootMark("Serial");

  // Get saved settings
  getSettings();
  bootMark("Einstellungen");

  setCpuFrequencyMhz(CLOCK_SPEED); //Set CPU clock in config.h
  getCpuFrequencyMhz(); //Get CPU clock

  Serial.printf("\nHaldenFunk %s (%s) - basiert auf sudomesh/disaster-radio\n", DAR_VERSION, BOARD_NAME);
  delay(STARTUP_STAGGER_MS); // gestaffelter Start: Spannung stabilisieren lassen
#ifndef WIFI_LATE
  setupNetwork();
#endif
  bootMark("SD");
  setupSD();
  bootMark("LittleFS");
  setupFS();
  setupHistory();
  setupSerial();
  board = new BoardClient(fsInitialized ? (fs::FS *)&LittleFS : NULL);
  radio->connect(board);
  delay(STARTUP_STAGGER_MS);
  bootMark("Versorgung");
  setupBoardPower();
  bootMark("LoRa");
  setupLoRa();
  bootMark("Display");
  setupDisplay();
  setupGPS();
#ifdef WIFI_LATE
  // WLAN zuletzt, mit Pause nach dem Funkmodul (Stromspitzen entzerren)
  delay(WIFI_LATE_DELAY_MS);
  setupNetwork();
#endif
  bootMark("fertig");

  internal_clients = radio->clients.size();

  radio->setup();
}

void loop()
{
  radio->loop();
  if(loraInitialized){
    int new_clients = radio->clients.size() - internal_clients;
    int new_routes = LL2->getRouteEntry();
    if (clients != new_clients || routes != new_routes)
    {
      clients = new_clients;
      routes = new_routes;
      Serial.printf("--> clients=%d routes=%d\n", clients, routes);
      drawStatusBar();
    }
  }
  // Freien Speicher alle 30 s seriell melden, unter HEAP_WARN_BYTES mit Warnung
  static unsigned long lastHeapPrint = 0;
  if (millis() - lastHeapPrint > 30000)
  {
    lastHeapPrint = millis();
    uint32_t freeHeap = ESP.getFreeHeap();
    Serial.printf("[HEAP] frei %u B | Minimum %u B | groesster Block %u B%s\n", (unsigned)freeHeap, (unsigned)ESP.getMinFreeHeap(),
                  (unsigned)ESP.getMaxAllocHeap(), freeHeap < HEAP_WARN_BYTES ? " | WARNUNG: wenig freier Speicher" : "");
  }
  // WLAN-AP pruefen/neu starten und Zugangsdaten regelmaessig ausgeben
  if (ssid[0] && WiFi.getMode() & WIFI_AP)
  {
    if (!apOk && millis() - lastApRetry > 5000)
    {
      lastApRetry = millis();
      Layer1Class::holdTx(3000);
      apOk = startSoftAP();
    }
    if (millis() - lastApPrint > 30000)
    {
      lastApPrint = millis();
      Serial.printf("[WLAN] %s | SSID: %s | offen, ohne Passwort | http://%s | Clients: %d\n", apOk ? "AP aktiv" : "AP FEHLER", ssid,
                    WiFi.softAPIP().toString().c_str(), WiFi.softAPgetStationNum());
#ifdef HAS_OLED
      if (displayInitialized && clients == 0)
      {
        display.setColor(BLACK);
        display.fillRect(0, STATUS_BAR_HEIGHT + 1, OLED_WIDTH, OLED_HEIGHT - STATUS_BAR_HEIGHT - 1);
        display.setColor(WHITE);
        display.setFont(ArialMT_Plain_10);
        display.setTextAlignment(TEXT_ALIGN_LEFT);
        display.drawString(0, 16, apOk ? "WLAN:" : "WLAN FEHLER:");
        display.drawString(0, 28, ssid);
        display.drawString(0, 40, "offen, ohne Passwort");
        display.drawString(0, 52, WiFi.softAPIP().toString());
        display.display();
      }
#endif
    }
  }
  // reconnect only in WiFi client mode 
#ifdef WIFI_SSID
  {
    checkWiFi();
  }
#endif
}

