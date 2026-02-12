# Debugging Protocol

Systematic troubleshooting for common rendering failures. Follow these sequences when a render produces unexpected results.

---

## Table of Contents

1. [General Rule](#general-rule)
2. [Black or Very Dark Render](#black-or-very-dark-render)
3. [Blown Out / All White Render](#blown-out--all-white-render)
4. [Object Not Visible](#object-not-visible)
5. [Noisy or Grainy Render](#noisy-or-grainy-render)
6. [Materials Look Wrong](#materials-look-wrong)
7. [Shadows Missing or Floating Object](#shadows-missing-or-floating-object)
8. [Render Takes Too Long](#render-takes-too-long)
9. [Cloud-Specific Issues](#cloud-specific-issues)

---

## General Rule

**Always screenshot the viewport first.** Before re-rendering, call `get_viewport_screenshot`. A viewport check takes seconds; a full render takes minutes. Most spatial, visibility, and camera issues are immediately obvious in the viewport.

---

## Black or Very Dark Render

This is the most common failure. Work through these checks in order:

### 1. Verify the Object Exists

```python
for obj in bpy.data.objects:
    print(f"{obj.name}: type={obj.type}, location={obj.location}, hide_render={obj.hide_render}")
```

If the object list is empty or the product isn't listed, it wasn't created or was deleted.

### 2. Check Lights / HDRI

```python
# Are there any lights?
lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
print(f"Lights in scene: {len(lights)}")
for l in lights:
    print(f"  {l.name}: energy={l.data.energy}, hide_render={l.hide_render}")

# Is the world shader emitting light?
world = bpy.context.scene.world
if world and world.use_nodes:
    for node in world.node_tree.nodes:
        if node.type == 'BACKGROUND':
            print(f"  World background strength: {node.inputs['Strength'].default_value}")
```

If there are no lights and no HDRI, the scene is unlit. Add lighting per the rendering standards.

### 3. Check Material Node Connections

A disconnected Principled BSDF -> Material Output link produces a black surface.

```python
for mat in bpy.data.materials:
    if mat.use_nodes:
        output_nodes = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL']
        for out in output_nodes:
            if not out.inputs['Surface'].links:
                print(f"WARNING: {mat.name} has disconnected Surface output!")
```

### 4. Check Camera Position

The camera might be inside the object or facing away from it.

```python
cam = bpy.context.scene.camera
if cam:
    print(f"Camera location: {cam.location}")
    print(f"Camera rotation: {cam.rotation_euler}")
```

Compare camera location to object location. If they're at the same position, the camera is inside the object.

---

## Blown Out / All White Render

### 1. Reduce HDRI Strength

```python
world = bpy.context.scene.world
for node in world.node_tree.nodes:
    if node.type == 'BACKGROUND':
        node.inputs['Strength'].default_value = 0.5  # Try 0.3-0.5
```

### 2. Check for Duplicate Lighting

If both an HDRI and manual lights are active, they compound. Disable manual lights when using HDRI:

```python
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        obj.hide_render = True
        print(f"Disabled light: {obj.name}")
```

### 3. Check for Emission Shaders

An accidental emission shader with high strength will blow out the image:

```python
for mat in bpy.data.materials:
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == 'EMISSION':
                print(f"WARNING: {mat.name} has Emission node, strength={node.inputs['Strength'].default_value}")
```

### 4. Reduce Exposure

```python
bpy.context.scene.view_settings.exposure = -1.0  # Bring it down
```

---

## Object Not Visible

### 1. Check Location and Scale

```python
obj = bpy.data.objects.get('ProductName')
if obj:
    print(f"Location: {obj.location}")
    print(f"Scale: {obj.scale}")
    print(f"Dimensions: {obj.dimensions}")
```

If scale is (0, 0, 0) or dimensions are enormous (>100m), the object is either invisible or too large for the camera to frame.

### 2. Check Visibility Flags

```python
if obj:
    print(f"hide_viewport: {obj.hide_viewport}")
    print(f"hide_render: {obj.hide_render}")
    print(f"hide_get: {obj.hide_get}")
```

Any of these being `True` will hide the object.

### 3. Check Collection Visibility

Objects in hidden collections won't render:

```python
for col in bpy.data.collections:
    print(f"Collection '{col.name}': hide_render={col.hide_render}")
```

---

## Noisy or Grainy Render

### 1. Increase Samples

For test renders, try 128 instead of 32-48:

```python
bpy.context.scene.cycles.samples = 128
```

### 2. Enable Denoising

```python
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'  # or 'OPTIX' for NVIDIA
```

### 3. Check for Problematic Shaders

Complex shader graphs with many transparent/glass layers slow convergence. Simplify where possible. Also check:

```python
# Clamping reduces fireflies (bright pixel noise)
bpy.context.scene.cycles.sample_clamp_indirect = 10.0
```

### 4. Check Light Path Bounces

Too few bounces cause noise in reflective/transparent scenes:

```python
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 4
bpy.context.scene.cycles.transmission_bounces = 12
```

---

## Materials Look Wrong

### Metallic Object Looks Plasticky
- Verify `Metallic` is set to 1.0 (not 0.0).
- Check that Base Color is the metal's actual color, not grey — metals get their color from Base Color when Metallic=1.

### Transparent Object Is Opaque
- Set `Transmission` to 1.0.
- Increase `transmission_bounces` to >= 12.
- Check that the mesh has proper normals (face normals pointing outward).

### Surface Has No Detail
- Add micro-roughness imperfections (see materials guide).
- Add bump/normal mapping for surface texture.

---

## Shadows Missing or Floating Object

### Object Not Touching Ground Plane
```python
# Snap object bottom to ground (Z=0)
obj = bpy.data.objects['ProductName']
bbox_min_z = min((obj.matrix_world @ mathutils.Vector(corner))[2] for corner in obj.bound_box)
obj.location.z -= bbox_min_z
```

### Shadow Catcher Not Set
If using a ground plane for shadows only (transparent background):

```python
ground = bpy.data.objects['Ground']
ground.is_shadow_catcher = True
bpy.context.scene.render.film_transparent = True
```

---

## Render Takes Too Long

For test renders that exceed 30 seconds:

1. Reduce resolution to 640x360.
2. Reduce samples to 32.
3. Enable denoising (compensates for low samples).
4. Simplify shader complexity — remove subsurface scattering, reduce bounce counts.
5. Verify GPU is being used:

```python
print(f"Device: {bpy.context.scene.cycles.device}")
print(f"Compute type: {bpy.context.preferences.addons['cycles'].preferences.compute_device_type}")
```

If stuck on CPU, try different compute device types (CUDA -> OPTIX -> METAL).

---

## Cloud-Specific Issues

These issues only apply when rendering on a remote pod (RunPod). For local rendering, skip this section.

### SSH Tunnel Disconnection (MCP Unresponsive Mid-Session)

If blender-mcp stops responding during a session, the SSH tunnel likely dropped.

**Diagnosis:**
```bash
# Check if the tunnel process is still alive
ps aux | grep "ssh.*-L 9876"
```

**Fix:**
1. Kill any stale tunnel processes: `pkill -f "ssh.*-L 9876.*-L 5900"`
2. Get fresh SSH connection info (IP and port change on restart):
   ```
   python3 SKILL_DIR/scripts/runpod_manager.py status --env-file ~/blender-files/runpod/.env
   ```
3. Re-establish the tunnel with the new IP/port (see `runpod-infrastructure.md` Start a Session).
4. Blender and the MCP socket server should still be running on the pod — reconnection is usually seamless.

### File Transfer Failures (SCP Port Changes)

SCP commands fail with "Connection refused" after a pod restart.

**Cause:** SSH IP and port change every time the pod restarts. Cached or hardcoded values are stale.

**Fix:** Always query fresh connection info before any SCP command:
```
python3 SKILL_DIR/scripts/runpod_manager.py status --env-file ~/blender-files/runpod/.env
```
Extract the new `ip` and `port` from the JSON output and use those in the SCP command.

### Pod GPU Memory Exhaustion

Render crashes or Blender becomes unresponsive on the pod.

**Diagnosis:**
```bash
ssh -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT "nvidia-smi"
```

**Fixes:**
- Reduce render resolution and samples
- Reduce texture resolution (use 1k instead of 4k textures)
- Close unnecessary Blender windows/viewports
- Simplify the scene (reduce polygon count, remove unused objects)
- As a last resort, restart the pod: `python3 SKILL_DIR/scripts/runpod_manager.py stop` then `start`

### Xvfb/VNC Not Starting After Pod Restart

The virtual display or VNC server fails to start because apt packages were wiped.

**Cause:** Only `/runpod` persists across pod restarts. Packages installed via `apt` (xvfb, x11vnc, etc.) are ephemeral.

**Fix:** Re-run the startup script, which reinstalls deps:
```bash
ssh -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT "bash /runpod/start_session.sh"
```

If `start_session.sh` itself fails, run the full setup script:
```bash
ssh -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT < SKILL_DIR/scripts/pod_setup.sh
```

### Checkpoint Render Exceeding 1 MB

Large checkpoint renders slow down SCP transfer and can overflow LLM context when read as images.

**Fix:** Ensure checkpoint render settings are applied before rendering:
```python
scene = bpy.context.scene
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.cycles.samples = 64
scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 85
```

JPEG at 85% quality and 1024x1024 typically produces 100-300 KB files. If still too large, reduce quality to 75% or resolution to 800x800.

### Blender Process Crashed on Pod

MCP commands fail and the viewport in VNC is frozen or gone.

**Diagnosis:**
```bash
ssh -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT "cat /tmp/blender_stdout.log | tail -50"
```

**Fix:**
1. Check the log for crash reasons (out of memory, segfault, addon error).
2. Restart Blender on the pod:
   ```bash
   ssh -i ~/.runpod/ssh/RunPod-Key-Go root@IP -p PORT "bash /runpod/start_session.sh"
   ```
3. The MCP addon auto-starts via `/runpod/autostart_mcp.py`, so the socket server will reconnect.
4. Reload the .blend file if one was saved before the crash.
