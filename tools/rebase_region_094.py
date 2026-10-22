#!/usr/bin/env python3
"""Einmaliger, reproduzierbarer Rebase des HaldenFunk-Overlays auf den LoRaLayer2-Kern 0.9.4."""
from pathlib import Path
import shutil, sys, tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_sync as cs

TARGET = "115695a0d5efb5c02d3bd2390e8277ce03c2abf1"
ROOT = cs.ROOT

def replace(path, pairs):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")

def main():
    conf, own = cs.conf()
    core = Path(tempfile.mkdtemp(prefix="hf-core-"))
    sha = cs.fetch_core(conf["repo"], TARGET, core)
    work, err = cs.expected(core, own)
    if not err:
        raise SystemExit("Das alte Overlay war bereits konfliktfrei; normalen core_sync --update verwenden")

    rejects = sorted(p.relative_to(work).as_posix() for p in work.rglob("*.rej"))
    expected = [".github/workflows/release.yml.rej", "firmware/main.ino.rej", "tools/ANLEITUNG.template.md.rej"]
    if rejects != expected:
        raise SystemExit(f"Unerwartete Konflikte: {rejects}")
    for rel in rejects:
        (work / rel).unlink()

    replace(work / "firmware/main.ino", [
        ("DisAHRsterRadio", "HaldenFunk"),
        ("disahrsterradio", "haldenfunk"),
        ("disahrster", "haldenfunk"),
        ("Willkommen bei HaldenFunk ", "Glueck Auf! Willkommen bei HaldenFunk "),
    ])
    replace(work / ".github/workflows/release.yml", [
        ("DisAHRsterRadio", "HaldenFunk"),
    ])
    release = work / ".github/workflows/release.yml"
    text = release.read_text(encoding="utf-8")
    marker = "      - name: Release-Text erzeugen\n"
    if "Flyer zur Tag-Version neu erzeugen" not in text and marker in text:
        flyer = """      - name: Flyer zur Tag-Version neu erzeugen
        run: |
          python3 -m pip install 'qrcode[pil]'
          python3 tools/flyer/flyer.py
          python3 - <<'PY'
          from pathlib import Path
          for name in ('HaldenFunk-Flyer.pdf', 'HaldenFunk-Flyer-digital.pdf'):
              path = Path('docs/flyer') / name
              assert path.is_file() and path.stat().st_size > 10000 and path.open('rb').read(5) == b'%PDF-', name
          PY
"""
        text = text.replace(marker, flyer + marker)
        release.write_text(text, encoding="utf-8")

    replace(work / "tools/ANLEITUNG.template.md", [
        ("Pietwars/DisAHRsterRadio", "Pietwars/HaldenFunk"),
        ("DisAHRsterRadio", "HaldenFunk"),
        ("disahrster.local", "haldenfunk.local"),
    ])

    # Version 0.9.4 mit den regionalen Versionsregeln eintragen.
    extras = []
    for rel in cs.files(ROOT):
        if cs.is_own(rel, own) and not (work / rel).exists():
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, work / rel)
            extras.append(rel)
    cs.normalize(work, ROOT / "tools/version.py", own, version=cs.ver())
    for rel in extras:
        (work / rel).unlink()

    exp = {rel for rel in cs.files(work) if not rel.startswith(".git/") and not rel.endswith(".rej")}
    have = {rel for rel in cs.files(ROOT) if not cs.is_own(rel, own)}
    for rel in sorted(have - exp):
        (ROOT / rel).unlink()
    for rel in sorted(exp):
        src, dst = work / rel, ROOT / rel
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    (ROOT / "region/CORE").write_text(f"repo={conf['repo']}\ncommit={sha}\n")
    cs.make_patch(core, own)
    print(f"HaldenFunk-Overlay auf {sha} neu aufgebaut; Konflikte semantisch aufgelöst.")

if __name__ == "__main__":
    main()
