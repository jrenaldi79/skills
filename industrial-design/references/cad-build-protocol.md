# CAD Build Protocol

Load this file when CAD MCP (Blender or Fusion 360) is confirmed available and you are starting Phase 6 L3 model generation. These protocols prevent the three most common CAD session failures: partial spec builds, missing reference comparison, and post-rebuild component drift.

---

## 1. Spec-Driven Build Protocol

When building from a design spec (`design-parameters.yaml`, `materials-and-finishes.yaml`, P4-DIMSKETCH-01):

### Before Starting

1. **Read the FULL spec** — every section, every dimension, every component
2. **Create a build checklist** — enumerate EVERY feature, component, and detail from the spec
3. **Do NOT start geometry until the checklist is complete**

### During Build

4. **Work the checklist top-to-bottom** — mark each item as you build it
5. **Do NOT skip "obvious" items** — if the spec says 5 components, build 5 components
6. **After each major geometry change**, verify ALL existing components are still correctly positioned:
   - Query each placed body for its bounding box and position
   - Check bounding boxes haven't shifted
   - Confirm internal components fit within enclosure with correct clearances

### Common Failure Mode

Reading a spec and then only building the "interesting" parts (shell, fillets) while skipping the "boring" parts (PCB, battery, sensors, connectors). The spec is the contract — every line item must be represented in the model.

### Spec Completion Check

Before declaring a model "done", diff your build against the spec:

```
For each item in spec:
├── Built in model?  → query design tree, confirm body exists
├── Correct dimensions?  → check bounding box against design-parameters.yaml
├── Correct position?  → verify relative to other components
└── Correct material/appearance?  → check against materials-and-finishes.yaml
```

---

## 2. Reference Image QA Protocol

When reference images exist (L2 renders, P3 sketches, P4-DIMSKETCH-01):

### MANDATORY: Compare Against References After Every Major Change

After building or modifying geometry:

1. **Take a viewport screenshot** from the CAD tool
2. **Open the reference image(s)** from the project artifacts (P3 sketches, L2 master render, P4-DIMSKETCH-01)
3. **Compare systematically** — check these attributes:
   - Overall proportions (length:width:height ratio)
   - Silhouette shape (rounded vs angular, dome curvature, edge profiles)
   - Feature placement (windows, buttons, ports — relative position on body)
   - Surface character (smooth vs faceted, fillet radii, draft angles)
   - Parting lines and seam visibility
4. **Document discrepancies** before moving on
5. **Fix critical mismatches immediately** — don't defer to "later"

### QA Trigger Points

Run reference comparison at these milestones:
- After creating the primary enclosure/shell shape
- After adding each major feature (window, groove, port)
- After applying fillets/chamfers that affect silhouette
- After placing internal components (hide shell to verify layout matches exploded views)
- Before ANY export or checkpoint save

### Common Failure Mode

Building geometry, taking a screenshot, seeing it "looks okay," and moving on without actually opening and comparing against the reference. Screenshots confirm what you built — references confirm what you SHOULD have built. Both are required.

---

## 3. Post-Modification Component Verification

When the enclosure/shell geometry changes (rebuild, remodel, new fillets):

### MANDATORY: Re-verify All Internal Components

Every body inside the enclosure may have been invalidated by the shell change. Run this checklist after ANY enclosure modification:

1. **List all bodies** — query the design tree, confirm expected count
2. **Check each component's bounding box**:
   - Is it still inside the enclosure?
   - Does it maintain correct clearance from walls?
   - Does it still align with its mounting feature (window, port, connector)?
3. **Check for interference** — components that were correctly placed relative to the OLD shell may now collide with the NEW shell or float in empty space
4. **Verify visibility** — hidden bodies from a previous approach may still exist. Either delete them or document why they're kept.

### Component Placement Cross-Check

For each component in the design spec, verify its relationship to the enclosure:
- Sensors/transducers → centered under their window? aligned with base opening?
- PCB → correct clearance above base plate? fits within internal envelope?
- Battery → expansion gap maintained? shock absorbers still adjacent?
- Connectors → aligned with shell cutouts? accessible from exterior?

Adapt this list to the specific product — the principle is: every component's position is defined relative to the enclosure, so when the enclosure changes, every position must be re-validated.

### Common Failure Mode

Rebuilding the shell from scratch but leaving internal components positioned for the OLD shell geometry. The new shell may have different wall thickness, fillet radii, or interior volume — all internal components need re-validation.

---

## 4. Build Tips

1. **Build everything in the spec** — if a spec lists 7 components, the model must have 7 components. Don't skip the "boring" ones.
2. **QA against references** — after every major milestone, compare your viewport screenshot against reference renders. Don't just eyeball — systematically check proportions, silhouette, and feature placement.
3. **Re-verify after rebuilds** — when shell geometry changes, every internal component position must be re-validated against the new interior volume.
4. **Export at milestones** — save STEP/F3D/blend checkpoints after each major feature group, not just at the end.
