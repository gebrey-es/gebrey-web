# -*- coding: utf-8 -*-
"""Construye el sitio GEBREY: dist/ (para el servidor) y preview/ (para la vista previa como artifact).
Una sola página con los proyectos, más el aviso legal."""
import os, shutil, html, datetime, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
PREV = os.path.join(ROOT, "preview")
SITE = "https://gebrey.es"
TODAY = datetime.date.today().isoformat()

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800'
         '&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap">')

FAVICON = ("data:image/svg+xml," + html.escape(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#14100e"/>'
    '<text x="32" y="46" text-anchor="middle" font-family="Arial Narrow, Arial, sans-serif" font-weight="800" font-size="40" fill="#ff5a47">R</text></svg>', quote=True))

SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a7 7 0 1 0 10.5 10.5z"/></svg>'

# El nombre solo aparece en el aviso legal (lo exige la LSSI); la portada es un escaparate de proyectos.
PERSON = dict(
    name="Francisco Gebrie Vicente", email="hola@gebrey.es", phone="+34 822 276 190", phone_tel="+34822276190",
    address=["Avda. Tres de Mayo 30, Edificio Ahlers, 1.ª planta", "38005 Santa Cruz de Tenerife"],
)
ORG = "https://gebrey.es/#org"
INDEXNOW_KEY = "bf8285b213157c518309b0364a3946ae"

def v(rel):
    """Huella del contenido de un asset (src/assets/...) para romper la caché cuando cambia."""
    path = os.path.join(SRC, rel)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]


# Vídeos del portal AppEquipo, servidos desde la web de MBTenerife (sin copia aquí): .mp4 y .webm
VIDEO_APPEQUIPO = "https://mbtenerife.es/video"

def video_shot(lap, mob, lap_label, mob_label, local=True):
    """Pantalla con vídeo: el portátil a pantalla completa y el móvil asomando. `lap`/`mob` son la ruta
    sin extensión (el JS añade .mp4/.webm al acercarse la escena). Los vídeos locales (src/assets/video,
    grabados con record.js) llevan huella de contenido en data-v para romper la caché cuando cambian."""
    def tag(cls, base, label, i):
        vv = f' data-v="{v(base + ".mp4")}"' if local else ''
        return (f'<video class="{cls} pc" style="--i:{i}" muted playsinline loop preload="none" disablepictureinpicture disableremoteplayback'
                f' data-src="{base}"{vv} aria-label="{html.escape(label, quote=True)}"></video>')
    return (f'<div class="shot video">\n  {tag("lap", lap, lap_label, 0)}\n'
            f'  <div class="phone pc" style="--i:3">{tag("mob", mob, mob_label, 3)}</div>\n</div>')

def site_shot(slug, name):
    """Recorrido grabado por la web del proyecto (record.js): portátil y móvil."""
    return video_shot(f"assets/video/{slug}-portatil", f"assets/video/{slug}-movil",
                      f"Recorrido por la web de {name} en un portátil", f"Recorrido por la web de {name} en un móvil")

# Qué es cada escena: un producto nuestro, el trabajo para un cliente o un servicio. Marnin es un cliente con su
# propietario (la Asociación de Socorrismo Marnin): le hicimos la web y su portal del empleado funciona con AppEquipo.
KINDS = {"producto": "Producto", "cliente": "Cliente", "servicio": "Servicio"}

SHOT_JORNADA = """<div class="shot flujo" aria-hidden="true">
  <div class="pasos">
    <div class="paso pc" style="--i:0"><span class="chip on">AppEquipo</span><span><b>08:02</b> Entrada, sellada en la cadena</span></div>
    <span class="linea pc" style="--i:1"></span>
    <div class="paso pc" style="--i:2"><span class="chip">Cierre del mes</span><span><b>1.284</b> fichajes, ninguno retocado</span></div>
    <span class="linea pc" style="--i:3"></span>
    <div class="paso pc" style="--i:4"><span class="chip">GR Gestor Despacho</span><span>Octubre, listo para las nóminas</span></div>
  </div>
  <div class="nomina pc" style="--i:5">
    <span class="nomina-t">Variables del mes</span>
    <div class="row"><span>Ordinarias</span><span class="price">162,50 h</span></div>
    <div class="row"><span>Extra</span><span class="price">2,25 h</span></div>
    <div class="row"><span>Nocturnas</span><span class="price">147,33 h</span></div>
    <div class="row"><span>Vacaciones</span><span class="price">3 días</span></div>
    <span class="bar w4 hot pc" style="--i:7"></span>
  </div>
</div>"""

