# Image Factory — Base64 Embedding Pipeline

Reusable module for any phase that produces HTML artifacts containing images.
Call these stages whenever you need to embed images into a self-contained HTML file.

## When to Use This Module

The Cowork artifact viewer enforces a Content Security Policy (CSP) that **blocks all
external resource loading**. External `<img src="https://...">` tags render as blank.
The only reliable strategy is **base64 data URI embedding**.

**Environment detection determines the method:**

| Environment | Image fetch method | How to detect |
|-------------|-------------------|---------------|
| Claude Code / CLI with bash | `curl -sL [url] \| base64` | Shell commands succeed, `curl` reaches external URLs |
| Cowork sandbox (network-restricted) | Desktop Commander MCP | `curl` blocked by proxy; DC `get_config` succeeds |
| No curl, no DC | Placeholder images only | Both methods fail during capability check |

**If you have working bash/curl access, use it directly** — skip the Desktop Commander
stages below and run `curl -sL [url] | base64` as before. The DC MCP pipeline exists
solely as a fallback for sandboxed environments where outbound HTTP is blocked.

---

## Stage 1: Discover Host Outputs Path (Sandbox Only)

> Skip this stage if bash/curl is available.

The sandbox shares a directory with the host at:
```
~/Library/Application Support/Claude/local-agent-mode-sessions/{session-ids}/outputs/
```

**Discovery procedure:**
1. From the sandbox, write a marker file: `echo "marker" > outputs/.image-factory-marker`
2. Use DC `execute_command` to find it on the host:
   ```
   find ~/Library/Application\ Support/Claude/local-agent-mode-sessions/ -name .image-factory-marker -maxdepth 4
   ```
3. The parent directory of the marker is the shared outputs path. Cache it for the session.

---

## Stage 2: Fetch Images

### Primary path (bash/curl available)

For each image URL extracted from the draft HTML:
```bash
curl -sL -o /tmp/img-{n}.jpg "[url]"
base64 < /tmp/img-{n}.jpg
```
Build a mapping of URL to data URI inline.

### Fallback path (sandbox — via Desktop Commander)

1. Extract all `<img src="https://...">` URLs from the draft HTML.
2. Use DC `write_file` to write `scripts/fetch-images.py` to host `/tmp/fetch-images.py`
   (or copy from the template in `scripts/fetch-images.py`).
3. Use DC `execute_command` to run it:
   ```
   python3 /tmp/fetch-images.py --urls "[url1]" "[url2]" ... --output /tmp/image-data-uris-{artifact-id}.json
   ```
4. Output: JSON file mapping each URL to its `data:image/...;base64,...` data URI.
   Failed fetches map to `null` (don't fail the batch).

---

## Stage 3: Embed Images

### Primary path (bash available)

Replace each `src="https://..."` with `src="data:image/jpeg;base64,{encoded}"` directly
in the HTML string. Write the final HTML to `artifacts/`.

### Fallback path (sandbox — via Desktop Commander)

1. Copy the draft HTML to the shared outputs directory.
2. Use DC `write_file` to write `scripts/embed-images.py` to host `/tmp/embed-images.py`
   (or copy from the template in `scripts/embed-images.py`).
3. Use DC `execute_command` to run it:
   ```
   python3 /tmp/embed-images.py /path/to/draft.html /tmp/image-data-uris-{id}.json /path/to/outputs/final.html
   ```
4. Copy the final HTML from outputs back to `artifacts/`.

---

## Caller Interface

Any phase producing HTML with images calls the same pipeline. The only decision point
is **which fetch method to use**, determined once during the capability check.

| Artifact | Phase | Notes |
|----------|-------|-------|
| P2-VISREF-01.html | Research | Visual reference board — typically 10-20 images |
| P4-MOOD-01.html | Refinement | Mood board |
| P4-MATBOARD-01.html | Refinement | Material board |
| P4-RENDER-01.html | Refinement | Rendered concepts |
| P6-HERORENDER-01.html | Final Spec | Hero render presentation |

---

## Size Management

- Target images at **600-800px wide** (resize if needed)
- Prefer **JPEG** over PNG for photographic content (smaller encoded size)
- Base64 adds ~33% size overhead — keep the final HTML under **15MB**
- If an image is too large, resize with `sips --resampleWidth 800 /tmp/img.jpg` (macOS)
  or `convert -resize 800x /tmp/img.jpg /tmp/img-resized.jpg` (ImageMagick)

---

## Fallback Behavior

If Desktop Commander is unavailable AND curl is blocked:
1. Keep external `<img src="https://...">` URLs in the HTML
2. Add a visible banner at the top of the artifact:
   ```html
   <div style="background:#fff3cd;padding:12px;border:1px solid #ffc107;margin-bottom:16px;">
     Images could not be embedded. Install Desktop Commander MCP to enable
     image fetching in sandboxed environments. See capability-check.md for setup.
   </div>
   ```
3. Convert each `<img>` to a clickable `<a>` link so the user can view images manually
4. Warn the user in the chat

---

## Desktop Commander MCP Tool Reference

> Only relevant when running in a sandboxed environment without bash/curl access.

The MCP tool prefix depends on the server name in `claude_desktop_config.json`. If
configured as `"desktop-commander"`, tools are called as
`mcp__desktop-commander__execute_command`, etc. Use whatever prefix the MCP server exposes.

| Tool | Parameters | Use in image factory |
|------|-----------|---------------------|
| `execute_command` | `command: str, shell: str` | Run fetch/embed Python scripts on host |
| `write_file` | `path: str, content: str, mode: str` | Write Python scripts to host `/tmp/` |
| `read_file` | `path: str, offset: int, length: int` | Read result files on host |
| `get_config` | `{}` | Test DC availability during capability check |

**Installation** (add to `claude_desktop_config.json` → `mcpServers`):
```json
"desktop-commander": {
  "command": "npx",
  "args": ["-y", "@anthropic/desktop-commander"]
}
```
