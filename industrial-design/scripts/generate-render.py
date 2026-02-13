#!/usr/bin/env python3
"""Unified Gemini API image generation for product renders.

Two modes:
  --mode master     Text-to-image. Generates one render from a text prompt.
  --mode variation  Image-conditioned. Requires --reference path to master image.

Exit codes: 0 success, 1 API error, 2 no image in response, 3 missing env var.
"""
import argparse
import base64
import json
import os
import ssl
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate product renders via Google Gemini API"
    )
    p.add_argument(
        "--mode",
        choices=["master", "variation"],
        required=True,
        help="master = text-to-image; variation = image-conditioned",
    )
    p.add_argument("--prompt", required=True, help="Generation prompt")
    p.add_argument("--output", required=True, help="Output image file path")
    p.add_argument(
        "--reference",
        help="Path to master image (required for variation mode)",
    )
    p.add_argument(
        "--model",
        default="gemini-3-pro-image-preview",
        help="Model ID (default: gemini-3-pro-image-preview)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds (default: 120 master, 180 variation)",
    )
    return p.parse_args()


def build_payload(args):
    """Build the API request payload."""
    if args.mode == "master":
        parts = [{"text": args.prompt}]
    else:
        if not args.reference:
            print("ERROR: --reference is required for variation mode", file=sys.stderr)
            raise SystemExit(3)
        with open(args.reference, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode("ascii")
        mime = "image/jpeg" if args.reference.lower().endswith((".jpg", ".jpeg")) else "image/png"
        parts = [
            {"inlineData": {"mimeType": mime, "data": ref_b64}},
            {"text": args.prompt},
        ]
    return json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }).encode("utf-8")


def call_api(url, payload, timeout, ctx):
    """Make the API call and return parsed JSON."""
    req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        print(f"API ERROR {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        raise SystemExit(1)


def extract_and_save(data, output_path):
    """Extract image from response, save image file and .b64.txt companion."""
    candidates = data.get("candidates", [])
    if not candidates:
        print(f"No candidates in response: {json.dumps(data, indent=2)[:500]}", file=sys.stderr)
        raise SystemExit(2)

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            mime = part["inlineData"].get("mimeType", "image/png")
            b64_data = part["inlineData"]["data"]
            img_bytes = base64.b64decode(b64_data)

            # Write image file
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_bytes)

            # Write .b64.txt companion with complete data URI
            b64_path = output_path + ".b64.txt"
            with open(b64_path, "w") as f:
                f.write(f"data:{mime};base64,{b64_data}")

            print(f"OK: {output_path} ({len(img_bytes):,} bytes)")
            print(f"OK: {b64_path} ({os.path.getsize(b64_path):,} bytes)")
            return
        elif "text" in part:
            print(f"Model text: {part['text'][:200]}")

    print(f"No image in response. Part keys: {[list(p.keys()) for p in parts]}", file=sys.stderr)
    raise SystemExit(2)


def main():
    args = parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set", file=sys.stderr)
        raise SystemExit(3)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent?key={api_key}"
    timeout = args.timeout or (120 if args.mode == "master" else 180)
    ctx = ssl.create_default_context()

    print(f"Mode: {args.mode} | Model: {args.model} | Timeout: {timeout}s", flush=True)
    payload = build_payload(args)
    data = call_api(url, payload, timeout, ctx)
    extract_and_save(data, args.output)


if __name__ == "__main__":
    main()
