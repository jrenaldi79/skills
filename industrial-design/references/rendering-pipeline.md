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

### Prompt Engineering for Dimensional Accuracy

Image models cannot interpret absolute dimensions (e.g., "12mm tall") with precision. To get correct proportions:

1. **State the aspect ratio explicitly** — "aspect ratio 4.6:3.2:1 (length:width:thickness)"
2. **Use real-world comparisons** — "as thin as an AirTag," "thickness of a pencil," "slim like a Tile Mate tracker"
3. **Emphasize the critical dimension** — if thickness is the hardest to get right, repeat it multiple times and say "this is the MOST IMPORTANT dimension"
4. **State what it must NOT look like** — "must NOT look like a thick dome, egg, or tall pebble"
5. **Request a camera angle that reveals the critical dimension** — for thin devices, request "slightly above eye level so the thinness of the profile is clearly visible"

Even with these techniques, the DTS evaluation step is essential — always verify the output visually against the P3 sketch before presenting to the user.

---

## Level 3: High Fidelity — CAD-Ready Specification (Blender / Fusion 360)

**Purpose:** Provide engineering-grade documentation sufficient for prototyping and manufacturing.

**Tools:**
- Primary: Blender MCP or Fusion 360 MCP (only if confirmed available via capability check)
- Fallback: dimensioned technical drawings (SVG/HTML) + parameter files

### CAD MCP Workflow (Blender or Fusion 360)

**Before starting:** Read `references/cad-build-protocol.md` for spec-driven build discipline, reference image QA, and post-modification verification procedures.

1. Write DTS for the CAD model (REQUIRED — see required L3 criteria below)
2. Read `design-parameters.yaml` and `materials-and-finishes.yaml` as the parametric source of truth
3. Generate model/mesh according to the parameter file
4. **Parametric verification** — query the model to check DTS criteria:
   - Bounding box dimensions (compare against envelope in `design-parameters.yaml`)
   - Wall thicknesses at critical sections
   - Feature positions and sizes
5. Render orthographic and perspective views to `./artifacts/images/`
6. **Visual verification** — ingest rendered views, cross-reference against P4-DIMSKETCH-01 and P3 sketches
7. If DTS FAIL → modify model, re-verify
8. If DTS PASS → proceed to technical drawings and hero render
9. Log DTS result in `artifact-index.md`

### Fallback Workflow (No CAD MCP)

1. Write DTS for the technical drawing (REQUIRED — see required L3 criteria below)
2. Generate high-precision dimensioned drawings (SVG/HTML) with tolerances and GD&T callouts where appropriate
3. **Self-evaluate** — verify every dimension in the drawing matches `design-parameters.yaml`
4. Include section views showing internal features (wall thickness, ribs, bosses)
5. Provide a CAD operator handoff pack: drawings + parameter file + manufacturing notes
6. If DTS FAIL → correct drawings, re-verify
7. Log DTS result in `artifact-index.md`

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

### Required DTS Criteria for L2 Renders

Every L2 render DTS MUST include these checks, derived from existing design artifacts. Do not generate renders without writing these first.

```
MUST HAVE — Dimensional Consistency:
- [ ] Overall proportions visually match the aspect ratio from P3 sketch
      (Reference: P3-SKETCH-XX side profile view and comparison table)
- [ ] Device thickness/height reads as [X]mm relative to length and width
      (Reference: design-parameters.yaml → envelope.height, or P3 dimensions)
- [ ] Form factor matches the selected concept (capsule vs. disc vs. T-form)
      (Reference: P3 concept description and top/side views)

MUST HAVE — Design Language Consistency:
- [ ] Color palette matches P4-DESIGNLANG-01 hex values
- [ ] Material finish matches spec (matte/gloss/textured)
- [ ] Key features present (LED window, gasket line, etc.)

MUST NOT HAVE:
- [ ] Text, labels, or branding on the device (unless specified)
- [ ] Features not in the P3 sketch (buttons, ports, screens, etc.)
- [ ] Proportions that contradict the side-profile sketch
```

### Required DTS Criteria for L3 CAD Outputs

Every L3 DTS MUST include these checks. L3 is engineering-grade — verification is parametric (query the model or inspect the drawing), not just visual.

```
MUST HAVE — Dimensional Accuracy:
- [ ] Bounding box matches design-parameters.yaml envelope dimensions
      within general tolerance (ISO 2768-mK unless overridden)
- [ ] All critical-to-function dimensions have explicit tolerances
      (Reference: design-parameters.yaml + engineering-standards.md §3–4)
- [ ] Wall thicknesses meet minimum for manufacturing process
      (Reference: materials-and-finishes.yaml → process constraints)
- [ ] Draft angles present on all molded/cast surfaces (typically ≥1°)
- [ ] Fillet/chamfer radii match design-parameters.yaml

MUST HAVE — Feature Completeness:
- [ ] All features from P4-DIMSKETCH-01 are present (holes, bosses,
      ribs, snap-fits, gasket grooves, windows, etc.)
- [ ] Assembly interfaces match mating part dimensions
- [ ] Datum references defined per engineering-standards.md §4
- [ ] GD&T applied to critical-to-function features (sealing faces,
      hole patterns, mating surfaces)

MUST HAVE — Model/Drawing Quality:
- [ ] No self-intersecting or non-manifold geometry (CAD MCP path)
- [ ] Section views show internal features: wall thickness, ribs,
      bosses, internal channels (drawing path)
- [ ] Materials and finishes called out per materials-and-finishes.yaml
- [ ] All dimensions labeled per spec integrity policy
      (Verified/User Requirement/Proposed Target)

MUST NOT HAVE:
- [ ] Dimensions that contradict design-parameters.yaml
- [ ] Unlabeled or untoleranced critical dimensions
- [ ] Features not in the approved design (P3 sketch + P4 refinement)
- [ ] Missing section views for enclosed/internal geometry
```

## Evaluation Rules by Fidelity

- **L1 (SVG/HTML):** Self-evaluate by inspecting your own code and checking all criteria.

- **L2 (Rendered Images):**
  1. **Ingest** the generated image (Read tool or vision inspection)
  2. **Cross-reference** against these existing artifacts:
     - P3 sketch side profile → Does the thickness/height look correct?
     - P3 sketch top view → Does the plan-view shape match?
     - design-parameters.yaml → Are key dimensions plausible?
     - P4-DESIGNLANG-01 → Do colors, materials, and tone match?
  3. **Score** each DTS criterion as PASS or FAIL
  4. If ANY "MUST HAVE" fails → regenerate with a corrected prompt before presenting to user
  5. If vision inspection is NOT available → explicitly flag which DTS criteria require user visual confirmation and ask before proceeding

- **L3 (CAD Models / Technical Drawings):**
  1. **Parametric check** (CAD MCP path): query the model for bounding box,
     wall thicknesses, feature dimensions. Compare against `design-parameters.yaml`.
  2. **Drawing check** (fallback path): inspect every annotated dimension
     in the SVG/HTML against `design-parameters.yaml`. Verify tolerances
     and GD&T callouts against `engineering-standards.md`.
  3. **Visual check**: ingest rendered orthographic views or the drawing itself.
     Cross-reference against P4-DIMSKETCH-01 for feature placement and proportions.
  4. **Score** each DTS criterion as PASS or FAIL
  5. If ANY "MUST HAVE" fails → modify model/drawing and re-verify
  6. Present to user only after DTS PASS

## Verification Log

Maintain a verification log as part of `artifact-index.md`. Record the DTS result (PASS/FAIL) for every visual artifact.
