---
name: seamless-mobile-safari
description: Make the areas behind iOS Safari's status bar and bottom toolbar match the page's top and bottom edges, including fixed backgrounds whose colors change as you scroll. Uses thin fixed "edge strips" that Safari samples, synced with the html/body backgrounds and theme-color. Use when the user sees white or mismatched bars above or below their content on iPhone Safari, wants a hero or full-bleed background to run under the browser chrome, wants different top and bottom chrome colors, or asks for a "seamless" or "edge-to-edge" look in mobile Safari. Based on Josh Puckett's "Seamless Backgrounds on Mobile Safari".
---

# Seamless Mobile Safari

## Overview

iOS Safari tints the areas behind its status bar (top) and toolbar (bottom). By default those tints often don't match the design. A hero gets a white bar above it, or a dark page gets a light toolbar under it. `<meta name="theme-color">` alone doesn't fix this. It works well for installed web apps, not for pages in the browser, and it only sets one color, so the top and bottom can't differ.

Safari does extend the background of a **fixed element touching the viewport edge** behind its controls. The technique is to put a thin, solid, fixed strip at the top and bottom edges, set to the color that should continue behind the chrome. Then keep those strips, the `html`/`body` backgrounds, and `theme-color` in sync from one set of color values, including while the user scrolls.

Source: https://joshpuckett.me/seamless-mobile-safari (Josh Puckett; fade refinement by Joe Bell).

## How Safari picks the edge color

This is WebKit's `LocalFrameView::fixedContainerEdges`. Every rule below comes from it, so use it when something doesn't work:

- **Hit test 4px inside each edge.** Safari hit-tests the midpoint of each side, inset by 4px, and walks up from the element it hits to find a `position: fixed` or `sticky` ancestor. A strip therefore needs **at least 5px visible** past the edge, and it must be the **top-most** thing at that point. If content scrolls over it, Safari falls back to the page background.
- **`pointer-events: none` is fine.** The first hit test ignores `pointer-events`, so a non-interactive strip still counts.
- **Must span the viewport.** An element narrower than about 90% of the viewport along that edge is skipped or treated as a sidebar. Use `left: 0; right: 0`.
- **More than 10px thick.** For a box more than 10px in both dimensions, Safari reads its CSS `background-color` directly. For a box 10px or thinner, Safari ignores the CSS color and samples rendered pixels instead, which is less reliable. That's why the strips are at least 12px tall, even when most of the strip is offscreen.
- **Full-screen fixed layers don't drive it.** A fixed element about the size of the viewport counts as a "viewport-sized" or dimming layer, and Safari keeps the color it already had. That's why a full-screen fixed gradient on its own doesn't update the chrome, and you need dedicated strips.
- **No `backdrop-filter`.** A blurred fixed bar means "multiple colors", and Safari won't use a single tint.
- **Opacity.** A background with alpha ≥ 0.75 is treated as fully opaque. Below that, it's blended over the page background. Use solid colors.
- **No negative `z-index`**, and the strip can't be `visibility: hidden` or transparent.
- **Fallback.** When no fixed container qualifies, Safari uses the page's extended background, which is the `html`/`body` background.

## Step 1: Inspect the page

Before writing anything, work out:

1. **What color sits at the very top and very bottom of the viewport.** Is it a solid color, a gradient that changes as you scroll, or an image? (For images, see Limitations.)
2. **The viewport meta.** Is `viewport-fit=cover` set? Where does the framework define it? In Next.js App Router it's the `viewport` export; elsewhere it's usually the root layout `<head>`.
3. **Existing `theme-color` tags.** Note any per-scheme tags that use `media="(prefers-color-scheme: …)"`.
4. **Fixed or sticky headers, footers, and tab bars.** A fixed header with a solid background at the top edge already drives Safari's top color. If it's the color you want, you don't need a top strip there. If it uses `backdrop-filter`, it blocks sampling at that edge. In that case, put the strip above it with a higher `z-index`.
5. **Transformed ancestors.** `transform`, `filter`, `perspective`, `contain: paint`, and `will-change: transform` on an ancestor make `position: fixed` relative to that ancestor. Mount the strips as direct children of `<body>`, or portal them there.