SHOT_WEB = """<div class="shot web" aria-hidden="true">
  <div class="dots"><i class="pc" style="--i:0"></i><i class="pc" style="--i:1"></i><i class="pc" style="--i:2"></i></div>
  <div class="win pc" style="--i:1">
    <div class="col"><span class="bar w4 hot pc" style="--i:2"></span><span class="bar w3 pc" style="--i:3"></span><span class="bar w2 pc" style="--i:4"></span><span class="bar w3 pc" style="--i:5"></span></div>
    <div class="col"><span class="bar w4 pc" style="--i:3"></span><span class="bar w4 pc" style="--i:4"></span><span class="bar w3 pc" style="--i:5"></span><span class="bar w2 pc" style="--i:6"></span></div>
  </div>
  <div class="status pc" style="--i:7"><span><b>SSL</b> activo</span><span><b>Copias</b> cada noche</span><span><b>Correo</b> en tu dominio</span></div>
</div>"""

PROJECTS = [
    dict(
        slug="appequipo", name="AppEquipo", color="var(--c-appequipo)", kind="producto",
        kicker="Portal del empleado y control horario",
        one="Fichajes que nadie puede retocar, cuadrantes de turnos, nóminas firmadas desde el móvil y partes diarios, con el nombre y el logo de cada empresa. Para equipos de limpieza, hoteles, obras, seguridad o socorrismo.",
        url="https://mbtenerife.es", link="Entrar en mbtenerife.es",
        schema='{"@type":"SoftwareApplication","name":"AppEquipo","applicationCategory":"BusinessApplication","operatingSystem":"Web","url":"https://mbtenerife.es","description":"Portal del empleado y control horario para equipos de campo: registro de jornada inalterable, cuadrantes, nóminas firmadas y partes.","author":{"@type":"Organization","name":"MBTenerife","url":"https://mbtenerife.es","parentOrganization":{"@id":"' + ORG + '"}},"offers":{"@type":"Offer","price":"3.50","priceCurrency":"EUR","description":"Desde 3,50 € por persona, según el volumen de la empresa"}}',
        # los vídeos reales del portal, servidos desde mbtenerife.es
        shot=video_shot(f"{VIDEO_APPEQUIPO}/portatil", f"{VIDEO_APPEQUIPO}/movil",
                        "Vídeo del portal en el portátil: coordinación aprueba unas vacaciones, revisa un fichaje, cubre un turno libre y abre el cuadrante del mes",
                        "Vídeo del portal en el móvil: una socorrista ficha la entrada, mira sus turnos, firma la nómina, hace la revisión de apertura y da un parte", local=False)),
    dict(
        slug="jornada", name="Jornada", color="var(--c-jornada)", kind="producto",
        kicker="AppEquipo + GR Gestor: del fichaje a la nómina",
        one="El equipo ficha en AppEquipo y la gestoría recibe las horas de cada mes en GR Gestor, listas para las nóminas. 1,50 € por empleado y mes, o incluido por la gestoría con GR Gestor Despacho + Jornada.",
        url="https://grgestor.es/#jornada", link="Ver el precio en grgestor.es",
        url2="https://mbtenerife.es/registro-de-jornada/#con-tu-gestoria", link2="Cómo es el registro",
        schema='{"@type":"SoftwareApplication","name":"Registro de jornada de AppEquipo con GR Gestor","applicationCategory":"BusinessApplication","operatingSystem":"Web, Android","url":"https://grgestor.es/#jornada","description":"El registro de jornada de AppEquipo conectado con GR Gestor Despacho: el equipo ficha desde el móvil y la gestoría recibe las horas de cada mes para las nóminas.","author":{"@id":"' + ORG + '"},"offers":[{"@type":"Offer","price":"1.50","priceCurrency":"EUR","description":"Por empleado y mes, impuestos aparte"},{"@type":"Offer","price":"0","priceCurrency":"EUR","description":"Incluido por la gestoría con GR Gestor Despacho + Jornada"}]}',
        shot=SHOT_JORNADA),
    dict(
        slug="grgestor", name="GR Gestor", color="var(--c-grgestor)", kind="producto",
        kicker="Facturación con VERI*FACTU para autónomos y gestorías",
        one="Facturas lacradas con VERI*FACTU que se escriben en una frase desde el móvil, lo que es de Hacienda apartado en su sobre y la gestoría viéndolo todo al momento, también las horas del equipo.",
        url="https://grgestor.es", link="Entrar en grgestor.es",
        schema='{"@type":"SoftwareApplication","name":"GR Gestor","applicationCategory":"FinanceApplication","operatingSystem":"Android, Web","url":"https://grgestor.es","description":"App de facturación con VERI*FACTU para autónomos y micropymes: facturas escritas en una frase, el IVA y el IRPF apartados en sobres y conexión con su gestoría, que trabaja con GR Gestor Despacho.","author":{"@id":"' + ORG + '"},"offers":[{"@type":"Offer","price":"0","priceCurrency":"EUR","description":"Gratis hasta 3 facturas al mes"},{"@type":"Offer","price":"2.99","priceCurrency":"EUR","description":"Facturas ilimitadas, al mes, IVA incluido"}]}',
        shot=site_shot("grgestor", "GR Gestor")),
    dict(
        slug="citras", name="Citras", color="var(--c-citras)", kind="producto",
        kicker="Coordinación de flotas de vehículos",
        one="Cada vehículo, cada servicio y cada aviso en una sola pantalla: rutas que se rehacen solas, avisos urgentes y un enlace para seguir cada vehículo en el mapa.",
        url="https://mbtenerife.es/citras/", link="Conocer Citras",
        schema='{"@type":"SoftwareApplication","name":"Citras","applicationCategory":"BusinessApplication","operatingSystem":"Web","url":"https://mbtenerife.es/citras/","description":"Citras coordina flotas de vehículos: rutas que se hacen y se rehacen solas, avisos urgentes y un enlace para seguir cada vehículo en el mapa. Un producto de MBTenerife.","author":{"@type":"Organization","name":"MBTenerife","url":"https://mbtenerife.es","parentOrganization":{"@id":"' + ORG + '"}}}',
        # la demo de Citras usada de verdad (record-citras.js), no un recorrido por su web
        shot=video_shot("assets/video/citras-portatil", "assets/video/citras-movil",
                        "Vídeo de la demo de Citras en el portátil: el centro de coordinación recibe un aviso urgente, activa la ambulancia que antes llega, replanifica las rutas y repasa la flota",
                        "Vídeo de la demo de Citras en el móvil: la tripulación guarda la revisión de la ambulancia y el paciente ve llegar la suya")),
    dict(
        slug="viaconextahub", name="ViaConextaHub", color="var(--c-vch)", kind="producto",
        kicker="Plataforma para agencias de viajes",
        one="Un solo buscador para que cada agencia reserve con todos sus mayoristas, usando sus propias claves.",
        url="https://viaconextahub.es", link="Entrar en viaconextahub.es",
        schema='{"@type":"SoftwareApplication","name":"ViaConextaHub","applicationCategory":"BusinessApplication","operatingSystem":"Web","url":"https://viaconextahub.es","description":"Plataforma SaaS que conecta a las agencias de viajes con sus mayoristas usando las claves de cada agencia.","author":{"@id":"' + ORG + '"},"offers":{"@type":"Offer","price":"25","priceCurrency":"EUR","description":"Suscripción mensual, más impuestos"}}',
        shot=site_shot("viaconextahub", "ViaConextaHub")),
    dict(
        slug="marnin", name="Marnin", color="var(--c-marnin)", kind="cliente",
        kicker="Su web, y su portal del empleado con AppEquipo",
        one="La Asociación de Socorrismo Marnin tiene su propia web, que le hicimos nosotros, y su equipo trabaja con AppEquipo: sus socorristas fichan, firman documentos y organizan cada turno desde el móvil.",
        url="https://marnin.es", link="Ver marnin.es",
        url2="https://marnin.appequipo.es", link2="Su portal, con AppEquipo",
        schema='{"@type":"WebSite","name":"Marnin","url":"https://marnin.es","description":"Web de la Asociación de Socorrismo Marnin (Adeje, Tenerife), hecha por GEBREY. Su portal del empleado funciona con AppEquipo en https://marnin.appequipo.es.","publisher":{"@type":"Organization","name":"Asociación de Socorrismo Marnin","url":"https://marnin.es"},"creator":{"@id":"' + ORG + '"}}',
        shot=site_shot("marnin", "Marnin")),
    dict(
        slug="web", name="Web y hosting", color="var(--c-web)", kind="servicio",
        kicker="Webs y portales a medida, alojados y mantenidos",
        one="Tu web o tu herramienta interna, en un servidor gestionado en España, con correo, copias y certificados. Como la de Marnin.",
        url="mailto:hola@gebrey.es?subject=Presupuesto", link="Pedir presupuesto", quote=True,
        schema='{"@type":"Service","serviceType":"Diseño web, desarrollo y hosting","provider":{"@id":"' + ORG + '"},"areaServed":"ES","description":"Webs, portales internos y alojamiento gestionado para asociaciones y pymes."}',
        shot=SHOT_WEB),
]

