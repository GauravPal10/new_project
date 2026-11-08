"""Package allowlisted source/support files; exclude credentials, caches and video."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOP = {"README.md", "START_HERE.txt", "RESEARCH.md", "PROVENANCE.md", "requirements.txt", ".env.example", ".gitignore", "run_eval.py", "run_openrouter.py", "make_zip.py", "check_project.py", "demo.py"}
DIRECTORIES = {"asof", "tasks", "reference", "examples", "tests", "results", "docs", "runs", "model_inputs"}
SUFFIXES = {".py", ".md", ".txt", ".json", ".sql", ".csv"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    target = Path(args.out).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink(): continue
        rel = path.relative_to(ROOT)
        if "__pycache__" in rel.parts or any(p.startswith("tmp") for p in rel.parts): continue
        if len(rel.parts) == 1:
            if path.name not in TOP: continue
        elif rel.parts[0] not in DIRECTORIES or path.suffix not in SUFFIXES:
            continue
        files.append((path, rel.as_posix()))
    manifest = {"format": 1, "files": {rel: hashlib.sha256(path.read_bytes()).hexdigest() for path,rel in sorted(files)}}
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, rel in sorted(files): archive.write(path, "asof_eval/" + rel)
        archive.writestr("asof_eval/MANIFEST.sha256.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None: raise SystemExit("Archive integrity failed")
    if target.stat().st_size >= 50_000_000: raise SystemExit("Archive exceeds conservative 50 MB limit")
    print(f"Created {target.name}: {len(files)+1} files, {target.stat().st_size:,} bytes")
    print("SHA256", hashlib.sha256(target.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
