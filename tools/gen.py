#!/usr/bin/env python3
"""Profile asset generator: keycap legends, light-mode card variants, text->outline.

Run from anywhere: python3 -I gen.py <assets_dir> <step>
steps: keys | light | outline
"""
import re, sys, copy
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTCollection, TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
q = lambda t: f"{{{SVG}}}{t}"

_c = TTCollection("/usr/share/fonts/inter/Inter.ttc")
FONTS = {
    ("sans", False): _c.fonts[0],   # Inter Regular
    ("sans", True): _c.fonts[14],   # Inter Bold
    ("mono", False): TTFont("/usr/share/fonts/noto/NotoSansMono-Regular.ttf"),
    ("mono", True): TTFont("/usr/share/fonts/noto/NotoSansMono-Bold.ttf"),
}
MISSING = set()


def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


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
    return "".join(d)


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

    total = sum(measure(FONTS[(fam, b)], t, size) for t, b, _ in runs)
    cx = x - (total / 2 if anchor == "middle" else total if anchor == "end" else 0)

    base = {k: v for k, v in el.attrib.items() if k not in SKIP}
    paths = []
    for t, b, extra in runs:
        f = FONTS[(fam, b)]
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
    with open(path, "a") as fh:
        fh.write("\n")
    return n


# ---- light-mode palette (dark card hex -> light card hex)
LIGHT = {
    # backgrounds / gradient stops
    "#241d30": "#fffaf7", "#34253a": "#fdeff2", "#402c43": "#f9e2ea", "#362638": "#fbe9ef",
    "#342940": "#f6e6ec", "#2b2334": "#f3e1e8",
    # frame
    "#5b4760": "#d9bcc8", "#987285": "#c4879b",
    # muted / label text
    "#b89fb2": "#85667d", "#9c859e": "#9a7f93", "#d9bec9": "#6d5167", "#8c6d82": "#a9849a",
    # green text + led
    "#97c4ab": "#3c7a5b", "#c5eecb": "#2f6b4c", "#c6ecb8": "#4a9a68", "#96c99b": "#7cc590", "#e6f6b9": "#58761f",
    # pink
    "#f7c2d3": "#b8456d", "#f7b5ca": "#e0698f",
    # cream text
    "#fff1e1": "#352733",
    # panels
    "#342b3e": "#f6e8ee", "#514353": "#dcc3cf", "#4c3046": "#fcdce6",
    "#243733": "#e5f3e8", "#577467": "#9bc4a9", "#2f4a43": "#d1e9d8", "#5d7f70": "#8dbb9f",
}


def make_light(src, dst):
    s = open(src).read()
    seen = set(h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", s))
    unmapped = sorted(seen - set(LIGHT) - {"#2a1d2b", "#ffffff"})
    out = re.sub(r"#[0-9a-fA-F]{6}", lambda m: LIGHT.get(m.group(0).lower(), m.group(0)), s)
    open(dst, "w").write(out)
    return unmapped


# ---- keycaps
KEYS = {  # file: (ext legend, main legend)
    "c": (".c", "C"), "java": (".java", "Java"), "php": (".php", "PHP"), "shell": (".sh", "Shell"),
    "html": (".html", "HTML"), "css": (".css", "CSS"), "javascript": (".js", "JavaScript"), "typescript": (".ts", "TypeScript"),
}
MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"


def rewrite_keys(d):
    for name, (ext, main) in KEYS.items():
        p = f"{d}/keycaps/{name}.svg"
        s = open(p).read()
        size = 13.5
        w = measure(FONTS[("sans", True)], main, size)
        if w > 62:
            size = round(13.5 * 62 / w, 2)
        new = (
            f'<text x="8" y="16" font-family="{MONO}" font-size="9" fill="#7a5f70">{ext}</text>\n'
            f'      <text x="37.5" y="39" text-anchor="middle" font-family="{SANS}" font-size="{size}" font-weight="bold">{main}</text>'
        )
        s2 = re.sub(r'<text x="8" y="23".*?</text>\s*<text x="8" y="44".*?</text>', new, s, flags=re.S)
        assert s2 != s, name
        open(p, "w").write(s2)


if __name__ == "__main__":
    d, step = sys.argv[1], sys.argv[2]
    if step == "keys":
        rewrite_keys(d)
    elif step == "light":
        for src, dst in [("workbench/lift-tracker-card.svg", "workbench/lift-tracker-card-light.svg"),
                         ("workbench/bit-vector-byte.svg", "workbench/bit-vector-byte-light.svg"),
                         ("linked-list.svg", "linked-list-light.svg")]:
            print(dst, "unmapped:", make_light(f"{d}/{src}", f"{d}/{dst}"))
    elif step == "outline":
        files = sys.argv[3:]
        for f in files:
            print(f, outline_file(f"{d}/{f}"), "texts")
        print("missing glyphs:", MISSING or "none")
