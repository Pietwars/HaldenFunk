# T-Deck startup image

`tdeck-splash.rgb565` is the existing `docs/images/disahrsterradio-header.jpg`
(Pietwars' valley and radio-network artwork), proportionally scaled to 320 x 213.
Each pixel is RGB565, little endian. Size: 136320 bytes. The landscape display
places it at (0, 13), preserving the entire image without cropping.

Only `tdeck-standalone` and `tdeck-screen-test` embed this asset. The startup renderer copies one
640-byte row at a time, avoiding a full-screen RAM allocation.
