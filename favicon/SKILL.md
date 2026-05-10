---
name: favicon
description: Generate a complete set of favicons (ICO, PNGs, web manifest) from a source image, then wire them into the project's framework (Next.js metadata, Rails layout, Astro head, plain HTML, etc.). Use when the user asks to create, generate, update, or replace favicons, app icons for the web, or wants a `favicon.ico` / `apple-touch-icon` / `site.webmanifest` from a source image (PNG, JPG, SVG, WEBP, GIF).
---

# Favicon

## Overview

Generate `favicon.ico`, sized PNGs (96, 180, 192, 512), and `site.webmanifest` from a source image using ImageMagick, then wire them into the project using whatever mechanism the detected framework expects.

## Step 1: Ensure ImageMagick is installed

Check for the `magick` CLI:

```bash
which magick
```

If missing, install it without prompting (the user already opted in by invoking this skill):

- **macOS** (Homebrew available): `brew install imagemagick`
- **Debian/Ubuntu**: `sudo apt-get install -y imagemagick`
- **Fedora/RHEL**: `sudo dnf install -y ImageMagick`
- **Other / install fails**: Stop and point the user to https://imagemagick.org/script/download.php

After installing, re-run `which magick` to confirm. If `magick` is still not found but `convert` is, the system has ImageMagick v6 — instruct the user to upgrade to v7+ via the link above. Do not silently fall back to `convert`.

## Step 2: Validate the source image

The user supplies a source image path as input.

1. Verify the file exists.
2. Verify the extension is one of: `.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`, `.gif` (case-insensitive).
3. Note whether it is an SVG — if so, it will additionally be copied as `favicon.svg`.

If validation fails, report the exact path tried and stop.

## Step 3: Detect the framework

Inspect the repo and form a best guess. Useful signals:

- `package.json` `dependencies`/`devDependencies` — `next`, `react-scripts`, `gatsby`, `@sveltejs/kit`, `astro`, `vite`, `@vue/cli-service`, `@angular/core`, `@11ty/eleventy`, `nuxt`, `remix`
- Config files at the repo root — `next.config.*`, `gatsby-config.*`, `svelte.config.*`, `astro.config.*`, `vite.config.*`, `nuxt.config.*`, `vue.config.*`, `angular.json`, `.eleventy.js`, `eleventy.config.*`, `hugo.toml`, `_config.yml`
- Rails — `config/routes.rb`, `Gemfile` with `rails`
- Plain static — `index.html` at the repo root with no framework markers

Frameworks have **two** things that matter here:

1. **Where static assets live** (e.g., `public/`, `static/`, `src/assets/`)
2. **How icons get registered** (HTML `<link>` tags, framework metadata API, file-based conventions like Next.js App Router's `app/icon.png`)

Form a best guess for both.

## Step 4: Confirm with the user

Use `AskUserQuestion` to confirm. Single question, options like:

- `Next.js (App Router)`
- `Next.js (Pages Router)`
- `<other detected framework>`
- `Plain HTML / something else`

Include a short description on each option naming the static-asset directory you'll use. The user can override via "Other" if your detection is wrong.

If the user picks something you don't already have working knowledge of (or you're unsure about its current best practice), use `WebFetch` against the framework's official docs to learn the correct icon-registration mechanism before proceeding. Examples of authoritative pages to check:

- Next.js App Router: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/app-icons
- Next.js Metadata API: https://nextjs.org/docs/app/api-reference/functions/generate-metadata#icons
- Astro: https://docs.astro.build/en/basics/project-structure/#public
- SvelteKit: https://svelte.dev/docs/kit/project-structure#project-files-static
- Nuxt: https://nuxt.com/docs/api/components/nuxt-link (and head config)
- Remix: https://remix.run/docs/en/main/route/links

Do not skip this lookup if you're guessing — frameworks change their icon conventions.

## Step 5: Determine the output directory

Based on the confirmed framework:

| Framework                     | Output directory   |
| ----------------------------- | ------------------ |
| Next.js, Vite, CRA, Vue, Astro, Nuxt, Remix, Rails | `public/`          |
| Gatsby, SvelteKit, Hugo       | `static/`          |
| Angular                       | `src/assets/`      |
| Jekyll, plain static          | repo root          |

**Override:** if existing favicon files (`favicon.ico`, `apple-touch-icon.png`, `site.webmanifest`) already exist somewhere in the repo, use that location instead — the project has already chosen.

For Next.js App Router specifically, the file-based convention puts `icon.png` / `apple-icon.png` / `favicon.ico` directly in the `app/` directory (alongside `layout.tsx`). If the user confirms App Router and there's no `public/` preference, prefer that convention — the docs you fetched will confirm.

Create the directory if it doesn't exist. Report the chosen directory.

## Step 6: Determine the app name and background color

**App name** — use the first available source:

1. Existing `site.webmanifest` `name` field (if present in the chosen output directory).
2. `package.json` `name` field at the repo root.
3. Current working directory name.

Convert kebab-case or snake_case to Title Case (e.g., `my-app` → `My App`).

**Background color** — needed for the opaque apple-touch-icon and maskable icon. Use the first that applies:

1. Existing `site.webmanifest` `background_color`, if present.
2. `#ffffff` (white) as the default.

Mention the chosen color in the final summary so the user can re-run with a different one if it clashes with their brand.

## Step 7: Generate favicon files

