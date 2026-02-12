---
name: runpod-blender
description: >
  Photorealistic product rendering in Blender via MCP — locally or on cloud GPUs (RunPod).
  Triggers: "render", "3D visualization", "product shot", "Blender scene", "photorealistic",
  "mockup", "lighting", "materials", "install Blender", "set up Blender MCP", "configure Blender",
  "Blender connection", "runpod", "remote blender", "cloud GPU", "blender session",
  or any first-time onboarding — even if the user doesn't explicitly say "use this skill."
---

# Blender Product Render Skill

Create photorealistic product renders by executing Blender Python (`bpy`) scripts through the Blender MCP — locally or on cloud GPUs (RunPod). This skill enforces a systematic workflow: clean scene -> build geometry -> apply materials -> light -> compose -> iterate -> deliver.

---

## When to Read Reference Files

Before starting any task, read the references relevant to your current phase:

| Phase | Read This |
|-------|-----------|
| First-time setup / installation | `references/onboarding-setup.md` |
| Scene setup, lighting, camera | `references/rendering-standards.md` |
| Applying materials, texturing | `references/materials-and-products.md` |
| Render is wrong (black, blown out, noisy) | `references/debugging.md` |
| RunPod pod lifecycle, SSH, VNC, file transfer | `references/runpod-infrastructure.md` |

If the user has never set up Blender MCP before, read **onboarding-setup.md** first and walk them through installation. Otherwise, read **rendering-standards.md** first on every render task. Read the others as needed.

---

## Environment Detection

Determine whether the user is rendering locally or on a cloud GPU:

- **Cloud path:** User mentions "RunPod", "cloud GPU", "remote", "pod", or "cloud session" -> read `references/runpod-infrastructure.md` for session management.
- **Local path:** User mentions "local", "my machine", or Blender MCP tools respond directly without SSH -> proceed with local workflow.
- **Unclear:** Ask the user: "Are you rendering locally or on a cloud GPU (RunPod)?"

Even on the cloud path, the MCP server runs locally and tunnels to the remote Blender instance. See `references/onboarding-setup.md` for full setup details.

---

## Onboarding: First-Time Setup

If the user hasn't set up Blender MCP yet — or if Blender tools aren't responding — read `references/onboarding-setup.md` and walk them through the full installation.

**Trigger phrases:** "set up Blender", "install Blender MCP", "how do I get started", "Blender tools aren't working", "connection error", "set up RunPod", or any indication this is the user's first time.

**Supported clients:** Claude Desktop, ChatWise, and Claude Code. The onboarding guide detects which client is installed and configures accordingly.

**Supported environments:** Local rendering and cloud GPU rendering (RunPod). The guide branches based on the user's choice.

---

## Workflow Overview

Every product render follows this sequence. Do not skip steps.

### Step 0: Environment Setup

**Cloud (RunPod):**
1. Read `references/runpod-infrastructure.md`.
2. Start the pod, run the startup script, establish SSH tunnel.
3. Verify MCP connection with `get_scene_info`.

**Local:**
1. Verify Blender is running and the MCP addon shows "Connected".
2. Verify MCP connection with `get_scene_info`.

### Step 1: Scene Initialization

Always begin by clearing the default scene. Leftover objects, lights, and cameras cause conflicts.

```python
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes.clear()
bg = world.node_tree.nodes.new('ShaderNodeBackground')
output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
world.node_tree.links.new(bg.outputs[0], output.inputs[0])
```

Set units to Metric, scene scale to 1.0.

### Step 2: Build or Import Geometry

- Model the product or import an existing asset (Poly Haven, Sketchfab, Hyper3D).
- Ensure real-world scale: a phone is ~0.15m, a mug is ~0.10m, a chair seat is ~0.45m.
- Apply bevel modifiers to hard-surface objects (see `references/rendering-standards.md` for width by object size).

### Step 3: Apply Materials

Read `references/materials-and-products.md` before assigning any material. Key principles:
- Use Principled BSDF for everything.
- Add micro-roughness imperfections — real surfaces are never perfectly smooth.
- Never use pure black (0,0,0) for dark materials.
- Consult the product-type table for glass, metal, plastic, fabric, leather, and ceramic.

### Step 4: Light the Scene

