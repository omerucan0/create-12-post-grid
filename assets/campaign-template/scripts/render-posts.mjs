import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const root = process.cwd();
const brand = JSON.parse(await fs.readFile(path.join(root, 'brand/brand.json'), 'utf8'));
const posts = JSON.parse(await fs.readFile(path.join(root, 'content/posts.json'), 'utf8'));
const template = await fs.readFile(path.join(root, 'templates/post.html'), 'utf8');
const outputDir = path.join(root, 'outputs/posts');
await fs.mkdir(outputDir, { recursive: true });

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const dataUrl = async (filename) => {
  const extension = path.extname(filename).slice(1).toLowerCase();
  const mime = extension === 'jpg' || extension === 'jpeg' ? 'image/jpeg' : extension === 'svg' ? 'image/svg+xml' : 'image/png';
  const data = await fs.readFile(filename);
  return `data:${mime};base64,${data.toString('base64')}`;
};

const fontStack = (name) => `"${String(name).replaceAll('"', '')}", "Helvetica Neue", Arial, sans-serif`;
const washFor = (anchor) => {
  if (anchor.startsWith('left')) return 'linear-gradient(90deg, rgba(0,0,0,.68) 0%, rgba(0,0,0,.22) 60%, rgba(0,0,0,.06) 100%)';
  if (anchor.startsWith('right')) return 'linear-gradient(270deg, rgba(0,0,0,.68) 0%, rgba(0,0,0,.22) 60%, rgba(0,0,0,.06) 100%)';
  if (anchor.endsWith('top')) return 'linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.10) 62%)';
  if (anchor.endsWith('bottom')) return 'linear-gradient(0deg, rgba(0,0,0,.68) 0%, rgba(0,0,0,.10) 68%)';
  return 'radial-gradient(circle at center, rgba(0,0,0,.55), rgba(0,0,0,.12) 72%)';
};

const logoConfig = brand.logo ?? { enabled: false };
let logoMarkup = '';
let logoPosition = 'left: 72px; bottom: 58px;';
if (logoConfig.enabled) {
  if (!logoConfig.file) throw new Error('brand.logo.enabled is true but brand.logo.file is empty');
  const logoPath = path.resolve(root, logoConfig.file);
  const logoData = await dataUrl(logoPath);
  const positions = {
    'bottom-left': 'left: 72px; bottom: 58px;',
    'bottom-right': 'right: 72px; bottom: 58px;',
    'top-left': 'left: 72px; top: 58px;',
    'top-right': 'right: 72px; top: 58px;',
  };
  logoPosition = positions[logoConfig.anchor] ?? positions['bottom-left'];
  logoMarkup = `<img class="logo" src="${logoData}" alt="">`;
}

const browser = await chromium.launch({ headless: true });
const renderedFiles = [];
try {
  const page = await browser.newPage({ viewport: brand.output, deviceScaleFactor: 1 });
  for (const post of posts) {
    const filename = `${String(post.index).padStart(2, '0')}-${post.slug}.png`;
    const background = await dataUrl(path.join(root, 'assets/backgrounds', filename));
    const headline = post.headlineLines.map((line, index) =>
      `<span class="${index === post.accentLine ? 'accent' : ''}">${escapeHtml(line)}</span>`
    ).join('');
    const replacements = {
      LANG: escapeHtml(brand.language),
      BODY_FONT: fontStack(brand.typography.body),
      HEADLINE_FONT: fontStack(brand.typography.headline),
      TEXT_COLOR: brand.colors.text,
      BACKGROUND_COLOR: brand.colors.background,
      ACCENT_COLOR: brand.colors.accent,
      BACKGROUND: background,
      WASH: washFor(post.anchor),
      INDEX: String(post.index).padStart(2, '0'),
      ANCHOR: post.anchor,
      EYEBROW: escapeHtml(post.eyebrow),
      HEADLINE_SCALE: post.headlineScale,
      HEADLINE: headline,
      SUBTEXT: escapeHtml(post.subtext),
      LOGO: logoMarkup,
      LOGO_POSITION: logoPosition,
      LOGO_WIDTH: Number(logoConfig.width ?? 160),
    };
    let html = template;
    for (const [key, value] of Object.entries(replacements)) {
      html = html.replaceAll(`{{${key}}}`, String(value));
    }
    await page.setContent(html, { waitUntil: 'load' });
    await page.screenshot({ path: path.join(outputDir, filename), fullPage: false });
    renderedFiles.push(filename);
  }
} finally {
  await browser.close();
}

await fs.writeFile(path.join(root, 'outputs/render-report.json'), JSON.stringify({
  status: 'PASS',
  renderedAt: new Date().toISOString(),
  files: renderedFiles,
  width: brand.output.width,
  height: brand.output.height,
}, null, 2) + '\n');

console.log(`RENDER_PASS count=${posts.length} size=${brand.output.width}x${brand.output.height}`);
