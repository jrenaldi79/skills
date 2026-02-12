# Design System — Modern Product Studio

Every HTML artifact produced by this skill MUST use this design system. Copy the CSS and HTML boilerplate below into each artifact's `<style>` and `<body>` blocks. Do not improvise styling — use these tokens and components verbatim.

---

## Fonts

System font stacks only. No Google Fonts or external `<link>` tags (blocked by Cowork CSP).

```css
/* Primary — body text, headings, labels */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;

/* Monospace — metadata, dimensions, code, artifact IDs */
font-family: "SF Mono", SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
```

---

## Color Palette

```css
/* Backgrounds */
--bg-page:       #f8f7f5;   /* page background behind the sheet */
--bg-sheet:      #faf9f7;   /* main content sheet */
--bg-card:       #ffffff;   /* cards, elevated content */
--bg-subtle:     #f0ece6;   /* subtle fills, tag backgrounds, table header bg */

/* Text */
--text-primary:  #2c2420;   /* headings, primary content */
--text-body:     #5a4a3a;   /* body text, table cells */
--text-muted:    #8a7a6a;   /* subtitles, secondary info */
--text-faint:    #b0a090;   /* view labels, section headers, timestamps */

/* Borders */
--border-strong: #d5cec4;   /* card borders, table rules */
--border-subtle: #e8e2da;   /* inner dividers, table row borders */
--border-faint:  #f0ece6;   /* lightest dividers */

/* Accent — annotations, callouts, design notes */
--accent:        #c17840;   /* annotation text */
--accent-border: #e8a060;   /* annotation left-border */
--accent-bg:     #fdf5ee;   /* annotation background (optional) */

/* Status */
--status-pass-text: #4a8c5c;
--status-pass-bg:   #eef5f0;
--status-fail-text: #b84830;
--status-fail-bg:   #fdf0ed;
--status-tbd-text:  #8a7a6a;
--status-tbd-bg:    #f0ece6;

/* Tags */
--tag-text:      #8a7a6a;
--tag-bg:        #f0ece6;

/* SVG drawing strokes (for L1 sketches) */
--stroke-primary:    #2c2420;  /* outlines, visible edges */
--stroke-hidden:     #a89888;  /* hidden lines (dashed) */
--stroke-center:     #b0a090;  /* center lines (dash-dot) */
--stroke-dimension:  #2c2420;  /* dimension lines + text */
--stroke-annotation: #c17840;  /* annotation leader lines + text */
--fill-light:        #f0ece6;  /* light fill for device bodies */
--fill-accent:       #dde8d8;  /* accent fill (transducer windows, etc.) */
```

---

## Type Scale

| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `heading-1` | 18px | 600 | Page title |
| `heading-2` | 14px | 600 | Section title, card title |
| `heading-3` | 12px | 600 | Sub-section, card heading |
| `subtitle` | 12px | 400 | Subtitle under page title |
| `body` | 11px | 400 | Body text, table cells, card content |
| `label` | 10px | 500 | View labels, section headers (uppercase, letter-spacing: 1.5px) |
| `meta` | 10px | 400 | Metadata block (monospace) |
| `small` | 9px | 400 | Table headers (uppercase, letter-spacing: 1px), tags |
| `annotation` | 10px | 400 | Annotation callouts (accent color) |

---

## Spacing

| Token | Value | Use |
|-------|-------|-----|
| `space-xs` | 4px | Tight inner padding |
| `space-sm` | 8px | Tag padding, compact gaps |
| `space-md` | 16px | Card padding, standard gaps |
| `space-lg` | 24px | Section gaps |
| `space-xl` | 32px | Sheet padding, major section breaks |
| `space-2xl` | 40px | Between view panels |
| `radius-sm` | 4px | Tags, status badges |
| `radius-md` | 8px | Cards |
| `radius-lg` | 12px | Sheet container |

---

## HTML Boilerplate