# Los productos propios (sin la escena de la conexión), para las descripciones.
PRODUCTOS = [p for p in PROJECTS if p["kind"] == "producto" and p["slug"] != "jornada"]

def letters(text, cls="l"):
    """Cada carácter en un span (para animarlos uno a uno). Los espacios se marcan."""
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            out.append(f'<span class="{cls} sp" style="--i:{i}"> </span>')
        else:
            out.append(f'<span class="{cls}" style="--i:{i}">{html.escape(ch)}</span>')
    return "".join(out)

def head(title, desc, canonical, css_rel, extra="", preview=False):
    base = (f'<title>{html.escape(title)}</title>'
            + ('<meta name="claude:viewport-fit-sides" content="cover">' if preview else '')
            + f'<meta name="description" content="{html.escape(desc, quote=True)}">'
            + f'<link rel="canonical" href="{canonical}">'
            + f'<meta property="og:title" content="{html.escape(title, quote=True)}">'
            + f'<meta property="og:description" content="{html.escape(desc, quote=True)}">'
            + f'<meta property="og:type" content="website"><meta property="og:url" content="{canonical}">'
            + f'<meta property="og:image" content="{SITE}/assets/img/og.png?v={v("assets/img/og.png")}"><meta name="twitter:card" content="summary_large_image">'
            + '<meta name="theme-color" content="#14100e" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#efe3cf" media="(prefers-color-scheme: light)">'
            + f'<link rel="icon" href="{FAVICON}">'
            + FONTS
            + f'<link rel="stylesheet" href="{css_rel}?v={v("assets/css/site.css")}">'
            + '<script>if(!matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("motion");</script>'
            + extra)
    if preview:
        return base
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            + base + '</head><body>')

