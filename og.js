/* Regenera src/assets/img/og.png (1200×630, la imagen al compartir en redes y chats) a partir de la
   lista de proyectos de build.py y de los colores de src/assets/css/site.css (tema oscuro).
   Uso: node og.js   (necesita Playwright y acceso a Google Fonts) */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const root = __dirname;
  const projects = JSON.parse(execFileSync('python3', ['-c',
    'import build, json; print(json.dumps([[p["name"], p["color"]] for p in build.PROJECTS if p["slug"] != "jornada"]))'], { cwd: root }));
  const css = fs.readFileSync(path.join(root, 'src/assets/css/site.css'), 'utf8');
  const colors = {};
  for (const m of css.matchAll(/(--c-[a-z]+):\s*(#[0-9a-f]{6})/gi)) if (!colors[m[1]]) colors[m[1]] = m[2];  // la primera es la del tema oscuro
  const items = projects.map(([name, color]) => {
    const hex = colors[color.replace(/^var\(|\)$/g, '')] || '#f3e9d8';
    return `<span><i style="background:${hex}"></i>${name}</span>`;
  }).join('');
  const page_html = `<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
  html, body { margin: 0; }
  body { width: 1200px; height: 630px; overflow: hidden; background: #14100e; color: #f3e9d8; font-family: "Instrument Sans", sans-serif; position: relative; }
  .glow { position: absolute; inset: 0; background: radial-gradient(38% 55% at 68% 40%, rgba(255, 90, 71, .16), transparent 70%); }
  .mark { position: absolute; left: 74px; top: 122px; font-family: "Bricolage Grotesque"; font-weight: 800; font-size: 232px; line-height: .84; letter-spacing: -.045em; font-variation-settings: "wdth" 88, "opsz" 96; }
  .mark b { color: #ff5a47; font-weight: inherit; }
  .tag { position: absolute; left: 74px; top: 388px; font-family: "Bricolage Grotesque"; font-weight: 600; font-size: 38px; line-height: 1.18; letter-spacing: -.02em; font-variation-settings: "opsz" 96; }
  .row { position: absolute; left: 74px; right: 60px; top: 518px; display: flex; flex-wrap: wrap; gap: 10px 28px; font-size: 24px; color: #c1b09b; }
  .row span { display: inline-flex; align-items: center; gap: 10px; white-space: nowrap; }
  .row i { width: 13px; height: 13px; border-radius: 50%; display: inline-block; }
</style></head><body>
<div class="glow"></div>
<div class="mark">GEB<b>R</b>EY</div>
<div class="tag">Proyectos de software y web.</div>
<div class="row">${items}</div>
</body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.setContent(page_html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const out = path.join(root, 'src/assets/img/og.png');
  await page.screenshot({ path: out, type: 'png' });
  await browser.close();
  console.log('ok', out, projects.length, 'proyectos');
})();
