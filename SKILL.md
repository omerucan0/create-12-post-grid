---
name: jett-social-media
description: Create a brand-specific 12-post Instagram campaign with generated backgrounds, deterministic typography, visual review, and delivery-ready 4:5 assets. Use for coordinated social media grids, branded feed series, and launch campaigns.
---

# Jett Social Media

Build one coherent 12-post campaign without leaking identity from any other client. Generate text-free backgrounds first, add exact copy and an optional logo with the deterministic renderer, and inspect the complete 3x4 feed before delivery.

## Non-negotiable rules

- Use only the current user's brand inputs and explicitly approved references.
- Never invent metrics, customers, results, guarantees, testimonials, certifications, prices, or proof.
- Generate one background image per post. Do not make collages or pre-composed grids.
- Background generation must contain no text, letters, numbers, logos, watermarks, UI, or signatures.
- Add exact copy and the optional supplied logo only through the renderer.
- Use the fixed `balanced-orderly` anchor matrix. Do not randomize text placement.
- Treat visual QA as `UNVERIFIED` until a person or vision-capable agent actually inspects the contact sheet and representative full-size posts.
- Report technical rendering, visual review, browser/runtime, and publication readiness separately.

## Required intake

Read [references/intake-contract.md](references/intake-contract.md). Obtain or propose the brand name, sector, offer, target audience, campaign goal, language, colors, typography, voice, CTA, logo policy, and visual references. Mark proposed identity choices as proposed; do not silently treat them as approved brand facts.

## Workflow

1. Inspect all supplied files. Label each as a brand reference, visual reference, logo asset, or proof asset. Never infer that a mood image is the brand itself.
2. Scaffold a campaign:

   ```bash
   python scripts/init_campaign.py \
     --dest /absolute/path/to/campaign \
     --brand-name "Your Brand" \
     --campaign-slug your-brand-campaign \
     --language tr
   ```

3. Write `brand/brand.json` and `content/posts.json`. Follow [references/content-architecture.md](references/content-architecture.md), keep claims source-safe, and validate:

   ```bash
   python scripts/validate_manifest.py --campaign /absolute/path/to/campaign
   ```

4. Read [references/image-generation.md](references/image-generation.md). Use the built-in image generation tool once per post. Generate a 4:5 text-free scene with negative space matching that post's anchor. Save it as `assets/backgrounds/NN-slug.png`.
5. Render deterministic overlays from the campaign directory:

   ```bash
   npm install
   npx playwright install chromium
   npm run build
   ```

6. Read [references/qa-and-delivery.md](references/qa-and-delivery.md). Inspect `outputs/preview/contact-sheet.png` plus at least four representative full-size posts. Record the result, then rerun verification:

   ```bash
   node scripts/record-visual-review.mjs --status pass --notes "Reviewed the contact sheet and posts 01, 04, 08, and 12."
   npm run verify
   ```

7. Package the final delivery:

   ```bash
   python scripts/package_delivery.py \
     --campaign /absolute/path/to/campaign \
     --desktop-dir /absolute/path/to/delivery
   ```

## Evidence contract

- `PASS`: directly checked in the current run.
- `FAIL`: directly checked and a defect was found.
- `UNVERIFIED`: not directly exercised or visually inspected.
- A successful manifest check does not prove visual quality.
- A successful render does not prove publication, scheduling, or platform upload.

## Bundled resources

- `scripts/init_campaign.py`: copy the reusable campaign engine.
- `scripts/validate_manifest.py`: enforce identity, layout, content, and proof rules.
- `scripts/package_delivery.py`: produce a clean desktop delivery and ZIP.
- `scripts/test_skill.py`: run the skill's regression tests.
- `assets/campaign-template/`: deterministic HTML/Playwright/Sharp rendering project.
