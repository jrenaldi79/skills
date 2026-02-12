#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard from CLAUDE.md and artifact-index.md.

Usage: python scripts/generate-dashboard.py [project-root]

Reads:  [project-root]/CLAUDE.md
        [project-root]/artifacts/artifact-index.md

Writes: [project-root]/index.html
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Phase metadata
# ---------------------------------------------------------------------------

PHASE_NAMES = {
    1: "Intake & Brief",
    2: "Research",
    3: "Ideation",
    4: "Refinement",
    5: "FMEA",
    6: "Final Spec",
}

PHASE_GATES = {1: "\U0001f513", 2: "\U0001f513", 3: "\U0001f512", 4: "\U0001f512", 5: "\U0001f513", 6: "\U0001f512"}

FIDELITY_COLORS = {"Doc": "#8a7a6a", "L1": "#c17840", "L2": "#2c2420", "L3": "#4a8c5c"}
DTS_COLORS = {"PASS": "#4a8c5c", "FAIL": "#b84830", "N/A": "#8a7a6a"}
FIDELITY_BG = {"Doc": "#f0ece6", "L1": "#fdf5ee", "L2": "#f0ece6", "L3": "#eef5f0"}
DTS_BG = {"PASS": "#eef5f0", "FAIL": "#fdf0ed", "N/A": "#f0ece6"}

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_claude_md(text):
    """Extract structured data from CLAUDE.md."""
    data = {}

    # Quick Context block
    m = re.search(r"## Quick Context\s*\n((?:- \*\*.*\n?)+)", text)
    if m:
        for line in m.group(1).strip().splitlines():
            km = re.match(r"- \*\*(.+?):\*\*\s*(.+)", line)
            if km:
                data[km.group(1).strip().lower()] = km.group(2).strip()

    # Key Decisions table (skip optional HTML comments before table)
    decisions = []
    m = re.search(r"## Key Decisions Made.*?\n(?:<!--.*?-->\s*\n|\s*\n)*\|.*\n\|[-| ]+\n((?:\|.*\n?)*)", text)
    if m:
        for row in m.group(1).strip().splitlines():
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 3 and cols[0] and not cols[0].startswith("["):
                decisions.append({"num": cols[0], "decision": cols[1], "rationale": cols[2]})
    data["decisions"] = decisions

    # Artifact Map table (skip optional HTML comments before table)
    artifact_map = []
    m = re.search(r"## Artifact Map.*?\n(?:<!--.*?-->\s*\n|\s*\n)*\|.*\n\|[-| ]+\n((?:\|.*\n?)*)", text)
    if m:
        for row in m.group(1).strip().splitlines():
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 4 and cols[0] and not cols[0].startswith("["):
                artifact_map.append(
                    {"id": cols[0], "file": cols[1].strip("`"), "status": cols[2], "description": cols[3]}
                )
    data["artifact_map"] = artifact_map

    # Active Design Direction (skip optional HTML comments / blank lines before bullets)
    direction = {}
    m = re.search(r"## Active Design Direction.*?\n(?:<!--.*?-->\s*\n|\s*\n)*((?:- \*\*.*\n?)+)", text)
    if m:
        for line in m.group(1).strip().splitlines():
            km = re.match(r"- \*\*(.+?):\*\*\s*(.+)", line)
            if km:
                val = km.group(2).strip()
                if val and not val.startswith("["):
                    direction[km.group(1).strip()] = val
    data["direction"] = direction

    # What's Next checklist (skip optional HTML comments before items)
    whats_next = []
    m = re.search(r"## What's Next.*?\n(?:<!--.*?-->\s*\n|\s*\n)*((?:- \[.\].*\n?)+)", text)
    if m:
        for line in m.group(1).strip().splitlines():
            nm = re.match(r"- \[([ xX])\]\s*(.+)", line)
            if nm:
                whats_next.append({"done": nm.group(1).strip().lower() == "x", "text": nm.group(2).strip()})
    data["whats_next"] = whats_next

    return data


