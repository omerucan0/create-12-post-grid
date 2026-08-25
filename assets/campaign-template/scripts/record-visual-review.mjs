import fs from 'node:fs/promises';
import path from 'node:path';

const args = process.argv.slice(2);
const valueFor = (flag) => {
  const index = args.indexOf(flag);
  return index === -1 ? '' : args[index + 1] ?? '';
};
const status = valueFor('--status').toLowerCase();
const notes = valueFor('--notes').trim();
if (!['pass', 'fail', 'unverified'].includes(status)) {
  throw new Error('--status must be pass, fail, or unverified');
}
if (status !== 'unverified' && !notes) {
  throw new Error('--notes is required when status is pass or fail');
}

const output = path.join(process.cwd(), 'outputs/visual-review.json');
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.writeFile(output, JSON.stringify({
  status: status.toUpperCase(),
  notes,
  inspectedAt: new Date().toISOString(),
}, null, 2) + '\n');
console.log(`VISUAL_REVIEW_RECORDED status=${status.toUpperCase()}`);