def header(home):
    return (f'<a class="skip" href="#main">Saltar al contenido</a>'
            f'<header class="top"><div class="wrap">'
            f'<a class="logo" href="{home}" aria-label="GEBREY, inicio">GEB<span class="r">R</span>EY</a>'
            f'<div class="top-right"><a href="mailto:{PERSON["email"]}">{PERSON["email"]}</a>'
            f'<button class="theme" type="button" aria-label="Cambiar entre tema claro y oscuro">{SUN}{MOON}</button></div>'
            f'</div></header>')

def scripts(rel, reel=False):
    s = f'<script src="{rel}assets/js/site.js?v={v("assets/js/site.js")}" defer></script>'
    if reel:
        s += f'<script src="{rel}assets/js/reel.js?v={v("assets/js/reel.js")}" defer></script>'
    return s

# ---------- pedir presupuesto: una frase con huecos ----------
QUOTE_TIPOS = ["una web", "una tienda online", "un portal interno", "una app", "hosting y mantenimiento", "todavía no lo sé"]
QUOTE_CUANDO = ["sin prisa", "este trimestre", "este mes", "ayer"]

def chips(name, options, checked=0):
    out = []
    for i, o in enumerate(options):
        out.append(f'<input type="radio" name="{name}" id="{name}-{i}" value="{html.escape(o, quote=True)}"{" checked" if i == checked else ""}>'
                   f'<label for="{name}-{i}">{html.escape(o)}</label>')
    return f'<span class="q-chips">{"".join(out)}</span>'