def parse_artifact_index(text):
    """Extract artifact rows from artifact-index.md and group by phase."""
    artifacts = []
    m = re.search(r"\|.*ID.*\n\|[-| ]+\n((?:\|.*\n?)*)", text)
    if m:
        for row in m.group(1).strip().splitlines():
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 7:
                artifacts.append(
                    {
                        "id": cols[0],
                        "phase": cols[1],
                        "type": cols[2],
                        "description": cols[3],
                        "fidelity": cols[4],
                        "dts": cols[5],
                        "file": cols[6],
                    }
                )

    grouped = {}
    for a in artifacts:
        try:
            p = int(a["phase"])
        except ValueError:
            p = 0
        grouped.setdefault(p, []).append(a)
    return grouped


def current_phase_number(context):
    """Derive current phase number from CLAUDE.md context."""
    phase_str = context.get("current phase", "")
    m = re.search(r"(\d)", phase_str)
    return int(m.group(1)) if m else 1


# ---------------------------------------------------------------------------
# HTML generation helpers
# ---------------------------------------------------------------------------


def esc(text):
    """Escape HTML entities."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def badge(label, fg, bg):
    return (
        f'<span style="display:inline-block;font-size:9px;padding:2px 8px;'
        f'border-radius:10px;color:{fg};background:{bg}">{esc(label)}</span>'
    )


def fidelity_badge(level):
    fg = FIDELITY_COLORS.get(level, "#8a7a6a")
    bg = FIDELITY_BG.get(level, "#f0ece6")
    return badge(level, fg, bg)


def dts_badge(result):
    fg = DTS_COLORS.get(result, "#8a7a6a")
    bg = DTS_BG.get(result, "#f0ece6")
    return badge(result, fg, bg)


# ---------------------------------------------------------------------------
# Main HTML builder
# ---------------------------------------------------------------------------


def build_html(context, grouped_artifacts, project_root):
    product = esc(context.get("product", "Untitled Project"))
    phase_num = current_phase_number(context)
    last_updated = esc(context.get("last updated", datetime.now().strftime("%Y-%m-%d")))
    target_customer = esc(context.get("target customer", ""))

    # Determine phase states
    phases_with_artifacts = set(grouped_artifacts.keys())

    parts = []
    parts.append(
        """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard &mdash; """
        + product
        + """</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f8f7f5;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#5a4a3a;padding:24px;line-height:1.6}
