# Spec Integrity & Engineering Standards

## 1. Dimensional / Materials / Spec Integrity Policy

Hardware specs are high-risk for accidental fabrication. These rules prevent presenting made-up numbers as facts.

### No Invented Facts
You must not present a dimension, mass, material grade, finish type, tolerance, or performance spec as "existing/verified" unless it is:
- **User-provided** — explicitly stated by the user
- **Cited** — source URL + retrieval date
- **Measured/derived** from a verifiable artifact you generated (e.g., your parameter file, your drawing geometry)

### Proposed vs. Verified Labeling
Every spec item in the design specification must be labeled as one of:
- **Verified (Source)** — includes citation
- **User Requirement** — directly from the brief
- **Proposed Target** — your design decision (not a claim about an existing product)

### Conflicting Sources
If research sources conflict:
- Record both values with sources
- Choose a working assumption
- Flag it as an open item to verify

### No Back-Calculating from Photos
Do not back-calculate "exact" competitor dimensions from photos unless you have a known scale reference and you clearly label the method and uncertainty. Prefer listings and datasheets.

---

## 2. Units

- **Linear dimensions:** millimeters (mm)
- **Angles:** degrees (deg)
- **Mass:** grams (g) or kilograms (kg) as appropriate
- **Surface roughness:** Ra in um (or uin if user requests imperial)

If you present imperial units, also provide metric and state whether values are converted/rounded.

---

## 3. Tolerancing Convention

- Default general tolerances: **ISO 2768-mK** (unless user specifies another standard)
- All critical-to-function dimensions must override the general tolerance with explicit tolerances (+/-) and/or GD&T

---

## 4. Datum and GD&T Guidance

When applicable:
- Define primary/secondary/tertiary datums for assemblies or critical features
- Apply GD&T only where it improves manufacturability or inspection clarity (e.g., flatness on sealing faces, position on hole patterns)
- If unsure, propose a conservative baseline and flag as "to confirm with manufacturing partner"

---

## 5. Rounding Rule

- Dimension rounding must be consistent (e.g., 0.1 mm resolution for plastics, 0.01 mm where machining requires)
- Never mix resolutions without justification