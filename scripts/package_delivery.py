#!/usr/bin/env python3
"""Package exactly twelve rendered posts and QA evidence for handoff."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--desktop-dir", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    campaign = args.campaign.expanduser().resolve()
    desktop = args.desktop_dir.expanduser().resolve()
    brand_file = campaign / "brand" / "brand.json"
    posts_file = campaign / "content" / "posts.json"
    if not brand_file.exists() or not posts_file.exists():
        print("ERROR: campaign manifests are missing", file=sys.stderr)
        return 2
    brand = json.loads(brand_file.read_text(encoding="utf-8"))
    posts = json.loads(posts_file.read_text(encoding="utf-8"))
    expected = [f"{post['index']:02d}-{post['slug']}.png" for post in posts]
    source_dir = campaign / "outputs" / "posts"
    actual = sorted(path.name for path in source_dir.glob("*.png"))
    if len(expected) != 12 or actual != sorted(expected):
        print("ERROR: outputs/posts must contain exactly the 12 manifest PNG files", file=sys.stderr)
        return 2

    destination = desktop / f"{brand['brandName']} - 12 Post Final"
    if destination.exists() and any(destination.iterdir()):
        if not args.force:
            print(f"ERROR: delivery destination is not empty: {destination}", file=sys.stderr)
            return 2
        shutil.rmtree(destination)
    preview = destination / "preview"
    preview.mkdir(parents=True, exist_ok=True)

    for filename in expected:
        shutil.copy2(source_dir / filename, destination / filename)
    for filename in ("contact-sheet.png", "qa-report.json"):
        source = campaign / "outputs" / "preview" / filename
        if source.exists():
            shutil.copy2(source, preview / filename)

    zip_path = preview / f"{brand['campaignSlug']}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in expected:
            archive.write(destination / filename, arcname=filename)
        for filename in ("contact-sheet.png", "qa-report.json"):
            path = preview / filename
            if path.exists():
                archive.write(path, arcname=f"preview/{filename}")

    print(f"DELIVERY_PASS {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
