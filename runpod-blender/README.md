# runpod-blender

A **Claude Code plugin** for photorealistic product rendering in Blender — locally or on cloud GPUs (RunPod).

> **This is a plugin, not a skill.** It bundles an MCP server (`blender-mcp`), a rendering skill, and pod-awareness hooks into a single installable package. Do not install it as a standalone skill — use the plugin install method below.

**Cost:** Cloud rendering runs ~$0.28-0.34/hr on RunPod. The plugin includes hooks that remind you when a pod is still running so you don't get surprise bills.

---

## What's Included

| Component | What It Does |
|-----------|-------------|
| **MCP server** (`blender-mcp`) | Auto-registered on install — no separate MCP config needed |
| **Rendering skill** | 8-step product photography workflow (geometry, materials, lighting, camera, render, iterate) |
| **Pod-awareness hooks** | Warns at session start/end/idle if your RunPod pod is still running |
| **RunPod scripts** | Pod lifecycle management (start, stop, status, create) |

---

## Install the Plugin

### 1. Clone the skills repo

```bash
git clone https://github.com/jrenaldi79/skills.git
cd skills
```

### 2. Install as a Claude Code plugin

```bash
claude plugin install ./runpod-blender
```

This registers the `blender-mcp` MCP server and makes the `runpod-blender` skill available automatically. No separate MCP configuration step is needed.

> **For development:** Use `claude --plugin-dir ./runpod-blender` to load the plugin from the local directory without installing.

### 3. Install uv (required for blender-mcp)

```bash
# macOS
brew install uv

# Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Create your `.env` file

Copy the template into your project working directory and add your RunPod API key:

```bash
cp runpod-blender/.env.example .env
```

Edit `.env` and set `RUNPOD_API_KEY` to your key (get one from RunPod > Settings > API Keys).

**Important:** Never commit `.env` to git — it contains your API key.

### 5. Install the RunPod CLI and SSH key

**macOS:**
```bash
mkdir -p ~/.local/bin
curl -Lo /tmp/runpodctl.tar.gz -L \
  https://github.com/runpod/runpodctl/releases/latest/download/runpodctl-darwin-all.tar.gz
tar xzf /tmp/runpodctl.tar.gz -C /tmp/
mv /tmp/runpodctl ~/.local/bin/runpodctl
chmod +x ~/.local/bin/runpodctl
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
mkdir -p ~/.local/bin
curl -Lo /tmp/runpodctl.tar.gz -L \
  https://github.com/runpod/runpodctl/releases/latest/download/runpodctl-linux-amd64.tar.gz
tar xzf /tmp/runpodctl.tar.gz -C /tmp/
mv /tmp/runpodctl ~/.local/bin/runpodctl
chmod +x ~/.local/bin/runpodctl
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then configure your API key and generate an SSH key:
```bash
runpodctl config --apiKey YOUR_API_KEY
runpodctl ssh add-key
```

### 6. First-time pod setup

Tell Claude: **"Set up a new RunPod pod for Blender"**

It will create a GPU pod, SSH in, install Blender 4.2 + dependencies to the persistent volume, and save your pod ID to `.env`. This takes ~5 minutes and only needs to happen once.

---

## Daily Usage

```
You:    "Start my blender session"
Claude: [starts pod, runs startup script, sets up SSH tunnel]
        "VNC is ready — connect to vnc://localhost:5900"

You:    [connect VNC to watch in real-time]
You:    "Create a product scene with a glass bottle and studio lighting"
Claude: [controls Blender via MCP, you watch in VNC]

You:    "Stop my blender session"
Claude: [stops pod, kills tunnel]
        "Pod stopped. No more charges."
```

### VNC Connection

- **macOS**: Finder > Cmd+K > `vnc://localhost:5900`
- **Linux**: `vncviewer localhost:5900`
- **Windows**: RealVNC Viewer > `localhost:5900`

### MCP Connection

The BlenderMCP addon auto-starts when Blender launches — no manual activation needed. Claude controls Blender through the MCP bridge over the SSH tunnel (port 9876).

---

## How It Works

