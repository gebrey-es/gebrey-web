/* Vídeos de las apps para Google Play, en formato móvil 9:16 (720×1280), para la escena "Apps":
   - Sorteo en Regla: se graba su interfaz real (la app es una página web empaquetada) haciendo un sorteo
     por lista: se ve la lista, se pulsa "Sortear ahora", sale el ganador con confeti y se abre el acta.
     Hace falta la carpeta del proyecto Android (su index.html); se pasa con --sorteo <ruta a assets/>.
   - Repertorios Oposiciones: el temario va cifrado dentro de la app, así que el vídeo se monta con las
     capturas de su ficha de Google Play (pase de pantallas); se pasa con --fichas <carpeta con los png>.
   Uso: node record-apps.js --sorteo /ruta/app/src/main/assets --fichas /ruta/telefono
        (cualquiera de los dos por separado) */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const OUT = path.join(__dirname, 'src', 'assets', 'video');
const FPS = 30;
const W = 720, H = 1280;

function encode(listFile, base, crf = [28, 38]) {
  const common = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', listFile, '-vf', `fps=${FPS},scale=${W}:${H}:flags=lanczos,format=yuv420p`, '-an'];
  execFileSync('ffmpeg', [...common, '-c:v', 'libx264', '-preset', 'slow', '-crf', String(crf[0]), '-profile:v', 'high', '-movflags', '+faststart', `${base}.mp4`]);
  execFileSync('ffmpeg', [...common, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', String(crf[1]), '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', `${base}.webm`]);
  const kb = (p) => Math.round(fs.statSync(p).size / 1024);
  console.log(`${path.basename(base)}: mp4 ${kb(base + '.mp4')} KB · webm ${kb(base + '.webm')} KB`);
}

/* ---- Sorteo en Regla: captura en tiempo real de su interfaz (screencast de CDP) ---- */
async function sorteo(assetsDir) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'gebrey-sorteo-'));
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 405, height: 720 }, deviceScaleFactor: W / 405, isMobile: true, hasTouch: true, locale: 'es-ES', timezoneId: 'Atlantic/Canary' });
  const page = await ctx.newPage();
  // lo que en el móvil pone Android (anuncios, PDF, cámara) y Firebase (sorteos con QR) aquí no hace falta: se simula vacío
  await page.addInitScript(() => {
    window.Android = { copy() {}, share() {}, pdf() {}, scan() {}, hasPrivacy() { return true; }, openPrivacy() {}, hasReport() { return true; }, report() {}, pendingCode() { return ''; }, ads() {}, interstitial() {}, privacyOptions() { return false; }, sha() { return null; } };
    const nop = () => Promise.resolve(null);
    window.__FBSTUB = { createRaffle: nop, join: nop, joinUrl: () => '', leave: nop, myEntry: nop, parseCode: () => null, qrSvg: () => '', saveResult: nop, watchEntries: () => () => {}, watchRaffle: () => () => {} };
  });
  await page.route('**/fb.js', (route) => route.fulfill({ contentType: 'application/javascript', body: 'window.FB = window.__FBSTUB;' }));
  await page.goto('file://' + path.join(assetsDir, 'index.html'));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(600);
  const cdp = await ctx.newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => {
    const file = path.join(dir, `${String(frames.length).padStart(5, '0')}.jpg`);
    fs.writeFileSync(file, Buffer.from(data, 'base64'));
    frames.push({ file, t: metadata.timestamp });
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: W, maxHeight: H, everyNthFrame: 1 });
  await page.waitForTimeout(300);
  const t0 = Date.now();
  const wait = (s) => page.waitForTimeout(s * 1000);
  const smooth = (sel) => page.locator(sel).first().evaluate((e) => e.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  await wait(2.0);
  await smooth('#participantes'); await wait(2.0);           // la lista de participantes
  await smooth('#btnDraw'); await wait(1.4);
  await page.locator('#btnDraw').click(); await wait(7.5);   // el sorteo: nombres girando, ganador y confeti
  const acta = page.locator('#stageActa');
  if (await acta.isVisible().catch(() => false)) { await acta.click(); await wait(3.2); }   // el acta del sorteo
  const secs = (Date.now() - t0) / 1000;
  await cdp.send('Page.stopScreencast').catch(() => {});
  await browser.close();
  if (frames.length < 2) throw new Error('la captura no dio fotogramas');
  const tEnd = frames[0].t + secs + 0.4;
  const list = frames.map((f, i) => `file '${f.file}'\nduration ${Math.max(0.01, (i + 1 < frames.length ? frames[i + 1].t : tEnd) - f.t).toFixed(4)}`).join('\n') + `\nfile '${frames[frames.length - 1].file}'\n`;
  const listFile = path.join(dir, 'frames.txt');
  fs.writeFileSync(listFile, list);
  fs.mkdirSync(OUT, { recursive: true });
  encode(listFile, path.join(OUT, 'sorteoenregla-movil'));
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(`sorteoenregla: ${secs.toFixed(1)} s, ${frames.length} fotogramas`);
}

/* ---- Repertorios Oposiciones: pase de las capturas de la ficha, deslizando como si se pasara de pantalla ---- */
function repertorios(fichasDir) {
  const pngs = fs.readdirSync(fichasDir).filter((f) => /^captura-\d+.*\.png$/.test(f)).sort();
  if (!pngs.length) throw new Error('no hay capturas captura-N-*.png en ' + fichasDir);
  const hold = 2.4, slide = 0.55;
  const inputs = [...pngs, pngs[0]].map((f) => path.join(fichasDir, f));   // vuelve a la primera para que el bucle no dé un salto
  const args = ['-y', '-loglevel', 'error'];
  inputs.forEach((f) => args.push('-loop', '1', '-t', String(hold + slide), '-i', f));
  let chain = '';
  let prev = '[0:v]';
  let offset = hold;
  for (let i = 1; i < inputs.length; i++) {
    const out = i === inputs.length - 1 ? '[v]' : `[x${i}]`;
    chain += `${prev}[${i}:v]xfade=transition=slideleft:duration=${slide}:offset=${offset.toFixed(3)}${out};`;
    prev = out;
    offset += hold;
  }
  chain = chain.slice(0, -1);
  fs.mkdirSync(OUT, { recursive: true });
  const base = path.join(OUT, 'repertorios-movil');
  const vf = `scale=${W}:${H}:flags=lanczos,fps=${FPS},format=yuv420p`;
  execFileSync('ffmpeg', [...args, '-filter_complex', chain + `;[v]${vf}[o]`, '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-profile:v', 'high', '-movflags', '+faststart', `${base}.mp4`]);
  execFileSync('ffmpeg', [...args, '-filter_complex', chain + `;[v]${vf}[o]`, '-map', '[o]', '-an', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '36', '-row-mt', '1', '-deadline', 'good', '-cpu-used', '2', `${base}.webm`]);
  const kb = (p) => Math.round(fs.statSync(p).size / 1024);
  console.log(`repertorios: ${pngs.length} capturas, ${(inputs.length * hold).toFixed(1)} s · mp4 ${kb(base + '.mp4')} KB · webm ${kb(base + '.webm')} KB`);
}

(async () => {
  const a = process.argv.slice(2);
  const get = (k) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : null; };
  const s = get('--sorteo'), f = get('--fichas');
  if (!s && !f) { console.error('indica --sorteo <assets/> y/o --fichas <carpeta de capturas>'); process.exit(1); }
  if (s) await sorteo(path.resolve(s));
  if (f) repertorios(path.resolve(f));
})().catch((e) => { console.error(e.message); process.exit(1); });