def quote_dialog():
    return f'''
<dialog class="quote" id="presupuesto" aria-labelledby="q-title">
  <div class="q-in">
    <button class="q-close" type="button" data-quote-close aria-label="Cerrar">×</button>
    <p class="q-kicker" id="q-title">Pedir presupuesto</p>
    <form class="q-form" method="post" action="presupuesto.php" novalidate>
      <p class="q-line"><span>Quiero</span> {chips("tipo", QUOTE_TIPOS)}</p>
      <p class="q-line"><label for="q-para">para</label> <input type="text" id="q-para" name="para" placeholder="mi negocio o mi idea" maxlength="120" autocomplete="organization" required></p>
      <p class="q-line"><label for="q-que">que sobre todo tiene que</label> <input type="text" id="q-que" name="que" placeholder="vender, reservar, fichar…" maxlength="160" required><span>.</span></p>
      <p class="q-line"><span>Lo necesito</span> {chips("cuando", QUOTE_CUANDO)}</p>
      <p class="q-line"><label for="q-nombre">Me llamo</label> <input type="text" id="q-nombre" name="nombre" placeholder="tu nombre" maxlength="80" autocomplete="name" required> <label for="q-correo">y me escribes a</label> <input type="email" id="q-correo" name="correo" placeholder="tu@correo.es" maxlength="120" autocomplete="email" required><span>.</span></p>
      <textarea name="mas" rows="2" maxlength="3000" placeholder="Si quieres contarme algo más (un enlace, un plazo, lo que ya tienes)…"></textarea>
      <p class="q-hp"><label>No rellenes esto <input type="text" name="web" tabindex="-1" autocomplete="off"></label></p>
      <input type="hidden" name="t" value="">
      <div class="q-actions">
        <button class="s-link q-send" type="submit">Enviar</button>
        <span class="q-note">Te contesto yo, normalmente el mismo día. O escríbeme a <a href="mailto:{PERSON["email"]}">{PERSON["email"]}</a>.</span>
      </div>
      <p class="q-error" role="alert" hidden></p>
    </form>
    <div class="q-done" hidden><p>Recibido. Te escribo en cuanto lo lea.</p><button class="s-link s-link-2" type="button" data-quote-close>Cerrar</button></div>
  </div>
</dialog>'''