Every HTML artifact starts from this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[ARTIFACT-ID] — [Product Name]</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #f8f7f5;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #5a4a3a;
    padding: 32px;
    line-height: 1.6;
  }
  .sheet {
    max-width: 1200px;
    margin: 0 auto;
    background: #faf9f7;
    border: 1px solid #d5cec4;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.04);
  }

  /* ----- Title Block ----- */
  .title-block {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e8e2da;
  }
  .title-block h1 {
    font-size: 18px;
    font-weight: 600;
    color: #2c2420;
    letter-spacing: -0.3px;
  }
  .title-block .subtitle {
    font-size: 12px;
    color: #8a7a6a;
    margin-top: 3px;
  }
  .title-block .meta {
    text-align: right;
    font-size: 10px;
    color: #b0a090;
    line-height: 1.7;
    font-family: "SF Mono", SFMono-Regular, Consolas, monospace;
  }

  /* ----- Section Labels ----- */
  .section-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #b0a090;
    font-weight: 500;
    margin-bottom: 8px;
  }

  /* ----- Tables ----- */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    margin: 12px 0;
  }
  th {
    text-align: left;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #b0a090;
    font-weight: 500;
    border-bottom: 1px solid #e8e2da;
    padding: 6px 10px;
  }
  td {
    padding: 7px 10px;
    border-bottom: 1px solid #f0ece6;
    color: #5a4a3a;
  }

  /* ----- Cards ----- */
  .card {
    background: #ffffff;
    border: 1px solid #e8e2da;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  }
  .card h3 {
    font-size: 13px;
    font-weight: 600;
    color: #2c2420;
    margin-bottom: 6px;
  }
  .card p {
    font-size: 11px;
    color: #6b5b4e;
    line-height: 1.6;
  }

  /* ----- Annotations ----- */
  .anno {
    font-size: 10px;
    color: #c17840;
    margin: 8px 0;
    padding-left: 12px;
    border-left: 2px solid #e8a060;
  }

  /* ----- Status Badges ----- */
  .status-pass {
    display: inline-block;
    font-size: 9px;
    color: #4a8c5c;
    background: #eef5f0;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .status-fail {
    display: inline-block;
    font-size: 9px;
    color: #b84830;
    background: #fdf0ed;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .status-tbd {
    display: inline-block;
    font-size: 9px;
    color: #8a7a6a;
    background: #f0ece6;
    padding: 2px 8px;
    border-radius: 10px;
  }

  /* ----- Tags ----- */
  .tag {
    display: inline-block;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 3px 8px;
    background: #f0ece6;
    color: #8a7a6a;
    border-radius: 10px;
    margin-right: 4px;
  }

  /* ----- Grid Layouts ----- */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

  /* ----- Section Divider ----- */
  .divider {
    border: none;
    border-top: 1px solid #e8e2da;
    margin: 32px 0;
  }

  /* ----- Image Cards (for visual reference boards) ----- */
  .img-card {
    background: #ffffff;
    border: 1px solid #e8e2da;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  }
  .img-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
  }
  .img-card .img-body {
    padding: 12px 14px;
  }
  .img-card .img-body h4 {
    font-size: 12px;
    font-weight: 600;
    color: #2c2420;
    margin-bottom: 4px;
  }
  .img-card .img-body p {
    font-size: 10px;
    color: #8a7a6a;
    line-height: 1.5;
  }
  .img-card .img-source {
    font-size: 9px;
    color: #b0a090;
    padding: 0 14px 10px;
  }
  .img-card .img-source a {
    color: #c17840;
    text-decoration: none;
  }

  /* ----- Notes Grid (bottom of sheet) ----- */
  .notes-grid h3 {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #b0a090;
    margin-bottom: 8px;
    font-weight: 500;
  }
  .notes-grid ul {
    list-style: none;
    font-size: 11px;
    line-height: 1.9;
    color: #6b5b4e;
  }
  .notes-grid ul li::before {
    content: "\2014\0020";
    color: #d5cec4;
  }

  /* ----- SVG Overrides (for L1 sketches) ----- */
  svg text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
</style>
</head>
<body>
<div class="sheet">

  <div class="title-block">
    <div>
      <h1>[Product Name]</h1>
      <div class="subtitle">[One-line description]</div>
    </div>
    <div class="meta">
      [ARTIFACT-ID] &middot; [Fidelity Level]<br>
      [Additional metadata]<br>
      Rev [X]
    </div>
  </div>

  <!-- Content goes here -->

</div>
</body>
</html>
```

---

## Component Reference

### Title Block
Every artifact starts with a `.title-block` containing the product name, subtitle, and metadata (artifact ID, fidelity level, revision).

### Cards (`.card`)
Use for competitor analysis entries, material comparisons, concept descriptions. White background, subtle border, rounded corners.

### Image Cards (`.img-card`)
Use for visual reference boards. Image at top (200px height, object-fit: cover), text body below, source link at bottom.

### Tables
Use for parameter lists, spec comparisons, artifact indexes. Uppercase headers, subtle row borders.

### Annotations (`.anno`)
Use for design notes, caveats, verification warnings. Amber left border, warm accent text.

### Status Badges
- `.status-pass` — green, for verified/proposed values
- `.status-fail` — red, for TBD/failed items
- `.status-tbd` — neutral, for undecided items

### Tags (`.tag`)
Use for category labels, product classifications. Pill-shaped, subtle background.

### Grids
- `.grid-2` — two-column layout (sketch views, side-by-side comparisons)
- `.grid-3` — three-column layout (notes grids, material comparisons)
- `.grid-4` — four-column layout (image reference boards)

### Section Dividers
Use `<hr class="divider">` between major sections.

### Section Labels
Use `<div class="section-label">` for uppercase section headers above content blocks.

---

## SVG Sketch Styling

For L1 structural sketches, use these SVG style conventions:

| Element | Stroke Color | Width | Style |
|---------|-------------|-------|-------|
| Visible outlines | `#2c2420` | 1.5px | solid |
| Detail lines | `#2c2420` | 0.75px | solid |
| Hidden lines | `#a89888` | 0.5px | `stroke-dasharray: 4,3` |
| Center lines | `#b0a090` | 0.4px | `stroke-dasharray: 8,3,2,3` |
| Dimension lines | `#2c2420` | 0.5px | solid, with arrowhead polygons |
| Dimension text | `#2c2420` | — | 9px, system sans-serif |
| Annotation lines | `#c17840` | 0.6px | solid, with 1px dot at origin |
| Annotation text | `#c17840` | — | 8.5px, system sans-serif |
| Light fill | `#f0ece6` | — | device bodies, shells |
| Accent fill | `#dde8d8` | — | transducer windows, special zones (opacity 0.4) |
| Skin/context fill | `#f5efe8` | — | body outlines in context views |