## Step 2: Static colors

Use this when the top and bottom colors don't change with scroll.

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="theme-color" content="#004bff" />
```

```html
<!-- direct children of <body>, outside any transformed ancestor -->
<div class="edge-top" aria-hidden="true"></div>
<div class="edge-bottom" aria-hidden="true"></div>
```

```css
:root {
  --edge-top-background: #004bff;
  --edge-bottom-background: #004bff;
}

html { background: var(--edge-top-background); }
body { background: var(--edge-bottom-background); }

.edge-top::after,
.edge-bottom::after {
  content: "";
  position: fixed;
  left: 0;
  right: 0;
  z-index: 10; /* above scrolling content, or Safari samples the content instead */
  pointer-events: none;
}
.edge-top::after {
  top: 0;
  height: max(12px, env(safe-area-inset-top));
  background: var(--edge-top-background);
}
.edge-bottom::after {
  bottom: 0;
  height: max(12px, env(safe-area-inset-bottom));
  background: var(--edge-bottom-background);
}
```

Notes:

- `html` gets the **top** color and `body` the **bottom** color. That way, rubber-band overscroll and Safari's fallback match the nearest edge.
- `max(12px, env(...))` makes the strip cover the notch or home-indicator inset, with 12px as the minimum where the inset is 0. Without `viewport-fit=cover`, every `env(safe-area-inset-*)` value is `0`.
- Keep the strips clear of real content. Pad fixed headers, footers, and first and last content with `env(safe-area-inset-*)` so text and controls never sit under a strip.
- Give the z-index whatever value puts the strips above page content but below modals and toasts in the project's stacking scale. Don't use 10 blindly.

## Step 3 (optional): Fade instead of a hard line

Joe Bell's refinement keeps only a thin solid band, 5px visible, which is enough for Safari's 4px hit test. A gradient then fades from that color to transparent, so the page has no hard horizontal edge under the chrome.

```css
.edge-top::after,
.edge-bottom::after {
  height: 12px;
  z-index: 10;
}
.edge-top::after {
  top: -7px; /* 5px visible */
  background: var(--edge-top-background);
}
.edge-bottom::after {
  bottom: -7px; /* 5px visible */
  background: var(--edge-bottom-background);
}

