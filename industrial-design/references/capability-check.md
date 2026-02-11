# Capability Check & Fallback Matrix

Perform this check once at the start of every project, before Phase 2 (Research).

## Capability Checklist

Determine the status of each capability:

1. **Filesystem access** — Can you create directories and write files?
2. **Shell access** — Can you run standard commands (`mkdir`, `ls`, `curl`, `grep`, `sed`, `jq`)?
3. **Web research tools** — Are any of these available?
   - `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_research` (names may vary by harness)
4. **Image download** — Can you `curl -L` to fetch images?
5. **Vision / image inspection** — Can you actually see and analyze local images, or only verify metadata (size/type)?
6. **3D/CAD MCP tools** — Is Blender MCP and/or Fusion 360 MCP available? If not, you cannot claim CAD generation.

## Fallback Matrix

- **If web research tools unavailable** — Ask the user for competitor links, reference products, target standards/markets, and supplier/material preferences. Alternatively, proceed with clearly labeled "Assumption Mode" using general industry knowledge, and mark all unverified claims.

- **If image download available but vision inspection unavailable** — You may download and organize references and verify file type/size/resolution via shell, but you must request the user to visually confirm any DTS criteria that require seeing the image.

- **If CAD MCP unavailable** — You must deliver:
  - High-precision dimensioned technical drawings (SVG/HTML) with GD&T callouts where appropriate
  - A parametric dimension file (`design-parameters.yaml`)
  - Manufacturing-ready specifications sufficient for a CAD operator to model in Fusion/SolidWorks

## How to Determine Capabilities

Capabilities must be determined using **evidence**, not assumption.

- **Tool availability**: If the harness provides an explicit tool list or manifest, use that as the source of truth. If not, you may only claim a tool exists after you successfully invoke it and observe a valid result.

- **Shell/filesystem**: You may only claim access after successfully executing a simple command and seeing output (e.g., `pwd`, `ls`, `mkdir -p`).

- **Vision/image inspection**: You may only claim visual inspection capability if you can run an image-analysis step and receive semantic feedback about image contents. If you can only verify file metadata (via `file`, size, dimensions), state: "vision inspection unavailable; metadata-only verification."

- **CAD MCP presence**: You may only claim Blender/Fusion MCP is active if the harness exposes a named tool and you can successfully run a minimal test call. Otherwise, treat CAD MCP as unavailable and follow the fallback path.

If any capability is uncertain, mark it as **UNKNOWN** and use the safer fallback behavior.