# Specification Templates

## Task-Specific Brief (Phase 1 Input)

Use this template to capture the project brief from the user. If fields are missing, ask the user to fill them in.

```
Product:            [What is the product?]
Target Customer:    [Who is the primary user?]
Key Requirements:   [List the must-have features and functions]
Budget:             [Target retail price range]
Material Preference:[Any preferred or required materials]
Size Constraints:   [Maximum dimensions, weight limits, etc.]
Production Volume:  [Expected annual units — needed for tooling amortization]
Distribution:       [DTC, retail, B2B — affects packaging and margin structure]
Competitive Refs:   [Any existing products to benchmark against or differentiate from]
Markets/Regions:    [US/EU/UK/CA/AU/etc. — affects compliance]
```

---

## Final Specification Format (Phase 6 Output — `P6-SPECSHEET-01.md`)

### Design Specification: [Product Name]

**1. Executive Summary**

**2. Design Rationale**
- Reference artifacts and decision log entries

**3. Key Features**

**4. Visual Specification**
- Reference verified visual artifacts (L1/L2/L3)

**5. Dimensional Specification**
- Pull from `design-parameters.yaml` and include:
  - Overall envelope dimensions (L x W x H)
  - Critical feature dimensions
  - Radii/fillets, chamfers
  - Draft angles (if molded)
  - Clearances/stack-ups (where relevant)
  - Tolerances and GD&T callouts (critical-to-function surfaces)
- All values must comply with the integrity policy (labeled Proposed / Verified / User Requirement)

**6. Material & Finish Specification**
- Pull from `materials-and-finishes.yaml`
- Include compliance notes (mechanical/materials focused)
- All values must comply with integrity labeling rules

**7. Manufacturing Considerations**
- Recommended process chain
- Surface finish specs (Ra where relevant)
- Tooling notes and QC checkpoints

**8. Failure Mode Summary**
- Reference `P5-FMEA-01`

**9. Safety & Compliance**
- Reference `P2-STANDARDS-01`
- Mechanical/materials/chemical compliance focus (unless brief includes electronics)

**10. Bill of Materials & Cost Analysis**
- Enforce costing policy (see `costing-policy.md`)

**11. Complete Artifact Index**
- Include the full `artifact-index.md`

**12. Open Items & Next Steps**
- Prototype plan + testing plan + timeline