import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const root = process.cwd();
const brand = JSON.parse(await fs.readFile(path.join(root, 'brand/brand.json'), 'utf8'));
const posts = JSON.parse(await fs.readFile(path.join(root, 'content/posts.json'), 'utf8'));
const errors = [];
const hashes = new Set();
const tiles = [];

if (posts.length !== 12) errors.push(`Expected 12 posts, found ${posts.length}`);
for (const post of posts) {
  const filename = `${String(post.index).padStart(2, '0')}-${post.slug}.png`;
  for (const folder of ['assets/backgrounds', 'outputs/posts']) {
    const file = path.join(root, folder, filename);
    try {
      const metadata = await sharp(file).metadata();
      if (metadata.width !== brand.output.width || metadata.height !== brand.output.height) {
        errors.push(`${folder}/${filename} is ${metadata.width}x${metadata.height}`);
      }
    } catch (error) {
      errors.push(`Cannot read ${folder}/${filename}: ${error.message}`);
    }
  }
  const finalFile = path.join(root, 'outputs/posts', filename);
  try {
    const buffer = await fs.readFile(finalFile);
    const hash = crypto.createHash('sha256').update(buffer).digest('hex');
    if (hashes.has(hash)) errors.push(`Duplicate final image content: ${filename}`);
    hashes.add(hash);
    const tile = await sharp(buffer).resize(432, 540, { fit: 'cover' }).png().toBuffer();
    tiles.push({ input: tile, left: ((post.index - 1) % 3) * 432, top: Math.floor((post.index - 1) / 3) * 540 });
  } catch {}
}

const previewDir = path.join(root, 'outputs/preview');
await fs.mkdir(previewDir, { recursive: true });
if (tiles.length === 12) {
  await sharp({ create: { width: 1296, height: 2160, channels: 4, background: brand.colors.background } })
    .composite(tiles)
    .png({ compressionLevel: 9 })
    .toFile(path.join(previewDir, 'contact-sheet.png'));
} else {
  errors.push(`Contact sheet requires 12 readable final posts, found ${tiles.length}`);
}

let visualReview = { status: 'UNVERIFIED', notes: 'No recorded visual inspection.', inspectedAt: null };
try {
  const recorded = JSON.parse(await fs.readFile(path.join(root, 'outputs/visual-review.json'), 'utf8'));
  if (['PASS', 'FAIL', 'UNVERIFIED'].includes(recorded.status)) visualReview = recorded;
} catch {}

let browserRuntime = {
  status: 'UNVERIFIED',
  note: 'No successful Playwright render report was found.',
};
try {
  const renderReport = JSON.parse(await fs.readFile(path.join(root, 'outputs/render-report.json'), 'utf8'));
  const expectedFiles = posts.map((post) => `${String(post.index).padStart(2, '0')}-${post.slug}.png`);
  const reportMatches = renderReport.status === 'PASS'
    && renderReport.width === brand.output.width
    && renderReport.height === brand.output.height
    && JSON.stringify(renderReport.files) === JSON.stringify(expectedFiles);
  browserRuntime = reportMatches
    ? { status: 'PASS', note: `Playwright rendered ${expectedFiles.length} manifest-matched posts.` }
    : { status: 'FAIL', note: 'The render report does not match the current campaign manifest or output size.' };
} catch {}

const report = {
  generatedAt: new Date().toISOString(),
  technical: {
    status: errors.length ? 'FAIL' : 'PASS',
    checks: {
      manifestPosts: posts.length,
      readableFinalPosts: tiles.length,
      uniqueFinalHashes: hashes.size,
      expectedDimensions: `${brand.output.width}x${brand.output.height}`,
      contactSheet: tiles.length === 12 ? 'PASS' : 'FAIL',
    },
    errors,
  },
  visual: visualReview,
  browserRuntime,
  publication: { status: 'UNVERIFIED', note: 'No social platform upload or scheduling was performed.' },
};
await fs.writeFile(path.join(previewDir, 'qa-report.json'), JSON.stringify(report, null, 2) + '\n');

if (errors.length) {
  console.error(`VERIFY_FAIL errors=${errors.length}`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log(`VERIFY_PASS posts=12 unique=12 visual=${visualReview.status}`);
