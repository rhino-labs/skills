# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools[woff]==4.68.0", "uharfbuzz==0.57.0"]
# ///
"""
Subset, instance and split web fonts into a preloaded core file and a
unicode-range extended file. Run by hand; commit the output.

    uv run scripts/subset-fonts.py            # build + check
    uv run scripts/subset-fonts.py --check-coverage dist/   # list uncovered characters in a build

Rerun when:
  - content uses a character outside the fonts' coverage (see --check-coverage)
  - a new weight / style / axis value / font-variation-settings / OpenType feature is used
  - font-optical-sizing is on and a font-size falls outside the opsz range
  - a source font is upgraded or added, or the core character set changes

TEMPLATE: adapt CONFIG, paths and the CSS output to the project. Every value in
CONFIG must come from the usage audit, not from guesses.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from itertools import product
from pathlib import Path

import uharfbuzz as hb
from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public/fonts"          # where served files go
CSS_OUT = ROOT / "src/styles/fonts.generated.css"
URL_PREFIX = "/fonts/"

# Browser-default features: on unless CSS turns them off. Keep them unless the
# audit proves they're disabled everywhere this font renders.
DEFAULT_FEATURES = ["kern", "liga", "clig", "calt", "locl", "ccmp", "mark", "mkmk", "rlig", "rvrn", "curs", "dist"]

CORE = set(range(0x20, 0x7F)) | {0xA0, 0x2018, 0x2019, 0x201C, 0x201D, 0x2013, 0x2014, 0x2026}
LATIN = set(range(0xA0, 0x100)) | set(range(0x100, 0x180))

CONFIG = [
    {
        "source": "fonts/source/Example[opsz,wght].ttf",
        "name": "example",                      # output file stem
        "family": "Example",                    # CSS font-family alias: unchanged from today
        "descriptors": {                        # copied exactly from the current @font-face
            "font-weight": "400 700",
            "font-style": "normal",
            "font-display": "swap",
        },
        # Axis limits from the audit. (min, max) limits a range; a number pins the axis;
        # None pins at the default. Only pin when nothing overrides the axis.
        "axes": {"wght": (400, 700), "opsz": (14, 32)},
        "features": DEFAULT_FEATURES + ["tnum"],
        "used_chars": "fonts/usage/example.txt",  # characters from the audit (UTF-8 text)
        "used_pairs": "fonts/usage/example.pairs.txt",  # adjacent pairs from the audit
        # Move extended characters whose kerning/shaping with a core neighbour would be
        # lost into core. True keeps rendering identical; False needs the user's approval.
        "promote_cross_split": True,
        "extra_codepoints": [0x2010],            # CSS-inserted, e.g. hyphens: auto
        # OFL Reserved Font Name: rename internally after subsetting. None if no RFN.
        "reserved_name": None,                  # e.g. "Example"
        "new_internal_name": None,              # e.g. "Site Sans" (must not contain the RFN)
    },
]


# --- building ----------------------------------------------------------------

def instance(font: TTFont, axes: dict) -> TTFont:
    if "fvar" not in font:
        return font
    limits = {tag: axes.get(tag, "keep") for tag in (a.axisTag for a in font["fvar"].axes)}
    unspecified = [t for t, v in limits.items() if v == "keep"]
    if unspecified:
        sys.exit(f"axes {unspecified} have no limit in CONFIG; decide from the audit")
    return instancer.instantiateVariableFont(font, limits)


# Tables the subsetter can't subset and silently drops, that a browser still uses.
# trak has no glyph references, so it's copied back unchanged. morx/kerx reference glyph IDs
# and can't be copied after subsetting; Safari then falls back to GSUB/GPOS. Diff in WebKit.
COPY_BACK = ("trak",)
SAFARI_ONLY = ("morx", "kerx", "mort", "kern")
HINTING = ("fpgm", "prep", "cvt ", "hdmx", "VDMX", "LTSH", "cvar")


def build_file(src: Path, cfg: dict, codepoints: set[int], suffix: str) -> tuple[Path, set[int]]:
    font = instance(TTFont(src), cfg["axes"])
    before = set(font.keys())
    copy_back = {t: font[t] for t in COPY_BACK if t in font}

    opts = subset.Options()
    opts.layout_features = cfg["features"]
    opts.hinting = False                 # drops fpgm/prep/cvt/hdmx/VDMX/LTSH/cvar and CFF hints
    opts.desubroutinize = True           # better WOFF2 compression for CFF
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.flavor = "woff2"
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=sorted(codepoints))
    sub.subset(font)
    for tag, table in copy_back.items():
        font[tag] = table
    dropped = sorted(before - set(font.keys()) - set(HINTING) - {"DSIG"})
    if dropped:
        print(f"  dropped tables: {dropped} (decide on each; see font-tooling.md)")
    if lost := [t for t in SAFARI_ONLY if t in before and t not in font]:
        print(f"  WARNING: {lost} dropped; Safari shaping may change. Diff in WebKit.")

    if cfg["reserved_name"]:
        rename_reserved(font, cfg["reserved_name"], cfg["new_internal_name"])

    contained = set(font.getBestCmap()) & codepoints
    font.flavor = "woff2"
    tmp = OUT_DIR / f"{cfg['name']}-{suffix}.tmp.woff2"
    font.save(tmp)
    digest = hashlib.sha256(tmp.read_bytes()).hexdigest()[:8]
    out = OUT_DIR / f"{cfg['name']}-{suffix}.{digest}.woff2"
    for stale in OUT_DIR.glob(f"{cfg['name']}-{suffix}.*.woff2"):
        if stale != tmp:
            stale.unlink()
    tmp.rename(out)
    return out, contained


# Name records that may (and under the OFL must) keep the original name.
KEEP_NAME_IDS = {0, 7, 13, 14}  # copyright, trademark, license, license URL


def rename_reserved(font: TTFont, reserved: str, new: str) -> None:
    """Replace the Reserved Font Name everywhere outside copyright/trademark/license,
    including fvar named-instance PostScript names (name IDs >= 256)."""
    if reserved.lower() in new.lower():
        sys.exit(f"new name {new!r} still contains the reserved name {reserved!r}")
    name = font["name"]
    variants = [(reserved, new), (reserved.replace(" ", ""), new.replace(" ", ""))]
    name.names = [r for r in name.names if r.nameID in KEEP_NAME_IDS or (r.platformID, r.langID) in ((3, 0x409), (1, 0))]
    for rec in name.names:
        if rec.nameID in KEEP_NAME_IDS:
            continue
        s = rec.toUnicode()
        for old, repl in variants:
            s = re.sub(re.escape(old), repl, s, flags=re.I)
        rec.string = s


# --- cross-split shaping -------------------------------------------------------

def shaped(font: hb.Font, text: str) -> list[tuple]:
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})
    return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def cross_split_losses(src: Path, cfg: dict, core: set[int], ext: set[int], pairs: list[str]) -> dict[str, list[str]]:
    """Pairs that the content puts side by side, with one character in each file, whose
    shaping changes when shaped separately (lost kerning, ligatures, contextual forms).
    Browsers shape each font's run on its own, so these render differently after the split."""
    face = hb.Face(hb.Blob.from_file_path(str(src)))
    font = hb.Font(face)
    ranges = {t: (v if isinstance(v, tuple) else (v, v)) for t, v in cfg["axes"].items() if v is not None}
    corners = [dict(zip(ranges, combo)) for combo in product(*ranges.values())] or [{}]
    losses: dict[str, list[str]] = {}
    for pair in pairs:
        a, b = pair
        if not ((ord(a) in core and ord(b) in ext) or (ord(a) in ext and ord(b) in core)):
            continue
        for loc in corners:
            font.set_variations(loc)
            if shaped(font, pair) != shaped(font, a) + shaped(font, b):
                moved = a if ord(a) in ext else b
                losses.setdefault(moved, []).append(pair)
                break
    return losses


