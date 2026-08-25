# QA and delivery

## Automated checks

- Exactly 12 manifest items and 12 final PNG files.
- Indices are exactly 1 through 12.
- Slugs and final-image hashes are unique.
- Anchors match the ordered matrix in `balanced-orderly` mode.
- Backgrounds and final posts are 1080x1350.
- Every proof, result, or guarantee claim has a source note.
- The contact sheet is generated from the final posts, not from backgrounds.

## Required visual checks

Inspect `outputs/preview/contact-sheet.png` and at least four representative full-size posts, including left-, center-, and right-anchored examples plus the CTA.

Check:

- The 3x4 feed reads as one campaign and does not feel scattered.
- Text blocks align consistently and stay within safe margins.
- Typography is legible and does not collide with important subjects.
- Accent color use is controlled.
- No background contains generated text, logos, watermarks, or malformed details.
- Copy is exact, grammatically correct, and source-safe.
- No unrelated brand identity appears.

Record `pass`, `fail`, or `unverified` with notes. If any defect remains, record `fail` and do not present the package as finished.

## Evidence labels

- `PASS`: directly checked during the current run.
- `FAIL`: directly checked and defective.
- `UNVERIFIED`: not directly exercised or inspected.

Keep technical QA, visual QA, browser/runtime readiness, and platform publication as separate facts.

## Delivery layout

Package to:

```text
<Brand Name> - 12 Post Final/
  01-slug.png
  ...
  12-slug.png
  preview/
    contact-sheet.png
    qa-report.json
    <campaign-slug>.zip
```

The twelve post files stay at the delivery root for easy direct upload. Supporting evidence belongs in `preview/`.
