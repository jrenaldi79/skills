#!/bin/bash
# First-time setup script for a RunPod pod.
# Run this ONCE on a new pod to install Blender and dependencies to /runpod.
# Usage: ssh root@IP -p PORT < pod_setup.sh

set -e

echo "=== Installing system dependencies ==="
apt update && apt install -y \
  wget xz-utils libxrender1 libxi6 libxext6 libx11-6 \
  libgl1-mesa-glx libxxf86vm1 libxfixes3 libxkbcommon0 \
  xvfb x11vnc novnc websockify 2>&1 | tail -5
echo "Done."

echo "=== Installing Blender 4.2 to /runpod ==="
if [ -d /runpod/blender-4.2.0-linux-x64 ]; then
  echo "Blender already installed on persistent volume."
else
  cd /runpod
  wget -q --show-progress https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz
  tar xf blender-4.2.0-linux-x64.tar.xz
  rm blender-4.2.0-linux-x64.tar.xz
  echo "Blender installed."
fi
ln -sf /runpod/blender-4.2.0-linux-x64/blender /usr/local/bin/blender

echo "=== Installing blender-mcp addon ==="
mkdir -p /runpod/blender-config
if [ ! -f /runpod/blender-config/blender_mcp_addon.py ]; then
  wget -q https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py \
    -O /runpod/blender-config/blender_mcp_addon.py
  echo "Addon downloaded."
else
  echo "Addon already on persistent volume."
fi
mkdir -p /root/.config/blender/4.2/scripts/addons
cp /runpod/blender-config/blender_mcp_addon.py \
   /root/.config/blender/4.2/scripts/addons/blender_mcp_server.py

echo "=== Creating MCP auto-start script ==="
cat > /runpod/autostart_mcp.py << 'MCPPY'
import bpy

def auto_start_mcp():
    """Enable the BlenderMCP addon and start the socket server."""
    try:
        bpy.ops.preferences.addon_enable(module="blender_mcp_server")
        bpy.ops.blendermcp.start_server()
        print("BlenderMCP server auto-started on port 9876")
    except Exception as e:
        print(f"MCP auto-start failed: {e}")
    return None  # Don't repeat the timer

# Delay 3 seconds so Blender is fully initialized
bpy.app.timers.register(auto_start_mcp, first_interval=3.0)
print("MCP auto-start scheduled (3s delay)...")
MCPPY

echo "=== Creating startup script ==="
cat > /runpod/start_session.sh << 'STARTUP'
#!/bin/bash
# Reinstall apt packages (wiped on restart) and start all services.
echo "Installing dependencies..."
apt update && apt install -y \
  libxrender1 libxi6 libxext6 libx11-6 libgl1-mesa-glx \
  libxxf86vm1 libxfixes3 libxkbcommon0 xvfb x11vnc novnc websockify \
  2>&1 | tail -5
if ! command -v Xvfb &>/dev/null || ! command -v x11vnc &>/dev/null; then
  echo "ERROR: Failed to install Xvfb or x11vnc. Run 'apt install -y xvfb x11vnc' manually."
  exit 1
fi

ln -sf /runpod/blender-4.2.0-linux-x64/blender /usr/local/bin/blender
mkdir -p /root/.config/blender/4.2/scripts/addons
cp /runpod/blender-config/blender_mcp_addon.py \
   /root/.config/blender/4.2/scripts/addons/blender_mcp_server.py

# Kill stale processes from previous sessions
pkill Xvfb 2>/dev/null; pkill x11vnc 2>/dev/null; pkill websockify 2>/dev/null
sleep 1

# Start virtual display
nohup Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &
sleep 2
export DISPLAY=:99

# Start VNC (-shared allows multiple connections, -forever keeps it running)
nohup x11vnc -display :99 -forever -shared -passwd blender123 \
  -listen 0.0.0.0 -rfbport 5900 >/dev/null 2>&1 &
sleep 2

# Start noVNC (web-based VNC viewer on port 6080)
nohup websockify --web=/usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1 &
sleep 1

# Start Blender with MCP auto-start
nohup blender --python /runpod/autostart_mcp.py > /tmp/blender_stdout.log 2>&1 &
sleep 5

# Verify everything is running
echo ""
echo "=== Session Ready ==="
echo "Blender:  $(blender --version 2>/dev/null | head -1)"
echo "Xvfb:     $(pgrep -c Xvfb) process(es)"
echo "x11vnc:   $(pgrep -c x11vnc) process(es)"
echo "MCP port: $(ss -tlnp | grep 9876 | wc -l) listener(s) on 9876"
echo "VNC:      port 5900 (password: blender123)"
echo "noVNC:    port 6080 (open http://localhost:6080/vnc.html in browser)"
echo "MCP:      port 9876 (auto-started)"
STARTUP
chmod +x /runpod/start_session.sh

echo ""
echo "=== First-time setup complete ==="
echo "Blender: $(blender --version | head -1)"
echo "Run 'bash /runpod/start_session.sh' to start a session."
