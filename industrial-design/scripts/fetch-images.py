#!/usr/bin/env python3
"""Fetch images and convert to base64 data URIs.

Runs on the host machine (via Desktop Commander in sandboxed environments,
or directly via bash when curl/shell access is available).

Usage:
    python3 fetch-images.py --urls URL1 URL2 ... --output /tmp/image-data-uris-ID.json
    python3 fetch-images.py --input /tmp/image-urls.json --output /tmp/image-data-uris-ID.json
"""
import argparse
import base64
import json
import sys
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
TIMEOUT = 15  # seconds per image


def fetch_as_data_uri(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
            data = resp.read()
            encoded = base64.b64encode(data).decode("ascii")
            print(f"  \u2705 {len(data):,} bytes  {url[:80]}")
            return f"data:{content_type};base64,{encoded}"
    except Exception as e:
        print(f"  \u274c FAILED  {url[:80]}  ({e})")
        return None


def main():
    parser = argparse.ArgumentParser(description="Fetch images as base64 data URIs")
    parser.add_argument("--urls", nargs="*", help="Image URLs to fetch")
    parser.add_argument("--input", help="JSON file containing a list of URLs")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    urls = args.urls or []
    if args.input:
        with open(args.input) as f:
            urls.extend(json.load(f))

    if not urls:
        print("\u26a0\ufe0f  No URLs provided")
        sys.exit(1)

    print(f"\U0001f4f7 Fetching {len(urls)} images...")
    results = {}
    for url in urls:
        results[url] = fetch_as_data_uri(url)

    with open(args.output, "w") as f:
        json.dump(results, f)

    ok = sum(1 for v in results.values() if v is not None)
    print(f"\n\u2728 Done: {ok}/{len(urls)} images fetched -> {args.output}")


if __name__ == "__main__":
    main()
