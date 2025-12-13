---
name: life360-brand
description: Official brand guidelines for Life360, including color palettes, typography, logo assets, UI layout principles, and photography style. Use this skill when designing emails, creating web content, or ensuring brand compliance for Life360 materials.
---

# Life360 Brand Guide

This skill provides the official brand guidelines for Life360, tailored for digital communication and design.

## Brand Identity

**Company Name:** Life360
**Mission:** Bringing families closer.

## Core Guidelines

### Logo Assets
**Primary Logo:** Horizontal Wordmark ("Life360" text + Loop Icon).
-   **Visual:** Purple (#8652FF) on White/Light Background is the standard for documents and UI.
-   **File Handling:** Always use verified transparent PNGs or SVGs. Do not use white-matted JPGs on gray backgrounds.
-   **App Icon:** The purple square tile is for *app Context only*. Do not use as a corporate logo header.

### UI & Layout
For layout principles including the "Card" aesthetic, rounding, and shadows, see [references/ui-layout.md](references/ui-layout.md).

### Imagery
For photography style, do's/don'ts, and "human connection" guidelines, see [references/imagery.md](references/imagery.md).

### Colors
See [references/colors.md](references/colors.md).

### Typography
See [references/typography.md](references/typography.md).

## Usage Checklist

1.  **Is the logo transparent?** (No white box on gray backgrounds).
2.  **Is the background #F6F5F8?** (Light gray canvas for contrast).
3.  **Is the content in a Card?** (White, rounded 16px, soft shadow).
4.  **Is the imagery authentic?** (Lifestyle photos preferred over gradients).

## Automation Tools

### Document Branding
Apply official Life360 fonts, colors, and logos to any .docx file automatically.

**Usage:**
```bash
python3 /Users/john_renaldi/skills/life360-brand/scripts/apply_brand_docx.py \
  /path/to/input.docx \
  /path/to/output.docx
```

### Developer Resources
-   **Configuration:** `config.json` contains machine-readable hex codes and font names.
-   **Visual Assets:** `assets/logo.txt` contains the verified Base64 string for the primary logo.
