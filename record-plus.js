/* Vídeos de GR Gestor Plus para su escena: se graba la app de verdad (la demo, con datos inventados)
   y se deja en src/assets/video/grgestorplus-portatil.{mp4,webm} (1200×750: la gestoría repasa su
   cartera y entra en un cliente) y grgestorplus-movil.{mp4,webm} (640×1386: la empresa en el móvil:
   inicio, cuentas, papeles y equipo).
   Hace falta la demo en marcha (en el repositorio de GR Gestor Plus: pnpm demo, o la API compilada con
   SUPERAPP_DEMO=true). Uso: node record-plus.js [dirección de la demo, por defecto http://localhost:8787] */
const { chromium, devices } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const DEMO = (process.argv[2] || 'http://localhost:8787').replace(/\/$/, '');
const OUT = path.join(__dirname, 'src', 'assets', 'video');
const FPS = 30;
const SHAPES = {
  portatil: { ctx: { viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 }, W: 1200, H: 750, crf: [27, 38], cuenta: 'gestoria' },
  movil: { ctx: { ...devices['iPhone 13'], defaultBrowserType: undefined, deviceScaleFactor: 1.64 }, W: 640, H: 1386, crf: [29, 40], cuenta: 'titular' },
};

function encode(listFile, base, W, H, crf) {
  const common = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listFile, '-vf', `fps=${FPS},scale=${W}:${H}:flags=lanczos,format=yuv420p`, '-an'];
  execFileSync('ffmpeg', [...common, '-c:v', 'libx264', '-preset', 'slow', '-crf', String(crf[0]), '-profile:v', 'high', '-movflags', '+faststart', `${base}.mp4`]);
  execFileSync('ffmpeg', [...common, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', String(crf[1]), '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', `${base}.webm`]);
  const kb = (p) => Math.round(fs.statSync(p).size / 1024);
  console.log(`${path.basename(base)}: mp4 ${kb(base + '.mp4')} KB · webm ${kb(base + '.webm')} KB`);
}

async function grabar(browser, forma, recorrido) {
  const S = SHAPES[forma];
  const ctx = await browser.newContext({ ...S.ctx, locale: 'es-ES', timezoneId: 'Europe/Madrid', colorScheme: 'light' });
  const page = await ctx.newPage();
  const r = await page.request.post(`${DEMO}/api/auth/entrar`, { data: { email: `${S.cuenta}@demo.invalid`, contrasena: 'demo-2026' } });
  if (!r.ok()) throw new Error(`no se puede entrar en la demo como ${S.cuenta}: ${r.status()}`);
  await page.goto(`${DEMO}/app/`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(800);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `grgestorplus-${forma}-`));
  const cdp = await ctx.newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => {
    const file = path.join(dir, `${String(frames.length).padStart(5, '0')}.jpg`);
    fs.writeFileSync(file, Buffer.from(data, 'base64'));
    frames.push({ file, t: metadata.timestamp });
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 90, maxWidth: S.W, maxHeight: S.H, everyNthFrame: 1 });
  await page.waitForTimeout(300);
  const t0 = Date.now();
  await recorrido(page);
  const secs = (Date.now() - t0) / 1000;
  await cdp.send('Page.stopScreencast').catch(() => {});
  await ctx.close();
  if (frames.length < 2) throw new Error('la captura no dio fotogramas');
  const tEnd = frames[0].t + secs + 0.4;
  const list = frames.map((f, i) => `file '${f.file}'\nduration ${Math.max(0.01, (i + 1 < frames.length ? frames[i + 1].t : tEnd) - f.t).toFixed(4)}`).join('\n') + `\nfile '${frames[frames.length - 1].file}'\n`;
  const listFile = path.join(dir, 'frames.txt');
  fs.writeFileSync(listFile, list);
  fs.mkdirSync(OUT, { recursive: true });
  encode(listFile, path.join(OUT, `grgestorplus-${forma}`), S.W, S.H, S.crf);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(`grgestorplus-${forma}: ${secs.toFixed(1)} s, ${frames.length} fotogramas`);
}

const esperar = (page, s) => page.waitForTimeout(s * 1000);
const bajar = (page, y) => page.evaluate((y) => window.scrollTo({ top: y, behavior: 'smooth' }), y);
async function ir(page, ruta) {
  await page.goto(ruta, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
}

// La gestoría: su cartera, un cliente por dentro (inicio, equipo y cuentas) y vuelta a la cartera.
async function portatil(page) {
  const cartera = page.url();
  await esperar(page, 2.6);
  const fila = page.getByText('Limpiezas Brillo SL').first();
  await fila.hover(); await esperar(page, 0.6);
  await fila.click(); await page.waitForLoadState('networkidle'); await esperar(page, 2.6);
  const cliente = page.url().replace(/\/$/, '');
  await ir(page, `${cliente}/equipo/cuadrante`); await esperar(page, 2.8);
  await ir(page, `${cliente}/cuentas`); await esperar(page, 1.4);
  await bajar(page, 420); await esperar(page, 2.2);
  await ir(page, cartera); await esperar(page, 1.2);
}

// La empresa en el móvil: el inicio con lo pendiente, cuentas, papeles, el equipo de hoy y vuelta al inicio.
async function movil(page) {
  const inicio = page.url().replace(/\/$/, '');
  await esperar(page, 2.2);
  await bajar(page, 700); await esperar(page, 2.0);
  await ir(page, `${inicio}/cuentas`); await esperar(page, 2.4);
  await ir(page, `${inicio}/papeles`); await esperar(page, 2.4);
  await ir(page, `${inicio}/equipo`); await esperar(page, 2.4);
  await ir(page, inicio); await esperar(page, 1.2);
}

(async () => {
  const solo = process.argv[3];
  const browser = await chromium.launch();
  try {
    if (!solo || solo === 'portatil') await grabar(browser, 'portatil', portatil);
    if (!solo || solo === 'movil') await grabar(browser, 'movil', movil);
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