The RunPod pod is an Ubuntu 22.04 Linux box with a dedicated GPU. During first-time setup, the full Blender 4.2 desktop application is downloaded and installed as a standalone binary on the pod's persistent volume (`/runpod/blender-4.2.0-linux-x64/`). It's the same Blender you'd run on a Linux workstation.

Since the pod is headless (no physical monitor), Blender renders to a **virtual display** (Xvfb). **x11vnc** streams that virtual display to your laptop over an SSH tunnel, so you can watch Blender in real-time through a VNC viewer. Claude controls Blender through the MCP addon, which also runs on the pod and communicates over a separate SSH tunnel.

```
Your Laptop                          RunPod GPU Pod (Ubuntu 22.04)
┌──────────────────┐                ┌──────────────────────────┐
│  Claude Code     │───port 9876──▶│  Blender 4.2 (full app)  │
│  blender-mcp     │   SSH Tunnel   │  + MCP Addon (auto-start)│
│                  │                │                          │
│  VNC Viewer      │───port 5900──▶│  Xvfb (virtual display)  │
│  (Screen Sharing)│                │  + x11vnc (VNC server)   │
└──────────────────┘                │                          │
                                    │  GPU (RTX 4080/4090)     │
                                    │  /runpod/ (persistent)   │
                                    └──────────────────────────┘
```

- **Blender**: Full desktop app installed on the pod — renders using the pod's GPU via CUDA/OptiX
- **Xvfb**: Virtual framebuffer that gives Blender a "screen" on the headless server
- **x11vnc**: Streams the virtual display to your VNC viewer so you can watch live
- **blender-mcp**: Bridge between Claude and Blender's Python API (runs inside Blender as an addon)
- **SSH tunnel**: Securely forwards ports 9876 (MCP) and 5900 (VNC) to your laptop

---

## Plugin Structure

```
runpod-blender/                      # This directory IS the plugin
├── .claude-plugin/
│   └── plugin.json                  # Plugin manifest
├── .mcp.json                        # Auto-registers blender-mcp
├── .env.example                     # Credential template
├── README.md                        # This file
├── skills/
│   └── runpod-blender/
│       ├── SKILL.md                 # Rendering workflow orchestrator
│       ├── scripts/                 # runpod_manager.py, pod_setup.sh
│       └── references/              # Standards, materials, debugging guides
├── hooks/
│   └── hooks.json                   # Pod reminder hooks
├── scripts/
│   └── pod_reminder.py              # Hook: checks if pod is running
└── evals/
    ├── evals.json                   # Behavioral test cases
    └── test_hooks.sh                # Hook integration tests
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| GPU unavailable when creating pod | Try a different GPU type. Ask Claude to list available GPUs. |
| Pod won't start after stopping | Host may be full. Delete and recreate the pod (re-run first-time setup). |
| SSH connection refused | Pod is still booting. Wait 30 seconds and retry. |
| `blender: command not found` | Expected after restart. The startup script fixes this automatically. |
| VNC won't connect | Check tunnel is running. Ask Claude to restart the session. |
| VNC needs a password | Default is `blender123`. |
| MCP not connecting | Should auto-start. Check tunnel is up and port 9876 is listening on the pod. |
| Black screen in VNC | Blender may have crashed. Ask Claude to restart Blender on the pod. |
| Render using CPU not GPU | In Blender: Edit > Preferences > System > CUDA > check your GPU. |
| Left pod running overnight | Stop it ASAP: `runpodctl stop pod YOUR_POD_ID` |

## GPU Options

| GPU | VRAM | $/hr | Notes |
|-----|------|------|-------|
| RTX 3090 | 24GB | $0.22 | Budget option |
| RTX 4080 SUPER | 16GB | $0.28 | Great value |
| RTX 4090 | 24GB | $0.34 | Best consumer GPU |
| A40 | 48GB | $0.35 | Pro, huge VRAM |

## Key Concept: Persistent Storage

Only the `/runpod` volume survives pod restarts. System packages and config files are wiped each time. The startup script handles reinstalling everything automatically — you don't need to worry about this.