def plan_split(src: Path, cfg: dict, keep: set[int]) -> tuple[set[int], set[int]]:
    core, ext = keep & CORE, keep - CORE
    pairs_file = cfg.get("used_pairs")
    if not pairs_file or not (ROOT / pairs_file).exists():
        print(f"{cfg['name']}: no pairs file; cross-split shaping NOT checked. Rely on the pixel diffs.")
        return core, ext
    pairs = [l for l in (ROOT / pairs_file).read_text("utf-8").split("\n") if len(l) == 2]
    while losses := cross_split_losses(src, cfg, core, ext, pairs):
        listing = ", ".join(f"{c} ({' '.join(ps[:4])})" for c, ps in sorted(losses.items()))
        if not cfg.get("promote_cross_split", True):
            print(f"{cfg['name']}: APPROVED LOSS of kerning/shaping across the split for: {listing}")
            break
        print(f"{cfg['name']}: moving to core to keep kerning/shaping with neighbours: {listing}")
        moved = {ord(c) for c in losses}
        core, ext = core | moved, ext - moved  # repeat: moved chars may now border other ext chars
    return core, ext


# --- checks ------------------------------------------------------------------

def unicode_range(cps: set[int]) -> str:
    cps = sorted(cps)
    out, i = [], 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        out.append(f"U+{cps[i]:X}" if i == j else f"U+{cps[i]:X}-{cps[j]:X}")
        i = j + 1
    return ", ".join(out)


