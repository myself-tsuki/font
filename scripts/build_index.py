#!/usr/bin/env python3
"""Regenerate fonts.json and the CSS files from the font files in this repo.

Usage:  pip install fonttools && python3 scripts/build_index.py
"""
import json
from pathlib import Path
from urllib.parse import quote

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
REPO = "myself-tsuki/font"
BRANCH = "main"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
CDN = f"https://cdn.jsdelivr.net/gh/{REPO}@{BRANCH}/"
FONT_EXT = {".ttf", ".otf", ".woff", ".woff2"}

# Metadata the font files don't carry.
META = {
    "Google Sans": {"category": "sans-serif", "designer": "Google", "source": "https://fonts.google.com/specimen/Google+Sans"},
    "Figtree": {"category": "sans-serif", "designer": "Erik Kennedy", "source": "https://fonts.google.com/specimen/Figtree"},
    "Outfit": {"category": "sans-serif", "designer": "Rodrigo Fuenzalida, Outfit.io", "source": "https://fonts.google.com/specimen/Outfit"},
    "Plus Jakarta Sans": {"category": "sans-serif", "designer": "Tokotype", "source": "https://fonts.google.com/specimen/Plus+Jakarta+Sans"},
    "Nunito": {"category": "sans-serif", "designer": "Vernon Adams, Cyreal, Jacques Le Bailly", "source": "https://fonts.google.com/specimen/Nunito"},
    "Inter": {"category": "sans-serif", "designer": "Rasmus Andersson", "source": "https://fonts.google.com/specimen/Inter"},
    "Atkinson Hyperlegible Next": {"category": "sans-serif", "designer": "Braille Institute, Applied Design Works, Elliott Scott, Megan Eiswerth, Letters From Sweden", "source": "https://fonts.google.com/specimen/Atkinson+Hyperlegible+Next"},
}

# Fonts whose license does not allow re-hosting: listed, served from the official CDN.
EXTERNAL = [
    {
        "family": "Satoshi",
        "slug": "satoshi",
        "category": "sans-serif",
        "designer": "Deni Anggara, Indian Type Foundry",
        "license": "ITF Free Font License (no redistribution)",
        "source": "https://www.fontshare.com/fonts/satoshi",
        "hosted": False,
        "note": "The license forbids re-hosting the files in a public repository, so they are not in this repo. Use the official Fontshare CSS or download from fontshare.com.",
        "css": "https://api.fontshare.com/v2/css?f[]=satoshi@1,2&display=swap",
        "download": "https://api.fontshare.com/v2/fonts/download/satoshi",
        "axes": [{"tag": "wght", "min": 300, "max": 900, "default": 400}],
        "weights": [300, 400, 500, 700, 900],
        "styles": ["normal", "italic"],
        "files": [],
    }
]

WEIGHT_NAMES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
                600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black", 1000: "ExtraBlack"}
FORMATS = {".ttf": "truetype", ".otf": "opentype", ".woff": "woff", ".woff2": "woff2"}


def num(v):
    return int(v) if float(v).is_integer() else v


def slugify(name):
    return name.lower().replace(" ", "-")


def describe(path):
    font = TTFont(path)
    name = font["name"]
    family = name.getDebugName(16) or name.getDebugName(1)
    italic = bool(font["OS/2"].fsSelection & 1) or "italic" in path.name.lower()
    axes, weights = [], []
    if "fvar" in font:
        for a in font["fvar"].axes:
            axes.append({"tag": a.axisTag, "min": num(a.minValue), "max": num(a.maxValue), "default": num(a.defaultValue)})
        w = next((a for a in axes if a["tag"] == "wght"), None)
        if w:
            weights = [x for x in WEIGHT_NAMES if w["min"] <= x <= w["max"]]
    else:
        weights = [font["OS/2"].usWeightClass]
    rel = path.relative_to(ROOT).as_posix()
    enc = quote(rel)
    return family, {
        "file": rel,
        "style": "italic" if italic else "normal",
        "variable": "fvar" in font,
        "format": FORMATS[path.suffix.lower()],
        "version": (name.getDebugName(5) or "").split(";")[0].replace("Version ", ""),
        "axes": axes,
        "weights": weights,
        "size": path.stat().st_size,
        "url": CDN + enc,
        "raw": RAW + enc,
    }


def font_face(fam, f):
    w = next((a for a in f["axes"] if a["tag"] == "wght"), None)
    weight = f"{w['min']} {w['max']}" if w else str(f["weights"][0])
    return (f"@font-face {{\n  font-family: '{fam}';\n  src: url('{f['url']}') format('{f['format']}');\n"
            f"  font-weight: {weight};\n  font-style: {f['style']};\n  font-display: swap;\n}}\n")


def main():
    families = {}
    files = sorted(p for p in ROOT.rglob("*") if p.suffix.lower() in FONT_EXT and ".git" not in p.parts)
    for p in files:
        fam, info = describe(p)
        families.setdefault(fam, []).append(info)

    out = []
    css_dir = ROOT / "css"
    css_dir.mkdir(exist_ok=True)
    all_css = []
    for fam in sorted(families):
        fs = sorted(families[fam], key=lambda f: f["style"] != "normal")
        slug = slugify(fam)
        lic = next((p for p in [ROOT / Path(fs[0]["file"]).parent / "OFL.txt"] if p.exists()), None)
        axes = {a["tag"]: a for f in fs for a in f["axes"]}
        css = "".join(font_face(fam, f) for f in fs)
        (css_dir / f"{slug}.css").write_text(css)
        all_css.append(css)
        out.append({
            "family": fam,
            "slug": slug,
            **META.get(fam, {}),
            "license": "SIL Open Font License 1.1",
            "licenseFile": (CDN + quote(lic.relative_to(ROOT).as_posix())) if lic else None,
            "hosted": True,
            "css": CDN + f"css/{slug}.css",
            "axes": list(axes.values()),
            "weights": sorted({w for f in fs for w in f["weights"]}),
            "styles": sorted({f["style"] for f in fs}, key=lambda s: s != "normal"),
            "files": fs,
        })
    out.extend(EXTERNAL)
    out.sort(key=lambda f: f["family"].lower())

    (css_dir / "all.css").write_text("\n".join(all_css))
    index = {
        "name": "myself-tsuki/font",
        "description": "Self-hosted font collection. Every family, axis, weight and file with direct download URLs.",
        "repository": f"https://github.com/{REPO}",
        "cdn": CDN,
        "allCss": CDN + "css/all.css",
        "count": len(out),
        "fonts": out,
    }
    (ROOT / "fonts.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(f"Indexed {len(out)} families, {len(files)} files")


if __name__ == "__main__":
    main()
