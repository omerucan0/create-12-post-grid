#!/usr/bin/env python3
"""Scaffold a reusable 12-post campaign from the bundled template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", required=True, type=Path)
    parser.add_argument("--brand-name", required=True)
    parser.add_argument("--campaign-slug", required=True)
    parser.add_argument("--language", default="tr")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.brand_name.strip():
        print("ERROR: --brand-name cannot be empty", file=sys.stderr)
        return 2
    if not SLUG_RE.fullmatch(args.campaign_slug):
        print("ERROR: --campaign-slug must be lowercase hyphenated ASCII", file=sys.stderr)
        return 2

    destination = args.dest.expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        print(f"ERROR: destination is not empty: {destination}", file=sys.stderr)
        return 2

    skill_root = Path(__file__).resolve().parent.parent
    template = skill_root / "assets" / "campaign-template"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "._*", ".DS_Store", "Thumbs.db", "__pycache__", "node_modules"
        ),
    )

    brand_example = destination / "brand" / "brand.example.json"
    brand_file = destination / "brand" / "brand.json"
    posts_example = destination / "content" / "posts.example.json"
    posts_file = destination / "content" / "posts.json"

    brand = json.loads(brand_example.read_text(encoding="utf-8"))
    brand["brandName"] = args.brand_name.strip()
    brand["campaignSlug"] = args.campaign_slug
    brand["language"] = args.language
    brand_file.write_text(json.dumps(brand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    posts_file.write_text(posts_example.read_text(encoding="utf-8"), encoding="utf-8")
    brand_example.unlink()
    posts_example.unlink()

    shutil.copy2(
        skill_root / "scripts" / "validate_manifest.py",
        destination / "scripts" / "validate_manifest.py",
    )
    print(f"CAMPAIGN_CREATED {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