This is the modern minimal set (per evilmartians' "How to Favicon in 2021/2025" and web.dev maskable icon guidance). Skip the legacy 16/32/48 separate PNGs — the multi-res `.ico` and SVG cover those cases.

Two best-practice rules baked into the commands below:

1. **`apple-touch-icon.png` must be opaque.** iOS renders any transparent pixels as black. Flatten alpha against a solid background (white by default — if the user has a brand background color, use that instead).
2. **The maskable icon needs a safe zone.** Content must fit within the inner ~80% (≈410×410 of 512×512). Outer 10% may be cropped by Android. Scale the source down and pad on an opaque background.

Substitute `$SRC` (source image), `$OUT` (output directory), and `$BG` (background hex, default `white`). Run in parallel:

```bash
# Multi-res ICO (16/32/48) — covers tab bar + legacy
magick "$SRC" \
  \( -clone 0 -resize 16x16 \) \
  \( -clone 0 -resize 32x32 \) \
  \( -clone 0 -resize 48x48 \) \
  -delete 0 -alpha on -background none \
  "$OUT/favicon.ico"

# Apple touch icon — opaque, slight inset (140 within 180)
magick "$SRC" -resize 140x140 -background "$BG" -alpha remove -alpha off \
  -gravity center -extent 180x180 "$OUT/apple-touch-icon.png"

# PWA "any" icons — transparency OK
magick "$SRC" -resize 192x192 -background none -alpha on "$OUT/web-app-manifest-192x192.png"
magick "$SRC" -resize 512x512 -background none -alpha on "$OUT/web-app-manifest-512x512.png"

# PWA maskable — opaque, safe-zone padded (410 within 512)
magick "$SRC" -resize 410x410 -background "$BG" -alpha remove -alpha off \
  -gravity center -extent 512x512 "$OUT/web-app-manifest-maskable-512x512.png"
```

If the source is an SVG, also copy it as `favicon.svg` (modern browsers prefer it; it scales perfectly and can support dark mode via embedded `<style>@media (prefers-color-scheme: dark) { … }</style>`):

```bash
cp "$SRC" "$OUT/favicon.svg"
```

For Next.js App Router using the file-based convention, additionally place these in `app/` (or `src/app/`):

- `favicon.ico` (copy from above)
- `icon.png` (use the 192×192 PNG)
- `apple-icon.png` (use the 180×180 PNG)

Next.js auto-emits the correct `<link>` tags from these filenames.

If any `magick` command fails, report the exact error and stop.

## Step 8: Create or update `site.webmanifest`

Skip this step for Next.js App Router — use the `manifest` export in `app/manifest.ts` instead (see Step 9).

Otherwise, write `$OUT/site.webmanifest`. Note the modern recommendation: provide separate `any` and `maskable` icon entries rather than overloading a single icon with `purpose: "any maskable"` — a maskable icon has padding that looks bad when used as a regular app icon.

```json
{
  "name": "[APP_NAME]",
  "short_name": "[APP_NAME]",
  "icons": [
    {
      "src": "/web-app-manifest-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/web-app-manifest-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/web-app-manifest-maskable-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

If `site.webmanifest` already exists, preserve its existing `theme_color`, `background_color`, and `display` values; only overwrite `name`, `short_name`, and `icons`.

## Step 9: Wire icons into the framework

Use the mechanism appropriate to the confirmed framework. If you're unsure of the current best practice, re-check the docs you fetched in Step 4 before editing.

**Next.js App Router (file-based, preferred):** Files in `app/` (Step 7) auto-register. For the manifest, create `app/manifest.ts` exporting a `MetadataRoute.Manifest` object instead of writing `site.webmanifest`.

**Next.js (Metadata API fallback):** Edit the root `layout.tsx`'s `metadata` export to include `icons` and `manifest` fields. Merge with existing fields.

**Rails:** Edit `app/views/layouts/application.html.erb`. Remove existing favicon/icon/manifest `<link>` tags from `<head>` and insert the snippet below.

**Static HTML / Jekyll / Eleventy / anything that ships an HTML file:** Edit the head of the relevant template (`index.html`, `_layouts/default.html`, etc.) using the snippet below.

**SvelteKit:** Edit `src/app.html`'s `<head>` with the snippet below.

**Astro:** Edit the layout component (often `src/layouts/Layout.astro`) `<head>` with the snippet below.

**Vue/Vite/CRA:** Edit `index.html` in the project root with the snippet below.

**Anything else:** Use the snippet below in whatever file owns the `<head>`. If unclear, ask the user which template file owns the document head.

### HTML snippet

The modern minimal set — four `<link>` tags plus `theme-color` and the iOS app title. Anything beyond this (legacy `shortcut icon`, separate 16/32 PNGs, msapplication-* tags) is no longer recommended; the SVG and ICO together cover every browser worth supporting.

```html
<link rel="icon" href="/favicon.ico" sizes="32x32" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="apple-mobile-web-app-title" content="[APP_NAME]" />
<meta name="theme-color" content="#ffffff" />
```

- Omit the `<link rel="icon" type="image/svg+xml" ...>` line if the source was not an SVG.
- Adjust `href` paths if the output directory isn't served from the web root (e.g., Angular's `src/assets/` → `/assets/favicon.ico`).
- Remove any pre-existing favicon-related `<link>` tags before inserting these to avoid duplicates (including legacy ones — old `shortcut icon`, multiple sized PNG icons, `msapplication-*` meta tags).

## Step 10: Summary

Report concisely:

- Detected and confirmed framework
- Output directory used
- Files generated (and which were overwritten)
- File(s) edited to register icons (or confirm Next.js auto-registration)
- App name used in the manifest
