# DisAHRsterRadio / HaldenFunk – Solarbox für LILYGO T3-S3 V1.3

Wetterfestes, 3D-druckbares Gehäuse für einen solarversorgten Mesh-Knoten (T3-S3 V1.3, SX1262, 868 MHz, WLAN-AP 24/7).
**Nur Konzept/Entwurf – nichts davon ist gedruckt oder praktisch getestet.** Erst ein Probedruck zeigt, ob alles passt.

Materialien: **PETG** für Gehäuse, Deckel, Schlitten und Halter · **TPU 95A** für Dichtung und USB-Stopfen.

## Dateien

| Datei | Material | Stück | Hinweis |
|---|---|---|---|
| `gehaeuse_unterteil.stl` | PETG | 1 | Öffnung nach oben drucken, Fase unter dem Flansch ist stützfrei (45°) |
| `gehaeuse_deckel.stl` | PETG | 1 | neutraler Deckel; **Oberseite aufs Druckbett** |
| `gehaeuse_deckel_haldenfunk.stl` | PETG | (1) | Deckel mit Förderturm-Logo, „HaldenFunk · Glück Auf“ (0,8 mm vertieft) |
| `gehaeuse_deckel_disahrsterradio.stl` | PETG | (1) | Deckel mit Ahrtal-Logo, „DisAHRsterRadio“ (0,8 mm vertieft) |
| `dichtung_tpu.stl` | TPU 95A | 1 | Dichtschnur 1,6 × 1,9 mm für die Nut im Unterteil |
| `usb_stopfen_tpu.stl` | TPU 95A | 1 | Stopfen für USB-C-Öffnung, Halteband mit Öse über die M12-Verschraubung |
| `platinenschlitten.stl` | PETG | 1 | Träger für die T3-S3-Platine über dem Akkuhalter |
| `solar_halter_wand.stl` | PETG | 2 | Wandteil des Neigungshalters (Gelenk, Raster 30/45/60/70°) |
| `solar_halter_arm.stl` | PETG | 2 | Arm, auf die Rückseite/den Rahmen des Paneels schrauben |
| `cad/solarbox.py` | – | – | parametrisches CadQuery-Modell (alle Maße oben im Skript) |
| `stl/pruefung_manifold.json` | – | – | trimesh-Prüfung: alle Teile wasserdicht/manifold, je 1 Körper |

Außenmaße Unterteil: 146 × 118 mm Flansch (Körper 130 × 102 mm), Tiefe 49 mm, mit Wandlaschen 134 mm hoch. Deckel 150 × 122 × 4 mm (+3 mm Tropfkante, +0,6 mm Feder).
Innenraum 124 × 96 × 46 mm.

## Druckeinstellungen

**PETG** (Unterteil, Deckel, Schlitten): 0,2 mm Schicht, **4 Wände**, 5 Boden-/Deckschichten, **30 % Infill** (Gyroid), 240 °C / Bett 80 °C, Kühlung 30–50 %, keine Stützen.
Solarhalter: 4 Wände, **60–100 % Infill** (Windlast!), Grundplatte aufs Bett.
**TPU 95A** (Dichtung, Stopfen): 0,2 mm, langsam (15–25 mm/s), 100 % Infill, keine Retraktion bzw. sehr kurz, 225–235 °C.
Dichtung flach drucken; die erste Schicht sauber kalibrieren (Ring ist nur 4 Linien breit).

## Elektrik (Empfehlung „Variante B“ – effizient)

```
10-W-Paneel 18 V ──(M12-Verschraubung)──► CN3791-MPPT-Lader (SOLAR IN; MPPT-Stufe passend zum 18-V-Paneel lt. Soldered-Doku wählen)
                                              │ BAT (+/–)  ── Sicherung ca. 5 A ──┐
                                              ▼                                   │
                            3 × 18650 parallel (1S3P) im Halter ◄─────────────────┘
                                              │ B+/B–
                                       1S-Schutzplatine (DW01)
                                              │ P+/P–
                                   JST-PH-2.0-Kabel ► T3-S3 Akkubuchse (VBAT)
```

* T3-S3 läuft direkt an der Akkuspannung (3,0–4,2 V) – effizienter als 5 V über einen Boost-Wandler.
* **Nicht** das Paneel direkt an den T3-S3 hängen: Der Solareingang des V1.3 verträgt laut LILYGO nur **4,5–5,6 V** (Zenerdiode). 6-V-Paneele haben 7,2 V Leerlauf.
* **USB-C am T3-S3 nicht anstecken, während der externe Lader lädt** (LILYGO: Onboard-Lader lässt sich nicht abschalten → zwei Lader parallel). USB-C nur zum Flashen/Warten.
* **JST-PH-Polarität prüfen!** Rot/Schwarz ist bei Kaufkabeln nicht genormt. Vor dem Einstecken mit dem Multimeter messen (+ muss auf den +-Pin der Buchse). Falsch gepolt = Board kaputt.
* Gleiche, neue Zellen gleicher Charge verwenden; vor dem Parallelschalten auf gleiche Spannung bringen (< 0,05 V Differenz).
* DW01-Schutz trennt erst bei 2,45 V – in der Firmware (ADC an GPIO1) besser ab ~3,3 V schlafen legen.

