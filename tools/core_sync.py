#!/usr/bin/env python3
"""HaldenFunk = gemeinsamer Kern (Pietwars/DisAHRsterRadio) + Regional-Overlay (region/).

Der Kern ist DisAHRsterRadio in einer festen Revision (region/CORE). Alle Dateien des Kerns, die nicht
regional sind (region/own.txt), werden in HaldenFunk aus dem Kern erzeugt: Kern-Datei + region/overlay.patch
(Namen, WLAN/mDNS, Begrüßung, Farben, Orte, Karten-Liste, Demo-Inhalte, Paketpräfix …) + Versionen aus VERSION.
Regionale Dateien (README, CHANGELOG, VERSION, Karten, Bilder, Doku, …) gehören allein HaldenFunk.

  python3 tools/core_sync.py --check           prüft, dass alle Kern-Dateien exakt Kern + Overlay entsprechen (CI)
  python3 tools/core_sync.py --update [REF]    holt den Kern in REF (Standard: main), wendet das Overlay an,
                                               schreibt die Dateien und region/CORE; Konflikte → *.rej
  python3 tools/core_sync.py --make-patch      erzeugt region/overlay.patch neu aus dem aktuellen Stand
                                               (nach einer gewollten regionalen Änderung an einer Kern-Datei)
Optionen: --core-dir PFAD  lokalen Kern-Checkout statt Download verwenden (Tests, offline)
"""
import fnmatch, importlib.util, io, os, shutil, subprocess, sys, tarfile, tempfile, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REGION = ROOT / 'region'
NORM = '0.0.0-dev'  # Versionen werden vor dem Vergleich/Patch auf diesen Wert gesetzt