# ---------- índice ----------
def index_page(preview=False):
    rel, home = "", "#inicio"
    # el índice, por tipos: cada etiqueta (Productos, Clientes, Servicios) va junto a sus enlaces
    grupos = []
    for p in PROJECTS:
        if not grupos or grupos[-1][0] != p["kind"]:
            grupos.append((p["kind"], []))
        grupos[-1][1].append(p)
    index, n = "", 0
    for kind, ps in grupos:
        links = ""
        for p in ps:
            links += f'<a href="#{p["slug"]}" style="--dot:{p["color"]};--i:{n}">{p["name"]}</a>'
            n += 1
        index += f'<span class="index-grupo"><span class="index-g" style="--i:{n - len(ps)}">{KINDS[kind]}s</span>{links}</span>'
    rail = "".join(f'<a href="#{p["slug"]}" style="--dot:{p["color"]}" data-name="{p["name"]}" aria-label="{p["name"]}"></a>' for p in PROJECTS)
    scenes = ""
    for p in PROJECTS:
        scenes += f'''
<section class="scene" id="{p["slug"]}" style="--c:{p["color"]}" aria-labelledby="t-{p["slug"]}">
  <div class="wrap s-in">
    <p class="s-kicker"><span class="s-kind">{KINDS[p["kind"]]}</span>{p["kicker"]}</p>
    <h2 class="s-name" id="t-{p["slug"]}" data-fit="{p["name"]}"><span class="vh">{p["name"]}</span><span aria-hidden="true">{letters(p["name"])}</span></h2>
    <div class="s-row">
      <div class="s-text">
        <p class="s-one">{p["one"]}</p>
        <div class="s-links"><a class="s-link" href="{p["url"]}"{' rel="noopener"' if p["url"].startswith("http") else ''}{' data-quote' if p.get("quote") else ''}>{p["link"]}</a>{f'<a class="s-link s-link-2" href="{p["url2"]}" rel="noopener">{p["link2"]}</a>' if p.get("url2") else ''}</div>
      </div>
      <div class="s-shot">{p["shot"]}</div>
    </div>
  </div>
</section>'''
    names = ", ".join(p["name"] for p in PRODUCTOS[:-1]) + " y " + PRODUCTOS[-1]["name"]
    street = html.escape(PERSON["address"][0], quote=True)
    schema = ('{"@context":"https://schema.org","@graph":['
              '{"@type":"Organization","@id":"' + ORG + '","name":"GEBREY","url":"https://gebrey.es","email":"hola@gebrey.es","telephone":"+34822276190",'
              '"address":{"@type":"PostalAddress","streetAddress":"' + street + '","postalCode":"38005","addressLocality":"Santa Cruz de Tenerife","addressRegion":"Canarias","addressCountry":"ES"},'
              '"description":"Software y webs a medida desde Tenerife: ' + names + ', y webs y portales para clientes como Marnin."},'
              + ",".join(p["schema"] for p in PROJECTS)
              + ']}')
    extra = f'<script type="application/ld+json">{schema}</script>'
    out = head("GEBREY — proyectos de software y web",
               "AppEquipo, el portal del empleado; GR Gestor, la facturación con VERI*FACTU; Citras y ViaConextaHub. Y webs a medida, como la de Marnin.",
               SITE + "/", "assets/css/site.css", extra, preview)
    out += header(home)
    out += f'''
<main id="main">
<section class="scene hero" id="inicio" aria-label="GEBREY">
  <div class="wrap hero-in">
    <div class="mark-slot" data-fit="GEBREY" data-fit-wdth="88"><span class="mark-ph" aria-hidden="true">GEBREY</span><a class="mark" href="#inicio" aria-label="GEBREY, inicio"><span class="lw" style="--i:0"><span class="l">G</span></span><span class="lw" style="--i:1"><span class="l">E</span></span><span class="lw" style="--i:2"><span class="l">B</span></span><span class="lw r" style="--i:3"><span class="l">R</span></span><span class="lw" style="--i:4"><span class="l">E</span></span><span class="lw" style="--i:5"><span class="l">Y</span></span></a></div>
    <h1 class="tag">Proyectos de software y web.</h1>
    <p class="hero-lead">Hacemos y mantenemos nuestros productos, conectados entre sí, y las webs y los portales de nuestros clientes. Desde Tenerife.</p>
    <nav class="index" aria-label="Productos, clientes y servicios">{index}</nav>
  </div>
  <a class="cue" href="#{PROJECTS[0]["slug"]}" aria-label="Bajar al primer proyecto"></a>
</section>
{scenes}
<section class="scene end" id="contacto" aria-labelledby="t-contacto">
  <div class="wrap s-in end-in">
    <h2 id="t-contacto">Cuéntame tu proyecto.</h2>
    <div class="mail-row">
      <a class="mail" id="mail" href="mailto:{PERSON["email"]}" data-fit="{PERSON["email"]}"><span class="vh">{PERSON["email"]}</span><span aria-hidden="true">{letters(PERSON["email"])}</span></a>
      <button class="copy" type="button" data-copy="{PERSON["email"]}" aria-controls="mail">Copiar el correo</button>
      <a class="copy q-open" href="mailto:{PERSON["email"]}?subject=Presupuesto" data-quote>Pedir presupuesto</a>
    </div>
    <div class="end-meta">
      <a class="tel" href="tel:{PERSON["phone_tel"]}">{PERSON["phone"]}</a>
      <address>{PERSON["address"][0]}<br>{PERSON["address"][1]}</address>
    </div>
    <div class="end-foot">
      <span>GEBREY</span>
      <a href="legal.html">Aviso legal y privacidad</a>
    </div>
  </div>
</section>
</main>
{quote_dialog()}
<nav class="rail" aria-label="Posición">{rail}</nav>
'''
    out += scripts(rel, reel=True)
    if not preview:
        out += '</body></html>'
    return out

