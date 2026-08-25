import { spawnSync } from 'node:child_process';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node scripts/run-python.mjs <script.py> [arguments...]');
  process.exit(2);
}

const candidates = process.env.PYTHON
  ? [[process.env.PYTHON]]
  : process.platform === 'win32'
    ? [['python'], ['py', '-3'], ['python3']]
    : [['python3'], ['python']];

for (const [command, ...prefix] of candidates) {
  const result = spawnSync(command, [...prefix, ...args], { stdio: 'inherit' });
  if (result.error?.code === 'ENOENT') continue;

  if (result.error) {
    console.error(`Could not start ${command}: ${result.error.message}`);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

console.error('Python 3 is required. Install it or set the PYTHON environment variable.');
process.exit(1);