.edge-top::before,
.edge-bottom::before {
  content: "";
  position: fixed;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 10;
  pointer-events: none;
}
.edge-top::before {
  top: 5px;
  background: linear-gradient(to bottom, var(--edge-top-background), transparent);
}
.edge-bottom::before {
  bottom: 5px;
  background: linear-gradient(to top, var(--edge-bottom-background), transparent);
}
```

These rules replace the `::after` heights from Step 2. They don't add to them. If the page has a large safe-area inset, consider making the fade at least `env(safe-area-inset-top)` tall so it covers the area behind the status bar.

## Step 4 (optional): Colors that change with scroll

Use this when the page has a fixed background, such as a gradient, that changes color as you scroll. Compute the palette **once per frame**. Then write the same values to every place that uses them: the visible background (through the CSS variables), both strips, `html`/`body`, and `theme-color`.

```js
// getColors(scrollY, viewportHeight) => { top: "#rrggbb", bottom: "#rrggbb" }
export function syncSafariEdges(getColors) {
  const root = document.documentElement;
  const body = document.body;

  let meta = document.querySelector('meta[name="theme-color"]:not([media])');
  const createdMeta = !meta;
  if (!meta) {
    meta = document.createElement("meta");
    meta.name = "theme-color";
    document.head.appendChild(meta);
  }

  const previous = {
    htmlBackground: root.style.background,
    bodyBackground: body.style.background,
    themeColor: meta.content,
  };

  let frame = 0;
  const apply = () => {
    frame = 0;
    const { top, bottom } = getColors(window.scrollY, window.innerHeight);
    root.style.setProperty("--edge-top-background", top);
    root.style.setProperty("--edge-bottom-background", bottom);
    root.style.background = top;
    body.style.background = bottom;
    meta.content = top;
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(apply);
  };

  apply();
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("pageshow", schedule); // bfcache / restored scroll position
  window.visualViewport?.addEventListener("resize", schedule); // toolbar expand/collapse

  return () => {
    cancelAnimationFrame(frame);
    window.removeEventListener("scroll", schedule);
    window.removeEventListener("resize", schedule);
    window.removeEventListener("pageshow", schedule);
    window.visualViewport?.removeEventListener("resize", schedule);
    root.style.removeProperty("--edge-top-background");
    root.style.removeProperty("--edge-bottom-background");
    root.style.background = previous.htmlBackground;
    body.style.background = previous.bodyBackground;
    if (createdMeta) meta.remove();
    else meta.content = previous.themeColor;
  };
}
```

Guidance:

- **Drive the visible background from the same variables** when you can, for example `background: linear-gradient(var(--edge-top-background), var(--edge-bottom-background))` on the fixed backdrop. Then the visible background and the chrome can't drift apart. If the visible gradient has more than two stops, `getColors` must return the colors actually showing at the viewport's top and bottom edges, not the gradient's endpoints.
- **Interpolate in a perceptual space** (OKLCH or OKLab) if you're blending between stops, and output a format `theme-color` accepts. Hex and `rgb()` are safest.
- **Restored scroll positions.** Call `apply()` on mount and on `pageshow`, so a page restored mid-scroll starts with the right colors and doesn't flash the top-of-page palette.
- **Per-scheme `theme-color` tags.** If the page has `media="(prefers-color-scheme: …)"` tags, update the one that matches the current scheme, or replace both while the effect is active and restore them in cleanup.
- **Cleanup is required in SPAs.** In React, call `syncSafariEdges` in a `useEffect` and return its cleanup. In other frameworks, run it on route enter and clean up on route leave. Otherwise the next page inherits this page's chrome colors and the inline `html`/`body` backgrounds.
- **`prefers-reduced-motion`** doesn't apply. The colors track scroll position, which the user controls directly.

## Limitations

Say these up front when they apply. Don't promise what the technique can't do.

- **Each edge gets exactly one solid color.** That color can change over time, but Safari won't extend an image, a video, or a gradient that changes color from left to right behind its controls. For an image hero, pick the dominant edge color, or accept the mismatch.
- **Safari only.** Other browsers ignore the strips, which are harmless there. `theme-color` covers some Android browsers' address bars.
- **Verify on a real iPhone.** Desktop Safari's responsive mode and Chrome device emulation don't reproduce this behavior. The iOS Simulator is reasonable for checking colors. Connect a device and use Safari → Develop to confirm while scrolling, after the toolbar collapses, and after back/forward navigation.

## Prompt form

If the user just wants the canonical instruction, this is Josh Puckett's prompt, lightly condensed:

> Make the colors behind mobile Safari's status bar and bottom controls match the visible top and bottom edges of this page, including when its background changes as you scroll. Use one set of color values for the page background, two thin fixed edge strips, and the document backgrounds. Create aria-hidden `.edge-top` and `.edge-bottom` elements outside transformed ancestors. Paint their `::after` pseudo-elements with `--edge-top-background` and `--edge-bottom-background`. Make them full-width, `pointer-events: none`, and `max(12px, env(safe-area-inset-top))` or `max(12px, env(safe-area-inset-bottom))` tall. Keep the strips clear of content and match each one to its adjacent background. Set the html background to the top color and the body background to the bottom color. Include a theme-color meta tag and update it with the top color. Use `viewport-fit=cover` while keeping text and controls inside the safe areas. If the palette changes, calculate it once and apply the same values everywhere. Handle scrolling, restored scroll positions, viewport resizing, and Safari's expanding or collapsing toolbar. Remove listeners and restore any shared document styles when leaving the page.

## Output

After implementing, report briefly:

- **Edge colors.** Which color drives the top and the bottom, and whether they're static or scroll-driven.
- **What changed.** Files touched, one line each: viewport meta, theme-color, strip markup and CSS, sync hook.
- **What needs a phone.** The chrome tint can't be verified from code or desktop emulation. List what to check on a real iPhone: at rest, mid-scroll, toolbar collapsed, and after back navigation.
