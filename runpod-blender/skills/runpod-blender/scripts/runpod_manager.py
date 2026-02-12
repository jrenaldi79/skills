#!/usr/bin/env python3
"""RunPod Blender session manager.

Reads credentials from .env file (RUNPOD_API_KEY, RUNPOD_POD_ID).
Falls back to CLI args for backward compatibility.

Usage:
    python3 runpod_manager.py start [--env-file PATH]
    python3 runpod_manager.py stop [--env-file PATH]
    python3 runpod_manager.py status [--env-file PATH]
    python3 runpod_manager.py ssh-info [--env-file PATH]
    python3 runpod_manager.py create [--env-file PATH] [--gpu GPU_TYPE]

Legacy (still supported):
    python3 runpod_manager.py start <pod_id> <api_key>
    python3 runpod_manager.py stop <pod_id> <api_key>
    python3 runpod_manager.py create <api_key>
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

API_URL = "https://api.runpod.io/graphql"


def load_env_file(path: str) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                os.environ.setdefault(key, value)


def find_env_file() -> str | None:
    """Search for .env file in standard locations."""
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", ""), ".env"),
        os.path.expanduser("~/blender-files/runpod/.env"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def get_api_key() -> str:
    key = os.environ.get("RUNPOD_API_KEY", "")
    if not key:
        print("Error: RUNPOD_API_KEY not set. Check your .env file.", file=sys.stderr)
        sys.exit(1)
    return key


def get_pod_id() -> str:
    pod_id = os.environ.get("RUNPOD_POD_ID", "")
    if not pod_id:
        print("Error: RUNPOD_POD_ID not set. Check your .env file.", file=sys.stderr)
        sys.exit(1)
    return pod_id


def graphql(api_key: str, query: str) -> dict:
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "runpod-blender/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_pod_status(pod_id: str, api_key: str) -> dict:
    result = graphql(api_key, f'''{{
        pod(input: {{podId: "{pod_id}"}}) {{
            id name desiredStatus
            runtime {{
                uptimeInSeconds
                ports {{ ip isIpPublic privatePort publicPort type }}
            }}
        }}
    }}''')
    return result.get("data", {}).get("pod", {})


def get_ssh_info(pod_id: str, api_key: str) -> dict | None:
    pod = get_pod_status(pod_id, api_key)
    if not pod or not pod.get("runtime") or not pod["runtime"].get("ports"):
        return None
    for port in pod["runtime"]["ports"]:
        if port.get("privatePort") == 22 and port.get("type") == "tcp":
            return {"ip": port["ip"], "port": port["publicPort"]}
    return None


def start_pod(pod_id: str, api_key: str) -> dict:
    result = graphql(api_key, f'''mutation {{
        podResume(input: {{podId: "{pod_id}", gpuCount: 1}}) {{
            id desiredStatus
        }}
    }}''')
    if result.get("errors"):
        return {"error": result["errors"][0]["message"]}
    return result.get("data", {}).get("podResume", {})


def stop_pod(pod_id: str, api_key: str) -> dict:
    result = graphql(api_key, f'''mutation {{
        podStop(input: {{podId: "{pod_id}"}}) {{
            id desiredStatus
        }}
    }}''')
    if result.get("errors"):
        return {"error": result["errors"][0]["message"]}
    return result.get("data", {}).get("podStop", {})


def create_pod(api_key: str, gpu_type: str = "NVIDIA GeForce RTX 4080 SUPER") -> dict:
    result = graphql(api_key, f'''mutation {{
        podFindAndDeployOnDemand(input: {{
            name: "blender-remote"
            gpuTypeId: "{gpu_type}"
            imageName: "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
            volumeInGb: 50
            cloudType: COMMUNITY
            startSsh: true
            ports: "22/tcp"
        }}) {{
            id name desiredStatus
        }}
    }}''')
    if result.get("errors"):
        return {"error": result["errors"][0]["message"]}
    return result.get("data", {}).get("podFindAndDeployOnDemand", {})


def wait_for_ssh(pod_id: str, api_key: str, timeout: int = 120) -> dict | None:
    start = time.time()
    while time.time() - start < timeout:
        info = get_ssh_info(pod_id, api_key)
        if info:
            return info
        time.sleep(5)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: runpod_manager.py <command> [--env-file PATH] [options]")
        sys.exit(1)

    command = sys.argv[1]

    # Load .env file: explicit --env-file flag, or auto-discover
    env_file = None
    if "--env-file" in sys.argv:
        idx = sys.argv.index("--env-file")
        env_file = sys.argv[idx + 1]
        # Remove from argv so it doesn't interfere with positional args
        sys.argv.pop(idx)
        sys.argv.pop(idx)
    else:
        env_file = find_env_file()

    if env_file:
        load_env_file(env_file)

    # Determine api_key and pod_id from CLI args (legacy) or env vars
    # Legacy: runpod_manager.py start <pod_id> <api_key>
    # Legacy: runpod_manager.py create <api_key>
    remaining_args = sys.argv[2:]  # after command

    if command == "create":
        api_key = remaining_args[0] if remaining_args else get_api_key()
        gpu_type = "NVIDIA GeForce RTX 4080 SUPER"
        if "--gpu" in sys.argv:
            idx = sys.argv.index("--gpu")
            gpu_type = sys.argv[idx + 1]
        result = create_pod(api_key, gpu_type)
        print(json.dumps(result, indent=2))

    elif command in ("start", "stop", "status", "ssh-info"):
        if len(remaining_args) >= 2:
            # Legacy mode: positional args
            pod_id = remaining_args[0]
            api_key = remaining_args[1]
        else:
            # .env mode
            pod_id = remaining_args[0] if remaining_args else get_pod_id()
            api_key = get_api_key()

        if command == "start":
            result = start_pod(pod_id, api_key)
            print(json.dumps(result, indent=2))
            if "error" not in result:
                print("\nWaiting for SSH to become available...", file=sys.stderr)
                info = wait_for_ssh(pod_id, api_key)
                if info:
                    print(json.dumps({"ssh": info}, indent=2))
                else:
                    print("Timed out waiting for SSH.", file=sys.stderr)

        elif command == "stop":
            result = stop_pod(pod_id, api_key)
            print(json.dumps(result, indent=2))

        elif command == "status":
            pod = get_pod_status(pod_id, api_key)
            print(json.dumps(pod, indent=2))

        elif command == "ssh-info":
            info = get_ssh_info(pod_id, api_key)
            if info:
                print(json.dumps(info, indent=2))
            else:
                print('{"error": "No SSH info available. Pod may not be running."}')
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
