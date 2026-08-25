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

let unsupportedVersion = '';
for (const [command, ...prefix] of candidates) {
  const probe = spawnSync(command, [...prefix, '--version'], {
    encoding: 'utf8',
    windowsHide: true,
  });
  if (probe.error?.code === 'ENOENT' || probe.status !== 0) continue;
  if (probe.error) continue;

  const versionText = `${probe.stdout ?? ''} ${probe.stderr ?? ''}`.trim();
  const match = versionText.match(/Python\s+(\d+)\.(\d+)/i);
  const supported = match
    && (Number(match[1]) > 3 || (Number(match[1]) === 3 && Number(match[2]) >= 12));
  if (!supported) {
    unsupportedVersion = versionText || command;
    continue;
  }

  const result = spawnSync(command, [...prefix, ...args], { stdio: 'inherit' });
  if (result.error) {
    console.error(`Could not start ${command}: ${result.error.message}`);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

const installHint = process.platform === 'win32'
  ? 'Install it with: winget install --exact --id Python.Python.3.12'
  : process.platform === 'darwin'
    ? 'Install it from https://www.python.org/downloads/ or run: brew install python'
    : 'Install it with your system package manager (for Ubuntu/Debian: sudo apt install python3)';

if (unsupportedVersion) console.error(`Unsupported interpreter found: ${unsupportedVersion}`);
console.error(`Python 3.12+ is required. ${installHint}`);
console.error('You can also point to an existing interpreter with the PYTHON environment variable.');
process.exit(1);