# ---------- legal ----------
def legal_page():
    out = head("Aviso legal — GEBREY", "Aviso legal y política de privacidad de gebrey.es.", SITE + "/legal.html", "assets/css/site.css")
    out += header("index.html")
    out += f'''
<main id="main" class="wrap"><div class="legal">
  <h1>Aviso legal y privacidad</h1>
  <h2>Titular</h2>
  <p>{PERSON["name"]}. NIF 07.979.288-J. Domicilio: {PERSON["address"][0]}, {PERSON["address"][1]}. Correo: {PERSON["email"]}. Teléfono: {PERSON["phone"]}.</p>
  <h2>Qué es este sitio</h2>
  <p>gebrey.es presenta los productos que desarrolla su titular y el trabajo hecho para sus clientes, y enlaza a cada uno. Cada producto y cada web de un cliente (como la de Marnin, que es de la Asociación de Socorrismo Marnin) tiene su propio titular, condiciones y política de privacidad.</p>
  <h2>Datos personales</h2>
  <p>Los únicos datos que se tratan son los que tú envías al escribir por correo o llamar: se usan para responderte y, si lo pides, para preparar un presupuesto. La base legal es tu consentimiento y, en su caso, la relación precontractual. No se ceden a terceros salvo obligación legal y se conservan mientras dure la conversación o la relación profesional.</p>
  <p>Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a {PERSON["email"]}. También puedes reclamar ante la Agencia Española de Protección de Datos.</p>
  <h2>Cookies</h2>
  <p>Este sitio no usa cookies de seguimiento ni analítica de terceros. Solo guarda en tu navegador, si la eliges, la preferencia de tema claro u oscuro.</p>
  <h2>Propiedad intelectual</h2>
  <p>Los textos, el diseño y el código de gebrey.es son de su titular. Las marcas de los proyectos enlazados pertenecen a sus respectivos titulares.</p>
  <p><a class="back" href="index.html">Volver a los proyectos</a></p>
</div></main>
'''
    out += scripts("")
    out += '</body></html>'
    return out

PHP = r"""<?php
// Recibe el formulario de presupuesto de gebrey.es y lo manda por correo a hola@gebrey.es.
// Responde JSON si lo pide el JS de la página; si no (sin JS), redirige a gracias.html.
$json = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');
$responder = function (bool $ok, string $error = '') use ($json) {
    if ($json) { header('Content-Type: application/json; charset=utf-8'); echo json_encode(['ok' => $ok, 'error' => $error]); }
    elseif ($ok) { header('Location: /gracias.html', true, 303); }
    else { header('Content-Type: text/plain; charset=utf-8'); if (http_response_code() === 200) http_response_code(400); echo $error; }
    exit;
};
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); $responder(false, 'Solo se admite POST.'); }
// cebo para robots: el campo "web" lo rellenan ellos, nunca una persona (va oculto); y nadie escribe en menos de 3 s
if (!empty($_POST['web'])) $responder(true);
$t = (int)($_POST['t'] ?? 0);
if ($t > 0 && time() - $t < 3) $responder(true);

$campo = function (string $k, int $max) {
    $v = trim(strip_tags((string)($_POST[$k] ?? '')));
    $v = preg_replace('/[\r\n\t\x00-\x1f]+/', ' ', $v);
    return mb_substr($v, 0, $max);
};
$tipo = $campo('tipo', 60); $para = $campo('para', 120); $que = $campo('que', 160); $cuando = $campo('cuando', 40);
$nombre = $campo('nombre', 80); $correo = filter_var($campo('correo', 120), FILTER_VALIDATE_EMAIL);
$mas = mb_substr(trim(strip_tags((string)($_POST['mas'] ?? ''))), 0, 3000);
if ($nombre === '' || !$correo) $responder(false, 'Falta tu nombre o un correo válido.');
if ($para === '' && $que === '' && $mas === '') $responder(false, 'Cuéntame al menos qué quieres.');

$frase = "Quiero $tipo para $para, que sobre todo tiene que $que. Lo necesito $cuando.\nMe llamo $nombre y me escribes a $correo.";
$cuerpo = $frase . ($mas !== '' ? "\n\n$mas" : '') . "\n\n— Enviado desde el formulario de gebrey.es el " . date('d/m/Y H:i') . " · IP " . ($_SERVER['REMOTE_ADDR'] ?? '?');
$asunto = '=?UTF-8?B?' . base64_encode("Presupuesto: $tipo para $para") . '?=';
$nombreCod = '=?UTF-8?B?' . base64_encode($nombre) . '?=';
$cabeceras = "From: GEBREY <hola@gebrey.es>\r\nReply-To: $nombreCod <$correo>\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";
$ok = @mail('hola@gebrey.es', $asunto, $cuerpo, $cabeceras);
$responder($ok, $ok ? '' : 'No se ha podido enviar. Escríbeme a hola@gebrey.es.');
"""

def gracias_page():
    out = head("Recibido — GEBREY", "Tu petición de presupuesto ha llegado.", SITE + "/gracias.html", "assets/css/site.css")
    out += header("index.html")
    out += '''
<main id="main" class="wrap"><div class="legal">
  <h1>Recibido.</h1>
  <p>Te escribo en cuanto lo lea, normalmente el mismo día.</p>
  <p><a class="back" href="index.html">Volver a los proyectos</a></p>
</div></main>
'''
    out += scripts("")
    out += '</body></html>'
    return out

