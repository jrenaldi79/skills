# Product Design Factory

A Claude skill that takes a product concept from brief through to manufacturable design specification — competitive research, material selection, concept sketching, FMEA, dimensioned drawings, and full spec sheets — in a structured 6-phase pipeline.

## Why This Exists

Software development has mature tooling for turning vague requirements into shipped code: linters catch errors before they compound, CI gates prevent broken deploys, test suites verify behavior, and project files persist state across sessions. Physical product design has the same needs — structured phases, verification at each gate, research that doesn't hallucinate specs, and artifacts that build on each other — but no equivalent tooling for AI-assisted workflows.

This skill applies patterns from software development to industrial design:

| Software development pattern | Product Design Factory equivalent |
|------------------------------|-----------------------------------|
| CI environment detection | Capability check — probe for available tools before starting work |
| Deployment gates / PR reviews | Phase gates (hard stops requiring user approval before proceeding) |
| Worker processes / task queues | Parallel research subagents with structured prompt templates |
| Project config / state files | `CLAUDE.md` updated at every phase gate for cross-session continuity |
| Lazy loading / code splitting | Progressive disclosure — reference files load only when their phase is reached |
| Test suites | Design Test Spec (DTS) verification loop on every visual artifact |
| Type safety / labeling | Spec integrity policy — every dimension labeled Verified, User Requirement, or Proposed |
| Architecture Decision Records | `decision-log.md` tracking rationale for every design choice |
| Build artifacts + manifests | Artifact registry with deterministic naming (`P[Phase]-[Type]-[Seq]`) |
| CI dashboards | Auto-generated `index.html` dashboard at every phase gate |
| Unit tests for the tool itself | Eval framework with discriminating assertions |

## Context Engineering

The skill is split into SKILL.md (~215 lines of core instructions) plus 11 reference files that load on demand. This keeps the context window lean — the agent only reads `research-workstreams.md` during Phase 2, `rendering-pipeline.md` during Phases 3-6, `engineering-standards.md` during Phases 4-6, and so on. The reference file table in SKILL.md tells the agent exactly when to read each file.

Subagent research uses the same principle: each of the 4 research workstreams runs in its own context via the Task tool, with a filled-in prompt template (`research-subagent-prompt.md`) that gives the subagent only what it needs — its specific mission, tasks, output path, and tool availability. The lead agent's context stays clean for synthesis and cross-referencing after the subagents return.

`CLAUDE.md` serves as cross-session memory. It's written during Phase 1 scaffolding and updated at every phase gate with current phase, artifact map, key decisions, and next actions. A new session reads this file first and knows exactly where to resume.

## Anti-Hallucination Measures

Hardware specs are high-risk for fabrication — a plausible-sounding but invented tolerance or material grade can propagate through a spec sheet unchecked. The skill addresses this at multiple levels:

- **Spec integrity labeling** — Every dimension, material grade, and tolerance must be tagged as *Verified (Source)*, *User Requirement*, or *Proposed Target*. No unlabeled numbers in deliverables.
- **Costing policy** — Cost claims require citations or clearly labeled P10/P50/P90 ranges with stated assumptions (region, volume, finish). No point estimates without sources.
- **Research subagent constraints** — Subagents are instructed to present data, not make design decisions. They must cite sources inline, report gaps explicitly, and never fabricate specs.
- **DTS verification** — Every visual artifact is checked against a Design Test Spec before delivery. The agent writes the DTS, generates the output, then evaluates against it.
- **Eval assertions** — The eval suite includes negative assertions ("does NOT fabricate specs", "does NOT skip to sketches") that specifically catch the most common failure mode: the agent racing ahead without evidence.

## Multi-Agent Research

Phase 2 uses a lead-agent/subagent orchestration pattern. The lead agent:

1. Reads the product brief and assesses complexity per workstream
2. Reads the subagent prompt template and fills `{{VARIABLE}}` placeholders for each of 4 workstreams (competitive intel, materials, standards, visual references)
3. Spawns all 4 as parallel background tasks (cost-efficient model)
4. Waits for completion, then cross-references findings (do candidate materials meet identified standards? do competitor price points align with material costs?)
5. Runs image post-processing on the visual reference board
6. Identifies gaps and spawns targeted follow-ups if needed

