/* Graba la demo de Citras (https://citras.es/demo/, la de GebRey) usándola de verdad, en tiempo real, y deja
   src/assets/video/citras-portatil.{mp4,webm} (1200×750) y citras-movil.{mp4,webm} (640×1386). Portátil: el
   centro de coordinación recibe un aviso urgente, activa el vehículo libre que antes llega, rehace las rutas y
   repasa la flota. Móvil: el equipo de un vehículo guarda su revisión y quien espera lo ve llegar en el mapa.
   La captura es en tiempo real (screencast de CDP) y se monta con ffmpeg.
   Los vídeos de ahora son los de la portada de citras.es: los graba, con este mismo guion, `python3 tools/citras.py
   videos` en gebrey-es/mbtenerife (la web de citras.es), y se copian aquí. Mientras citras.es no esté publicada,
   CITRAS_DEMO puede apuntar a esa demo servida en local.
   Uso: node record-citras.js        (los dos)
        node record-citras.js d      (solo portátil; m = solo móvil) */
const { chromium, devices } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const URL = process.env.CITRAS_DEMO || 'https://citras.es/demo/';
const OUT = path.join(__dirname, 'src', 'assets', 'video');
const FPS = 30;

const SHAPES = {
  d: { suffix: 'portatil', ctx: { viewport: { width: 1200, height: 750 }, deviceScaleFactor: 1 }, size: { width: 1200, height: 750 }, out: '1200:750', crf: [26, 36] },
  m: { suffix: 'movil', ctx: { ...devices['iPhone 13'], defaultBrowserType: undefined, deviceScaleFactor: 1.64 }, size: { width: 640, height: 1384 }, out: '640:1386', crf: [28, 38] },
};

// el guion de cada grabación: esperas (segundos) y clics (selectores), en orden
const SCRIPTS = {
  d: [
    3.0, ['click', '#simUrg'],                       // llega un aviso urgente
    3.2, ['click', '[data-activar]'],                // se activa la unidad que antes llega
    4.0, ['click', '[data-pest="prog"]'],            // rutas…
    1.8, ['click', '#optimizar'],                    // …replanificadas
    3.2, ['click', '[data-pest="flota"]'],           // la flota
    3.0, ['click', '[data-pest="curso"]'],           // y de vuelta a lo que está en curso
    3.0,
  ],
  m: [
    2.2, ['click', '[data-vista="trip"]'],           // la app de la tripulación
    2.6, ['scroll', '[data-todo-ok]'],               // la revisión de la ambulancia…
    1.4, ['click', '[data-todo-ok]'],
    1.4, ['click', '[data-guardar-rev]'],            // …guardada
    2.6, ['scroll', 'header.barra'],
    1.2, ['click', '[data-vista="pac"]'],            // lo que ve el paciente: su ambulancia llegando
    4.6,
  ],
};

async function run(step, page) {
  if (typeof step === 'number') return page.waitForTimeout(step * 1000);
  const [what, sel] = step;
  const el = page.locator(sel).first();
  if (what === 'scroll') return el.evaluate((e) => e.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  await el.waitFor({ state: 'visible', timeout: 8000 });
  return el.click();
}

async function record(browser, shape) {
  const S = SHAPES[shape];
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `gebrey-citras-${shape}-`));
  const ctx = await browser.newContext({ ...S.ctx, locale: 'es-ES', timezoneId: 'Atlantic/Canary' });
  const page = await ctx.newPage();
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  // captura en tiempo real por CDP: cada repintado llega como un fotograma con su marca de tiempo
  // (así el móvil emulado se graba a su escala real, cosa que recordVideo no hace bien)
  const cdp = await ctx.newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => {
    const file = path.join(dir, `${String(frames.length).padStart(5, '0')}.jpg`);
    fs.writeFileSync(file, Buffer.from(data, 'base64'));
    frames.push({ file, t: metadata.timestamp });
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: S.size.width, maxHeight: S.size.height, everyNthFrame: 1 });
  await page.waitForTimeout(400);
  const t0 = Date.now();
  for (const step of SCRIPTS[shape]) await run(step, page);
  const secs = (Date.now() - t0) / 1000;
  await cdp.send('Page.stopScreencast').catch(() => {});
  await ctx.close();
  if (frames.length < 2) throw new Error('la captura no dio fotogramas');
  // lista para ffmpeg: cada fotograma dura hasta el siguiente; el último, hasta el final del guion
  const tEnd = frames[0].t + secs + 0.4;
  const list = frames.map((f, i) => `file '${f.file}'\nduration ${Math.max(0.01, (i + 1 < frames.length ? frames[i + 1].t : tEnd) - f.t).toFixed(4)}`).join('\n') + `\nfile '${frames[frames.length - 1].file}'\n`;
  const listFile = path.join(dir, 'frames.txt');
  fs.writeFileSync(listFile, list);
  fs.mkdirSync(OUT, { recursive: true });
  const base = path.join(OUT, `citras-${S.suffix}`);
  const common = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listFile, '-vf', `fps=${FPS},scale=${S.out}:flags=lanczos,format=yuv420p`, '-an'];
  execFileSync('ffmpeg', [...common, '-c:v', 'libx264', '-preset', 'slow', '-crf', String(S.crf[0]), '-profile:v', 'high', '-movflags', '+faststart', `${base}.mp4`]);
  execFileSync('ffmpeg', [...common, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', String(S.crf[1]), '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', `${base}.webm`]);
  fs.rmSync(dir, { recursive: true, force: true });
  const kb = (p) => Math.round(fs.statSync(p).size / 1024);
  console.log(`citras ${S.suffix}: ${secs.toFixed(1)} s, ${frames.length} fotogramas capturados · mp4 ${kb(base + '.mp4')} KB · webm ${kb(base + '.webm')} KB`);
}

(async () => {
  const shapes = process.argv[2] ? process.argv[2].split('') : ['d', 'm'];
  const browser = await chromium.launch();
  for (const shape of shapes) await record(browser, shape);
  await browser.close();
})();
