#!/usr/bin/env python3
"""Rebuild outlined profile SVGs from editable <text> sources in tools/src/.

Usage:
    python3 -I tools/build.py [repo_root]
"""

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen  # noqa: E402


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent
    src_root = HERE / "src"
    assets_root = repo / "assets"

    built = 0
    for src_svg in sorted(src_root.rglob("*.svg")):
        rel = src_svg.relative_to(src_root)
        # Skip raw animation source SVGs used to render looping APNGs
        if rel.parts and rel.parts[0] == "animations":
            continue
        dest = assets_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_svg, dest)
        n = gen.outline_file(str(dest))
        built += 1
        print(f"assets/{rel.as_posix()}: {n} text nodes outlined")

    print(f"Built {built} SVGs; missing glyphs: {gen.MISSING or 'none'}")
    return 1 if gen.MISSING else 0


if __name__ == "__main__":
    raise SystemExit(main())
