# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""
Measure font bytes per page, and pixel-diff a baseline build against the optimized one.

    # font requests, bytes and preloads per page (no cache)
    uv run scripts/compare-fonts.py measure --base http://localhost:4173 --pages pages.txt --out fonts/report/after.json

    # screenshots of both builds + per-pixel diff
    uv run scripts/compare-fonts.py diff --before http://localhost:4100 --after http://localhost:4173 \
        --pages pages.txt --out fonts/report/diff

First run: uv run --with playwright==1.64.1 playwright install chromium webkit
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageChops
from playwright.sync_api import Page, sync_playwright

FONT_EXT = (".woff2", ".woff", ".ttf", ".otf")
VIEWPORTS = [("mobile", 390, 844), ("desktop", 1280, 900)]
SCALES = [1, 2]
BROWSERS = ["chromium", "webkit"]

# Freeze anything that moves so only glyphs can differ.
FREEZE_CSS = """
*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }
html { scroll-behavior: auto !important; }
"""


def pages(path: str) -> list[str]:
    return [l.strip() for l in Path(path).read_text().splitlines() if l.strip() and not l.startswith("#")]


def settle(page: Page) -> None:
    """Wait for every font load, including unicode-range files triggered by layout."""
    page.evaluate("document.fonts.ready")
    # Scroll through the page so lazy content renders and requests its fonts.
    page.evaluate("""async () => {
        for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight) {
            scrollTo(0, y); await new Promise(r => requestAnimationFrame(() => r()));
        }
        scrollTo(0, 0);
    }""")
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")


def measure(args) -> None:
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in pages(args.pages):
            ctx = browser.new_context()  # fresh context: empty cache
            page = ctx.new_page()
            fonts, warnings = [], []
            page.on("console", lambda m: warnings.append(m.text) if "preload" in m.text.lower() else None)

            def on_response(resp):
                if urlparse(resp.url).path.lower().endswith(FONT_EXT) or resp.request.resource_type == "font":
                    fonts.append({"url": resp.url, "status": resp.status})
            page.on("response", on_response)
            page.goto(args.base.rstrip("/") + path, wait_until="load")
            settle(page)
            page.wait_for_timeout(3500)  # Chrome warns about unused preloads after ~3s
            for f in fonts:
                entry = page.evaluate("u => performance.getEntriesByName(u)[0]?.encodedBodySize ?? null", f["url"])
                f["bytes"] = entry
            preloads = page.evaluate("""() => [...document.querySelectorAll('link[rel=preload][as=font]')]
                .map(l => ({ href: l.href, crossorigin: l.crossOrigin, type: l.type }))""")
            loaded = page.evaluate("""() => [...document.fonts].filter(f => f.status === 'loaded')
                .map(f => `${f.family} ${f.style} ${f.weight} ${f.unicodeRange}`)""")
            results.append({
                "page": path,
                "font_bytes": sum(f["bytes"] or 0 for f in fonts),
                "fonts": fonts,
                "preloads": preloads,
                "loaded_faces": loaded,
                "preload_warnings": warnings,
            })
            print(f"{path}: {results[-1]['font_bytes']} font bytes, {len(fonts)} requests, "
                  f"{len(preloads)} preloads{', WARN ' + '; '.join(warnings) if warnings else ''}")
            ctx.close()
        browser.close()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, indent=2), "utf-8")


def shoot(p, engine: str, base: str, path: str, w: int, h: int, scale: int, out: Path) -> None:
    browser = getattr(p, engine).launch()
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(base.rstrip("/") + path, wait_until="load")
    page.add_style_tag(content=FREEZE_CSS)
    settle(page)
    page.screenshot(path=str(out), full_page=True, animations="disabled", caret="hide")
    browser.close()


def diff(args) -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    with sync_playwright() as p:
        for path in pages(args.pages):
            slug = path.strip("/").replace("/", "_") or "index"
            for engine in args.browsers:
                for vname, w, h in VIEWPORTS:
                    for scale in SCALES:
                        stem = f"{slug}.{engine}.{vname}@{scale}x"
                        a, b = out / f"{stem}.before.png", out / f"{stem}.after.png"
                        shoot(p, engine, args.before, path, w, h, scale, a)
                        shoot(p, engine, args.after, path, w, h, scale, b)
                        ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
                        if ia.size != ib.size:
                            summary.append({"shot": stem, "result": "SIZE CHANGED", "before": ia.size, "after": ib.size})
                            print(f"{stem}: SIZE CHANGED {ia.size} -> {ib.size}")
                            continue
                        d = ImageChops.difference(ia, ib)
                        mask = d.convert("L").point(lambda v: 255 if v else 0)
                        changed = sum(1 for v in mask.getdata() if v)
                        bbox = mask.getbbox()
                        if changed:
                            # Red over a faded copy of the "after" shot, for locating differences.
                            faded = Image.blend(ib, Image.new("RGB", ib.size, "white"), 0.7)
                            faded.paste(Image.new("RGB", ib.size, (255, 0, 0)), mask=mask)
                            faded.save(out / f"{stem}.diff.png")
                        else:
                            a.unlink(); b.unlink()
                        summary.append({"shot": stem, "changed_pixels": changed, "bbox": bbox,
                                        "max_channel_delta": max(e[1] for e in d.getextrema())})
                        print(f"{stem}: {changed} changed pixels" + (f" in {bbox}" if bbox else ""))
    (out / "summary.json").write_text(json.dumps(summary, indent=2), "utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--base", required=True)
    m.add_argument("--pages", required=True)
    m.add_argument("--out", required=True)
    d = sub.add_parser("diff")
    d.add_argument("--before", required=True)
    d.add_argument("--after", required=True)
    d.add_argument("--pages", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--browsers", nargs="+", default=BROWSERS)
    args = ap.parse_args()
    measure(args) if args.cmd == "measure" else diff(args)
