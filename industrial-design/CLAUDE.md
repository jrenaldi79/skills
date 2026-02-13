# Industrial Design Skill — Development Guide

This file is for developing and maintaining the skill itself. `SKILL.md` is what the LLM reads when using the skill on a design project — don't conflate the two.

## Repo & Location

- **Repo:** `github.com/jrenaldi79/skills` (branch: `main`)
- **Local path:** `/Users/john_renaldi/.skills-storage/vendor/jrenaldi79__skills/industrial-design/`
- **Multi-skill repo:** Other skills (docx, life360-brand, etc.) share this repo. Only stage `industrial-design/` files unless explicitly told otherwise.
- Other skills often have unstaged changes and untracked `node_modules/` — stash before `git pull --rebase` if push is rejected.

## Build & Deploy

After any file change:

```bash
cd /Users/john_renaldi/.skills-storage/vendor/jrenaldi79__skills/industrial-design
rm -f industrial-design.skill
zip -r industrial-design.skill SKILL.md references/ scripts/ evals/ -x "scripts/shadcn-components.tar.gz"
```

Then stage only industrial-design files, commit, and push.

## Skill Architecture

**Context engineering is a first-class concern.** The skill is split into `SKILL.md` (~230 lines) plus reference files that load on demand. The agent only reads what it needs for the current phase. Don't bloat `SKILL.md` with phase-specific detail — put it in a reference file and add a row to the reference table.

### Current file inventory

- `SKILL.md` — Core identity, principles, 6-phase workflow, reference table
- 12 reference files in `references/`
- 6 scripts in `scripts/`
- 1 eval suite in `evals/`

### When adding a new reference file

1. Create the file in `references/`
2. Add a row to the **Reference Files** table in `SKILL.md` with when-to-read guidance
3. Add it to the **Skill Structure** tree in `README.md`
4. Wire it into the relevant pipeline doc (e.g., `rendering-pipeline.md` says "read `cad-build-protocol.md` before starting")
5. Rebuild `.skill`

### When modifying an existing file

Check cross-references. Key files are mentioned in multiple places:
- `rendering-pipeline.md` is referenced from `SKILL.md`, `README.md`, `image-factory.md`
- `capability-check.md` is referenced from `SKILL.md`, `README.md`, `image-factory.md`
- `design-system.md` is referenced from `SKILL.md`, `README.md`, `rendering-pipeline.md`
- `image-factory.md` is referenced from `rendering-pipeline.md`, `capability-check.md`, `design-system.md`

If you rename a section header or change a file's scope, grep for references.

## Development Pattern

Changes are **RCA-driven**: run the skill on a real project → encounter a failure → write or receive an RCA → implement targeted fixes.

When implementing an RCA:
1. Read all files that will be modified (get current state)
2. Make changes
3. Check for architectural fit (e.g., tool-specific content belongs in a separate reference file, not inline)
4. Rebuild `.skill`
5. Run verification greps (cross-references exist, no stale file-path image refs, etc.)
6. Commit with descriptive message explaining the RCA and what changed

## Commit Style

```
Short summary line (imperative mood)

Context paragraph explaining the why — typically the RCA finding.

- Bullet points for each specific change
- Include file names
- Rebuild note

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

## Key Design Decisions

- **Tool-agnostic at L3:** The skill supports both Blender MCP and Fusion 360 MCP. Don't hardcode tool-specific API calls in `SKILL.md` or `rendering-pipeline.md`. Put tool-specific procedures in `cad-build-protocol.md` or a dedicated reference file.
- **Base64 everywhere:** All images in HTML artifacts must be data URIs. `generate-render.py` writes `.b64.txt` companion files. The image-factory pipeline handles web-fetched images.
- **DTS is mandatory for L2 and L3:** Every render and CAD output must have a DTS written before generation and evaluated after. Required criteria blocks exist for both levels.
- **Master-conditioned renders:** L2 renders use a two-stage workflow — master render (hard gate) → conditioned variations. Never generate variations from independent prompts.
- **Progressive disclosure:** Reference files load only when their phase is reached. Don't front-load instructions the agent won't need for 4 phases.

## Testing

Eval suite: `evals/evals.json` (3 test cases exercising Phase 1 behavior). Run evals after changes that affect Phase 1 flow, capability check, or brief handling.
