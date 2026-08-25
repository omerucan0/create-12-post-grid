#!/usr/bin/env python3
"""Regression tests for campaign scaffolding and fail-closed validation."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
INIT = SKILL_ROOT / "scripts" / "init_campaign.py"
VALIDATE = SKILL_ROOT / "scripts" / "validate_manifest.py"
PACKAGE = SKILL_ROOT / "scripts" / "package_delivery.py"


def run(
    *args: str,
    expect: int = 0,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True, check=False, cwd=cwd)
    if result.returncode != expect:
        raise AssertionError(
            f"expected exit {expect}, got {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def write_posts(campaign: Path, posts: list[dict]) -> None:
    (campaign / "content" / "posts.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="grid-skill-test-") as temp:
        root = Path(temp)
        campaign = root / "anonymous-campaign"
        run(
            sys.executable, str(INIT), "--dest", str(campaign),
            "--brand-name", "Anonymous Brand", "--campaign-slug", "anonymous-launch",
            "--language", "en",
        )
        placeholder_result = run(
            sys.executable, str(VALIDATE), "--campaign", str(campaign), expect=1
        )
        if "placeholder" not in placeholder_result.stdout:
            raise AssertionError("untouched scaffold must fail on placeholder intake")
        brand_file = campaign / "brand" / "brand.json"
        brand = json.loads(brand_file.read_text(encoding="utf-8"))
        brand["sector"] = "Independent creative services"
        brand["offer"] = "A documented strategy workshop"
        brand["targetAudience"] = "Small teams preparing a product launch"
        brand_file.write_text(
            json.dumps(brand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        run(sys.executable, str(VALIDATE), "--campaign", str(campaign))
        node = shutil.which("node")
        if node is not None:
            run(
                node,
                str(campaign / "scripts" / "run-python.mjs"),
                "scripts/validate_manifest.py",
                "--campaign",
                ".",
                cwd=campaign,
            )

        metadata_files = [path for path in campaign.rglob("*") if path.name.startswith("._")]
        if metadata_files:
            raise AssertionError(f"campaign scaffold includes AppleDouble metadata: {metadata_files}")

        pristine = json.loads((campaign / "content" / "posts.json").read_text(encoding="utf-8"))

        cases: list[tuple[str, list[dict]]] = []
        cases.append(("eleven posts", copy.deepcopy(pristine[:-1])))
        duplicate = copy.deepcopy(pristine)
        duplicate[1]["slug"] = duplicate[0]["slug"]
        cases.append(("duplicate slug", duplicate))
        invalid_anchor = copy.deepcopy(pristine)
        invalid_anchor[0]["anchor"] = "somewhere"
        cases.append(("invalid anchor", invalid_anchor))
        unsupported_proof = copy.deepcopy(pristine)
        unsupported_proof[0]["claimType"] = "result"
        unsupported_proof[0]["proofSource"] = ""
        cases.append(("proof without source", unsupported_proof))

        for name, posts in cases:
            write_posts(campaign, posts)
            result = run(sys.executable, str(VALIDATE), "--campaign", str(campaign), expect=1)
            if "MANIFEST_FAIL" not in result.stdout:
                raise AssertionError(f"{name}: missing MANIFEST_FAIL")

        run(
            sys.executable, str(INIT), "--dest", str(root / "bad-slug"),
            "--brand-name", "Anonymous Brand", "--campaign-slug", "Bad Slug",
            expect=2,
        )

        write_posts(campaign, pristine)
        post_directory = campaign / "outputs" / "posts"
        for post in pristine:
            filename = f"{post['index']:02d}-{post['slug']}.png"
            (post_directory / filename).write_bytes(b"test-image")

        evidence_directory = campaign / "outputs" / "preview"
        (evidence_directory / "contact-sheet.png").write_bytes(b"test-contact-sheet")
        (evidence_directory / "qa-report.json").write_text("{}\n", encoding="utf-8")

        delivery_root = root / "delivery"
        run(
            sys.executable,
            str(PACKAGE),
            "--campaign",
            str(campaign),
            "--desktop-dir",
            str(delivery_root),
        )

        delivery = delivery_root / "Anonymous Brand - 12 Post Final"
        archive_path = delivery / "preview" / "anonymous-launch.zip"
        with zipfile.ZipFile(archive_path) as archive:
            members = set(archive.namelist())
            if len(members) != 14 or "preview/qa-report.json" not in members:
                raise AssertionError(f"delivery archive has unexpected contents: {sorted(members)}")

    print("TESTS_PASS valid=1 invalid=6 scaffold=clean python_runner=verified delivery=verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
