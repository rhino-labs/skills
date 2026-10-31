# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.64.1"]
# ///
"""
Rendered-pass font usage audit. Loads every page in Chromium at several widths,
walks every text node, form control and pseudo-element, and records, per web
font face (family + style), what the browser actually asks of it.

    uv run scripts/audit-font-usage.py --base http://localhost:4173 --pages pages.txt --out fonts/usage

pages.txt: one path per line (or pass --sitemap to read <base>/sitemap.xml).
Writes <out>/usage.json, <out>/<family>-<style>.txt (characters) and <family>-<style>.pairs.txt
(adjacent character pairs, for the cross-split shaping check), both read by subset-fonts.py.

This does not see :hover/:focus styles, content shown only after interaction, or
breakpoints you didn't render. Grep for those separately (see usage-audit.md).
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = [375, 768, 1280, 1920]

COLLECT = r"""
() => {
  const faces = new Set([...document.fonts].map(f => f.family.replace(/^["']|["']$/g, "")));
  const out = {};
  const unquote = s => s.trim().replace(/^["']|["']$/g, "");
  const primary = ff => {
    for (const raw of ff.split(",")) { const n = unquote(raw); if (faces.has(n)) return n; }
    return "(no web font)";
  };
  const MARKERS = {
    disc: "\u2022", circle: "\u25E6", square: "\u25AA", "disclosure-open": "\u25BE", "disclosure-closed": "\u25B8",
    decimal: "0123456789.", "decimal-leading-zero": "0123456789.",
    "lower-alpha": "abcdefghijklmnopqrstuvwxyz.", "lower-latin": "abcdefghijklmnopqrstuvwxyz.",
    "upper-alpha": "ABCDEFGHIJKLMNOPQRSTUVWXYZ.", "upper-latin": "ABCDEFGHIJKLMNOPQRSTUVWXYZ.",
    "lower-roman": "ivxlcdm.", "upper-roman": "IVXLCDM.",
  };
  const transformed = (text, cs, el) => {
    const lang = (el.closest("[lang]")?.getAttribute("lang")) || undefined;
    switch (cs.textTransform) {
      case "uppercase": return text.toLocaleUpperCase(lang);
      case "lowercase": return text.toLocaleLowerCase(lang);
      case "capitalize": return text + text.toLocaleUpperCase(lang); // superset is safe
      default: return text;
    }
  };
  const record = (el, cs, text) => {
    if (!text) return;
    const key = primary(cs.fontFamily) + "|" + cs.fontStyle.split(" ")[0];
    const e = out[key] ??= { chars: "", weights: [], stretch: [], sizes: [], variation: [], features: [],
      variants: [], opticalSizing: [], kerning: [], synthesis: [], examples: {}, pairs: {} };
    let t = transformed(text, cs, el);
    if (cs.hyphens === "auto") t += "\u2010-";
    if (cs.textOverflow === "ellipsis") t += "\u2026";
    e.chars += t;
    // Adjacent pairs involving a non-ASCII character: if the two land in different
    // files (core/extended), the browser can't kern or shape across them.
    const cs_ = Array.from(t);
    for (let i = 1; i < cs_.length; i++) {
      const a = cs_[i - 1], b = cs_[i];
      if ((a.codePointAt(0) > 0x7E || b.codePointAt(0) > 0x7E) && a.trim() && b.trim()) e.pairs[a + b] = 1;
    }
    const add = (list, v) => { if (!list.includes(v)) list.push(v); };
    add(e.weights, cs.fontWeight);
    add(e.stretch, cs.fontStretch);
    add(e.sizes, parseFloat(cs.fontSize));
    add(e.variation, cs.fontVariationSettings);
    add(e.features, cs.fontFeatureSettings);
    add(e.variants, [cs.fontVariantLigatures, cs.fontVariantNumeric, cs.fontVariantCaps,
      cs.fontVariantEastAsian, cs.fontVariantPosition, cs.fontVariantAlternates].join(" / "));
    add(e.opticalSizing, cs.fontOpticalSizing);
    add(e.kerning, cs.fontKerning);
    add(e.synthesis, cs.fontSynthesis);
    // Remember one element per unusual setting so one-off overrides can be traced back.
    const sig = [cs.fontWeight, cs.fontVariationSettings, cs.fontFeatureSettings].join(" ");
    if (!e.examples[sig] && Object.keys(e.examples).length < 50) {
      e.examples[sig] = el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") +
        (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).slice(0, 3).join(".") : "");
    }
  };
  const SKIP = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "HEAD", "TITLE"]);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const el = n.parentElement;
    if (!el || SKIP.has(el.tagName) || !n.data.trim()) continue;
    record(el, getComputedStyle(el), n.data);
  }
  for (const el of document.body.querySelectorAll("*")) {
    if (SKIP.has(el.tagName)) continue;
    for (const pseudo of ["::before", "::after"]) {
      const cs = getComputedStyle(el, pseudo);
      if (!cs.content || cs.content === "none" || cs.content === "normal") continue;
      let text = [...cs.content.matchAll(/"((?:\\.|[^"\\])*)"/g)].map(m => m[1].replace(/\\(.)/g, "$1")).join("");
      if (/counter/.test(cs.content)) text += "0123456789";
      if (/(open|close)-quote/.test(cs.content)) text += "\u201C\u201D\u2018\u2019\u201E\u201A\u00AB\u00BB\u2039\u203A";
      record(el, cs, text);
    }
    const cs = getComputedStyle(el);
    if (cs.display === "list-item" && cs.listStyleType !== "none") {
      const lst = cs.listStyleType;
      const m = getComputedStyle(el, "::marker");
      record(el, m, MARKERS[lst] ?? (lst.startsWith('"') ? unquote(lst) : "0123456789."));
    }
    if (el.tagName === "Q") record(el, cs, "\u201C\u201D\u2018\u2019\u201E\u201A\u00AB\u00BB\u2039\u203A");
    if (el.matches("input, textarea, select, button")) {
      record(el, cs, (el.value ?? "") + [...(el.options ?? [])].map(o => o.text).join(""));
      if (el.placeholder) record(el, getComputedStyle(el, "::placeholder"), el.placeholder);
    }
  }
  return out;
}
"""


def page_list(base: str, pages: str | None, sitemap: bool) -> list[str]:
    if sitemap:
        xml = urllib.request.urlopen(base.rstrip("/") + "/sitemap.xml").read().decode()
        return [re.sub(r"^https?://[^/]+", "", u) for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    return [l.strip() for l in Path(pages).read_text().splitlines() if l.strip() and not l.startswith("#")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--pages")
    ap.add_argument("--sitemap", action="store_true")
    ap.add_argument("--out", default="fonts/usage")
    args = ap.parse_args()

    merged: dict[str, dict] = {}
    pages_with_char: dict[str, set[str]] = defaultdict(set)
    paths = page_list(args.base, args.pages, args.sitemap)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in paths:
            for width in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.goto(args.base.rstrip("/") + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                for key, e in page.evaluate(COLLECT).items():
                    m = merged.setdefault(key, {k: ([] if isinstance(v, list) else {} if isinstance(v, dict) else "")
                                                for k, v in e.items()})
                    m["chars"] = "".join(sorted(set(m["chars"]) | set(e["chars"])))
                    for k, v in e.items():
                        if isinstance(v, list):
                            m[k] = sorted(set(m[k]) | set(v), key=str)
                        elif isinstance(v, dict):
                            m[k].update(v)
                    for c in set(e["chars"]):
                        pages_with_char[c].add(path)
                page.close()
            print(f"audited {path}")
        browser.close()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for key, e in merged.items():
        e["sizes"] = [min(e["sizes"]), max(e["sizes"])] if e["sizes"] else []
        fam, style = key.split("|")
        if fam != "(no web font)":
            stem = f"{re.sub(r'[^A-Za-z0-9]+', '-', fam).strip('-').lower()}-{style}"
            (out / f"{stem}.txt").write_text(e["chars"], "utf-8")
            (out / f"{stem}.pairs.txt").write_text("\n".join(sorted(e["pairs"])) + "\n", "utf-8")
        e["pairs"] = len(e["pairs"])
    # How many pages use each non-ASCII character: decides what goes in the core file.
    freq = sorted(((c, len(ps)) for c, ps in pages_with_char.items() if ord(c) > 0x7E),
                  key=lambda x: (-x[1], x[0]))
    report = {"pages": len(paths), "faces": merged,
              "non_ascii_by_pages": [{"char": c, "codepoint": f"U+{ord(c):04X}", "pages": n} for c, n in freq]}
    (out / "usage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
    print(f"wrote {out}/usage.json and per-face character files")


if __name__ == "__main__":
    main()
