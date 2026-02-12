#!/usr/bin/env python3
"""Replace external image URLs with base64 data URIs in an HTML file.

Runs on the host machine (via Desktop Commander in sandboxed environments,
or directly via bash when shell access is available).

Usage:
    python3 embed-images.py <draft-html> <image-json> <output-html>

Arguments:
    draft-html   Path to the HTML file with external <img src="https://..."> tags
    image-json   Path to JSON mapping URLs -> data URIs (from fetch-images.py)
    output-html  Path to write the final HTML with embedded images
"""
import json
import sys


def main():
    if len(sys.argv) != 4:
        print("Usage: embed-images.py <draft-html> <image-json> <output-html>")
        sys.exit(1)

    draft_path, json_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    with open(draft_path) as f:
        html = f.read()

    with open(json_path) as f:
        image_map = json.load(f)

    count = 0
    for url, data_uri in image_map.items():
        if data_uri and url in html:
            html = html.replace(url, data_uri)
            count += 1

    with open(output_path, "w") as f:
        f.write(html)

    print(f"\u2728 Embedded {count}/{len(image_map)} images -> {output_path}")


if __name__ == "__main__":
    main()
