# gebrey.es

Web de GEBREY: una sola página con los productos (GR Gestor; GR Gestor Plus; GR Fichajes, el registro de jornada de la familia GR Gestor; Citras; ViaConextaHub, y las Apps para Android), un cliente (Marnin: su web la hicimos nosotros y su portal del empleado funciona con AppEquipo; no es un producto de GEBREY) y el servicio de Web y hosting, más el aviso legal, la página de gracias y `presupuesto.php` (el formulario de presupuesto, una frase con huecos, que manda el correo a hola@gebrey.es desde el propio hosting). Cada producto con demo sin cuenta la enlaza («Probar la demo»). El nombre del titular solo aparece en el aviso legal.

## Estructura

- `src/` — fuentes: `assets/css/site.css`, `assets/js/reel.js` (coreografía de scroll y vídeos), `assets/js/site.js` (tema y copiar correo), `assets/img/og.png`, `assets/video/` (los recorridos grabados por cada web).
- `build.py` — genera la página desde los datos de los proyectos (`PROJECTS`, cada uno con su tipo en `kind`: producto, cliente o servicio; el servicio va el último) y los textos de contacto (`PERSON`). Escribe `dist/` (para el servidor) y `preview/` (vista previa). Los vídeos de AppEquipo no se copian: se sirven desde `https://mbtenerife.es/video/` (`VIDEO_APPEQUIPO`).
- `record.js` — graba con Playwright un recorrido por cada web (portátil 1200×750 y móvil 640×1386) y lo guarda en `src/assets/video/`; vuelve a ejecutarlo cuando cambie una web (`node record.js marnin` para una sola). Los vídeos de AppEquipo son los del portal y se sirven desde mbtenerife.es.
- `record-citras.js` — graba la demo de Citras (citras.es/demo) usándola en tiempo real, en portátil y móvil. Los vídeos de ahora son los de la portada de citras.es (`python3 tools/citras.py videos` en gebrey-es/mbtenerife), copiados aquí.
- `record-plus.js` — graba GR Gestor Plus en su demo (la gestoría en el portátil y la empresa en el móvil) y lo deja en `src/assets/video/grgestorplus-*`; hace falta la demo en marcha (`pnpm demo` en su repositorio): `node record-plus.js http://localhost:8787`.
- `record-apps.js` — vídeos móviles 9:16 de la escena Apps: graba la interfaz real de Sorteo en Regla (hace falta la carpeta `assets/` de su proyecto Android) y monta el pase de pantallas de Repertorios Oposiciones con las capturas de su ficha de Google Play.
- `og.js` — regenera `src/assets/img/og.png` (la imagen al compartir) con Playwright; ejecútalo si cambia la lista de proyectos.
- `site/` — copia de `dist/` que se publica. **Es lo que sube el workflow.**
- `shot.js` — capturas con Playwright para revisar escritorio, móvil y tema claro.

## Cambiar algo

1. Edita `build.py` (textos, enlaces, teléfono) o `src/assets/…` (estilos, movimiento).
2. `python3 build.py` y copia `dist/` a `site/`.
3. Commit y push a `main`: el workflow **Publicar gebrey.es** sube `site/` por FTPS a `public_html`.

Los secretos del workflow (`FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`) están en Settings → Secrets and variables → Actions.

## Comprobar las demos

El workflow **Comprobar las demos** abre desde fuera la demo sin cuenta de cada proyecto que enlaza la web (ViaConextaHub, AppEquipo, Citras, GR Fichajes y su página de precios, GR Gestor, GR Gestor Despacho y GR Gestor Plus) y dice si responde. Para las que tienen interruptor (GR Gestor y GR Gestor Plus), dice además si está abierta. No cambia nada.
