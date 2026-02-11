# Blender Product Render Skill

A Claude Code skill for photorealistic product rendering in Blender, locally or on cloud GPUs (RunPod).

Describe a product, and Claude Code models it, textures it, lights it, and renders it through Blender's Python API. No Blender experience required.

![Smart speaker render](https://raw.githubusercontent.com/jrenaldi79/skills/main/runpod-blender/assets/smart_speaker_render.jpg)

## What It Does

- Models 3D geometry from a text description
- Applies PBR materials (glass, metal, plastic, fabric, leather, ceramic)
- Sets up studio HDRI lighting and camera composition
- Renders iterative checkpoints, evaluates each against a 6-point quality checklist, and fixes issues automatically
- Produces final HD/4K renders
- Supports local rendering or cloud GPUs on RunPod (~$0.28/hr)

## File Structure

```
runpod-blender/
  SKILL.md                              # Main orchestrator
  .env.example                          # Environment variable template
  runpod-blender.skill.zip              # Packaged skill (all files)
  scripts/
    runpod_manager.py                   # Pod lifecycle (start, stop, status, create)
    pod_setup.sh                        # First-time pod setup
  references/
    onboarding-setup.md                 # First-time setup (Blender, MCP, RunPod account)
    rendering-standards.md              # Engine config, lighting, camera, render settings
    materials-and-products.md           # PBR material recipes by product type
    debugging.md                        # Troubleshooting render failures
    runpod-infrastructure.md            # Pod lifecycle, SSH, VNC, file transfer
```

## Quick Start

### Option 1: Install from zip

1. Download `runpod-blender.skill.zip`
2. Unzip into your Claude Code skills directory:
   ```bash
   mkdir -p ~/.claude/skills/runpod-blender
   unzip runpod-blender.skill.zip -d ~/.claude/skills/runpod-blender
   ```

### Option 2: Symlink from this repo

```bash
git clone https://github.com/jrenaldi79/skills.git ~/skills-repo
ln -s ~/skills-repo/runpod-blender ~/.claude/skills/runpod-blender
```

### Configure MCP

Create `.mcp.json` in your project directory:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"]
        }
    }
}
```

### For Cloud Rendering (Optional)

1. Create a [RunPod](https://runpod.io) account and generate an API key
2. Install the RunPod CLI: `pip install runpodctl`
3. Generate an SSH key: `runpodctl ssh add-key`
4. Copy `.env.example` to `.env` in your project directory and fill in your values:
   ```
   RUNPOD_API_KEY=rpa_...
   RUNPOD_POD_ID=           # filled after pod creation
   VNC_PASSWORD=blender123
   ```
5. Never commit `.env` to git

See `references/onboarding-setup.md` for the full walkthrough.

## How It Works

The skill teaches Claude Code a structured rendering workflow:

1. **Scene Init** — Clear defaults, set Cycles engine
2. **Geometry** — Model or import at real-world scale, apply bevel modifiers
3. **Materials** — Principled BSDF with micro-roughness imperfections
4. **Lighting** — Studio HDRI (Poly Haven) or 3-point light rig
5. **Camera** — 50-85mm focal length, depth of field, off-axis composition
6. **Iterate** — Render checkpoint, evaluate against 6 criteria, fix, repeat
7. **Deliver** — Final HD/4K render
8. **Cleanup** — Save .blend, stop pod (cloud only)

The 6-point evaluation gate checks framing, edge highlights, shadow grounding, exposure balance, material read, and composition before anything gets called "done."

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Blender 3.0+ (local) or a RunPod account (cloud)
- Claude Code with MCP support

## Supported LLM Clients

The onboarding guide covers setup for:
- Claude Code (`.mcp.json`)
- Claude Desktop (`claude_desktop_config.json`)
- ChatWise (SQLite database)

## License

MIT
