#!/usr/bin/env python3
"""Build or verify outlined profile SVGs from tools/src/."""
import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", type=Path, nargs="?", default=HERE.parent)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    source = HERE / "src"
    templates = sorted(p.relative_to(source) for p in source.rglob("*.svg")
                       if p.relative_to(source).parts[0] != "animations")
    gen.MISSING.clear()
    if args.check:
        readme = (repo / "README.md").read_text(encoding="utf-8")
        missing = [link for link in re.findall(r'(?:src|href|srcset)="(\./assets/[^"]+)"', readme)
                   if not (repo / link).is_file()]
        for link in missing:
            print(f"Missing README asset: {link}", file=sys.stderr)
        if missing:
            return 1
    else:
        repo.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=repo) as directory:
        staging = Path(directory)
        for relative in templates:
            dest = staging / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, dest)
            gen.outline_file(dest)
        if gen.MISSING:
            print(f"Missing glyphs: {sorted(gen.MISSING)}", file=sys.stderr)
            return 1
        if args.check:
            stale = [relative for relative in templates
                     if not (repo / "assets" / relative).is_file()
                     or (repo / "assets" / relative).read_bytes() != (staging / relative).read_bytes()]
            for relative in stale:
                print(f"Stale generated SVG: assets/{relative}", file=sys.stderr)
            if stale:
                return 1
        else:
            for relative in templates:
                dest = repo / "assets" / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                (staging / relative).replace(dest)

    print(f"{'Verified' if args.check else 'Built'} {len(templates)} profile SVGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
