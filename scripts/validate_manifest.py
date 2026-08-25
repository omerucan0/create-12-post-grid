#!/usr/bin/env python3
"""Validate campaign identity, post structure, ordered anchors, and proof rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ANCHORS = {
    "left-top", "center-top", "right-top", "left-bottom", "center",
    "right-bottom", "center-bottom",
}
ORDERED_ANCHORS = [
    "left-top", "center-top", "right-top", "left-bottom", "center",
    "right-bottom", "left-top", "center-bottom", "right-top",
    "left-bottom", "center-top", "right-bottom",
]
ROLES = {
    "problem", "aspiration", "education", "process", "authority",
    "differentiation", "proof", "faq", "cta",
}
CLAIMS = {"none", "narrative", "process", "proof", "result", "guarantee"}
PROOF_REQUIRED = {"proof", "result", "guarantee"}
SCALES = {"compact", "standard", "display"}
PLACEHOLDER_PREFIXES = ("replace with", "todo", "tbd")


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
    return None


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower().startswith(PLACEHOLDER_PREFIXES)


def validate_campaign(campaign: Path) -> list[str]:
    errors: list[str] = []
    brand = load_json(campaign / "brand" / "brand.json", errors)
    posts = load_json(campaign / "content" / "posts.json", errors)
    if not isinstance(brand, dict) or not isinstance(posts, list):
        return errors or ["brand must be an object and posts must be an array"]

    for field in (
        "brandName", "campaignSlug", "sector", "offer", "targetAudience",
        "campaignGoal", "language", "colors", "typography", "layoutMode", "output",
    ):
        if field not in brand:
            errors.append(f"brand.{field} is required")

    for field in ("brandName", "sector", "offer", "targetAudience", "campaignGoal", "language"):
        if field in brand and not nonempty(brand[field]):
            errors.append(f"brand.{field} must be a non-empty string")
        elif field in brand and is_placeholder(brand[field]):
            errors.append(f"brand.{field} still contains scaffold placeholder text")
    if "campaignSlug" in brand and not (
        isinstance(brand["campaignSlug"], str) and SLUG_RE.fullmatch(brand["campaignSlug"])
    ):
        errors.append("brand.campaignSlug must be lowercase hyphenated ASCII")

    colors = brand.get("colors")
    if not isinstance(colors, dict):
        errors.append("brand.colors must be an object")
    else:
        for field in ("background", "text", "accent"):
            if not isinstance(colors.get(field), str) or not HEX_RE.fullmatch(colors[field]):
                errors.append(f"brand.colors.{field} must be a 6-digit hex color")
        if colors.get("status") not in {"approved", "proposed"}:
            errors.append("brand.colors.status must be approved or proposed")

    typography = brand.get("typography")
    if not isinstance(typography, dict):
        errors.append("brand.typography must be an object")
    else:
        for field in ("headline", "body"):
            if not nonempty(typography.get(field)):
                errors.append(f"brand.typography.{field} must be non-empty")
        if typography.get("status") not in {"approved", "proposed"}:
            errors.append("brand.typography.status must be approved or proposed")

    output = brand.get("output")
    if not isinstance(output, dict) or output.get("width") != 1080 or output.get("height") != 1350:
        errors.append("brand.output must be exactly 1080x1350")

    if len(posts) != 12:
        errors.append(f"content/posts.json must contain exactly 12 posts, found {len(posts)}")
    indices = [post.get("index") for post in posts if isinstance(post, dict)]
    if indices != list(range(1, 13)):
        errors.append("post indices must be ordered exactly 1 through 12")
    slugs = [post.get("slug") for post in posts if isinstance(post, dict)]
    if len(slugs) != len(set(slugs)):
        errors.append("post slugs must be unique")

    for position, post in enumerate(posts, start=1):
        prefix = f"post {position:02d}"
        if not isinstance(post, dict):
            errors.append(f"{prefix} must be an object")
            continue
        slug = post.get("slug")
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            errors.append(f"{prefix}.slug must be lowercase hyphenated ASCII")
        if post.get("role") not in ROLES:
            errors.append(f"{prefix}.role is invalid")
        for field in ("eyebrow", "subtext", "backgroundPrompt"):
            if not nonempty(post.get(field)):
                errors.append(f"{prefix}.{field} must be non-empty")
        prompt = post.get("backgroundPrompt")
        if isinstance(prompt, str) and len(prompt.strip()) < 40:
            errors.append(f"{prefix}.backgroundPrompt is too short")
        lines = post.get("headlineLines")
        if not isinstance(lines, list) or not 1 <= len(lines) <= 3 or not all(nonempty(line) for line in lines):
            errors.append(f"{prefix}.headlineLines must contain 1 to 3 non-empty strings")
            line_count = 0
        else:
            line_count = len(lines)
        accent = post.get("accentLine")
        if not isinstance(accent, int) or accent < -1 or accent >= line_count:
            errors.append(f"{prefix}.accentLine must be -1 or a valid headline line index")
        if post.get("anchor") not in ANCHORS:
            errors.append(f"{prefix}.anchor is invalid")
        if post.get("headlineScale") not in SCALES:
            errors.append(f"{prefix}.headlineScale is invalid")
        claim = post.get("claimType")
        if claim not in CLAIMS:
            errors.append(f"{prefix}.claimType is invalid")
        if claim in PROOF_REQUIRED and not nonempty(post.get("proofSource")):
            errors.append(f"{prefix}.proofSource is required for claimType {claim}")
        if "proofSource" not in post or not isinstance(post.get("proofSource"), str):
            errors.append(f"{prefix}.proofSource must be a string")

    if brand.get("layoutMode") == "balanced-orderly":
        anchors = [post.get("anchor") for post in posts if isinstance(post, dict)]
        if anchors != ORDERED_ANCHORS:
            errors.append("balanced-orderly mode requires the fixed 12-post anchor matrix")
    elif brand.get("layoutMode") not in {"custom"}:
        errors.append("brand.layoutMode must be balanced-orderly or custom")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", required=True, type=Path)
    args = parser.parse_args()
    campaign = args.campaign.expanduser().resolve()
    errors = validate_campaign(campaign)
    if errors:
        print("MANIFEST_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("MANIFEST_PASS posts=12 size=1080x1350 layout=balanced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
