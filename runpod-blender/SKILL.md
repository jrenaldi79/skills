---
name: runpod-blender
description: >
  Manage RunPod GPU pods for remote Blender sessions. Use when the user wants to:
  start/stop a cloud GPU for Blender, set up a remote Blender session, connect to
  RunPod, render on a cloud GPU, or mentions "runpod", "remote blender", "cloud GPU",
  or "blender session". Also handles first-time workspace setup, project scaffolding,
  pod lifecycle, SSH tunneling, VNC setup, and blender-mcp configuration.
---

# RunPod Blender Session Manager

## Configuration

All secrets live in `~/blender-files/runpod/.env` (never committed to git):
```
RUNPOD_API_KEY=rpa_...
RUNPOD_POD_ID=abc123
VNC_PASSWORD=blender123
```

The script auto-discovers `.env` from the working directory or `~/blender-files/runpod/.env`.
SSH key is at `~/.runpod/ssh/RunPod-Key-Go`.

## Scripts

- `scripts/runpod_manager.py` — Pod lifecycle (start, stop, status, ssh-info, create). Reads from `.env` automatically.
- `scripts/pod_setup.sh` — First-time pod setup (installs Blender + deps to `/runpod`)

## First-Time Workspace Setup

Run this when a student says "set up RunPod for Blender" and has no existing workspace.

1. Create directory structure:
   ```
   mkdir -p ~/blender-files/runpod/projects
   mkdir -p ~/blender-files/runpod/skill/scripts
   ```
2. Copy skill files into `~/blender-files/runpod/skill/` (SKILL.md, scripts/)
3. Initialize git:
   ```
   cd ~/blender-files/runpod && git init
   ```
4. Create `.gitignore` (exclude `.env`, `.DS_Store`, `*.blend1`, `__pycache__/`)
5. Create `.env` from the template (`skill/.env.example`):
   - Ask the user for their RunPod API key
   - Write it to `~/blender-files/runpod/.env`
   - Leave `RUNPOD_POD_ID` blank (filled after pod creation)
6. Proceed to **First-Time Pod Setup** below

## First-Time Pod Setup

1. Read API key from `.env`
2. Create pod:
   ```
   python3 SKILL_DIR/scripts/runpod_manager.py create --env-file ~/blender-files/runpod/.env
   ```
3. Extract pod ID from JSON output
4. **Save pod ID** to `.env`:
   - Update `RUNPOD_POD_ID=<new_pod_id>` in `~/blender-files/runpod/.env`
5. Wait for SSH, then pipe setup script:
   ```
   ssh -o StrictHostKeyChecking=no -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT \
     < SKILL_DIR/scripts/pod_setup.sh
   ```
6. Commit initial setup:
   ```
   cd ~/blender-files/runpod && git add -A && git commit -m "Initial RunPod Blender setup"
   ```

## Start a Session

1. Read `.env` (api key, pod ID, VNC password)
2. Start pod:
   ```
   python3 SKILL_DIR/scripts/runpod_manager.py start --env-file ~/blender-files/runpod/.env
   ```
3. Extract SSH ip/port from JSON output
4. Run startup script on pod:
   ```
   ssh -o StrictHostKeyChecking=no -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT \
     "bash /runpod/start_session.sh" 2>&1 | tail -10
   ```
5. Set up SSH tunnel:
   ```
   pkill -f "ssh.*-L 9876.*-L 5900" 2>/dev/null
   ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 \
     -i ~/.runpod/ssh/RunPod-Key-Go -N -f \
     -L 9876:localhost:9876 -L 5900:localhost:5900 -L 6080:localhost:6080 root@IP -p PORT
   ```
6. Tell user: open **http://localhost:6080/vnc.html** in their browser to view Blender live. Enter the VNC password from `.env` when prompted. MCP server auto-starts on port 9876 — no manual addon activation needed.

## Stop a Session

1. `python3 SKILL_DIR/scripts/runpod_manager.py stop --env-file ~/blender-files/runpod/.env`
2. `pkill -f "ssh.*-L 9876.*-L 5900.*-L 6080" 2>/dev/null`
3. Confirm pod stopped and billing ended

## Check Status

```
python3 SKILL_DIR/scripts/runpod_manager.py status --env-file ~/blender-files/runpod/.env
```

## New Project

When the user starts a new Blender project:

1. Create project directory:
   ```
   mkdir -p ~/blender-files/runpod/projects/<project-name>
   ```
2. This is the working directory for render scripts, .blend files, output renders, and assets for that project.

## Rendering Workflow

There are two render tiers. Use **checkpoint renders** during iterative design work, and **final renders** only when the design is locked.

### Checkpoint Renders (< 1 MB)

Use these for all design iteration and LLM image analysis. Large images cause context/token issues and slow down feedback loops.

Settings — apply before render, restore originals after:
```python
render.resolution_x = 1024
render.resolution_y = 1024
render.resolution_percentage = 100
scene.cycles.samples = 64
render.image_settings.file_format = 'JPEG'
render.image_settings.quality = 85
render.filepath = "/runpod/projects/<project>/checkpoint_render.jpg"
```
This typically produces files around 100–300 KB.

### Final Renders

Use full resolution and samples only when the design is approved. Output as PNG for quality.

### Workflow

1. **Checkpoint render** with the settings above
2. SCP to local project directory (see **File Transfer** section)
3. **Always open locally** with `open <path>` so the user can see it
4. Read the image with the Read tool to analyze it alongside the user
5. Iterate with checkpoint renders until the design is approved
6. **Final render** at full resolution/samples, SCP + open locally

## File Transfer

All file transfers between the pod and local machine use SCP with the RunPod SSH key. Do NOT use blender-mcp for file transfers — it's too slow for anything beyond small text.

**Get SSH connection info first:**
```
python3 SKILL_DIR/scripts/runpod_manager.py status --env-file ~/blender-files/runpod/.env
```
Extract the SSH `ip` and `port` from the JSON output (the entry with `privatePort: 22`).

**Download from pod to local:**
```
scp -i ~/.runpod/ssh/RunPod-Key-Go -P PORT -o StrictHostKeyChecking=no \
  root@IP:/runpod/path/to/file ~/blender-files/runpod/projects/<project>/file
```

**Upload from local to pod:**
```
scp -i ~/.runpod/ssh/RunPod-Key-Go -P PORT -o StrictHostKeyChecking=no \
  ~/blender-files/runpod/projects/<project>/file root@IP:/runpod/path/to/file
```

## Save / Download Project

To save a Blender project locally (for backup, version control, or loading later):

1. Save the .blend file on the pod via blender-mcp:
   ```python
   import bpy, os
   os.makedirs("/runpod/projects/<project>", exist_ok=True)
   bpy.ops.wm.save_as_mainfile(filepath="/runpod/projects/<project>/<name>.blend")
   ```
2. SCP the .blend file to the local project directory (see **File Transfer** above)
3. To reload later, upload the .blend file back to the pod and open it:
   ```python
   bpy.ops.wm.open_mainfile(filepath="/runpod/projects/<project>/<name>.blend")
   ```

## Key Details

- Only `/runpod` persists across pod restarts. Apt packages and `/root` config are ephemeral.
- The startup script on the pod (`/runpod/start_session.sh`) handles reinstalling deps.
- SSH IP and port change every restart — always query fresh via the API.
- The blender-mcp addon and socket server auto-start via `/runpod/autostart_mcp.py`.
- The local MCP server is configured in `~/blender-files/runpod/.mcp.json` (uses `uvx blender-mcp`).
- Secrets go in `.env`, never in scripts or markdown. The `.env` file is git-ignored.
