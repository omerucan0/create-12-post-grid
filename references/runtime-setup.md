# Runtime setup

Jett Social Media uses two local runtimes:

- Python 3.12+ for campaign scaffolding, JSON manifest validation, regression tests, and delivery packaging.
- Node.js 20+ with npm for background normalization, Playwright rendering, contact sheets, and QA reports.

Installing system software changes the user's machine. Detect missing tools and explain the relevant command, but wait for the user's approval before installing them.

## Preflight

Run the commands appropriate for the operating system:

```text
Windows:       python --version  (or py -3 --version)
macOS/Linux:   python3 --version
All systems:   node --version
               npm --version
```

Continue when Python is at least 3.12 and Node.js is at least 20. If the installed versions are older, recommend a supported upgrade before creating the campaign.

## Python installation

### Windows 10/11

Use Windows Package Manager:

```powershell
winget install --exact --id Python.Python.3.12
```

Close and reopen the terminal after installation. Verify with `python --version`, then try `py -3 --version` if the first command is unavailable.

### macOS

Use the official installer from <https://www.python.org/downloads/> or Homebrew:

```bash
brew install python
```

Verify with `python3 --version`.

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3
```

Verify with `python3 --version`.

For other operating systems, use the instructions linked from <https://www.python.org/downloads/>.

## Node.js installation

Install a current LTS build from <https://nodejs.org/en/download>, reopen the terminal, and verify `node --version` plus `npm --version`.

The campaign renderer also needs Chromium. Install the project dependencies and browser from the scaffolded campaign directory:

```bash
npm install
npx playwright install chromium
```

## Python command selection

The generated campaign's npm scripts select `python`, `py -3`, or `python3` automatically. To use a specific interpreter, set `PYTHON` to its executable path before running npm:

```powershell
$env:PYTHON = "C:\Path\To\python.exe"
npm run validate
```

```bash
PYTHON=/path/to/python3 npm run validate
```
