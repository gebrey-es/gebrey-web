/* Graba un recorrido por cada web del escaparate y lo deja en src/assets/video/<slug>-portatil.{mp4,webm}
   (1200×750, como la pantalla ilustrada) y <slug>-movil.{mp4,webm} (640×1386, como el móvil de AppEquipo).
   El recorrido: se queda en la portada, baja con suavidad unas pantallas, se detiene y vuelve arriba,
   para que el bucle sea continuo. Fotograma a fotograma con Playwright y montaje con ffmpeg.
   Uso: node record.js            (todas)
        node record.js marnin     (solo una; también "marnin,citras")
        node record.js marnin m   (solo móvil: d = portátil, m = móvil) */
const { chromium, devices } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const SITES = {
  viaconextahub: { url: 'https://viaconextahub.es/' },
  citras: { url: 'https://mbtenerife.es/citras/' },
  marnin: { url: 'https://marnin.es/' },
  grgestor: { url: 'https://grgestor.es/' },
};
const FPS = 30;
const OUT = path.join(__dirname, 'src', 'assets', 'video');

const SHAPES = {
  // portátil: el mismo tamaño que el vídeo del portal de AppEquipo
  d: { suffix: 'portatil', ctx: { viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 }, size: '1200x750', reach: 4200, speed: 480, crf: [27, 38] },
  // móvil: un iPhone a escala 1,64 → 640×1384, que ffmpeg ajusta a 640×1386
  m: { suffix: 'movil', ctx: { ...devices['iPhone 13'], defaultBrowserType: undefined, deviceScaleFactor: 1.64 }, size: '640x1386', reach: 4400, speed: 560, crf: [29, 40] },
};

// perfil de velocidad trapezoidal: arranca y frena con suavidad, y en medio baja a ritmo constante
function profile(t, ramp = 0.14) {
  const a = ramp, b = 1 - ramp, area = 1 - ramp;      // distancia total normalizada
  if (t < a) return (t * t / (2 * a)) / area;
  if (t < b) return (a / 2 + (t - a)) / area;
  const u = 1 - t;
  return (area - u * u / (2 * a)) / area;
}
const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

async function settle(page) {
  // deja que carguen fuentes e imágenes perezosas: un paseo rápido por la página y vuelta arriba
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = 'auto';   // por CSSOM: algunas webs bloquean estilos inline por CSP
    document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = 'eager'; });
  });
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 500) { await page.evaluate((y) => window.scrollTo(0, y), y); await page.waitForTimeout(120); }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(1500);
}

async function record(browser, slug, shape) {
  const S = SHAPES[shape];
  const ctx = await browser.newContext({ ...S.ctx, locale: 'es-ES', timezoneId: 'Atlantic/Canary' });
  const page = await ctx.newPage();
  if (process.env.DEBUG) page.on('framenavigated', (f) => { if (f === page.mainFrame()) console.log('  navegación a', f.url()); });
  await page.goto(SITES[slug].url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await settle(page);
  const vh = S.ctx.viewport.height;
  const max = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
  const dist = Math.max(0, Math.min(max, S.reach));
  const down = Math.min(10, Math.max(4, dist / S.speed));        // segundos bajando
  const plan = [[1.6, () => 0], [down, (t) => profile(t) * dist], [1.1, () => dist], [1.3, (t) => (1 - easeInOut(t)) * dist]];
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `gebrey-${slug}-${shape}-`));
  let n = 0;
  for (const [secs, f] of plan) {
    const frames = Math.round(secs * FPS);
    for (let i = 0; i < frames; i++) {
      const y = Math.round(f(frames > 1 ? i / (frames - 1) : 1));
      await page.evaluate((y) => window.scrollTo(0, y), y);
      await page.screenshot({ path: path.join(dir, `${String(n++).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 90 });
    }
  }
  await ctx.close();
  fs.mkdirSync(OUT, { recursive: true });
  const base = path.join(OUT, `${slug}-${S.suffix}`);
  const common = ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, '%04d.jpg'), '-vf', `scale=${S.size.replace('x', ':')}:flags=lanczos,format=yuv420p`, '-an'];
  execFileSync('ffmpeg', [...common, '-c:v', 'libx264', '-preset', 'slow', '-crf', String(S.crf[0]), '-profile:v', 'high', '-movflags', '+faststart', `${base}.mp4`]);
  execFileSync('ffmpeg', [...common, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', String(S.crf[1]), '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', `${base}.webm`]);
  fs.rmSync(dir, { recursive: true, force: true });
  const kb = (p) => Math.round(fs.statSync(p).size / 1024);
  console.log(`${slug} ${S.suffix}: ${n} fotogramas, ${(n / FPS).toFixed(1)} s, recorre ${dist}px de ${max}px · mp4 ${kb(base + '.mp4')} KB · webm ${kb(base + '.webm')} KB`);
}

(async () => {
  const only = process.argv[2] ? process.argv[2].split(',') : Object.keys(SITES);
  const shapes = process.argv[3] ? process.argv[3].split('') : ['d', 'm'];
  const browser = await chromium.launch();
  for (const slug of only) {
    if (!SITES[slug]) { console.error('no conozco', slug); continue; }
    for (const shape of shapes) {
      // una web puede recargarse a mitad de grabación: se reintenta
      for (let intento = 1; ; intento++) {
        try { await record(browser, slug, shape); break; }
        catch (e) { console.error(`${slug} ${shape}: ${e.message.split('\n')[0]}`); if (intento >= 3) throw e; }
      }
    }
  }
  await browser.close();
})();
