"""Archive the exact ELF before buildfs can remove it; verify against app descriptor."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys


def collect(build, output):
    image = (build / "firmware.bin").read_bytes()
    elf = build / "firmware.elf"
    digest = hashlib.sha256(elf.read_bytes()).hexdigest()
    # ESP image header (24), first segment header (8), esp_app_desc_t.
    if image[0] != 0xE9 or struct.unpack_from("<I", image, 32)[0] != 0xABCD5432:
        raise ValueError("Invalid ESP application descriptor")
    if image[176:208].hex() != digest:
        raise ValueError("ELF SHA does not match firmware application descriptor")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("firmware.elf", "firmware.map"):
        shutil.copy2(build / name, output / name)
    root = Path(__file__).resolve().parents[1]
    report = {
        "elf_sha256": digest,
        "firmware_sha256": hashlib.sha256(image).hexdigest(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "environment": build.name,
        "note": "ELF hash must match the panic log before decoding addresses",
    }
    (output / "build.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    collect(Path(sys.argv[1]), Path(sys.argv[2]))