.sheet{max-width:1100px;margin:0 auto;background:#faf9f7;border:1px solid #d5cec4;border-radius:12px;padding:32px;box-shadow:0 2px 16px rgba(0,0,0,.04)}
h1{font-size:18px;font-weight:600;color:#2c2420;letter-spacing:-.3px}
h2{font-size:14px;font-weight:600;color:#2c2420;margin-bottom:12px}
h3{font-size:12px;font-weight:600;color:#2c2420;margin-bottom:6px}
.subtitle{font-size:12px;color:#8a7a6a;margin-top:3px}
.meta{font-size:10px;color:#b0a090;font-family:"SF Mono",SFMono-Regular,Consolas,monospace}
.section-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#b0a090;font-weight:500;margin-bottom:8px}
.header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;padding-bottom:12px;border-bottom:1px solid #e8e2da}
.phase-badge{display:inline-block;font-size:9px;padding:3px 10px;border-radius:10px;color:#fff;background:#c17840;margin-left:8px;vertical-align:middle}
.divider{border:none;border-top:1px solid #e8e2da;margin:28px 0}

/* Timeline */
.timeline{display:flex;align-items:center;justify-content:space-between;margin:0 0 28px;padding:16px 0}
.timeline-step{display:flex;flex-direction:column;align-items:center;flex:1;position:relative}
.timeline-step .dot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;border:2px solid #d5cec4;background:#faf9f7;color:#8a7a6a;z-index:1}
.timeline-step.completed .dot{background:#c17840;border-color:#c17840;color:#fff}
.timeline-step.current .dot{background:#fff;border-color:#c17840;color:#c17840;box-shadow:0 0 0 3px rgba(193,120,64,.2)}
.timeline-step .label{font-size:9px;text-transform:uppercase;letter-spacing:.8px;color:#b0a090;margin-top:6px;text-align:center}
.timeline-step.completed .label,.timeline-step.current .label{color:#2c2420}
.timeline-step .gate{font-size:10px;margin-top:2px}
.timeline-line{flex:1;height:2px;background:#e8e2da;margin:0 -8px;position:relative;top:-14px;z-index:0}
.timeline-line.done{background:#c17840}

/* Artifact grid */
.phase-group{margin-bottom:24px}
.phase-group-title{font-size:11px;font-weight:600;color:#2c2420;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.phase-group-title .num{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:#c17840;color:#fff;font-size:10px;font-weight:600}
.artifact-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.card{background:#fff;border:1px solid #e8e2da;border-radius:8px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.card .card-id{font-size:9px;font-family:"SF Mono",SFMono-Regular,Consolas,monospace;color:#8a7a6a;margin-bottom:4px}
.card .card-type{font-size:8px;text-transform:uppercase;letter-spacing:.8px;color:#8a7a6a;background:#f0ece6;display:inline-block;padding:2px 6px;border-radius:4px;margin-bottom:6px}
.card .card-desc{font-size:11px;color:#5a4a3a;margin-bottom:8px}
.card .card-badges{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.card .card-link{font-size:10px;margin-top:8px}
.card .card-link a{color:#c17840;text-decoration:none}
.card .card-link a:hover{text-decoration:underline}
.card .missing{color:#b84830;font-size:9px;margin-top:4px}

/* Sidebar / panels */
.content-grid{display:grid;grid-template-columns:1fr 300px;gap:24px}
@media(max-width:800px){.content-grid{grid-template-columns:1fr}.artifact-grid{grid-template-columns:1fr}}
.sidebar .panel{background:#fff;border:1px solid #e8e2da;border-radius:8px;padding:14px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.sidebar .panel h3{margin-bottom:8px}
.sidebar .panel .kv{font-size:11px;color:#5a4a3a;margin-bottom:4px}
.sidebar .panel .kv strong{color:#2c2420;font-weight:500}

/* Decisions table */
.decisions-table{width:100%;border-collapse:collapse;font-size:11px;margin-top:8px}
.decisions-table th{text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#b0a090;font-weight:500;border-bottom:1px solid #e8e2da;padding:5px 8px}
.decisions-table td{padding:6px 8px;border-bottom:1px solid #f0ece6;color:#5a4a3a}
.decisions-table td:first-child{font-family:"SF Mono",SFMono-Regular,Consolas,monospace;color:#8a7a6a;width:30px}

/* Checklist */
.checklist{list-style:none;font-size:11px;color:#5a4a3a}
.checklist li{padding:3px 0;display:flex;align-items:baseline;gap:6px}
.checklist .check{color:#4a8c5c;font-size:12px}
.checklist .uncheck{color:#d5cec4;font-size:12px}

.footer{margin-top:24px;padding-top:12px;border-top:1px solid #e8e2da;font-size:9px;color:#b0a090;text-align:center}
</style>
</head>
<body>
<div class="sheet">
"""
    )

    # -- Header --
    parts.append(f'<div class="header"><div><h1>{product}')
    parts.append(f'<span class="phase-badge">Phase {phase_num}</span></h1>')
    if target_customer:
        parts.append(f'<div class="subtitle">Target: {target_customer}</div>')
    parts.append(f'</div><div class="meta">Last updated: {last_updated}</div></div>')

    # -- Phase Timeline --
    parts.append('<div class="timeline">')
    for i in range(1, 7):
        if i < phase_num:
            cls = "completed"
        elif i == phase_num:
            cls = "current"
        else:
            cls = ""
        parts.append(f'<div class="timeline-step {cls}">')
        parts.append(f'<div class="dot">{i}</div>')
        parts.append(f'<div class="label">{esc(PHASE_NAMES[i])}</div>')
        parts.append(f'<div class="gate">{PHASE_GATES[i]}</div>')
        parts.append("</div>")
        if i < 6:
            line_cls = "done" if i < phase_num else ""
            parts.append(f'<div class="timeline-line {line_cls}"></div>')
    parts.append("</div>")

    # -- Content grid: main + sidebar --
    has_direction = bool(context.get("direction"))
    if has_direction:
        parts.append('<div class="content-grid"><div>')
    else:
        parts.append("<div>")

    # -- Artifact Grid --
    parts.append('<div class="section-label">Artifacts</div>')
    if not grouped_artifacts:
        parts.append('<p style="font-size:11px;color:#8a7a6a">No artifacts yet.</p>')
    for phase in sorted(grouped_artifacts.keys()):
        if phase == 0:
            continue
        name = PHASE_NAMES.get(phase, f"Phase {phase}")
        parts.append(f'<div class="phase-group">')
        parts.append(f'<div class="phase-group-title"><span class="num">{phase}</span> {esc(name)}</div>')
        parts.append('<div class="artifact-grid">')
        for a in grouped_artifacts[phase]:
            file_path = a["file"].strip().lstrip("./")
            full_path = project_root / file_path
            exists = full_path.exists()
            parts.append('<div class="card">')
            parts.append(f'<div class="card-id">{esc(a["id"])}</div>')
            parts.append(f'<div class="card-type">{esc(a["type"])}</div>')
            parts.append(f'<div class="card-desc">{esc(a["description"])}</div>')
            parts.append('<div class="card-badges">')
            parts.append(fidelity_badge(a["fidelity"]))
            parts.append(dts_badge(a["dts"]))
            parts.append("</div>")
            if exists:
                parts.append(f'<div class="card-link"><a href="{esc(file_path)}">{esc(file_path)}</a></div>')
            else:
                parts.append(f'<div class="card-link"><a href="{esc(file_path)}">{esc(file_path)}</a></div>')
                parts.append('<div class="missing">\u26a0 File not found</div>')
            parts.append("</div>")
        parts.append("</div></div>")

    if has_direction:
        parts.append("</div>")  # close main column

    # -- Sidebar: Design Direction --
    if has_direction:
        parts.append('<div class="sidebar">')
        parts.append('<div class="panel">')
        parts.append("<h3>Design Direction</h3>")
        for key, val in context["direction"].items():
            parts.append(f'<div class="kv"><strong>{esc(key)}:</strong> {esc(val)}</div>')
        parts.append("</div>")
        parts.append("</div>")  # close sidebar
        parts.append("</div>")  # close content-grid

    if not has_direction:
        parts.append("</div>")  # close non-grid wrapper

    # -- Key Decisions --
    if context["decisions"]:
        parts.append('<hr class="divider">')
        parts.append('<div class="section-label">Key Decisions</div>')
        parts.append('<table class="decisions-table"><thead><tr>')
        parts.append("<th>#</th><th>Decision</th><th>Rationale</th>")
        parts.append("</tr></thead><tbody>")
        for d in context["decisions"]:
            parts.append(
                f'<tr><td>{esc(d["num"])}</td><td>{esc(d["decision"])}</td><td>{esc(d["rationale"])}</td></tr>'
            )
        parts.append("</tbody></table>")

    # -- What's Next --
    if context["whats_next"]:
        parts.append('<hr class="divider">')
        parts.append('<div class="section-label">What\'s Next</div>')
        parts.append('<ul class="checklist">')
        for item in context["whats_next"]:
            icon = '<span class="check">\u2713</span>' if item["done"] else '<span class="uncheck">\u25cb</span>'
            parts.append(f"<li>{icon} {esc(item['text'])}</li>")
        parts.append("</ul>")

    # -- Footer --
    parts.append(
        f'<div class="footer">Generated by Product Design Factory &middot; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>'
    )

    parts.append("</div></body></html>")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    project_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

    claude_md_path = project_root / "CLAUDE.md"
    artifact_index_path = project_root / "artifacts" / "artifact-index.md"

    # Validate inputs
    if not claude_md_path.exists():
        print(f"\u274c CLAUDE.md not found at {claude_md_path}")
        sys.exit(1)
    if not artifact_index_path.exists():
        print(f"\u274c artifact-index.md not found at {artifact_index_path}")
        sys.exit(1)

    print(f"\U0001f4c2 Project root: {project_root}")

    # Parse inputs
    claude_text = claude_md_path.read_text(encoding="utf-8")
    index_text = artifact_index_path.read_text(encoding="utf-8")

    context = parse_claude_md(claude_text)
    grouped = parse_artifact_index(index_text)

    # Validate artifact file paths
    total = sum(len(v) for v in grouped.values())
    missing = 0
    for phase_artifacts in grouped.values():
        for a in phase_artifacts:
            fp = a["file"].strip().lstrip("./")
            if not (project_root / fp).exists():
                missing += 1
                print(f"\u26a0\ufe0f  Missing: {fp}")

    print(f"\U0001f4e6 Artifacts: {total} found, {missing} missing files")

    # Generate HTML
    html = build_html(context, grouped, project_root)

    # Write output
    output_path = project_root / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\u2705 Dashboard written to {output_path}")


if __name__ == "__main__":
    main()
