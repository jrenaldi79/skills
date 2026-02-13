# Progressive Fidelity Rendering Pipeline

Design outputs move through three fidelity levels, mirroring how a real design studio works. Each level serves a different purpose and uses different tools.

**Default progression:** L1 → L2 → L3
You may skip L2 only if it does not serve the user's stated goal, and only after explicitly stating the rationale and obtaining user confirmation.

---

## Level 1: Low Fidelity — Structural Sketches (SVG / HTML Files)

**Purpose:** Rapidly explore form, proportion, layout, and functional arrangement.
**Tools:** React + Tailwind + shadcn/ui (via `scripts/init-artifact.sh` → `scripts/bundle-artifact.sh`). Inline SVG for technical drawings inside React components.
**Style:** Clean line drawings using the Modern Product Studio SVG conventions (see `design-system.md`). Dark strokes on light background. Annotation callouts for dimensions, features, materials. Orthographic views (front, top, side) where needed.
**When:** Phase 3 (Ideation) and early Phase 4 (Refinement).
**Action:** Scaffold with `init-artifact.sh`, develop in React with inline SVG, bundle to `./artifacts/P3-SKETCH-XX.html`.
**Console output:** "Created sketch at `artifacts/P3-SKETCH-01.html`. Open this file in your browser to view."

---

## Base64 Data URI Requirement

All images in HTML artifacts MUST use base64 data URIs, not file paths. The Cowork artifact viewer cannot resolve local filesystem paths. See `image-factory.md` Stage 2b for encoding local files.

---

## Level 2: Medium Fidelity — Inspiration Renders (Image Generation API)

**Purpose:** Visualize materials, color, finish, lighting, and emotional tone. These are directional — not engineering-precise.
**Tools:** `scripts/generate-render.py` (requires `GOOGLE_API_KEY` — see `capability-check.md` #8).

### Two-Stage Master-Conditioned Workflow

**Why this matters:** Without image conditioning, independent prompts produce visually different devices — different proportions, surface details, feature placement. The render set becomes unusable for stakeholder communication. The master render establishes visual identity; all variations are conditioned on it.

#### Stage 1 — Master Render (Hard Gate)

1. Write a DTS for the master render
2. Construct a detailed prompt covering: form, dimensions, materials, hex colors, camera angle, lighting, exclusions
3. Generate:
   ```bash
   python3 scripts/generate-render.py --mode master \
     --prompt "..." \
     --output ./artifacts/images/P4-IMG-RENDER-MASTER.png
   ```
4. Verify the master against the DTS
5. **STOP** — present the master render to the user for approval. This establishes the visual identity for all subsequent variations. Do not proceed until approved.

#### Stage 2 — Conditioned Variations

1. Write a DTS for each variation
2. Variation prompts start with "Using this EXACT same device design..."
3. Generate each variation using the approved master as reference:
   ```bash
   python3 scripts/generate-render.py --mode variation \
     --reference ./artifacts/images/P4-IMG-RENDER-MASTER.png \
     --prompt "Using this EXACT same device design, ..." \
     --output ./artifacts/images/P4-IMG-RENDER-XX.png
   ```
4. Typical variation set: hero shot, usage context, material detail, lifestyle
5. Wait 2 seconds between API calls (rate limiting)
6. Embed renders in `P4-RENDER-01.html` using the `.b64.txt` companion files written by the script
7. Register all renders in `artifact-index.md`

### Fallback — When Image Generation API Unavailable

**Prompt packages:** Produce the master prompt and variation prompts as a deliverable for the user to run externally. Include instructions for using `generate-render.py` once they have a `GOOGLE_API_KEY`.

**Canvas-design skill alternative:** The `/example-skills:canvas-design` skill (invoked via the Skill tool) can produce high-fidelity `.png` or `.pdf` visual artifacts that communicate material feel, color story, and emotional tone. This is particularly effective for mood boards (`P4-MOOD-01`) and material boards (`P4-MATBOARD-01`). To use it:
1. Invoke the skill via the Skill tool
2. Provide the chosen concept, material palette, and aesthetic direction as the input
3. The skill creates a design philosophy, then expresses it as a polished visual artifact
4. Save the output to `./artifacts/` and register in `artifact-index.md`

Note: Canvas-design outputs are abstract and compositional — they convey *feeling*, not engineering geometry. They complement but do not replace L1 structural sketches or L3 CAD documentation.

---

## Level 3: High Fidelity — CAD-Ready Specification (Blender / Fusion 360)

**Purpose:** Provide engineering-grade documentation sufficient for prototyping and manufacturing.

**Tools:**
- Primary: Blender MCP or Fusion 360 MCP (only if confirmed available via capability check)
- Fallback: dimensioned technical drawings (SVG/HTML) + parameter files

**Action (if CAD MCP available):**
- Generate model/mesh according to the parameter file
- Render orthographic and perspective views to `./artifacts/images/`

**Action (if CAD MCP NOT available):**
- Generate high-precision drawings with tolerances and GD&T callouts where appropriate
- Provide a CAD operator handoff pack: drawings + parameter file + manufacturing notes

---

# Design Verification Framework (The "Vision" Loop)

Every visual output — at any fidelity level — must be verified against a Design Test Spec (DTS) before being presented to the user.

## How It Works

```
1. DEFINE   → Write the DTS
2. GENERATE → Produce the visual output
3. INGEST   → Read file / (if possible) attach image to context
4. EVALUATE → Score output against DTS
5. DECIDE   → Pass or regenerate (or ask user for confirmation if vision unavailable)
```

## DTS Format

Before generating any visual artifact, write a DTS. The DTS is an internal working document — show it to the user only if they ask.

```
DTS: [Artifact Name]
Fidelity Level: [L1 / L2 / L3]
Intent: [What this visual is meant to communicate]

MUST HAVE (fail if missing):
- [ ] ...
SHOULD HAVE (note if missing):
- [ ] ...
MUST NOT HAVE (fail if present):
- [ ] ...
```

## Evaluation Rules by Fidelity

- **L1 (SVG/HTML):** Self-evaluate by inspecting your own code and checking all criteria.
- **L2/L3 (Images/Renders):**
  - If vision inspection available: ingest and evaluate directly.
  - If vision inspection NOT available: evaluate prompt/config + file properties; then request user confirmation for visual DTS checks that require human viewing.

## Verification Log

Maintain a verification log as part of `artifact-index.md`. Record the DTS result (PASS/FAIL) for every visual artifact.