def conf():
    c = dict(l.split('=', 1) for l in (REGION / 'CORE').read_text().split() if '=' in l)
    own = [l.strip() for l in (REGION / 'own.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    return c, own

def is_own(rel, own): return any(fnmatch.fnmatch(rel, p) for p in own)

def files(tree):
    out = []
    for p in sorted(Path(tree).rglob('*')):
        rel = p.relative_to(tree).as_posix()
        if p.is_file() and rel != '.git' and not rel.startswith('.git/') and '/__pycache__/' not in '/' + rel and not rel.startswith('.pio/'): out.append(rel)
    return out

def fetch_core(repo, ref, dest, core_dir=None):
    if core_dir:
        if ref and (Path(core_dir) / '.git').exists():
            data = subprocess.run(['git', '-C', core_dir, 'archive', ref], check=True, capture_output=True).stdout
            tarfile.open(fileobj=io.BytesIO(data)).extractall(dest, filter='data')
            return subprocess.run(['git', '-C', core_dir, 'rev-parse', ref], check=True, capture_output=True, text=True).stdout.strip()
        shutil.copytree(core_dir, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', '.pio', '__pycache__'))
        return ref or 'lokal'
    sha = ref
    if len(ref) != 40:
        with urllib.request.urlopen(f'https://api.github.com/repos/{repo}/commits/{ref}') as r:
            import json; sha = json.load(r)['sha']
    with urllib.request.urlopen(f'https://codeload.github.com/{repo}/tar.gz/{sha}') as r:
        t = tarfile.open(fileobj=io.BytesIO(r.read()), mode='r:gz')
        for m in t.getmembers():
            m.name = m.name.split('/', 1)[1] if '/' in m.name else ''
        t.extractall(dest, members=[m for m in t.getmembers() if m.name], filter='data')
    return sha

def normalize(tree, version_py, own, version=NORM):
    """Setzt in den Kern-Dateien von tree alle Versionsstellen (Regeln aus version_py) auf version."""
    spec = importlib.util.spec_from_file_location('v', version_py); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.ROOT = Path(tree)
    vfile = Path(tree) / 'VERSION'; old = vfile.read_bytes() if vfile.exists() else None
    vfile.write_text(f'VERSION={version}\n')
    rules = [r for r in m.RULES if not is_own(r[0], own)]
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()): rc = m.run(rules, [])
    if old is None: vfile.unlink()
    else: vfile.write_bytes(old)
    if rc: sys.exit(f'Versionsregeln passen nicht ({version_py})')

def git(cwd, *a, **k): return subprocess.run(['git', '-C', str(cwd), *a], check=True, capture_output=True, **k)

def stage(core, own):
    """Temporäres Git-Repo mit den Kern-Dateien (normalisiert) als Basis-Commit."""
    work = Path(tempfile.mkdtemp(prefix='kern-'))
    for rel in files(core):
        if not is_own(rel, own):
            (work / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(Path(core) / rel, work / rel)
    normalize_core(work, core, own)
    git(work, 'init', '-q'); git(work, 'add', '-A'); git(work, '-c', 'user.name=k', '-c', 'user.email=k@k', 'commit', '-qm', 'kern')
    return work

def normalize_core(work, core, own):
    # Kern-eigene Versionsregeln brauchen u. U. Kern-README usw.: auf einer vollständigen Kopie normalisieren
    tmp = Path(tempfile.mkdtemp(prefix='kernv-')); shutil.copytree(core, tmp, dirs_exist_ok=True)
    normalize(tmp, tmp / 'tools' / 'version.py', own)
    for rel in files(work): shutil.copy2(tmp / rel, work / rel)
    shutil.rmtree(tmp)

def hf_normalized(own):
    tmp = Path(tempfile.mkdtemp(prefix='hfv-'))
    for rel in files(ROOT):
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / rel, tmp / rel)
    normalize(tmp, ROOT / 'tools' / 'version.py', own)
    return tmp

def make_patch(core, own):
    work = stage(core, own); hf = hf_normalized(own)
    for rel in files(work): (work / rel).unlink()
    for rel in files(hf):
        if not is_own(rel, own):
            (work / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(hf / rel, work / rel)
    git(work, 'add', '-A')
    patch = git(work, 'diff', '--cached', '--binary', '--no-color').stdout
    (REGION / 'overlay.patch').write_bytes(patch)
    shutil.rmtree(work); shutil.rmtree(hf)
    return patch

def expected(core, own):
    """Kern + Overlay + HaldenFunk-Versionen → Verzeichnis mit den erwarteten Kern-Dateien."""
    work = stage(core, own)
    p = REGION / 'overlay.patch'
    if p.stat().st_size:
        r = subprocess.run(['git', '-C', str(work), 'apply', '--reject', '--whitespace=nowarn', str(p)], capture_output=True, text=True)
        if r.returncode:
            rej = [x for x in files(work) if x.endswith('.rej')]
            return work, (r.stderr.strip() + ('\nKonflikte: ' + ', '.join(rej) if rej else ''))
    # HaldenFunk-Versionen eintragen (Regeln brauchen ggf. regionale Dateien wie README → mitkopieren und wieder entfernen)
    extra = []
    for rel in files(ROOT):
        if is_own(rel, own) and not (work / rel).exists():
            (work / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / rel, work / rel); extra.append(rel)
    normalize(work, ROOT / 'tools' / 'version.py', own, version=ver())
    for rel in extra: (work / rel).unlink()
    return work, None

def ver():
    for l in (ROOT / 'VERSION').read_text().splitlines():
        if l.startswith('VERSION='): return l.split('=', 1)[1].strip()

def main(argv):
    c, own = conf()
    core_dir = argv[argv.index('--core-dir') + 1] if '--core-dir' in argv else None
    tmp = Path(tempfile.mkdtemp(prefix='kernsrc-'))
    if '--update' in argv:
        i = argv.index('--update'); ref = argv[i + 1] if len(argv) > i + 1 and not argv[i + 1].startswith('--') else 'main'
    else:
        ref = c['commit']
    sha = fetch_core(c['repo'], ref, tmp, core_dir)
    if '--make-patch' in argv:
        n = len(make_patch(tmp, own)); print(f'region/overlay.patch neu erzeugt ({n} Bytes) gegen {c["repo"]}@{sha[:12]}'); return 0
    work, err = expected(tmp, own)
    if err: print('Overlay passt nicht auf den Kern:\n' + err); return 1
    exp = {rel for rel in files(work) if not rel.startswith('.git/')}
    have = {rel for rel in files(ROOT) if not is_own(rel, own)}
    if '--update' in argv:
        for rel in sorted(have - exp): (ROOT / rel).unlink(); print('entfernt:', rel)
        for rel in sorted(exp):
            src, dst = work / rel, ROOT / rel
            if not dst.exists() or dst.read_bytes() != src.read_bytes():
                dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst); print('aktualisiert:', rel)
        (REGION / 'CORE').write_text(f'repo={c["repo"]}\ncommit={sha}\n')
        make_patch(tmp, own); print(f'Kern jetzt {c["repo"]}@{sha[:12]}; region/overlay.patch neu erzeugt. Bitte bauen, testen, committen.')
        return 0
    bad = sorted(rel for rel in exp & have if (work / rel).read_bytes() != (ROOT / rel).read_bytes())
    bad += [f'{rel} (fehlt in HaldenFunk)' for rel in sorted(exp - have)]
    bad += [f'{rel} (weder im Kern noch in region/own.txt)' for rel in sorted(have - exp)]
    if bad:
        print('Kern-Abgleich fehlgeschlagen – diese Dateien weichen von Kern + Overlay ab:\n  ' + '\n  '.join(bad))
        print('Gewollte regionale Änderung: python3 tools/core_sync.py --make-patch · Kern-Änderung: in DisAHRsterRadio umsetzen, dann --update')
        return 1
    print(f'Kern-Abgleich OK: {len(exp)} Dateien = {c["repo"]}@{sha[:12]} + region/overlay.patch ({len(own)} regionale Muster)')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