ROBOTS = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: PerplexityBot
Allow: /

Sitemap: https://gebrey.es/sitemap.xml
"""

def sitemap():
    urls = [SITE + "/", SITE + "/legal.html"]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'

def llms():
    lines = ["# GEBREY", "", "> Software y webs a medida desde Tenerife: productos propios conectados entre sí (AppEquipo, GR Gestor, Citras y ViaConextaHub) y webs y portales para clientes.", "",
             f"Contacto: {PERSON['email']} · {PERSON['phone']} · {PERSON['address'][0]}, {PERSON['address'][1]}"]
    for kind, titulo in (("producto", "Productos"), ("cliente", "Clientes"), ("servicio", "Servicios")):
        lines += ["", f"## {titulo}", ""]
        for p in (x for x in PROJECTS if x["kind"] == kind):
            site = p["url"] if p["url"].startswith("http") else "https://gebrey.es/#web"
            app = f" Más: {p['url2']}" if p.get("url2") else ""
            primera = p["kicker"].split()[0]
            # solo la inicial, y no en un nombre propio como AppEquipo: VERI*FACTU y GR Gestor se quedan como son
            kicker = p["kicker"] if any(c.isupper() for c in primera[1:]) else p["kicker"][0].lower() + p["kicker"][1:]
            lines.append(f"- {p['name']} ({kicker}): {p['one']} Sitio: {site}{app}")
    lines += ["", "## Páginas", "", "- [Inicio](https://gebrey.es/)", "- [Aviso legal y privacidad](https://gebrey.es/legal.html)"]
    return "\n".join(lines) + "\n"

HTACCESS = """RewriteEngine On
# https siempre
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# www y gebrey.com redirigen a gebrey.es
RewriteCond %{HTTP_HOST} !^gebrey\\.es$ [NC]
RewriteRule ^ https://gebrey.es%{REQUEST_URI} [L,R=301]
# las antiguas páginas de proyecto van a su escena
RedirectMatch 301 ^/proyectos/viaconextahub\\.html$ /#viaconextahub
RedirectMatch 301 ^/proyectos/citras\\.html$ /#citras
RedirectMatch 301 ^/proyectos/teidetravel\\.html$ /
RedirectMatch 301 ^/proyectos/web-hosting\\.html$ /#web
# tipos y caché: el HTML se revalida siempre; CSS/JS/imágenes llevan ?v=huella y pueden cachearse mucho
AddType text/plain .txt
AddType video/mp4 .mp4
AddType video/webm .webm
<IfModule mod_headers.c>
  <FilesMatch "\\.(html|xml|txt)$">
    Header set Cache-Control "no-cache, must-revalidate"
  </FilesMatch>
  <FilesMatch "\\.(css|js|png|svg|webp|jpg|mp4|webm)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType video/mp4 "access plus 1 year"
  ExpiresByType video/webm "access plus 1 year"
</IfModule>
"""

def write(path, content, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(content)

def build():
    for d in (DIST, PREV):
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(os.path.join(SRC, "assets"), os.path.join(d, "assets"))
    write(os.path.join(DIST, "index.html"), index_page(False))
    write(os.path.join(DIST, "legal.html"), legal_page())
    write(os.path.join(DIST, "robots.txt"), ROBOTS)
    write(os.path.join(DIST, "sitemap.xml"), sitemap())
    write(os.path.join(DIST, "llms.txt"), llms())
    write(os.path.join(DIST, ".htaccess"), HTACCESS)
    write(os.path.join(DIST, "presupuesto.php"), PHP)
    # IndexNow: la clave publicada en la raíz permite avisar a Bing, Yandex y otros buscadores de cada cambio
    # (python3 indexnow.py tras publicar)
    write(os.path.join(DIST, INDEXNOW_KEY + ".txt"), INDEXNOW_KEY)
    write(os.path.join(DIST, "gracias.html"), gracias_page())
    # preview (artifact): index sin esqueleto, resto igual
    write(os.path.join(PREV, "index.html"), index_page(True))
    write(os.path.join(PREV, "legal.html"), legal_page())
    print("ok")

if __name__ == "__main__":
    build()
