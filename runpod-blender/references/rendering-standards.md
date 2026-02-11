# Rendering Standards Reference

Detailed technical standards for engine configuration, lighting, camera setup, and geometry. Read this before starting any product render.

---

## Table of Contents

1. [Engine Configuration](#engine-configuration)
2. [Lighting & Environment](#lighting--environment)
3. [Camera & Composition](#camera--composition)
4. [Geometry Realism](#geometry-realism)
5. [Render Settings Quick Reference](#render-settings-quick-reference)

---

## Engine Configuration

Always use Cycles. Eevee's rasterization approach lacks the ray-traced light bounces, caustics, and global illumination that make product renders look real.

```python
import bpy

bpy.context.scene.render.engine = 'CYCLES'

# Prefer GPU rendering — try CUDA, then OPTIX, then METAL, then fallback to CPU
prefs = bpy.context.preferences.addons['cycles'].preferences
for device_type in ['OPTIX', 'CUDA', 'METAL']:
    try:
        prefs.compute_device_type = device_type
        prefs.get_devices()
        bpy.context.scene.cycles.device = 'GPU'
        break
    except:
        continue
else:
    bpy.context.scene.cycles.device = 'CPU'
```

### Color Management

Set the view transform to produce accurate, film-like tones:

```python
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium Contrast'
```

Filmic handles highlights and shadows more gracefully than the default Standard transform. Use "Medium Contrast" as a starting point; adjust to "High Contrast" for dramatic product shots or "None" if doing post-processing.

---

## Lighting & Environment

Product lighting makes or breaks photorealism. The goal is controlled, directional light that reveals form, material, and edges.

### HDRI Lighting (Preferred)

Before downloading any HDRI, always check availability:

```
Call get_polyhaven_status first.
```

If Poly Haven is available, use a studio HDRI. Good defaults:
- `brown_photostudio_02` — warm neutral studio
- `studio_small_09` — clean, even illumination
- `photo_studio_loft_hall` — larger, more dramatic

#### HDRI Setup Pattern

Always add a Mapping node to control HDRI rotation:

```python
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

# Build node chain: Texture Coordinate -> Mapping -> Environment Texture -> Background -> Output
tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
env_tex = nodes.new('ShaderNodeTexEnvironment')
background = nodes.new('ShaderNodeBackground')
output = nodes.new('ShaderNodeOutputWorld')

links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
links.new(env_tex.outputs['Color'], background.inputs['Color'])
links.new(background.outputs['Background'], output.inputs['Surface'])

# Load HDRI (after downloading via download_polyhaven_asset)
# env_tex.image = bpy.data.images.load('/path/to/hdri.hdr')
background.inputs['Strength'].default_value = 0.8
```

#### Finding the Rim Light

Rotate the HDRI's Z-axis in the Mapping node until specular highlights catch the object's edges. This edge separation is what makes the product "pop" against the background.

```python
import math
mapping.inputs['Rotation'].default_value[2] = math.radians(45)  # Adjust incrementally
```

Test at 0, 45, 90, 135 degrees and pick the angle with the best edge definition.

#### Exposure Control

If the render is blown out:
1. Lower HDRI strength to 0.3-0.5.
2. Disable any additional lights that may be doubling the illumination.
3. Check the exposure setting: `bpy.context.scene.view_settings.exposure = -0.5`

### Fallback: 3-Point Light Rig

If Poly Haven is unavailable, build a procedural studio setup:

```python
import bpy
import math

def add_area_light(name, energy, location, rotation, size=1.0):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = [math.radians(r) for r in rotation]
    light.data.color = (1.0, 0.95, 0.9)  # Warm white ~5500K
    return light

# Key Light: 45 degrees above and to the right
add_area_light("Key", 500, (2, -2, 3), (45, 0, 45), size=2.0)

# Fill Light: Opposite side, softer
add_area_light("Fill", 150, (-2, -1, 2), (30, 0, -30), size=3.0)

# Rim Light: Behind and above for edge separation
add_area_light("Rim", 300, (0, 3, 3), (-45, 0, 180), size=1.5)
```

The fill light should be larger (softer) and weaker than the key. The rim light creates the edge highlights that separate the object from the background.

---

## Camera & Composition

### Focal Length

| Shot Type | Focal Length | Notes |
|-----------|-------------|-------|
| Standard product | 50mm-85mm | Minimizes distortion, natural perspective |
| Macro / detail | 85mm-135mm | Tight crop on textures, mechanisms, labels |
| Environmental / interior | 24mm-35mm | Only for context shots showing the product in use |

Avoid wide angles (<35mm) for hero product shots — they distort edges and exaggerate perspective.

### Depth of Field

Enable DOF for hero shots to draw focus and add cinematic quality:

```python
cam = bpy.context.scene.camera
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bpy.data.objects['ProductName']  # or use focus_distance
cam.data.dof.aperture_fstop = 4.0  # f/2.8-f/5.6 range
```

### Framing Rules

- Object fills **70-80%** of the frame. No unintended edge cropping.
- Place objects on a **ground plane** with a PBR material (wood, concrete, fabric, seamless studio sweep).
- Rotate the object **slightly off-axis** — a 15-30 degree diagonal rotation looks natural. Rigid front-on alignment reads as CAD, not photography.
- For multiple products, use **odd numbers** and vary heights/angles.

---

## Geometry Realism

### Bevel Modifier

Every hard-surface object needs beveled edges. In reality, no edge is infinitely sharp — and without a bevel, edges won't catch specular highlights, making the object look like a 3D model rather than a photograph.

| Object Size | Bevel Width | Examples |
|-------------|-------------|----------|
| Small (handheld) | 0.0005m-0.001m | Phones, earbuds, pens, USB drives |
| Medium | 0.001m-0.003m | Appliances, tools, bottles, speakers |
| Large | 0.002m-0.005m | Furniture, fixtures, large electronics |

```python
obj = bpy.data.objects['ProductName']
bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.001  # Adjust per object size
bevel.segments = 3
bevel.limit_method = 'ANGLE'
bevel.angle_limit = math.radians(30)
```

### Scale Verification

Before rendering, verify your object dimensions match reality:

```python
obj = bpy.data.objects['ProductName']
dims = obj.dimensions
print(f"Dimensions: {dims.x:.3f}m x {dims.y:.3f}m x {dims.z:.3f}m")
```

Common reference sizes: phone ~0.075x0.015x0.15m, coffee mug ~0.08x0.08x0.10m, laptop ~0.32x0.22x0.015m, chair ~0.50x0.50x0.85m.

---

## Render Settings Quick Reference

### Test Render (Iterative — Local)

```python
scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.compression = 50
```

### Cloud Checkpoint Render (RunPod)

Optimized for SCP transfer speed and LLM image analysis. Use this for all iterative design work on cloud pods. Apply before rendering, restore original settings after.

```python
scene = bpy.context.scene
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 85
scene.render.filepath = "/runpod/projects/<project>/checkpoint_render.jpg"
```

This typically produces files around 100-300 KB. After rendering:
1. SCP the file to the local project directory.
2. Open locally with `open <path>` so the user can view it.
3. Read the image to analyze it.

**Important:** Save and restore original render settings after a checkpoint render so they aren't accidentally used for the final delivery.

### Final Render (Delivery)

```python
scene = bpy.context.scene
scene.render.resolution_x = 1920  # or 3840 for 4K
scene.render.resolution_y = 1080  # or 2160 for 4K
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.compression = 15
```
