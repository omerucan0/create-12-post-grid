import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const root = process.cwd();
const posts = JSON.parse(await fs.readFile(path.join(root, 'content/posts.json'), 'utf8'));
const brand = JSON.parse(await fs.readFile(path.join(root, 'brand/brand.json'), 'utf8'));
const width = brand.output.width;
const height = brand.output.height;

for (const post of posts) {
  const filename = `${String(post.index).padStart(2, '0')}-${post.slug}.png`;
  const source = path.join(root, 'assets/backgrounds', filename);
  const temporary = `${source}.normalized.png`;
  try {
    await fs.access(source);
  } catch {
    throw new Error(`Missing background: ${source}`);
  }
  await sharp(source)
    .resize(width, height, { fit: 'cover', position: 'centre' })
    .png({ compressionLevel: 9 })
    .toFile(temporary);
  await fs.rename(temporary, source);
}

console.log(`NORMALIZE_PASS count=${posts.length} size=${width}x${height}`);
