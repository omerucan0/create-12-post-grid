# Image generation

Use the built-in image generation tool once per post. Twelve separate calls and twelve separate files are preferred because each composition needs its own text-safe area.

## Prompt skeleton

Combine these parts:

1. Brand-safe visual world derived only from the current user's approved references.
2. Post-specific subject and scene.
3. Camera position, lens feel, lighting, materials, and color grading.
4. A calm negative-space zone matching the manifest anchor.
5. Output constraints: vertical 4:5, one scene, no collage.
6. Negative constraints: no text, letters, numbers, logos, watermarks, signatures, UI, borders, or mockup frames.

Example structure:

> Create one premium vertical 4:5 campaign photograph for a [sector] brand. [Scene and subject]. [Lighting, lens, materials, color grade]. Keep the [anchor] region calm, dark or uncluttered for later typography. One continuous scene, no collage. No text, letters, numbers, logo, watermark, signature, interface, border, or frame.

## Reference discipline

- Pass brand references to establish the current brand's identity only.
- Pass visual references for mood or composition only.
- Do not pass unrelated client material.
- Use the minimum number of references needed for the post.

## Acceptance check for each background

- Correct 4:5 orientation.
- One coherent scene.
- No visible or pseudo text.
- No accidental logos or watermarks.
- Text anchor has enough negative space.
- Scene is meaningfully distinct from the other eleven while retaining campaign cohesion.

Save accepted files as `assets/backgrounds/NN-slug.png`, matching the manifest exactly.