Each subagent follows an OODA research loop (observe-orient-decide-act) with a fixed tool-call budget (8-20 calls depending on complexity) and strict source quality evaluation.

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
│   ├── image-factory.md            # Base64 image embedding pipeline + sandbox fallback
│   ├── artifact-registry.md        # Naming conventions, required artifacts, YAML source-of-truth files
│   ├── engineering-standards.md    # Spec integrity policy, units, tolerancing, GD&T, rounding
│   ├── costing-policy.md           # Anti-hallucination rules for cost/material claims
│   └── spec-template.md            # Brief intake template + Phase 6 final spec format
├── evals/
│   └── evals.json                  # 3 test cases with assertions
├── scripts/
│   ├── init-artifact.sh            # Scaffold React + Tailwind + shadcn/ui artifact project
│   ├── bundle-artifact.sh          # Bundle artifact into single-file HTML
│   ├── generate-dashboard.py       # Generate index.html project dashboard
│   ├── generate-render.py          # Gemini API image generation (master + variation modes)
│   ├── fetch-images.py             # Fetch images as base64 data URIs (host-side)
│   ├── embed-images.py             # Replace external URLs with data URIs in HTML
│   └── shadcn-components.tar.gz    # Pre-packaged shadcn/ui components
└── assets/
```

## The 6-Phase Pipeline

Each phase produces specific artifacts and ends at a gate. Hard gates (locked) require user approval; soft gates (unlocked) auto-advance.

1. **Intake** (soft) — Parse brief against template, run capability check, ask clarifying questions, scaffold project directory with `CLAUDE.md`
2. **Research** (soft) — Orchestrate 4 parallel research subagents, synthesize findings, post-process visual references with base64 image embedding
3. **Ideation** (hard) — Generate 2-3 concepts with L1 structural sketches, present trade-offs. Stop and wait for user to select a direction.
4. **Refinement** (hard) — Design language brief, mood boards, material boards, L2 inspiration renders via two-stage master-conditioned workflow (master render + conditioned variations, all base64-embedded), dimensioned sketches with parameter files. Stop for approval.
5. **FMEA** (soft) — Failure mode analysis, mitigations folded back into specs and parameters
6. **Final Spec** (hard) — L3 technical drawings with tolerances and GD&T, hero render, complete spec sheet. Stop for sign-off.

`CLAUDE.md` is updated and the project dashboard regenerated at every phase transition.

### Progressive Fidelity Rendering

Visual outputs move through three fidelity levels, each serving a different purpose:

| Level | Name | Purpose | Tools |
|-------|------|---------|-------|
| L1 | Structural Sketches | Form, proportion, layout | React + Tailwind + inline SVG |
| L2 | Inspiration Renders | Materials, color, emotional tone | Image-gen API (`scripts/generate-render.py`) or canvas-design skill |
| L3 | CAD-Ready Spec | Engineering documentation | Blender/Fusion MCP or dimensioned drawings |

### Image Embedding

All HTML artifacts use base64 data URI embedding so images render in any viewer, including environments with restrictive Content Security Policies. This applies to both web-fetched images and locally generated renders (from `scripts/generate-render.py`, which writes `.b64.txt` companion files). The primary fetch path uses bash/curl directly. In sandboxed environments where outbound HTTP is blocked (e.g., Cowork), the skill falls back to Desktop Commander MCP to fetch images from the host machine. See `references/image-factory.md` for the pipeline and `references/capability-check.md` for setup.

### Design System

All HTML artifacts share a consistent visual language (Modern Product Studio style) defined in `references/design-system.md` — warm earth tones, system font stacks, standardized components. No external stylesheets or fonts.

## Installation

Copy `industrial-design/` into your skills directory:
- Cowork: `.skills/skills/industrial-design/`
- Claude Code: `.claude/skills/industrial-design/`

Or upload `industrial-design.skill` (a zip) directly in Claude Desktop.

The skill triggers on keywords like "product design", "industrial design", "DFM", "design spec", "material selection", or casual phrases like "design me a tool" or "I have a product idea."

---

## Eval Framework

The skill ships with an eval suite (3 test cases) that exercises Phase 1 behavior across different brief completeness levels. This section documents the approach so it can be reused for other skills.

### What the Evals Test

| Eval | Prompt | Tests |
|------|--------|-------|
| 1 | Magnetic torpedo level (65% complete brief) | Capability check, clarifying questions, missing field identification |
| 2 | Premium hand trowel (80% complete brief) | Targeted (not broad) questions, DFM reasoning, artifact naming, spec labeling |
| 3 | Modular scaffolding connector (30% complete brief) | Vague brief handling, safety emphasis, standards identification, no fabricated specs |

### How to Run

**Execute:** For each eval in `evals/evals.json`, run the eval prompt through the skill and save a transcript.

**Grade:** Evaluate each transcript against the assertions in `evals.json`. PASS = clear evidence the assertion holds. FAIL = no evidence or contradicting evidence.

**Review:** Each `grading.json` includes:
- `claims` — facts the agent stated, verified against the transcript (catches hallucinated specs even when assertions pass)
- `eval_feedback` — grader suggestions for tightening assertions or adding coverage

### Assertion Design

Assertions are designed to be discriminating — they pass when the skill works correctly and fail when it doesn't:

- **Negative assertions** ("does NOT fabricate specs", "does NOT skip to sketches") catch the agent racing ahead without following the workflow
- **Domain-specific assertions** ("emphasizes safety for scaffolding") verify adaptation to product category
- **Completeness checks** ("identifies missing fields", "asks at least 2 questions") verify the agent follows the brief template
- **Labeling assertions** ("cost claims labeled as Verified/Proposed/User Requirement") catch spec hallucination
