#!/usr/bin/env python3
"""Pod reminder hook — warns if RunPod pod is still running."""
import json
import os
import sys
import urllib.request


def main():
    hook_input = json.load(sys.stdin)
    cwd = hook_input.get("cwd", os.getcwd())

    # Find .env
    candidates = [
        os.path.join(cwd, ".env"),
        os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", ""), ".env"),
        os.path.expanduser("~/blender-files/runpod/.env"),
    ]
    env_file = next((p for p in candidates if p and os.path.exists(p)), None)
    if not env_file:
        sys.exit(0)  # No .env, nothing to check

    # Load env
    env = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")

    api_key = env.get("RUNPOD_API_KEY", "")
    pod_id = env.get("RUNPOD_POD_ID", "")
    if not api_key or not pod_id:
        sys.exit(0)

    # Query pod status
    query = json.dumps({
        "query": f'{{ pod(input: {{podId: "{pod_id}"}}) {{ desiredStatus runtime {{ uptimeInSeconds }} }} }}'
    })
    req = urllib.request.Request(
        "https://api.runpod.io/graphql",
        data=query.encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        pod = data.get("data", {}).get("pod", {})
        status = pod.get("desiredStatus", "")
        uptime = pod.get("runtime", {}).get("uptimeInSeconds", 0) if pod.get("runtime") else 0

        if status == "RUNNING":
            hours = uptime / 3600
            cost = hours * 0.28
            print(json.dumps({
                "systemMessage": (
                    f"RunPod pod is still running (uptime: {hours:.1f}h, est. cost: ${cost:.2f}). "
                    f"Stop it when done: python3 scripts/runpod_manager.py stop --env-file .env"
                )
            }))
    except Exception:
        sys.exit(0)  # Network error — don't block the session


if __name__ == "__main__":
    main()