Read `references/rendering-standards.md` for the full lighting protocol.

**Critical first step:** Call `get_polyhaven_status` before attempting any HDRI download.

- If Poly Haven is available -> use a studio HDRI.
- If Poly Haven is unavailable -> build a 3-point light rig (details in reference file).

Rotate the HDRI or key light until rim highlights separate the object from the background.

### Step 5: Set Up Camera

- Focal length: 50mm-85mm for product shots.
- Frame the object at ~70-80% of the image area.
- Enable depth of field (f/2.8-f/5.6) for hero shots.
- Place the object on a contextual ground plane (wood, concrete, fabric, or seamless sweep).
- Rotate the object slightly off-axis for a natural, non-CAD appearance.

### Step 6: Test Render -> Evaluate -> Iterate

This is the critical loop. Render small, evaluate fast, fix issues, repeat.

**Test render settings (environment-aware):**

| Setting | Local | Cloud (RunPod) |
|---------|-------|----------------|
| Resolution | 1280x720 | 1024x1024 |
| Samples | 48 | 64 |
| Format | PNG | JPEG 85% |
| File size goal | < 1 MB | < 300 KB |
| Denoising | Enabled | Enabled |

**Cloud:** After rendering, SCP the checkpoint image to the local project directory, then open locally with `open <path>`. Read the image to analyze. Save and restore original render settings after checkpoint.

**Evaluation checklist — check all six before proceeding:**

1. **Framing** — Object fully visible, filling ~70-80% of frame?
2. **Edge highlights** — Specular highlights catching edges, separating object from background?
3. **Shadow grounding** — Shadows anchoring the object to the surface?
4. **Exposure balance** — No blown-out whites or crushed blacks?
5. **Material read** — Can you clearly distinguish different materials?
6. **Composition** — Placement feels natural, not rigidly centered?

If any criterion fails, diagnose and fix before re-rendering. If the render is black, white, or missing the object entirely, go to `references/debugging.md`.

### Step 7: Final Delivery

Only after all six evaluation criteria pass and the user approves the composition:

- Resolution: 1920x1080 (HD) or 3840x2160 (4K).
- Samples: 256-1024.
- Save to disk for the user. **DO NOT** feed final renders back into the chat context — they will overflow.

**Cloud:** SCP the final render to the local project directory, then open locally.

### Step 8: Save and Cleanup

**Cloud (RunPod):**
1. Save the .blend file on the pod (see `references/runpod-infrastructure.md` Save / Download Project).
2. SCP the .blend file to the local project directory.
3. Stop the pod to end billing.

**Local:**
1. Save the .blend file to the project directory.

---

## Key Rules (Always in Effect)

1. **Always use Cycles.** Eevee cannot produce the light bounce accuracy needed for photorealism.
2. **Always check Poly Haven status** before downloading HDRIs or textures.
3. **Always screenshot the viewport** (`get_viewport_screenshot`) before a full render if something looks wrong — it's faster and catches most spatial issues.
4. **Never skip the bevel modifier** on hard-surface objects. Sharp edges don't exist in reality and kill photorealism.
5. **Keep test renders small.** Context overflow from large images breaks the iterative loop.
6. **Break scripts into small steps.** Execute one logical operation per `execute_blender_code` call — don't try to build an entire scene in a single script. This makes debugging dramatically easier.
7. **Always stop the pod when done** (cloud only). It charges ~$0.28/hr.
8. **Always query fresh SSH info** before SCP or tunnel commands (cloud only). IP and port change on every pod restart.
9. **Use SCP for file transfers** (cloud only). Do not use blender-mcp for file transfers — it's too slow.
10. **Save checkpoint renders as JPEG** (cloud only). PNG files are too large for efficient SCP transfer and LLM analysis.

---

## Output Deliverables (Capstone Context)

For academic or capstone projects, each product visualization should produce:

1. **Final render(s):** High-resolution PNG at HD or 4K.
2. **Blender file (.blend):** Complete scene with materials, lighting, and camera preserved.
3. **Design rationale:** 3-5 sentences explaining the lighting strategy, material choices, and composition decisions — connecting them to the visual outcome.

This ensures the project demonstrates intentional design thinking, not just tool proficiency.
