# gebrey.es

Web de GEBREY: un escaparate de proyectos en una sola página (ViaConextaHub, AppEquipo, Citras, GR Gestor, Marnin y Web y hosting) más el aviso legal, la página de gracias y `presupuesto.php` (el formulario de presupuesto, una frase con huecos, que manda el correo a hola@gebrey.es desde el propio hosting). El nombre del titular solo aparece en el aviso legal.

## Estructura

- `src/` — fuentes: `assets/css/site.css`, `assets/js/reel.js` (coreografía de scroll y vídeos), `assets/js/site.js` (tema y copiar correo), `assets/img/og.png`, `assets/video/` (los recorridos grabados por cada web).
- `build.py` — genera la página desde los datos de los proyectos (`PROJECTS`) y los textos de contacto (`PERSON`). Escribe `dist/` (para el servidor) y `preview/` (vista previa). Los vídeos de AppEquipo no se copian: se sirven desde `https://mbtenerife.es/video/` (`VIDEO_APPEQUIPO`).
- `record.js` — graba con Playwright un recorrido por cada web (portátil 1200×750 y móvil 640×1386) y lo guarda en `src/assets/video/`; vuelve a ejecutarlo cuando cambie una web (`node record.js marnin` para una sola). Los vídeos de AppEquipo son los del portal y se sirven desde mbtenerife.es.
- `record-citras.js` — graba la demo de Citras (mbtenerife.es/ambulancias) usándola en tiempo real, en portátil y móvil.
- `record-apps.js` — vídeos móviles 9:16 de la escena Apps: graba la interfaz real de Sorteo en Regla (hace falta la carpeta `assets/` de su proyecto Android) y monta el pase de pantallas de Repertorios Oposiciones con las capturas de su ficha de Google Play.
- `og.js` — regenera `src/assets/img/og.png` (la imagen al compartir) con Playwright; ejecútalo si cambia la lista de proyectos.
- `site/` — copia de `dist/` que se publica. **Es lo que sube el workflow.**
- `shot.js` — capturas con Playwright para revisar escritorio, móvil y tema claro.

## Cambiar algo

1. Edita `build.py` (textos, enlaces, teléfono) o `src/assets/…` (estilos, movimiento).
2. `python3 build.py` y copia `dist/` a `site/`.
3. Commit y push a `main`: el workflow **Publicar gebrey.es** sube `site/` por FTPS a `public_html`.

Los secretos del workflow (`FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`) están en Settings → Secrets and variables → Actions.