## Energiebilanz (Schätzung!)

| Größe | Wert | Grundlage |
|---|---|---|
| Stromaufnahme T3-S3 mit WLAN-AP 24/7 | 80–120 mA, **typ. 100 mA** am Akku (Schätzung) | Forum core-electronics (T3-S3 Meshtastic ~60 mA idle, ~120 mA TX); andimoto (T3 V1.6.1 mit WLAN 135 mA @ 5 V) |
| Tagesbedarf | 7,1 / **8,9** / 10,7 Wh (80/100/120 mA × 3,7 V × 24 h) | Rechnung |
| Akku 3 × Samsung 35E (3,5 Ah, 3,6 V) | 37,8 Wh nominal, ~32 Wh nutzbar (85 %, Annahme) | Händlerangaben |
| Autarkie ohne Sonne | **3,0–3,6 Tage** (120/100 mA) | Rechnung |
| Systemwirkungsgrad Solar → Akku | ~0,62 = 0,78 (MPPT-Lader lt. Waveshare-Angabe für CN3791-Modul) × 0,8 (Temperatur, Schmutz, Winkel, Kabel; Annahme) | Schätzung |
| Dezember, ~1 Volllaststunde/Tag | Bedarf ≥ 14–17 W Paneel. 10 W liefert ~6,2 Wh/Tag → Defizit ~2,7–4,5 Wh/Tag | Rechnung |
| Frühjahr/Herbst, ~2,5 h (Annahme) | ≥ 6–7 W → 10 W reicht (~15,6 Wh/Tag) | Rechnung |
| Sommer, 4–5 h | ≥ 3,2–3,8 W → 10 W liefert ~28 Wh/Tag | Rechnung |

**Fazit:** 1 × 10 W deckt etwa März–Oktober voll; im Dezember/Januar reicht es für 24/7-WLAN-AP **nicht** (Akku überbrückt rechnerisch ~1–2 Wochen Defizit). Für echten Winterbetrieb: **2 × 10 W parallel** (~12,5 Wh/Tag im Dezember; Ladestrom dann bis ~4,2 A → Lader direkt am Zellblock, Sicherung) **oder** in der Firmware einen Wintermodus (WLAN-AP zeitgesteuert/auf Tastendruck).

## Stückliste (Preise vom 17.10.2026, inkl. MwSt., zzgl. Versand)

| Teil | Preis | Quelle |
|---|---|---|
| Waveshare Polysilizium-Solarpanel 18 V 10 W (Vmp 17,6 V, Voc 21,6 V, 0,57 A), IP67, 340 × 232 × 17 mm, 0,935 kg, Stecker 3,5 × 1,35 mm (WS-19598) | 11,50 € | https://www.berrybase.de/waveshare-polysilizium-solarpanel-18v-10w-36-zellen-340x232x17-mm-20-umwandlungseffizienz-ip67 |
| Soldered MPPT-Lader CN3791, JST-PH, 54 × 38 mm (SOL-333136) | 12,45 € | https://www.berrybase.de/soldered-mppt-li-ion-cn3791-ladeboard-solar-ladecontroller-fuer-lithium-akkus-jst-ph-6-18v |
| 3 × Samsung INR18650-35E (3500 mAh, ungeschützt) | 3 × 3,99 € | https://www.ttt48.de/akku/lithium-ionen/18650/samsung-inr-18650-35e-36v-37v-3500mah-lithium-ionen-akku-produktionsdatum-2026.html |
| Batteriehalter 3 × 18650, MPD BK-18650-PC6 (77,7 × 59,69 × 21,45 mm) | 7,25 € (lieferbar ab 14.1.2027) | https://www.reichelt.de/de/de/shop/produkt/batteriehalter_fuer_3_18650-213342 |
| 1S-Schutzplatine DW01+8205A, 2,5 A | 1,28 € | https://www.roboter-bausatz.de/p/3.7v-1s-2.5a-18650-li-ion-bms-pcm-battery-protection-board-lade-modul |
| Pigtail IPEX/U.FL → SMA-Einbaubuchse, 20 cm (WiMo 40350.SF) | 14,00 € | https://www.wimo.com/de/40350-sf |
| Kabelverschraubung M12 × 1,5, IP68, Ø 2,5–6,5 mm (AGRO 1555.12.06) | 0,70 € | https://www.reichelt.de/de/de/shop/produkt/kabelverschraubung_syntec_m12_x_1_5_mm_2_5_-_6_5_mm-299753 |
| **Summe Variante B (ohne Board, Filament, Schrauben, Kabel, Sicherung, Druckausgleich)** | **59,15 €** | |
| optional 2. Paneel für Winter | +11,50 € | s. o. |
| LILYGO T3-S3 (Board, falls nicht vorhanden) | 23,65 USD | https://lilygo.cc/products/t3s3-v1-0 |

