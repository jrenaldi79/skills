# Materials & Products Guide

Detailed PBR material workflows for common product types. Read this before assigning any material in a product render.

---

## Table of Contents

1. [PBR Fundamentals](#pbr-fundamentals)
2. [Micro-Roughness Imperfections](#micro-roughness-imperfections)
3. [Product-Type Material Recipes](#product-type-material-recipes)
4. [Poly Haven Textures](#poly-haven-textures)
5. [Common Material Mistakes](#common-material-mistakes)

---

## PBR Fundamentals

Use `ShaderNodeBsdfPrincipled` for every material. It implements a physically-based shading model that responds correctly to lighting — which is the foundation of photorealism.

```python
import bpy

def create_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    # Clear defaults and rebuild
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat, bsdf, nodes, links
```

### Key Principled BSDF Inputs

| Input | Range | What It Controls |
|-------|-------|------------------|
| Base Color | RGB | The diffuse color of the surface |
| Metallic | 0.0–1.0 | 0 = dielectric (plastic, wood), 1 = metal |
| Roughness | 0.0–1.0 | 0 = mirror-smooth, 1 = fully diffuse |
| IOR | 1.0–2.5 | Index of refraction (glass=1.45, water=1.33, diamond=2.42) |
| Transmission | 0.0–1.0 | 0 = opaque, 1 = fully transparent |
| Coat Weight | 0.0–1.0 | Clear coat layer (car paint, ceramics, lacquer) |
| Sheen | 0.0–1.0 | Fabric-like sheen at grazing angles |
| Anisotropic | 0.0–1.0 | Directional roughness (brushed metal, hair) |

---

## Micro-Roughness Imperfections

Real surfaces are never uniformly smooth. Adding subtle roughness variation is one of the highest-impact improvements for photorealism. Without it, materials look plasticky and CG.

```python
def add_roughness_imperfection(nodes, links, bsdf, base_roughness=0.3, noise_scale=80):
    """Add subtle roughness variation to any material."""
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = noise_scale
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    # Narrow the range around the base roughness
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (base_roughness - 0.05, base_roughness - 0.05, base_roughness - 0.05, 1)
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (base_roughness + 0.08, base_roughness + 0.08, base_roughness + 0.08, 1)

    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])
```

Noise scale of 50–100 works for most products. Use higher values (150+) for very fine grain, lower (20–40) for visible surface variation.

---

## Product-Type Material Recipes

### Glass & Transparent Objects

Bottles, lenses, screens, crystal.

```python
mat, bsdf, nodes, links = create_material("Glass")
bsdf.inputs['Transmission'].default_value = 1.0
bsdf.inputs['IOR'].default_value = 1.45        # Standard glass
bsdf.inputs['Roughness'].default_value = 0.0    # Perfectly smooth
bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)  # Clear

# IMPORTANT: Increase light path bounces for glass
bpy.context.scene.cycles.max_bounces = 16
bpy.context.scene.cycles.transparent_max_bounces = 16
```

For colored glass, tint the Base Color. For frosted glass, increase Roughness to 0.1–0.3.

### Matte Plastic

Consumer electronics housings, toys, kitchenware.

```python
mat, bsdf, nodes, links = create_material("MattePlastic")
bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.25, 1)  # Dark plastic
bsdf.inputs['Roughness'].default_value = 0.5
bsdf.inputs['Specular IOR Level'].default_value = 0.5
add_roughness_imperfection(nodes, links, bsdf, base_roughness=0.5, noise_scale=60)
```

Add subtle color variation by connecting a noise texture to Base Color as well — real plastic has slight color inconsistency from the molding process.

### Glossy Plastic

Phone cases, appliance accents, glossy packaging.

```python
mat, bsdf, nodes, links = create_material("GlossyPlastic")
bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)  # Red
bsdf.inputs['Roughness'].default_value = 0.1
bsdf.inputs['Coat Weight'].default_value = 0.5
bsdf.inputs['Coat Roughness'].default_value = 0.05
add_roughness_imperfection(nodes, links, bsdf, base_roughness=0.1, noise_scale=100)
```

### Brushed Metal

Laptop bodies, appliance panels, watch cases.

```python
mat, bsdf, nodes, links = create_material("BrushedAluminum")
bsdf.inputs['Base Color'].default_value = (0.7, 0.72, 0.73, 1)  # Aluminum
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.25
bsdf.inputs['Anisotropic'].default_value = 0.4
bsdf.inputs['Anisotropic Rotation'].default_value = 0.0
```

The Anisotropic value stretches highlights along the brush direction. Rotate Anisotropic Rotation to match the real brush pattern.

### Dark / Black Metal

Camera bodies, tripods, matte black hardware.

**Never use pure black (0,0,0) for Base Color.** Pure black absorbs all light and erases geometric detail. Use dark grey instead.

```python
mat, bsdf, nodes, links = create_material("DarkMetal")
bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1)  # Dark grey, NOT black
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.35
add_roughness_imperfection(nodes, links, bsdf, base_roughness=0.35, noise_scale=80)
```

### Fabric & Soft Goods

Bags, pouches, upholstery, clothing on mannequins.

```python
mat, bsdf, nodes, links = create_material("Fabric")
bsdf.inputs['Base Color'].default_value = (0.15, 0.2, 0.35, 1)
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Sheen Weight'].default_value = 0.7
bsdf.inputs['Sheen Tint'].default_value = (1, 1, 1, 1)
```

For woven texture, add a Wave or Voronoi texture to the Bump/Normal input. Consider a displacement modifier for visible weave at close range.

### Leather

Watch straps, bags, wallets, seats.

```python
mat, bsdf, nodes, links = create_material("Leather")
bsdf.inputs['Base Color'].default_value = (0.15, 0.08, 0.04, 1)  # Brown leather
bsdf.inputs['Roughness'].default_value = 0.6
bsdf.inputs['Specular IOR Level'].default_value = 0.3

# Pore texture via Voronoi
voronoi = nodes.new('ShaderNodeTexVoronoi')
voronoi.inputs['Scale'].default_value = 150
voronoi.distance = 'CHEBYCHEV'

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.15

links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
```

### Glossy Ceramic

Mugs, vases, plates, bathroom fixtures.

```python
mat, bsdf, nodes, links = create_material("Ceramic")
bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.88, 1)  # Off-white
bsdf.inputs['Roughness'].default_value = 0.08
bsdf.inputs['Coat Weight'].default_value = 1.0
bsdf.inputs['Coat Roughness'].default_value = 0.03
```

The clear coat simulates the glaze layer. For matte/unglazed ceramic, remove the coat and increase roughness to 0.6–0.8.

### Rubber & Silicone

Phone cases, grips, seals, kitchen tools.

```python
mat, bsdf, nodes, links = create_material("Rubber")
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.7
bsdf.inputs['Specular IOR Level'].default_value = 0.2
bsdf.inputs['Subsurface Weight'].default_value = 0.05  # Slight light penetration
```

---

## Poly Haven Textures

When using Poly Haven PBR textures for ground planes or product surfaces:

1. Call `get_polyhaven_status` to verify availability.
2. Search with `search_polyhaven_assets(asset_type="textures", categories="wood,concrete,fabric")`.
3. Download with `download_polyhaven_asset`.
4. Apply with `set_texture(object_name, texture_id)`.

Good ground plane textures for product shots:
- `wood_table_001` — warm product photography surface
- `concrete_floor_02` — industrial/minimal
- `fabric_pattern_05` — soft goods context
- `marble_01` — luxury/premium feel

---

## Common Material Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| Pure black Base Color on metals | Absorbs all light, kills geometry detail | Use dark grey (v ≥ 0.10) |
| Uniform roughness (no variation) | Looks CG / plasticky | Add noise texture → roughness |
| Metallic on non-metals | Wrong reflection model, unrealistic | Metallic = 0 for plastic, wood, etc. |
| Forgetting to increase bounces for glass | Glass renders opaque or black | Set max_bounces ≥ 12 |
| Very high IOR on glass | Creates unrealistic diamond-like refraction | Glass = 1.45, water = 1.33 |
| Mixing Metallic and Transmission | Physically impossible combination | Use one or the other |
