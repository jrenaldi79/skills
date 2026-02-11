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

When tools are available, execute research in this order:
1. **Broad discovery** — search for competitors, materials, standards
2. **Deep extraction** — pull specs, material data, standard details from discovered pages
3. **Image collection** — download and register reference images
4. **Synthesis** — compile findings into the required artifacts

---

## IP / Patent / Design Registration Disclaimer

If you research patents or design registrations:
- Provide citations/links and summarize cautiously
- State clearly: **"This is not legal advice and not a freedom-to-operate (FTO) determination."**
- Recommend consulting qualified IP counsel for FTO decisions

---

## Reference Image Management

Throughout research, save valuable images (competitor photos, material samples, environment shots, inspiration) as artifacts.

**How to save reference images:**
1. Identify the image URL from research results
2. Download using bash tools: `curl -L -o ./artifacts/images/P2-IMG-COMP-01.jpg "https://..."`
3. Register as an artifact with a descriptive ID and metadata in `artifact-index.md`
4. Reference by artifact ID in all subsequent work

**Inspection rules:**
- If vision inspection is available: ingest/analyze the image and extract useful details (materials, joins, part lines, ergonomics cues)
- If vision inspection is NOT available: verify file properties (type, resolution, file size) and ask the user to confirm key visual details needed for DTS checks

**Image naming convention:**
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