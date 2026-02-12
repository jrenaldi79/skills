# Research Workstreams (Phase 2)

You are the lead designer. Delegate research to these structured workstreams, which may run sequentially or in parallel depending on harness constraints.

## Competitive Intelligence Workstream

**Mission:** Build a comprehensive picture of the existing product landscape.
**Preferred tools (if available):** `tavily_search`, `tavily_extract`, `tavily_crawl`

**Tasks:**
- Search for each competitor product listed in the brief (and discover unlisted competitors)
- Extract product specs: dimensions, materials, weight, price, key features
- Identify customer reviews highlighting pain points and praise
- Look for patents or design registrations that may influence the design space (see IP disclaimer below)
- Find product images and save them as reference artifacts (see Image Management section)

**Output artifact:** `P2-COMP-01.md` (Competitive Landscape Board)

---

## Material & Manufacturing Research Workstream

**Mission:** Gather current data on candidate materials, finishes, and manufacturing processes.
**Preferred tools (if available):** `tavily_search`, `tavily_extract`, `tavily_research`

**Tasks:**
- Gather relevant material properties (density, hardness, corrosion resistance, temperature limits, impact strength where relevant)
- Gather finish options (anodizing types, coatings, surface treatments) with durability notes
- Gather supplier pricing signals and availability for candidate materials when possible
- Capture manufacturability constraints per process (minimum wall thickness, draft angles, achievable tolerances, surface finish norms)

**Output artifacts:** `P2-MATINNO-01.md` (Material Innovation Notes), feeds into `P4-MATBOARD-01`

---

## Standards & Compliance Workstream

**Mission:** Identify applicable standards and regulatory requirements for the mechanical product and its materials/chemicals, as relevant to the target markets.
**Preferred tools:** `tavily_search`, `tavily_extract`

**Tasks:**
- Identify relevant ISO/ASTM/EN standards for the product category (mechanical safety, performance, labeling if applicable)
- Identify chemical/material regulations (e.g., REACH, Proposition 65) where relevant
- Identify consumer safety frameworks (e.g., CPSIA) if it's a consumer product
- Avoid electronics-centric compliance unless the product includes electronics per the brief

**Output artifact:** `P2-STANDARDS-01.md` (Standards & Compliance Summary)

---

## Visual Reference Workstream

**Mission:** Collect visual references for aesthetic direction, usage context, and design inspiration.
**Preferred tools:** `tavily_search`, `tavily_extract`

**Tasks:**
- Gather competitor product photography
- Gather material/finish references (brushed aluminum, matte black anodize, overmold textures, etc.)
- Gather images of the target user in their work environment (context)
- Gather adjacent-category inspiration and industrial design trend references

**Output artifacts:** `P2-VISREF-01.html` (Visual Reference Collection), feeds into `P4-MOOD-01`

---

## Research Orchestration

**Delegation strategy:** Spawn each workstream as a parallel subagent via the Task tool.

