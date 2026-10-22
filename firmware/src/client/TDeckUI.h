#pragma once

// T-Deck Plus experimental on-device UI. Only built with -DTDECK_SCREEN.
// Stable WiFi-only T-Deck and T-Watch profiles remain unchanged.
#if defined(LILYGO_TDECK) && defined(TDECK_SCREEN)

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <TinyGPS++.h>
#include <Wire.h>
#include "BoardClient.h"
#include "../DisasterClient.h"
#include "TDeckTrackball.h"
#include "TDeckTouch.h"
#include "TDeckTouchTransform.h"

class TDeckUI : public DisasterClient {
public:
  void attachBoard(BoardClient *board) { board_ = board; }
  void beginDisplay();
  void loop() override;
  void receive(struct Datagram datagram, size_t len) override;
private:
  enum Page : uint8_t { CHAT = 0, QUICK = 1, BOARD = 2, MAP = 3, SETTINGS = 4 };
  TFT_eSPI lcd_;
  HardwareSerial gnss_{1};
  TinyGPSPlus gps_;
  BoardClient *board_ = nullptr;
  Page page_ = CHAT;
  String messages_[12];
  String draft_;
  uint8_t count_ = 0, selected_ = 0;
  uint8_t quickPending_ = 255;
  uint8_t chatScroll_ = 0;
  uint32_t confirmAt_ = 0, lastKeyboardPoll_ = 0, lastPaint_ = 0, lastPosition_ = 0;
  uint32_t splashUntil_ = 0;
  TDeckTrackball trackball_;
  TDeckTouch touch_;
  TDeckTouchTransform touchTransform_, pendingTransform_;
  bool touchFound_=false, keyboardFound_=false, touchCalibrated_=false, calibrating_=false;
  bool touchDown_=false;
  bool touchGestureValid_=false;
  uint8_t calibrationStep_=0;
  int calibrationX_[3]={}, calibrationY_[3]={};
  int touchStartX_=0, touchStartY_=0, touchLastX_=0, touchLastY_=0;
  uint32_t lastTouchPoll_=0, touchStartedAt_=0;
  uint32_t calibrationAcceptAt_=0;
  uint32_t lastMessageAt_ = 0;
  bool ready_ = false, dirty_ = true, autoFollow_ = true;
  double latitude_ = 0.0, longitude_ = 0.0;
  int zoom_ = 1;    // 0 = local, 1 = district, 2 = regional
  int viewX_ = 0, viewY_ = 0;

  void draw();
  void header();
  void bottom(const String &text);
  void text(int x, int y, const String &value, uint16_t color = 0xffff, uint8_t scale = 1);
  void drawChat();
  void drawQuick();
  void drawBoard();
  void drawMap();
  void drawSettings();
  void readTouch();
  void handleTouch(int x, int y, int endX, int endY);
  void startCalibration();
  void drawCalibration();
  void calibrationTap(int rawX, int rawY);
  void movePage(int delta);
  void handleKey(char ch);
  void handleClick();
  void receiveChat(const char *src, size_t bytes);
  void sendChat(const String &value);
  void sendBoard(const String &value);
  void readKeyboard();
  void readTrackball();
  void readGps();
  void appendMessage(const String &value);
  static String readable(String input);
};
#endif
