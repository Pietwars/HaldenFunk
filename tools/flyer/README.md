# Flyer-Generator (A5, Druck + digital)

`flyer.py` erzeugt aus `tools/flyer/flyer.json` und der Datei `VERSION` eines Repositorys:
`docs/flyer/<Name>-Flyer.pdf` (Druck, QR-Codes), `<Name>-Flyer-digital.pdf` (alle Links klickbar), `<Name>-Flyer-vorschau.jpg`, QR-PNGs.

    python3 -m venv /tmp/flyervenv && /tmp/flyervenv/bin/pip install qrcode pillow
    cd <Repository> && /tmp/flyervenv/bin/python tools/flyer/flyer.py

Chrome/Chromium headless wird über `$CHROME`, `google-chrome`, `chromium` oder Playwright-Browser gefunden
(z. B. `PLAYWRIGHT_BROWSERS_PATH=… npx playwright install chromium`). Vorschau braucht `pdftoppm` (poppler-utils).
Platzhalter in flyer.json: `@VERSION@`, `@RELEASE@` (Release-Seite des Tags v@VERSION@).
Eine Kopie liegt in jedem Repository unter `tools/flyer/` (Generator + Konfiguration); Master: /workspace/flyer/build.
Der Workflow `release.yml` hängt `docs/flyer/*-Flyer.pdf` und `*-Flyer-digital.pdf` an jede Vorabversion an.