Alternative **Variante A (Stecklösung, weniger effizient):** Waveshare Solar Power Manager (C) – MPPT (CN3791), Halter für 3 × 18650, Schutzschaltungen, 5 V/3 A an USB – 18,90 € bei https://www.berrybase.de/waveshare-solar-power-manager-c-5v-3a-mppt-usb-c-fuer-6v-24v-solarpanels-3x-18650-batteriehalter (19,19 USD bei waveshare.com). Das Board hängt dann per USB-C an 5 V: 5-V-Boost + 3,3-V-Regler kosten Energie → geschätzt 15–18 Wh/Tag, nur ~1,8–2,2 Tage Autarkie. Ruhestrom für (C) nicht eindeutig angegeben. Modul (119 × 71 × 25,2 mm) passt nur mit größerem Innenraum (`IZ = 50`, `PILLAR_H = 28` im Skript).

## Montage

1. Drei Kabelverschraubungs-/Antennenlöcher prüfen: unten 2 × Ø 12,3 (M12: Solarkabel + Druckausgleich/Blindstopfen), unten USB-C-Schlitz 14 × 9 mm, oben Ø 6,6 für SMA-Einbaubuchse (mit O-Ring außen).
2. Akkuhalter (MPD BK-18650-PC6, 77,7 × 59,7 mm) in den Eckwinkeln platzieren, mit 2 Kabelbindern durch die Brücken sichern. Zellen parallel verdrahten (Lötpins).
3. CN3791-Board rechts mit Kabelbindern/doppelseitigem Klebeband (VHB) befestigen.
4. Schutzplatine an den Halter kleben, verdrahten, Sicherung einschleifen.
5. T3-S3 auf die Leisten des Schlittens legen (USB-C zur unteren Wand), mit 2 Kabelbindern niederhalten; Schlitten mit 4 × M3×8 (selbstschneidend, Ø 2,6-Vorbohrung) auf die Säulen schrauben. **Vorher USB-Flucht prüfen** (Schlitz-Mitte 39,7 mm über Außenboden).
6. Antennen-Pigtail (IPEX/U.FL → SMA-Einbaubuchse) zur oberen Wand führen, SMA-Buchse mit O-Ring + Mutter festziehen, Antenne senkrecht nach oben.
7. Dichtung in die Nut drücken (nicht dehnen), Deckel mit 6 × M3×12 (Edelstahl, selbstschneidend) gleichmäßig über Kreuz anziehen – der Deckel liegt hart auf dem Flansch auf, die Feder verpresst die Dichtung um ~26 %.
8. USB-Stopfen einsetzen, Öse vor dem Kontern über die M12-Verschraubung legen.
9. Gehäuse mit 4 Schrauben (Ø 5,3-Langlöcher) senkrecht an die Wand: Verschraubungen nach **unten**, Antenne oben. Kabel mit Tropfschlaufe.
10. Paneel mit 2 Haltern (Achse M5 Edelstahl, Raster-Stift/Schraube M4) auf **60–70°** neigen (Winterertrag, Schnee rutscht ab), Ausrichtung Süd. Box möglichst im Schatten unter dem Paneel.

## Belüftung / Kondenswasser
Völlig dichte Boxen „atmen“ bei Temperaturwechseln und ziehen Feuchte an. Zweites M12-Loch für ein **Druckausgleichselement (Membran)** vorgesehen; alternativ Blindstopfen + Trockenmittelbeutel (Silicagel), jährlich tauschen.

## Grenzen & Hinweise
* PETG ist draußen brauchbar, aber nicht so UV-fest wie ASA; helle Farbe wählen, Box in den Schatten des Paneels.
* TPU 95A ist für eine Dichtung relativ hart – sauber drucken, Schrauben gleichmäßig anziehen; bei Undichtigkeit Nut mit Silikonfett.
* Platinenmaße aus der offiziellen LILYGO-DXF (Leiterplatte 27,3 × 64,6 mm); die Lage der M2-Löcher war daraus nicht sicher lesbar → Halterung über Auflageleisten + Kabelbinder.
* Lithium-Ionen-Zellen **nicht unter 0 °C laden** (Lithium-Plating). Weder der T3-S3-Lader (TEMP-Pin per 0-Ω auf GND, also ohne Temperaturfühler) noch – soweit geprüft – das CN3791-Board haben eine Kälte-Ladesperre. Für Wintereinsatz NTC-Abschaltung nachrüsten oder bewusst in Kauf nehmen.
* Kein zertifiziertes Notrufsystem. Im Notfall immer 112.

Lizenz der Konstruktion: wie das Projekt (GPLv3/AGPLv3), © Pietwars.