def vertical_metrics(f: TTFont) -> tuple:
    os2 = f["OS/2"]
    return (f["head"].unitsPerEm, f["hhea"].ascent, f["hhea"].descent, f["hhea"].lineGap,
            os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap, os2.usWinAscent, os2.usWinDescent,
            bool(os2.fsSelection & (1 << 7)))


def glyphs_at(font: TTFont, location: dict, cps: set[int]) -> dict[int, tuple[int, list]]:
    """Advance width and flattened outline points per codepoint, at one axis location."""
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, location, static=True)
    cmap, hmtx, glyphset = font.getBestCmap(), font["hmtx"], font.getGlyphSet()
    out = {}
    for cp in cps:
        if cp in cmap:
            pen = DecomposingRecordingPen(glyphset)  # components drawn as outlines
            glyphset[cmap[cp]].draw(pen)
            out[cp] = (hmtx[cmap[cp]][0], [xy for _, args in pen.value for xy in args])
    return out


# Narrowing an axis range makes the instancer rescale and re-round gvar deltas, so
# outlines between masters can move by a unit or so. Under this many font units the
# change is sub-pixel at text sizes (1 unit at 2048 UPM and 32px = 0.016px).
MAX_OUTLINE_DELTA_UNITS = 2
# HVAR deltas get the same re-rounding, so advances between masters can shift by 1 unit.
# That's sub-pixel per glyph, but it adds up along a line: the pixel diffs must confirm
# no line break moved.
MAX_ADVANCE_DELTA_UNITS = 1


def check(src: Path, out: Path, cfg: dict, wanted: set[int], contained: set[int], rng: str) -> list[str]:
    errors = []
    source, built = TTFont(src), TTFont(out)
    cmap = set(built.getBestCmap())

    if cmap & wanted != contained:
        errors.append("cmap does not match the codepoints reported at build time")
    if rng != unicode_range(cmap & wanted):
        errors.append("unicode-range does not equal the cmap")

    if vertical_metrics(source) != vertical_metrics(built):
        errors.append(f"vertical metrics changed: {vertical_metrics(source)} -> {vertical_metrics(built)}")

    hint_tables = [t for t in HINTING if t in built]
    if hint_tables:
        errors.append(f"hinting tables left: {hint_tables}")

    for tag in ("GSUB", "GPOS"):
        if tag in built:
            feats = {r.FeatureTag for r in built[tag].table.FeatureList.FeatureRecord}
            extra = feats - set(cfg["features"])
            if extra:
                errors.append(f"{tag} has unplanned features: {sorted(extra)}")

    # Advances must match exactly, and outlines within rounding, at every corner and
    # midpoint of the kept axis ranges. Unspecified axes are pinned at their default,
    # which is what None pins to in CONFIG.
    locations = [{}]
    if "fvar" in built:
        axes = {a.axisTag: (a.minValue, a.maxValue) for a in built["fvar"].axes}
        print("  axes:", axes)
        for tag, (lo, hi) in axes.items():
            locations = [{**l, tag: v} for l in locations for v in sorted({lo, (lo + hi) / 2, hi})]
    pinned = {t: v for t, v in cfg["axes"].items() if isinstance(v, (int, float))}
    # Shrink the source to the same characters first: subsetting doesn't touch outlines,
    # advances or variations of kept glyphs, and instancing a full font per location is slow.
    reference = TTFont(src)
    ref_opts = subset.Options(layout_features=[], notdef_outline=True, glyph_names=True)
    ref_sub = subset.Subsetter(ref_opts)
    ref_sub.populate(unicodes=sorted(cmap & wanted))
    ref_sub.subset(reference)
    worst, worst_adv, adv_changed, structure = 0.0, 0, set(), set()
    for loc in locations:
        a = glyphs_at(reference, {**pinned, **loc}, cmap & wanted)
        b = glyphs_at(built, loc, cmap & wanted)
        for cp, (adv, pts) in a.items():
            adv2, pts2 = b[cp]
            if adv != adv2:
                adv_changed.add(chr(cp))
                worst_adv = max(worst_adv, abs(adv - adv2))
            if len(pts) != len(pts2):
                structure.add(chr(cp))
            else:
                worst = max([worst] + [max(abs(x1 - x2), abs(y1 - y2)) for (x1, y1), (x2, y2) in zip(pts, pts2)])
    print(f"  vs source over {len(locations)} axis locations: outlines move <= {worst:.2f} units, "
          f"advances <= {worst_adv} units ({len(adv_changed)} glyphs)")
    if structure:
        errors.append(f"outline structure changed: {''.join(sorted(structure))}")
    if worst > MAX_OUTLINE_DELTA_UNITS + 0.01:
        errors.append(f"outlines moved by up to {worst:.2f} units; more than rounding")
    if worst_adv > MAX_ADVANCE_DELTA_UNITS:
        errors.append(f"advance widths changed by up to {worst_adv} units: {''.join(sorted(adv_changed))[:40]}")

    if cfg["reserved_name"]:
        r = cfg["reserved_name"].lower()
        leaks = [(n.nameID, n.toUnicode()) for n in built["name"].names
                 if n.nameID not in KEEP_NAME_IDS and (r in n.toUnicode().lower() or r.replace(" ", "") in n.toUnicode().lower())]
        if leaks:
            errors.append(f"reserved name still present: {leaks[:5]}")
    return errors


