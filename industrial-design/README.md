# Industrial Design Skill

A Claude skill that transforms product concepts into manufacturable design specifications through a structured 6-phase workflow.

## Origin

Created from `industrial-design-agent.md` — a 520-line system prompt originally written for Claude Code / CLI harness use. Converted to a modular skill with progressive disclosure (SKILL.md + 9 reference files) so it only loads what's needed per phase.

## Skill Structure

```
industrial-design/
├── SKILL.md                        # Core instructions — identity, principles, 6-phase workflow
├── industrial-design.skill         # Packaged skill (zip) for Claude Desktop upload
├── references/
│   ├── capability-check.md         # Tool detection + fallback matrix
│   ├── claude-md-template.md       # CLAUDE.md project context template (cross-session memory)
│   ├── design-system.md            # Visual design system — colors, type, components, CSS boilerplate
│   ├── research-workstreams.md     # 4 research workstreams + orchestrator delegation + image strategy
│   ├── research-subagent-prompt.md # Subagent prompt template with {{VARIABLE}} placeholders
│   ├── rendering-pipeline.md       # L1/L2/L3 fidelity levels + DTS verification loop
│   ├── artifact-registry.md        # Naming conventions, required artifacts, YAML source-of-truth files
│   ├── engineering-standards.md    # Spec integrity policy, units, tolerancing, GD&T, rounding
│   ├── costing-policy.md           # Anti-hallucination rules for cost/material claims
│   └── spec-template.md            # Brief intake template + Phase 6 final spec format
├── evals/
│   └── evals.json                  # 3 test cases with assertions
├── scripts/
│   ├── init-artifact.sh            # Scaffold React + Tailwind + shadcn/ui artifact project
│   ├── bundle-artifact.sh          # Bundle artifact into single-file HTML
│   └── shadcn-components.tar.gz    # Pre-packaged shadcn/ui components
└── assets/
```

## How It Works

The skill guides Claude through 6 phases with explicit gates:

1. **Intake** (🔓) — Parse brief against template, capability check, clarifying questions, project scaffolding (creates `CLAUDE.md` + directory structure)
2. **Research** (🔓) — Lead agent acts as **orchestrator**: reads `research-subagent-prompt.md` template, fills variables per workstream, spawns **4 parallel subagents** (Task tool, `general-purpose` type, `haiku` model) for competitive intel, materials, standards, and visual references. Synthesizes and cross-references after all complete.
3. **Ideation** (🔒) — 2-3 concepts with L1 sketches. Hard stop for user selection.
4. **Refinement** (🔒) — Design language brief, mood boards, L2 renders, dimensioned sketches. Optional canvas-design skill for high-fidelity mood boards. Hard stop for approval.
5. **FMEA** (🔓) — Failure mode analysis, mitigations folded into spec
6. **Final Spec** (🔒) — Technical drawings, hero render, full spec sheet. Hard stop for sign-off.

`CLAUDE.md` is updated at every phase gate so new sessions can resume mid-project. Reference files load only when the workflow reaches their phase, keeping context lean.

### Design System

All HTML artifacts share a consistent visual language (Modern Product Studio style) defined in `references/design-system.md` — warm earth tones, system font stacks, standardized components (cards, tables, tags, annotations). No external stylesheets or fonts (blocked by Cowork CSP).

### Image Strategy

Visual reference boards use **base64 data URI embedding** for images. A two-stage build process handles this: the research subagent collects external image URLs, then the lead agent fetches and base64-encodes them into the final HTML. This ensures images render in all viewers including Cowork's CSP-restricted artifact viewer.

## Installation

Copy `industrial-design/` into your skills directory:
- Cowork: `.skills/skills/industrial-design/`
- Claude Code: `.claude/skills/industrial-design/`

The skill triggers on keywords like "product design", "industrial design", "DFM", "design spec", "material selection", or casual phrases like "design me a tool" or "I have a product idea."

---

## Eval Framework

We built a lightweight eval harness to test the skill before shipping. This section documents how it works so you can reuse the pattern for other skills.

### What We Tested

Three eval prompts that exercise different Phase 1 behaviors:

| Eval | Prompt | Tests |
|------|--------|-------|
| 1 | Magnetic torpedo level (65% complete brief) | Capability check, clarifying questions, missing field identification |
| 2 | Premium hand trowel (80% complete brief) | Targeted (not broad) questions, DFM reasoning, artifact naming, spec labeling |
| 3 | Modular scaffolding connector (30% complete brief) | Vague brief handling, safety emphasis, standards identification, no fabricated specs |

### Eval Structure

```
industrial-design-workspace/
├── eval-1/
│   └── with_skill/
│       ├── inputs/              # (empty for these evals — no input files needed)
│       ├── outputs/
│       │   └── transcript.md    # Full execution transcript
│       └── grading.json         # Pass/fail per assertion with evidence
├── eval-2/
│   └── with_skill/
│       ├── outputs/
│       │   └── transcript.md
│       └── grading.json
└── eval-3/
    └── with_skill/
        ├── outputs/
        │   └── transcript.md
        └── grading.json
```

### How to Run Evals

**Step 1: Execute.** For each eval in `evals/evals.json`, spawn an agent (or run inline) that:
- Reads SKILL.md and relevant reference files
- Executes the eval prompt following the skill's instructions
- Saves a transcript to `workspace/eval-N/with_skill/outputs/transcript.md`

**Step 2: Grade.** For each transcript, evaluate against the assertions in `evals.json`:
- Search the transcript for evidence of each assertion
- PASS = clear evidence the assertion is true
- FAIL = no evidence, or evidence contradicts the assertion
- Save results to `workspace/eval-N/with_skill/grading.json`

**Step 3: Review.** Check pass rates and the grader's `eval_feedback` field for suggestions on tightening assertions.

### Reviewing Results

Each `grading.json` contains per-assertion pass/fail verdicts with cited evidence, plus two useful fields:

- **`claims`** — Facts the agent stated during execution, verified against the transcript. Catches hallucinated specs even when all assertions pass.
- **`eval_feedback`** — The grader's suggestions for tightening weak assertions or adding missing coverage. Use this to iterate on `evals.json` between runs.

### Assertion Design Notes

Good assertions for skills like this are **discriminating** — they pass when the skill genuinely works and fail when it doesn't. Some patterns that worked:

- **Negative assertions** ("does NOT fabricate specs", "does NOT skip to sketches") catch the most common failure mode: the agent racing ahead without following the workflow.
- **Domain-specific assertions** ("emphasizes safety for scaffolding") verify the agent adapts its response to the product category rather than giving generic output.
- **Completeness checks** ("identifies missing fields", "asks at least 2 questions") verify the agent follows the brief template rather than winging it.
- **Labeling assertions** ("cost claims labeled as Verified/Proposed/User Requirement") catch spec hallucination — the highest-risk failure mode for hardware design skills.