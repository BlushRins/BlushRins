#!/usr/bin/env python3
"""Profile asset generator: keycap legends, light-mode card variants, text->outline.

Run from anywhere: python3 -I gen.py <assets_dir> <step>
steps: keys | outline
"""
import os
import re
import sys
from functools import cache
from pathlib import Path
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTCollection, TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
q = lambda t: f"{{{SVG}}}{t}"

FONT_ROOT = Path(os.environ.get("PROFILE_FONT_ROOT", "/usr/share/fonts"))


@cache
def font_for(family, bold):
    weight = "Bold" if bold else "Regular"
    if family == "mono":
        return TTFont(FONT_ROOT / "noto" / f"NotoSansMono-{weight}.ttf")

    path = FONT_ROOT / "inter" / "Inter.ttc"
    collection = TTCollection(path)
    name = f"Inter-{weight}"
    expected_weight = 700 if bold else 400
    for font in collection.fonts:
        if font["name"].getDebugName(6) == name and font["OS/2"].usWeightClass == expected_weight:
            return font
    raise ValueError(f"{path} does not contain the {name} face")


MISSING = set()


def num(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def compact_path(d):
    """Strip redundant spaces around SVG path commands and negative coordinates."""
    d = re.sub(r"\s*([MLHVCSQTAZmlhvcsqtaz])\s*", r"\1", d)
    d = re.sub(r"\s+", " ", d)
    d = re.sub(r" (?=-)", "", d)
    return d.strip()


def family(attr):
    return "mono" if "monospace" in attr else "sans"


def measure(font, text, size):
    cmap, hmtx, upem = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    w = 0
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            MISSING.add(ch)
            continue
        w += hmtx[g][0]
    return w * size / upem


def outline(font, text, size, x, y):
    gs, cmap, hmtx, upem = font.getGlyphSet(), font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    s = size / upem
    d = []
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            MISSING.add(ch)
            continue
        pen = SVGPathPen(gs, ntos=num)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        d.append(pen.getCommands())
        x += hmtx[g][0] * s
    return compact_path("".join(d))


SKIP = {"font-family", "font-size", "font-weight", "text-anchor", "x", "y"}


def convert_text(el):
    """Return replacement element (path or group of paths) for a <text>."""
    fam = family(el.get("font-family", ""))
    size = float(el.get("font-size"))
    bold = el.get("font-weight") == "bold"
    x, y = float(el.get("x", 0)), float(el.get("y", 0))
    anchor = el.get("text-anchor", "start")

    runs = []  # (text, bold, extra attrs)
    if el.text:
        runs.append((el.text, bold, {}))
    for ts in el:
        b = ts.get("font-weight", "bold" if bold else "") == "bold"
        runs.append((ts.text or "", b, {k: v for k, v in ts.attrib.items() if k not in SKIP}))
        if ts.tail:
            runs.append((ts.tail, bold, {}))

    total = sum(measure(font_for(fam, b), t, size) for t, b, _ in runs)
    cx = x - (total / 2 if anchor == "middle" else total if anchor == "end" else 0)

    base = {k: v for k, v in el.attrib.items() if k not in SKIP}
    paths = []
    for t, b, extra in runs:
        f = font_for(fam, b)
        d = outline(f, t, size, cx, y)
        cx += measure(f, t, size)
        if d:
            p = ET.Element(q("path"), {"d": d, **extra})
            paths.append(p)
    if len(paths) == 1 and not paths[0].attrib.keys() - {"d"}:
        paths[0].attrib.update(base)
        return paths[0]
    g = ET.Element(q("g"), base)
    g.extend(paths)
    return g


def outline_file(path):
    tree = ET.parse(path)
    root = tree.getroot()
    root.attrib.setdefault("role", "img")
    n = 0
    INHERIT = ("font-family", "font-size", "font-weight", "text-anchor")

    def walk(parent, inherited):
        nonlocal n
        for i, child in enumerate(list(parent)):
            if child.tag == q("text"):
                for k, v in inherited.items():
                    child.attrib.setdefault(k, v)
                parent[i] = convert_text(child)
                n += 1
            else:
                walk(child, {**inherited, **{k: child.attrib[k] for k in INHERIT if k in child.attrib}})

    walk(root, {})
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=False)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n")
    return n


# ---- keycaps
KEYS = {  # file: (ext legend, main legend)
    "c": (".c", "C"), "java": (".java", "Java"), "php": (".php", "PHP"), "shell": (".sh", "Shell"),
    "python": (".py", "Python"), "html": (".html", "HTML"), "css": (".css", "CSS"),
    "javascript": (".js", "JavaScript"), "typescript": (".ts", "TypeScript"),
}
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"


def rewrite_keys(d):
    for name, (ext, main) in KEYS.items():
        p = f"{d}/keycaps/{name}.svg"
        s = Path(p).read_text(encoding="utf-8")
        size = 13.5
        w = measure(font_for("sans", True), main, size)
        if w > 62:
            size = round(13.5 * 62 / w, 2)
        new = (
            f'<text x="8" y="16" font-family="{MONO}" font-size="9" fill="#7a5f70">{ext}</text>\n'
            f'      <text x="37.5" y="39" text-anchor="middle" font-family="{SANS}" font-size="{size}" font-weight="bold">{main}</text>'
        )
        s2 = re.sub(r'<text x="8" y="23".*?</text>\s*<text x="8" y="44".*?</text>', new, s, flags=re.S)
        assert s2 != s, name
        Path(p).write_text(s2, encoding="utf-8")


if __name__ == "__main__":
    d, step = sys.argv[1], sys.argv[2]
    if step == "keys":
        rewrite_keys(d)
    elif step == "outline":
        files = sys.argv[3:]
        for f in files:
            print(f, outline_file(f"{d}/{f}"), "texts")
        print("missing glyphs:", MISSING or "none")
        sys.exit(bool(MISSING))
