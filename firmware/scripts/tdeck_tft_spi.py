"""Apply only the upstream S3 register-port fix to pinned TFT_eSPI 2.5.43.

Arduino FSPI is 0 on S3; TFT_eSPI's register macros need peripheral number 2.
Keep TFT_eSPI's default SPI reference (shared with RadioLib), rather than
USE_HSPI_PORT (different peripheral) or USE_FSPI_PORT (another SPIClass).
Upstream: Bodmer/TFT_eSPI commit 83d4d16, Processors/TFT_eSPI_ESP32_S3.h.
"""
from hashlib import sha256
from pathlib import Path

ORIGINAL_SHA256 = "9db8713e0a969af82c77034b0380f764cf4b1da7cd09c19fc7eac31db304e2b1"
OLD = b"#define SPI_PORT FSPI"
NEW = b"#define SPI_PORT 2"


def patch_header(path):
    source = path.read_bytes().replace(b"\r\n", b"\n")
    # Also accept our already patched file; reject any unexpected dependency.
    original = source if OLD in source else source.replace(NEW + b"\n  #endif", OLD + b"\n  #endif")
    if sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise RuntimeError("Unexpected TFT_eSPI S3 header; review the scoped SPI fix")
    patched = original.replace(OLD, NEW)
    if source != patched:
        path.write_bytes(patched)


if __name__ != "__main__":
    Import("env")
    if env["PIOENV"] not in ("tdeck-screen-test", "tdeck-standalone"):
        raise RuntimeError("TFT workaround is restricted to the T-Deck display profiles")
    patch_header(Path(env.subst("$PROJECT_LIBDEPS_DIR/$PIOENV")) /
                 "TFT_eSPI/Processors/TFT_eSPI_ESP32_S3.h")