# --- main --------------------------------------------------------------------

def read_chars(path: str) -> set[int]:
    return {ord(c) for c in (ROOT / path).read_text("utf-8") if not c.isspace() or c in "   "}


def build_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    css, failed = [], False
    for cfg in CONFIG:
        src = ROOT / cfg["source"]
        source_cmap = set(TTFont(src).getBestCmap())
        requested = read_chars(cfg["used_chars"]) | LATIN | set(cfg["extra_codepoints"]) | CORE
        keep = requested & source_cmap
        missing = requested - source_cmap
        if missing:
            print(f"{cfg['name']}: source has no glyph for {len(missing)} codepoints; they fall back as today: "
                  + unicode_range(missing)[:200])
        core, ext = plan_split(src, cfg, keep)
        parts = {"core": core, "ext": ext}
        for suffix, cps in parts.items():
            if not cps:
                continue
            out, contained = build_file(src, cfg, cps, suffix)
            rng = unicode_range(contained)
            print(f"{out.name}: {out.stat().st_size} bytes, {len(contained)} codepoints")
            errors = check(src, out, cfg, cps, contained, rng)
            for e in errors:
                print(f"  FAIL {e}")
            failed |= bool(errors)
            desc = "".join(f"\n  {k}: {v};" for k, v in cfg["descriptors"].items())
            css.append(f"@font-face {{\n  font-family: \"{cfg['family']}\";\n"
                       f"  src: url(\"{URL_PREFIX}{out.name}\") format(\"woff2\");{desc}\n"
                       f"  unicode-range: {rng};\n}}")
    CSS_OUT.write_text("/* Generated by scripts/subset-fonts.py. Do not edit; rerun the script. */\n\n"
                       + "\n\n".join(css) + "\n", "utf-8")
    print(f"wrote {CSS_OUT.relative_to(ROOT)}")
    if failed:
        sys.exit(1)


def check_coverage(build_dir: str) -> None:
    """Rough check: characters in built HTML that no generated file covers.
    The usage audit is the source of truth; this only flags when to rerun it."""
    covered = set()
    for f in OUT_DIR.glob("*.woff2"):
        covered |= set(TTFont(f).getBestCmap())
    text = "".join(html.unescape(re.sub(r"<[^>]+>", " ", p.read_text("utf-8", errors="ignore")))
                   for p in Path(build_dir).rglob("*.html"))
    uncovered = sorted({ord(c) for c in text if not c.isspace()} - covered)
    for cp in uncovered:
        print(f"U+{cp:04X} {chr(cp)}")
    print(f"{len(uncovered)} uncovered characters (CJK and others that fall back to system fonts today are expected)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-coverage", metavar="BUILD_DIR")
    args = ap.parse_args()
    check_coverage(args.check_coverage) if args.check_coverage else build_all()