Each subagent prompt should include:
1. The workstream section below (mission, tasks, output artifact name)
2. The product brief from Phase 1
3. Capability check results (which tools are available)
4. The **absolute** output file path (not relative — subagents may not share the lead agent's working directory)
5. Image embedding instructions from the Reference Image Management section

### Subagent Capability Constraints

Subagents spawned via the Task tool may have DIFFERENT capabilities than the
lead agent. In particular:

- **Bash/curl access:** Subagents may not be able to execute shell commands
  or make outbound HTTP requests. Do NOT instruct subagents to download files
  via curl.
- **Filesystem writes:** Subagents CAN typically write files to the output
  directory. Provide the ABSOLUTE path, not a relative one.
- **Web research tools:** Subagents DO have access to Tavily and similar
  research tools. Instruct them to use `include_images: true` in Tavily
  search calls to get image URLs.

When delegating to subagents, the lead agent should:
1. Pass the absolute output file path (not relative)
2. Instruct the subagent to collect image URLs and embed them as external `<img src>` placeholders
   (the lead agent will post-process these into base64 data URIs — see Image Embedding Strategy)
3. Verify the subagent's output after it completes (see Verification below)

**After all subagents complete:**
1. Read each output artifact
2. Cross-reference findings (e.g., do material choices align with standards?)
3. Identify gaps — spawn targeted follow-up searches if needed
4. Run **Visual Reference Post-Processing** (see below)
5. Register all artifacts in `artifact-index.md`

### Visual Reference Post-Processing (Required)

The subagent produces a draft HTML with external `<img src="https://...">` URLs.
The Cowork artifact viewer enforces a Content Security Policy (CSP) that **blocks
all external resource loading** — external `<img>` tags and Google Fonts `<link>`
tags render as blank. The only reliable image strategy is **base64 data URI embedding**.

**Two-stage build process:**

**Stage 1 (subagent):** Build the HTML structure with external image URLs as placeholders.
Collect the best image URLs from Tavily search results (use `include_images: true`).

**Stage 2 (lead agent post-processing):** After the subagent completes:
1. Read `P2-VISREF-01.html`
2. Extract all `<img src="https://...">` URLs
3. For each URL, fetch the image and convert to a base64 data URI:
   - Use `curl -sL [url] | base64` (or Python equivalent) to fetch and encode
   - Replace the `src` with `src="data:image/jpeg;base64,[encoded_data]"`
   - If a fetch fails, keep the source URL as a visible `<a>` link and remove the `<img>` tag
4. Verify the final HTML contains at least 5 `data:image` URIs
5. Search for "not available" or "no-image" — if found, the deliverable FAILS
6. If verification fails: rebuild using image URLs from Competitive Intelligence
   and Material Research outputs
7. Write the final post-processed file back to `P2-VISREF-01.html`

**Size guidance:** Base64 encoding adds ~33% overhead. Target images at 600-800px
wide (resize if needed with `sips` or ImageMagick) to keep the HTML file under 10MB.

---

## IP / Patent / Design Registration Disclaimer

If you research patents or design registrations:
- Provide citations/links and summarize cautiously
- State clearly: **"This is not legal advice and not a freedom-to-operate (FTO) determination."**
- Recommend consulting qualified IP counsel for FTO decisions

---

## Reference Image Management

### Image Embedding Strategy

The Cowork artifact viewer enforces a **Content Security Policy (CSP)** that blocks
all external resource loading. External `<img src="https://...">` tags and Google
Fonts `<link>` tags are silently blocked and render as blank. The only fully reliable
image strategy is **base64 data URI embedding**.

**Final delivery format:**
```html
<img src="data:image/jpeg;base64,/9j/4AAQ..." alt="[descriptive alt text]">
```

The image data lives inside the HTML file itself — no network request needed.

**How the two-stage build works:**

1. **Subagent stage:** Use Tavily search with `include_images: true` to find images.
   Build the HTML with external `<img src="https://...">` tags as placeholders.
2. **Lead agent post-processing:** Fetch each image URL, base64-encode it, and
   replace the `src` attribute with a `data:image/...;base64,...` URI. See the
   Visual Reference Post-Processing section for the full procedure.

**Image URL quality checks (for the subagent stage):**
- Prefer manufacturer/official press images (higher resolution, less likely to break)
- Avoid thumbnail URLs (< 200px) — look for full-size variants
- Avoid URLs with session tokens or temporary parameters (will expire)
- Verify URLs end in image extensions (.jpg, .png, .webp) or come from known CDNs

**Size management:**
- Target images at 600-800px wide (resize during post-processing if needed)
- Base64 adds ~33% size overhead — keep the final HTML under 10MB
- Prefer JPEG over PNG for photographic content (smaller encoded size)

### Image naming convention (for locally downloaded images, when curl IS available)
```
P[phase]-IMG-[category]-[sequence].[ext]

Categories:
  COMP    = Competitor product photo
  MAT     = Material/finish reference
  ENV     = Usage environment / context
  INSPO   = Design inspiration
  MOOD    = Mood board element
  RENDER  = Generated render output
```

---

## Visual Reference Board HTML Specification

The `P2-VISREF-01.html` file must be a self-contained, single-file HTML page with:

### Required Sections
1. **Direct Competitors** — Product photos + specs + design lessons
2. **Analogous Devices** — Best-in-class benchmarks from adjacent categories
3. **Academic/Emerging** — Research-stage references (if applicable)
4. **Material & Finish Direction** — Material palette with visual swatches
5. **Usage Environment** — Context for where/how the product is used
6. **Design Direction Synthesis** — Summary of aesthetic direction

### Per-Card Requirements
Each product/reference card must include:
- `<img>` tag with base64 data URI (after lead agent post-processing) and descriptive `alt` text
- Source URL as a visible `<a>` link below the image for reference
- Product name and company
- Key specs (dimensions, materials, form factor)
- "Design Lessons for [Product]" section

### Styling Requirements
- **Fully self-contained** — CSS in `<style>` block, NO external stylesheets, NO Google Fonts `<link>` tags
- **System font stacks only** — the Cowork CSP blocks external font loading. Use:
  - Sans-serif: `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;`
  - Monospace: `font-family: "SF Mono", SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;`
- Responsive grid layout
- Professional, clean typography
- Color-coded category tags for quick scanning
