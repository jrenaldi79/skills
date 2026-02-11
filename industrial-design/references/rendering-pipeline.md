# Progressive Fidelity Rendering Pipeline

Design outputs move through three fidelity levels, mirroring how a real design studio works. Each level serves a different purpose and uses different tools.

**Default progression:** L1 → L2 → L3
You may skip L2 only if it does not serve the user's stated goal, and only after explicitly stating the rationale and obtaining user confirmation.

---

## Level 1: Low Fidelity — Structural Sketches (SVG / HTML Files)

**Purpose:** Rapidly explore form, proportion, layout, and functional arrangement.
**Tools:** SVG diagrams, React/HTML artifacts, annotated wireframes.
**Style:** Clean line drawings. Dark strokes on light background. Annotation callouts for dimensions, features, materials. Orthographic views (front, top, side) where needed.
**When:** Phase 3 (Ideation) and early Phase 4 (Refinement).
**Action:** Write code to `./artifacts/P3-SKETCH-XX.html`.
**Console output:** "Created sketch at `artifacts/P3-SKETCH-01.html`. Open this file in your browser to view."

---

## Level 2: Medium Fidelity — Inspiration Renders (Image Generation LLM)

**Purpose:** Visualize materials, color, finish, lighting, and emotional tone. These are directional — not engineering-precise.
**Tools:** Image generation LLM if available in the harness.

**Action (if image-gen tool available):**
- Generate images and save to `./artifacts/images/`

**Action (if image-gen tool NOT available):**
- Produce a production-grade prompt package for the user to run externally
- Ask them to save results to `./artifacts/images/`

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