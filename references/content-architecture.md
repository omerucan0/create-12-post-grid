# Content architecture

## Default 12-post story

- Posts 01-03: problem, tension, or aspiration.
- Posts 04-06: education, solution mechanics, or process.
- Posts 07-09: authority and differentiation without unsupported claims.
- Posts 10-11: sourced proof when available; otherwise FAQ, process, or objection handling.
- Post 12: clear CTA and next step.

## Balanced-orderly anchor matrix

Use this matrix unless the user explicitly approves another ordered system:

| Post | Anchor |
|---|---|
| 01 | `left-top` |
| 02 | `center-top` |
| 03 | `right-top` |
| 04 | `left-bottom` |
| 05 | `center` |
| 06 | `right-bottom` |
| 07 | `left-top` |
| 08 | `center-bottom` |
| 09 | `right-top` |
| 10 | `left-bottom` |
| 11 | `center-top` |
| 12 | `right-bottom` |

This creates variation without a scattered feed. Do not randomize anchors.

## Post manifest fields

Each item in `content/posts.json` must include:

- `index`: integer from 1 through 12.
- `slug`: unique lowercase hyphenated filename token.
- `role`: `problem`, `aspiration`, `education`, `process`, `authority`, `differentiation`, `proof`, `faq`, or `cta`.
- `eyebrow`: short context label.
- `headlineLines`: one to three exact overlay lines.
- `accentLine`: zero-based index of the line rendered in the accent color, or `-1` for none.
- `subtext`: supporting copy.
- `anchor`: one of the matrix anchors.
- `headlineScale`: `compact`, `standard`, or `display`.
- `claimType`: `none`, `narrative`, `process`, `proof`, `result`, or `guarantee`.
- `proofSource`: exact source note, or an empty string when no source is required.
- `backgroundPrompt`: the subject, composition, lighting, and negative-space direction for this post.

`proof`, `result`, and `guarantee` claims require a non-empty `proofSource`. A guarantee should normally be rejected unless the supplied source and business authority are unambiguous.

## Pair copy and image direction

- Place the main subject away from the text anchor.
- Keep the text-safe zone calm, low-detail, and high-contrast.
- Give adjacent posts different scene scale or camera position while preserving one visual world.
- Write exact short headlines; never ask the image model to draw the headline.
- Use repeated lighting, material, lens, and grading language to create family resemblance.
