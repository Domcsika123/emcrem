#!/usr/bin/env python3
"""Statikus oldalgenerátor az emcremdefibrillator.hu oldalhoz.

Használat:  python build.py
A kimenet a ./public mappába kerül (ezt kell feltölteni a tárhely gyökerébe).
A közös fejléc, lábléc, SEO meta és strukturált adatok itt, egy helyen módosíthatók.

Környezeti változók (a GitHub Pages munkafolyamat használja):
  SITE_BASE=/emcrem/   ha az oldal almappában fut (pl. felhasznalo.github.io/emcrem/)
  FORM_MODE=mailto     ha nincs PHP: az űrlap a látogató levelezőjében nyit új levelet
"""
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent / "public"
SITE = "https://emcremdefibrillator.hu"
LASTMOD = "2026-10-21"
_base = os.environ.get("SITE_BASE", "").strip("/")
BASE = f"/{_base}/" if _base else "/"
FORM_MAILTO = os.environ.get("FORM_MODE") == "mailto"

ORG = {
    "name": "Emcrem Kft.",
    "brand": "Emcrem",
    "phone_display": "06 30 488 3083",
    "phone_tel": "+36304883083",
    "phone_intl": "+36 30 488 3083",
    "email": "aed@emcrem.hu",
    "email2": "defi@emcrem.hu",
    "street": "Új utca 12.",
    "city": "Esztergom",
    "zip": "2500",
    "facebook": "https://www.facebook.com/Emcrem-103013304733028",
    "instagram": "https://www.instagram.com/aedemcrem/",
}

# kép neve -> (eredeti szélesség, magasság, elérhető szélességek)
IMGS = {
    "aed-3100-made-in-japan": (800, 800, [800, 480]),
    "aed-3100-automata-defibrillator": (800, 800, [800, 480]),
    "aed-3100-nyitott-fedellel": (800, 800, [800, 480]),
    "aed-3100-hordtaska": (800, 800, [800, 480]),
    "aed-fali-tarolo-szekreny": (800, 800, [800, 480]),
    "munkahelyi-elsosegely-oktatas": (500, 334, [500]),
    "automata-defibrillator-csalad": (500, 257, [500]),
    "oktatas-extrak": (500, 449, [500]),
    "szakmai-felhasznaloknak": (500, 333, [500]),
    "lifeline-arm-mellkaskompresszios-keszulek": (800, 800, [800, 480]),
    "lifeline-arm-oldalnezet": (800, 800, [800, 480]),
    "lifeline-arm-hordtaska": (800, 800, [800, 480]),
    "lifeline-arm-hasznalat-kozben": (1694, 800, [1200, 640]),
    "cpr-assist-mellkaskompresszio-ellenorzo": (800, 800, [800, 480]),
    "cpr-assist-hasznalat-kozben": (800, 592, [800, 480]),
    "nihon-kohden-tec-5600-defibrillator-monitor": (800, 800, [800, 480]),
    "nihon-kohden-tec-5600-allvanyon": (800, 800, [800, 480]),
    "nihon-kohden-tec-5600-korhazi-hasznalat": (800, 800, [800, 480]),
}

ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
    "voice": '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    "wifi": '<path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><path d="M12 20h.01"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "cap": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "steth": '<path d="M11 2v2M5 2v2"/><path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
    "play": '<circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4V8z"/>',
    "news": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8V6Z"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "instagram": '<rect width="20" height="20" x="2" y="2" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "cert": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M14 2v6h6"/><path d="m9 15 2 2 4-4"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><path d="M8 21h8M12 17v4"/><path d="M6 10h3l1.5-3 2 6 1.5-3H18"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "battery": '<rect width="16" height="10" x="2" y="7" rx="2"/><path d="M22 11v2M6 11v2M10 11v2"/>',
}


def esc(s):
    return html.escape(s, quote=True)


def icon(name, cls=""):
    c = f"icon {cls}".strip()
    return f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def img(name, alt, sizes="100vw", eager=False, cls=""):
    w, h, widths = IMGS[name]
    big = max(widths)
    hh = round(h * big / w)
    srcset = ", ".join(f"/assets/img/{name}-{x}.webp {x}w" for x in sorted(widths))
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    ss = f' srcset="{srcset}" sizes="{sizes}"' if len(widths) > 1 else ""
    return (f'<img src="/assets/img/{name}-{big}.webp"{ss} width="{big}" height="{hh}" '
            f'alt="{esc(alt)}" {load} decoding="async"{c}>')


def src_of(name):
    return f"/assets/img/{name}-{max(IMGS[name][2])}.webp"


def gallery(items, label, cover=False):
    """items: [(img_name, alt)]"""
    first, alt0 = items[0]
    thumbs = []
    for i, (n, a) in enumerate(items):
        w, h, widths = IMGS[n]
        srcset = ", ".join(f"/assets/img/{n}-{x}.webp {x}w" for x in sorted(widths))
        small = min(widths)
        thumbs.append(
            f'<li><button type="button" class="gallery__thumb" aria-current="{"true" if i == 0 else "false"}" '
            f'data-src="{src_of(n)}" data-srcset="{srcset}" data-alt="{esc(a)}" aria-label="Kép {i+1}: {esc(a)}">'
            f'<img src="/assets/img/{n}-{small}.webp" width="{small}" height="{round(h*small/w)}" alt="" loading="lazy" decoding="async"></button></li>')
    n = len(items)
    return f'''<div class="gallery" data-gallery role="group" aria-label="{esc(label)}">
  <div class="gallery__main{' gallery__main--cover' if cover else ''}">{img(first, alt0, "(min-width: 960px) 560px, 100vw")}</div>
  <p class="gallery__caption" aria-live="polite">{esc(alt0)}</p>
  <ul class="gallery__thumbs gallery__thumbs--{n}">{"".join(thumbs)}</ul>
</div>'''


# ---------------------------------------------------------------------------
# Navigáció
# ---------------------------------------------------------------------------
TRAINING_SUB = [
    ("/munkahelyi-elsosegely-oktatas/", "Munkahelyi elsősegély-oktatás", "Kötelező munkahelyi képzés tanúsítvánnyal", "cert"),
    ("/oktatas-extrak/", "Oktatás extrák", "Szimuláció, gyermek-, iskolai és angol nyelvű oktatás", "cap"),
]


def nav(current):
    def link(href, label):
        cur = ' aria-current="page"' if current == href else ""
        return f'<li class="nav-item"><a class="nav-link" href="{href}"{cur}>{label}</a></li>'

    sub_active = any(current == h for h, *_ in TRAINING_SUB)
    subs = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if current == h else ""}>'
        f'<span class="sub-icon">{icon(ic)}</span><span><strong>{t}</strong><span>{d}</span></span></a></li>'
        for h, t, d, ic in TRAINING_SUB)
    return f'''<nav class="main-nav" id="main-nav" aria-label="Fő navigáció">
        <ul class="nav-list">
          {link("/automata-defibrillator/", "Automata defibrillátor")}
          <li class="nav-item has-sub">
            <button class="nav-link{" is-active" if sub_active else ""}" type="button" aria-expanded="false" aria-controls="sub-oktatas">Elsősegély-oktatás {icon("chevron")}</button>
            <ul class="submenu" id="sub-oktatas">{subs}</ul>
          </li>
          {link("/szakmai-felhasznaloknak/", "Szakmai felhasználóknak")}
          {link("/erdekes-linkek-sajtofigyelo/", "Sajtófigyelő")}
          {link("/kapcsolat/", "Kapcsolat")}
          <li class="mobile-only"><a class="btn btn--primary" href="/ajanlatkeres/">Ajánlatkérés {icon("arrow", "icon--arrow")}</a></li>
          <li class="mobile-only"><a class="btn btn--secondary" href="tel:{ORG["phone_tel"]}">{icon("phone")} {ORG["phone_display"]}</a></li>
        </ul>
      </nav>'''


def header(current):
    return f'''<a class="skip-link" href="#tartalom">Ugrás a tartalomra</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/" aria-label="Emcrem – kezdőlap"><img src="/assets/img/emcrem-logo.png" width="409" height="113" alt="Emcrem"></a>
    {nav(current)}
    <div class="header-actions">
      <a class="header-phone" href="tel:{ORG["phone_tel"]}" aria-label="Telefon: {ORG["phone_display"]}">{icon("phone")}<span>{ORG["phone_display"]}</span></a>
      <a class="btn btn--primary btn--sm" href="/ajanlatkeres/">Ajánlatkérés</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Menü megnyitása">{icon("menu", "icon-menu")}{icon("x", "icon-close")}</button>
    </div>
  </div>
</header>'''


def footer():
    o = ORG
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="/assets/img/emcrem-logo-white.png" width="409" height="113" alt="Emcrem" loading="lazy">
        <p>Nihon Kohden automata defibrillátorok Japánból, valamint gyakorlatorientált munkahelyi és iskolai elsősegély-oktatás.</p>
        <div class="social">
          <a href="{o["facebook"]}" rel="noopener" target="_blank" aria-label="Emcrem a Facebookon">{icon("facebook")}</a>
          <a href="{o["instagram"]}" rel="noopener" target="_blank" aria-label="Emcrem az Instagramon">{icon("instagram")}</a>
        </div>
      </div>
      <div>
        <h2>Szolgáltatások</h2>
        <ul class="footer-links">
          <li><a href="/automata-defibrillator/">Automata defibrillátor</a></li>
          <li><a href="/munkahelyi-elsosegely-oktatas/">Munkahelyi elsősegély-oktatás</a></li>
          <li><a href="/oktatas-extrak/">Oktatás extrák</a></li>
          <li><a href="/szakmai-felhasznaloknak/">Szakmai felhasználóknak</a></li>
        </ul>
      </div>
      <div>
        <h2>Információ</h2>
        <ul class="footer-links">
          <li><a href="/ajanlatkeres/">Ajánlatkérés</a></li>
          <li><a href="/kapcsolat/">Kapcsolat</a></li>
          <li><a href="/erdekes-linkek-sajtofigyelo/">Érdekes linkek, sajtófigyelő</a></li>
          <li><a href="/adatkezelesi-tajekoztato/">Adatkezelési tájékoztató</a></li>
        </ul>
      </div>
      <div>
        <h2>Kapcsolat</h2>
        <ul class="footer-contact">
          <li>{icon("phone")}<a href="tel:{o["phone_tel"]}">{o["phone_display"]}</a></li>
          <li>{icon("mail")}<a href="mailto:{o["email"]}">{o["email"]}</a></li>
          <li>{icon("pin")}<address>{o["name"]}<br>{o["zip"]} {o["city"]}, {o["street"]}</address></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="mb-0">© <span data-year>2026</span> {o["name"]} Minden jog fenntartva.</p>
      <ul>
        <li><a href="/adatkezelesi-tajekoztato/">Adatkezelési tájékoztató</a></li>
        <li><a href="/kapcsolat/">Impresszum és elérhetőség</a></li>
      </ul>
    </div>
  </div>
</footer>'''


def breadcrumbs(crumbs):
    """crumbs: [(név, útvonal)] – a kezdőlap automatikusan bekerül."""
    full = [("Kezdőlap", "/")] + crumbs
    lis = []
    for i, (name, path) in enumerate(full):
        if i == len(full) - 1:
            lis.append(f'<li><span aria-current="page">{name}</span></li>')
        else:
            lis.append(f'<li><a href="{path}">{name}</a></li>')
    vis = f'<nav class="breadcrumbs" aria-label="Morzsamenü"><ol>{"".join(lis)}</ol></nav>'
    ld = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p}
            for i, (n, p) in enumerate(full)
        ],
    }
    return vis, ld


def org_ld():
    o = ORG
    return {
        "@type": ["Organization", "LocalBusiness"],
        "@id": SITE + "/#org",
        "name": o["name"],
        "alternateName": "Emcrem defibrillátor",
        "url": SITE + "/",
        "logo": SITE + "/assets/img/emcrem-logo.png",
        "image": SITE + "/assets/img/og-image.jpg",
        "email": o["email"],
        "telephone": o["phone_intl"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": o["street"],
            "addressLocality": o["city"],
            "postalCode": o["zip"],
            "addressCountry": "HU",
        },
        "areaServed": {"@type": "Country", "name": "Magyarország"},
        "sameAs": [o["facebook"], o["instagram"]],
    }


def page(path, title, desc, body, current=None, schema=None, noindex=False,
         og_type="website", og_image="/assets/img/og-image.jpg", page_type="WebPage"):
    url = SITE + path
    graph = [
        org_ld(),
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Emcrem defibrillátor",
         "inLanguage": "hu-HU", "publisher": {"@id": SITE + "/#org"}},
        {"@type": page_type, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "inLanguage": "hu-HU", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#org"}},
    ] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    doc = f'''<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0b1d36">
<meta property="og:locale" content="hu_HU">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Emcrem defibrillátor">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon-32x32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-latin-ext.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css?v={LASTMOD}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{header(current or path)}
<main id="tartalom">
{body}
</main>
{footer()}
<script src="/assets/js/main.js?v={LASTMOD}" defer></script>
</body>
</html>
'''
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    if path.endswith(".html"):
        out = ROOT / path.strip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(with_base(doc), encoding="utf-8")
    return path, noindex


def with_base(text):
    """Root-relative links ("/assets/...") -> BASE-relative, for hosting in a subfolder."""
    if BASE == "/":
        return text
    text = re.sub(r'((?:href|src|action|data-src)=")/(?!/)', lambda m: m.group(1) + BASE, text)
    return re.sub(r'((?:srcset|data-srcset)=")([^"]*)"',
                  lambda m: m.group(1) + re.sub(r'(^|, )/', lambda n: n.group(1) + BASE, m.group(2)) + '"', text)


def cta_band(title="Kérjen személyre szabott ajánlatot",
             text="Írja meg, hány főre szervezne oktatást, vagy hová szánja a defibrillátort, és rövid időn belül jelentkezünk."):
    return f'''<section class="cta-section" aria-labelledby="cta-cim">
  <div class="container cta-band__grid">
    <div>
      <h2 id="cta-cim">{title}</h2>
      <p>{text}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn--primary" href="/ajanlatkeres/">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a>
      <a class="btn btn--ghost-light" href="tel:{ORG["phone_tel"]}">{icon("phone")} {ORG["phone_display"]}</a>
    </div>
  </div>
</section>'''


def page_hero(crumbs_html, eyebrow, h1, lead, media=None, buttons=""):
    media_html = f'<div class="page-hero__media">{media}</div>' if media else ""
    return f'''<section class="page-hero">
  <div class="container">
    {crumbs_html}
    <div class="page-hero__grid">
      <div>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
        {buttons}
      </div>
      {media_html}
    </div>
  </div>
</section>'''


def faq_block(items, heading_id="gyik-cim", title="Gyakori kérdések", soft=True):
    det = "".join(
        f'<details><summary>{q}{icon("plus")}</summary><div class="faq-answer"><p>{a}</p></div></details>'
        for q, a in items)
    ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    htm = f'''<section class="section{" section--soft" if soft else ""}" aria-labelledby="{heading_id}">
  <div class="container">
    <div class="section-head section-head--center">
      <h2 id="{heading_id}">{title}</h2>
    </div>
    <div class="faq">{det}</div>
  </div>
</section>'''
    return htm, ld


# ---------------------------------------------------------------------------
# Tartalom
# ---------------------------------------------------------------------------
PRESS = [
    ("2021-10-28", "Mentőhívás, AED, felmérés", "Felmérés a mentőhívásról, az újraélesztésről és a laikus elsősegélynyújtásról.",
     [("index.hu", "https://index.hu/belfold/2021/10/05/mento-eletmentes-elsosegely-ujraelesztes-felmeres/", "news")]),
    ("2021-10-28", "AED az életben! – Defibrillátorral mentettek életet egy debreceni tornateremben", "Valós eset arról, hogy egy helyben elérhető defibrillátor életet ment.",
     [("haon.hu", "https://haon.hu/kek-hirek/helyi-kek-hirek/defibrillatorral-mentettek-eletet-egy-debreceni-tornateremben-5771540/", "news")]),
    ("2021-07-18", "Életmentő szülők", "Videó a laikus újraélesztésről.",
     [("YouTube-videó", "https://www.youtube.com/watch?v=Jw5z_3dnisU&t=315s", "play")]),
    ("2020-11-08", "COVID napló – avagy ez történt, miután pozitív lett a tesztem", "Személyes beszámoló egy orvostanhallgató tollából.",
     [("orvostanhallgato.com", "http://orvostanhallgato.com/2020/11/08/covid-naplo-avagy-ez-tortent-miutan-pozitiv-lett-a-tesztem/", "news")]),
    ("2020-10-15", "Ne parázz, sokkolj!", "Videó az automata defibrillátor használatáról.",
     [("YouTube-videó", "https://www.youtube.com/watch?v=EgFhnGPjnLI", "play")]),
    ("2020-07-21", "Defibrillation (angol nyelvű)", "A defibrilláció története és működése.",
     [("Wikipedia", "https://en.wikipedia.org/wiki/Defibrillation#History", "globe")]),
    ("2020-07-21", "Defibrillátor – mikor és hogyan kell használni?", "Gyakorlati útmutató a defibrillátor használatáról.",
     [("WEBBeteg", "https://www.webbeteg.hu/cikkek/elsosegely/6757/defibrillator", "news"),
      ("Élethosszig", "https://elethosszig.hu/defibrillator-eletet-menthet/", "news")]),
    ("2020-07-21", "Hirtelen szívhalál, automata defibrillátor", "Tájékoztató a hirtelen szívhalálról és az AED szerepéről.",
     [("mnsza.hu", "http://www.mnsza.hu/hirtelen/index.php", "news")]),
]


def hu_date(iso):
    return iso.replace("-", ".") + "."


def press_items(items, heading="h2"):
    out = []
    for d, title, summary, links in items:
        ls = "".join(
            f'<a class="press-link" href="{u}" target="_blank" rel="noopener">{lbl} {icon("external")}'
            f'<span class="visually-hidden"> (új lapon nyílik)</span></a>' for lbl, u, ic in links)
        out.append(f'''<li class="press-item">
  <time datetime="{d}">{hu_date(d)}</time>
  <div><{heading}>{title}</{heading}><p>{summary}</p></div>
  <div class="press-links">{ls}</div>
</li>''')
    return f'<ul class="press-list">{"".join(out)}</ul>'


AED_FAQ = [
    ("Mennyibe kerül az AED-3100 automata defibrillátor?",
     "Az AED-3100 automata defibrillátor ára 580.000 Ft + ÁFA. Kompletten, üzemkészen szállítjuk, teleppel és elektródával."),
    ("Mit kapok a defibrillátor mellé?",
     "A megrendelőnek ingyen biztosítunk egy újraélesztő tanfolyamot (az AED-3100 saját gyakorló defibrillátorával, számítógépes értékelésű szimulációs eszközökkel), vagy egy teljes körű munkahelyi elsősegély-tanfolyamot legfeljebb 20 fő részére."),
    ("Gyermekeknél is használható a készülék?",
     "Igen, az AED-3100 felnőtt és gyermek páciensek esetén is alkalmazható."),
    ("Milyen nyelven ad utasításokat a defibrillátor?",
     "A készülék magyar nyelvű hangutasításokat ad, az érvényben lévő újraélesztési protokolloknak megfelelően."),
    ("Mennyi a garancia, és hogyan ellenőrizhető az üzemkészség?",
     "A készülékre 8 év garanciát biztosítunk. Az AED naponta önellenőrzést (önteszt) végez, opcionálisan WiFi-alapú távfelügyelettel is kérhető."),
    ("Mennyi ideig tart és mennyibe kerül a munkahelyi elsősegély-oktatás?",
     "A képzés a választott tematikától függően 4–8 óra. Ára 9.000 Ft/fő (minimum 5 fő). Automata defibrillátor vásárlása esetén legfeljebb 20 főig ingyenes."),
]


def build_home():
    services = [
        ("/automata-defibrillator/", "automata-defibrillator-csalad", "Automata defibrillátor gyermekkel játszó anya mellett",
         "Automata defibrillátor", "Nihon Kohden AED-3100 kompletten, üzemkészen – 8 év garanciával és ajándék tanfolyammal."),
        ("/munkahelyi-elsosegely-oktatas/", "munkahelyi-elsosegely-oktatas", "Újraélesztés gyakorlása babán elsősegély-tanfolyamon",
         "Munkahelyi elsősegély-oktatás", "Kötelező munkahelyi képzés tanúsítvánnyal, korszerű demonstrációs eszközökkel."),
        ("/oktatas-extrak/", "oktatas-extrak", "Piros szív és sztetoszkóp",
         "Oktatás extrák", "Szimulációs „Éles helyzetben” tréning, gyermek-, középiskolai és angol nyelvű oktatás."),
        ("/szakmai-felhasznaloknak/", "szakmai-felhasznaloknak", "Mentők ellátják a sérültet",
         "Szakmai felhasználóknak", "Lifeline ARM mellkaskompressziós készülék, CPR Assist és TEC-5600 manuális defibrillátor."),
    ]
    cards = "".join(f'''<article class="card card--link reveal">
  <div class="card__media">{img(n, a, "(min-width: 1000px) 280px, (min-width: 640px) 50vw, 100vw")}</div>
  <div class="card__body">
    <h3><a href="{h}">{t}</a></h3>
    <p>{d}</p>
    <span class="link-arrow">Részletek {icon("arrow")}</span>
  </div>
</article>''' for h, n, a, t, d in services)
    faq_html, faq_ld = faq_block(AED_FAQ, soft=False)
    body = f'''<section class="hero" aria-labelledby="hero-cim">
  <div class="container hero-grid">
    <div>
      <p class="eyebrow">AED defibrillátorok Japánból</p>
      <h1 id="hero-cim">Automata defibrillátor és <span class="accent">elsősegély-oktatás</span> egy helyen</h1>
      <p class="lead">Nihon Kohden AED-3100 automata defibrillátorok üzemkészen, valamint gyakorlatorientált munkahelyi és iskolai elsősegély-oktatás, sürgősségi ellátásban jártas oktatókkal.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="/ajanlatkeres/">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a>
        <a class="btn btn--secondary" href="/automata-defibrillator/">Az AED-3100 részletei</a>
      </div>
      <ul class="hero-points">
        <li>{icon("check")} 8 év garancia</li>
        <li>{icon("check")} Magyar hangutasítás</li>
        <li>{icon("check")} Ingyenes tanfolyam AED mellé</li>
      </ul>
    </div>
    <div class="hero-visual">
      <div class="hero-visual__img">{img("aed-3100-made-in-japan", "Nihon Kohden Cardiolife AED-3100 automata defibrillátor – Made in Japan", "(min-width: 960px) 520px, 90vw", eager=True)}</div>
    </div>
  </div>
</section>

<section class="statement-section" aria-label="Küldetésünk">
  <div class="container">
    <p class="statement reveal">A defibrillátor akkor ér igazán sokat, ha a környezetében lévők <em>magabiztosan használják.</em> Ezért a készülékek mellé gyakorlatorientált oktatást is kínálunk.</p>
  </div>
</section>

<section class="section" aria-labelledby="szolg-cim">
  <div class="container">
    <div class="section-head">
      <h2 id="szolg-cim">Eszköz és tudás – hogy vészhelyzetben is cselekedni tudjon</h2>
    </div>
    <div class="grid grid--4">{cards}</div>
  </div>
</section>

<section class="section section--soft" aria-labelledby="aed-cim">
  <div class="container split">
    <div class="media-frame media-frame--product reveal">{img("aed-3100-nyitott-fedellel", "Nyitott fedelű AED-3100 defibrillátor elektródával és képes útmutatóval", "(min-width: 960px) 560px, 100vw")}</div>
    <div>
      <h2 id="aed-cim">Nihon Kohden AED-3100 automata defibrillátor</h2>
      <p class="lead">Kompletten, üzemkészen – teleppel és elektródával szállítva.</p>
      <ul class="checklist checklist--2">
        <li>{icon("check")} Felnőtt és gyermek páciensekhez</li>
        <li>{icon("check")} ActiBiphasic technológia</li>
        <li>{icon("check")} Magyar nyelvű hangutasítások</li>
        <li>{icon("check")} Napi önteszt</li>
        <li>{icon("check")} 8 év garancia</li>
        <li>{icon("check")} Opcionális WiFi-távfelügyelet</li>
      </ul>
      <div class="price-box price-box--cta">
        <div>
          <span class="price-box__label">Ár</span>
          <span class="price-box__value">580.000 Ft <small>+ ÁFA</small></span>
          <span class="price-box__note">Ajándék tanfolyammal (max. 20 fő).</span>
        </div>
        <a class="btn btn--primary" href="/ajanlatkeres/?targy=aed">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a>
      </div>
      <a class="link-arrow" href="/automata-defibrillator/">Az AED-3100 termékoldala {icon("arrow")}</a>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="oktatas-cim">
  <div class="container split split--reverse">
    <div class="media-frame reveal">{img("munkahelyi-elsosegely-oktatas", "Elsősegély-oktatás: újraélesztés gyakorlása babán, laptopon oktatóanyag", "(min-width: 960px) 560px, 100vw")}</div>
    <div>
      <h2 id="oktatas-cim">Munkahelyi elsősegély-oktatás tanúsítvánnyal</h2>
      <p>Munkahelyek számára kötelező, gyakorlatorientált képzés, amely a komplex helyzetkezelésre is felkészít. Oktatóink jártasak a sürgősségi ellátásban.</p>
      <ul class="checklist">
        <li>{icon("check")} Korszerű demonstrációs eszközök</li>
        <li>{icon("check")} 4–8 óra, a választott tematikától függően</li>
        <li>{icon("check")} 9.000 Ft/fő (min. 5 fő) – AED vásárlása esetén ingyenes</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--primary" href="/ajanlatkeres/?targy=oktatas">Oktatást kérek {icon("arrow", "icon--arrow")}</a>
        <a class="btn btn--secondary" href="/munkahelyi-elsosegely-oktatas/">Részletek</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--soft" aria-labelledby="sajto-cim">
  <div class="container">
    <div class="section-head">
      <h2 id="sajto-cim">Érdekes linkek a témában</h2>
    </div>
    {press_items(PRESS[:3], "h3")}
    <p style="margin-top:24px"><a class="link-arrow" href="/erdekes-linkek-sajtofigyelo/">Összes link {icon("arrow")}</a></p>
  </div>
</section>

{faq_html}

<section class="section section--soft section--tight" aria-labelledby="gyarto-cim">
  <div class="container">
    <div class="section-head section-head--center">
      <h2 id="gyarto-cim">Közvetlen kapcsolat a gyártóval</h2>
    </div>
    <div class="partners partners--center">
      <a class="partner" href="https://eu.nihonkohden.com/en/contactus" target="_blank" rel="noopener"><img src="/assets/img/nihon-kohden-logo.png" width="357" height="48" alt="Nihon Kohden" loading="lazy"></a>
      <a class="partner" href="https://nkuniversity.org/" target="_blank" rel="noopener"><img src="/assets/img/nihon-kohden-university-logo.png" width="362" height="61" alt="Nihon Kohden University" loading="lazy"></a>
    </div>
  </div>
</section>

{cta_band()}'''
    return page("/", "AED defibrillátor és elsősegély-oktatás | Emcrem",
                "Nihon Kohden AED-3100 automata defibrillátor Japánból 8 év garanciával, valamint munkahelyi és iskolai elsősegély-oktatás tanúsítvánnyal. Kérjen ajánlatot!",
                body, schema=[faq_ld])


def build_aed():
    crumbs, bc = breadcrumbs([("Automata defibrillátor", "/automata-defibrillator/")])
    gal = gallery([
        ("aed-3100-automata-defibrillator", "Nihon Kohden Cardiolife AED-3100 automata defibrillátor elölnézetből"),
        ("aed-3100-nyitott-fedellel", "AED-3100 nyitott fedéllel, elektródával és képes útmutatóval"),
        ("aed-3100-hordtaska", "AED-3100 narancssárga hordtáskában"),
        ("aed-fali-tarolo-szekreny", "AED fali tárolószekrény ajtónyitásra megszólaló riasztóval"),
        ("aed-3100-made-in-japan", "AED-3100 – Made in Japan"),
    ], "AED-3100 termékképek")
    specs = [
        ("users", "Felnőtt és gyermek páciensekhez"),
        ("zap", "ActiBiphasic technológia"),
        ("voice", "Magyar hangutasítások, aktuális protokoll"),
        ("calendar", "Napi önteszt"),
        ("shield", "8 év garancia"),
        ("wifi", "WiFi-távfelügyelet (opcionális)"),
    ]
    spec_html = "".join(f'<li><span class="spec-icon">{icon(i)}</span>{t}</li>' for i, t in specs)
    faq_html, faq_ld = faq_block(AED_FAQ[:5])
    product_ld = {
        "@type": "Product",
        "@id": SITE + "/automata-defibrillator/#product",
        "name": "Nihon Kohden Cardiolife AED-3100 automata defibrillátor",
        "model": "AED-3100",
        "brand": {"@type": "Brand", "name": "Nihon Kohden"},
        "image": [SITE + src_of("aed-3100-automata-defibrillator"), SITE + src_of("aed-3100-nyitott-fedellel"),
                  SITE + src_of("aed-3100-hordtaska")],
        "description": "Automata külső defibrillátor (AED) felnőtt és gyermek páciensekhez, ActiBiphasic technológiával, magyar nyelvű hangutasításokkal, napi önteszttel és 8 év garanciával. Kompletten, üzemkészen, teleppel és elektródával.",
        "countryOfOrigin": "JP",
        "offers": {
            "@type": "Offer",
            "url": SITE + "/automata-defibrillator/",
            "priceCurrency": "HUF",
            "price": "580000",
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": "580000", "priceCurrency": "HUF",
                                   "valueAddedTaxIncluded": False},
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {"@id": SITE + "/#org"},
        },
    }
    body = f'''<section class="section" style="padding-top:clamp(16px,3vh,48px)">
  <div class="container">
    {crumbs}
    <div class="product">
      <div class="product__gallery">{gal}</div>
      <div>
        <h1>AED-3100 automata defibrillátor</h1>
        <p class="lead">A Nihon Kohden Cardiolife AED-3100 kompletten, üzemkészen érkezik – teleppel és elektródával –, így azonnal a helyére kerülhet.</p>
        <h2 class="visually-hidden">Főbb tulajdonságok</h2>
        <ul class="spec-list">{spec_html}</ul>
        <div class="price-box price-box--cta">
          <div>
            <span class="price-box__label">Ár</span>
            <span class="price-box__value">580.000 Ft <small>+ ÁFA</small></span>
            <span class="price-box__note">Komplett csomag: készülék, telep és elektróda.</span>
          </div>
          <a class="btn btn--primary" href="/ajanlatkeres/?targy=aed">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a>
        </div>
        <p class="mb-0 text-muted">Kérdése van? Hívjon: <a href="tel:{ORG["phone_tel"]}"><strong>{ORG["phone_display"]}</strong></a></p>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight" aria-labelledby="ajandek-cim" style="padding-top:0">
  <div class="container">
    <div class="gift reveal">
      <span class="feature-icon feature-icon--red">{icon("gift")}</span>
      <div>
        <h2 id="ajandek-cim">A megrendelőnek ingyen biztosítjuk</h2>
        <p class="text-muted mb-0">Hogy a készüléket vészhelyzetben is magabiztosan használják, a vásárlás mellé oktatást adunk.</p>
        <div class="gift-options">
          <div class="gift-option"><strong>1 db újraélesztő tanfolyam</strong><p>Az AED-3100 saját gyakorló defibrillátorával, számítógépes értékelésű szimulációs eszközökkel.</p></div>
          <div class="gift-or" aria-hidden="true">vagy</div>
          <div class="gift-option"><strong>Teljes körű munkahelyi elsősegély-tanfolyam</strong><p>Legfeljebb 20 fő részére. <a href="/munkahelyi-elsosegely-oktatas/">A képzés részletei</a></p></div>
        </div>
      </div>
    </div>
  </div>
</section>

{faq_html}
{cta_band("Kérjen ajánlatot az AED-3100 készülékre", "Segítünk kiválasztani a megfelelő elhelyezést és kiegészítőket, és megszervezzük az ajándék tanfolyamot is.")}'''
    return page("/automata-defibrillator/", "AED-3100 automata defibrillátor – ár, garancia | Emcrem",
                "Nihon Kohden AED-3100 automata defibrillátor: magyar hangutasítás, napi önteszt, 8 év garancia. Ár: 580.000 Ft + ÁFA, ajándék elsősegély-tanfolyammal.",
                body, schema=[bc, product_ld, faq_ld], og_type="product", page_type="ItemPage")


def build_training():
    crumbs, bc = breadcrumbs([("Munkahelyi elsősegély-oktatás", "/munkahelyi-elsosegely-oktatas/")])
    why = [
        ("cert", "Elfogadott tanúsítvány", "Munkahelyek számára kötelező képzés, amely az OMMF által elfogadott tanúsítványt is nyújt."),
        ("heart", "Gyakorlatorientált", "Korszerű demonstrációs eszközök, a komplex helyzetkezelésre felkészítő oktatás."),
        ("steth", "Tapasztalt oktatók", "A sürgősségi ellátásban jártassággal rendelkező oktatók."),
    ]
    why_html = "".join(f'<div class="feature reveal"><span class="feature-icon">{icon(i)}</span><h3>{t}</h3><p>{d}</p></div>'
                       for i, t, d in why)
    course_ld = {
        "@type": "Course",
        "@id": SITE + "/munkahelyi-elsosegely-oktatas/#course",
        "name": "Munkahelyi elsősegély-oktatás",
        "description": "Munkahelyek számára kötelező, gyakorlatorientált elsősegély-képzés tanúsítvánnyal, korszerű demonstrációs eszközökkel, sürgősségi ellátásban jártas oktatókkal. Időtartam: 4–8 óra.",
        "inLanguage": "hu",
        "provider": {"@id": SITE + "/#org"},
        "offers": {"@type": "Offer", "category": "Paid", "price": "9000", "priceCurrency": "HUF",
                   "priceSpecification": {"@type": "UnitPriceSpecification", "price": "9000", "priceCurrency": "HUF",
                                          "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitText": "fő"}}},
        "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": "PT4H"},
    }
    body = f'''{page_hero(crumbs, "Elsősegély-oktatás", "Munkahelyi elsősegély-oktatás",
                     "Munkahelyek számára kötelező, gyakorlatorientált képzés tanúsítvánnyal – korszerű demonstrációs eszközökkel, a sürgősségi ellátásban jártas oktatókkal.",
                     img("munkahelyi-elsosegely-oktatas", "Újraélesztés gyakorlása babán munkahelyi elsősegély-tanfolyamon", "(min-width: 960px) 460px, 100vw", eager=True),
                     f'<div class="btn-row"><a class="btn btn--primary" href="/ajanlatkeres/?targy=oktatas">Oktatást kérek {icon("arrow", "icon--arrow")}</a><a class="btn btn--secondary" href="/oktatas-extrak/">Oktatás extrák</a></div>')}

<section class="section" aria-labelledby="miert-cim">
  <div class="container">
    <div class="section-head">
      <h2 id="miert-cim">Felkészít a valós helyzetekre</h2>
    </div>
    <div class="grid grid--3">{why_html}</div>
  </div>
</section>

<section class="section section--soft" aria-labelledby="tartalom-cim">
  <div class="container split">
    <div>
      <h2 id="tartalom-cim">Minden képzés tartalmazza</h2>
      <ul class="checklist">
        <li>{icon("check")} Alapvető járványtani ismeretek</li>
        <li>{icon("check")} A megelőzés aktuális kérdései</li>
        <li>{icon("check")} Infekciókontroll</li>
        <li>{icon("check")} Személyes higiénia a gyakorlatban</li>
      </ul>
    </div>
    <div class="info-cards" style="grid-template-columns:1fr">
      <div class="info-card"><span class="feature-icon">{icon("clock")}</span><span class="info-card__label">Időtartam</span><span class="info-card__value">4–8 óra <small>a választott tematikától függően</small></span></div>
      <div class="info-card"><span class="feature-icon">{icon("users")}</span><span class="info-card__label">Ár</span><span class="info-card__value">9.000 Ft/fő <small>(min. 5 fő)</small></span></div>
      <div class="info-card info-card--highlight"><span class="feature-icon">{icon("gift")}</span><span class="info-card__label">Automata defibrillátor vásárlása esetén</span><span class="info-card__value">Ingyenes – max. 20 főig <small><a href="/automata-defibrillator/">AED-3100 →</a></small></span></div>
    </div>
  </div>
</section>

{cta_band("Szervezzen oktatást a munkahelyén", "Írja meg a létszámot és az időpont-elképzelést, és összeállítjuk a megfelelő tematikát.")}'''
    return page("/munkahelyi-elsosegely-oktatas/", "Munkahelyi elsősegély-oktatás tanúsítvánnyal | Emcrem",
                "Kötelező munkahelyi elsősegély-oktatás tanúsítvánnyal, 4–8 órában, sürgősségi ellátásban jártas oktatókkal. 9.000 Ft/fő, AED vásárlásakor ingyenes.",
                body, schema=[bc, course_ld])


def build_extras():
    crumbs, bc = breadcrumbs([("Oktatás extrák", "/oktatas-extrak/")])
    blocks = [
        ("alert", "red", "„Éles helyzetben” – elsősegély-oktatás imitátorok bevonásával",
         "<p>Cél a stresszhelyzetekben történő döntés- és cselekvőképesség fejlesztése. A jelentős pszichés terhelést jelentő váratlan helyzetek, balesetek szimulációja és azok megoldásában való aktív részvétel az egyik leghatékonyabb formája a tudás biztonságossá tételének.</p>"
         "<p>A szimuláció a sebzések, sérülések, váratlan tünetek élethű megjelenítésétől a több sérültes balesetig terjedhet.</p>",
         ["Megrendelés előtt előzetes egyeztetés szükséges"]),
        ("smile", "orange", "Elsősegély-oktatás gyermekeknek",
         "<p>Általános iskolásoknak, életkor szerinti csoportbontásban. Kis létszámú csoportfoglalkozás, melynek célja a potenciális veszélyek, veszélyhelyzetek felismerése és kezelése az életkori sajátosságok figyelembevételével. A módszertant szituációs gyakorlatok, játékos feladatok alkotják.</p>"
         "<p>A foglalkozást két fő, egy pszichológus és egy orvos vezeti.</p>",
         ["2 × 45 perc", "Max. 12 fő", "Pszichológus + orvos"]),
        ("book", "", "Középiskolai elsősegély-oktatás",
         "<p>Órarendbe illesztetten vagy azon kívül, szaktanár vezetésével.</p>", ["Órarendbe illeszthető"]),
        ("steth", "green", "Egészségügyi szakmai oktatás",
         "<p>Szakmai oktatás keretében, elsősorban a sürgősségi ellátás szaktárgyait érintően.</p>", ["Sürgősségi ellátás"]),
        ("globe", "", "Elsősegély-oktatás angol nyelven",
         "<p>Az angol nyelvben és a mentőellátásban is járatos oktatókkal.</p>", ["English"]),
    ]
    cards = []
    for i, (ic, col, title, text, tags) in enumerate(blocks):
        tg = "".join(f'<span class="tag">{icon("check")} {t}</span>' for t in tags)
        cls = f" feature-icon--{col}" if col else ""
        cards.append(f'<article class="row-item reveal"><div class="row-item__head"><span class="feature-icon{cls}">{icon(ic)}</span>'
                     f'<h2>{title}</h2></div><div class="row-item__body">{text}<div class="meta">{tg}</div></div></article>')
    body = f'''{page_hero(crumbs, "Speciális képzések", "Oktatás extrák",
                     "Szimulációs tréning, gyermek- és középiskolai foglalkozások, egészségügyi szakmai és angol nyelvű elsősegély-oktatás – a célcsoporthoz igazítva.",
                     img("oktatas-extrak", "Piros szív és sztetoszkóp", "(min-width: 960px) 460px, 100vw", eager=True),
                     f'<div class="btn-row"><a class="btn btn--primary" href="/ajanlatkeres/?targy=extrak">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a></div>')}

<section class="section" aria-label="Képzések">
  <div class="container">
    <div class="rows">{"".join(cards)}</div>
  </div>
</section>

{cta_band("Egyedi képzést tervez?", "Iskolai csoport, egészségügyi intézmény vagy nemzetközi csapat – mondja el az igényeit, és összeállítjuk a programot.")}'''
    return page("/oktatas-extrak/", "Elsősegély-oktatás iskoláknak, angolul | Emcrem",
                "„Éles helyzetben” szimulációs elsősegély-tréning, gyermek- és középiskolai oktatás, egészségügyi szakmai képzés és angol nyelvű elsősegély-oktatás.",
                body, schema=[bc])


def build_pro():
    crumbs, bc = breadcrumbs([("Szakmai felhasználóknak", "/szakmai-felhasznaloknak/")])

    def product(pid, eyebrow, title, desc_html, gal, url, reverse=False):
        return f'''<article class="pro-product split{" split--reverse" if reverse else ""}" id="{pid}" aria-labelledby="{pid}-cim">
  <div>{gal}</div>
  <div>
    <h2 id="{pid}-cim">{title}</h2>
    {desc_html}
    <div class="btn-row">
      <a class="btn btn--primary" href="/ajanlatkeres/?targy=szakmai">Ajánlatot kérek {icon("arrow", "icon--arrow")}</a>
      <a class="btn btn--secondary" href="{url}" target="_blank" rel="noopener">Részletek a gyártónál {icon("external")}<span class="visually-hidden"> (új lapon nyílik)</span></a>
    </div>
  </div>
</article>'''

    p1 = product("lifeline-arm", "Mellkaskompresszió", "Lifeline ARM mellkaskompressziós készülék",
                 '<p class="lead">Automatikus mellkaskompressziós készülék a folyamatos, egyenletes újraélesztéshez.</p>',
                 gallery([("lifeline-arm-mellkaskompresszios-keszulek", "Lifeline ARM mellkaskompressziós készülék"),
                          ("lifeline-arm-oldalnezet", "Lifeline ARM oldalnézetből"),
                          ("lifeline-arm-hordtaska", "Lifeline ARM piros hordtáskában"),
                          ("lifeline-arm-hasznalat-kozben", "Lifeline ARM használat közben a páciens mellkasán")],
                         "Lifeline ARM képek"),
                 "https://eu.nihonkohden.com/products/resuscitation/lifeline-arm")
    p2 = product("cpr-assist", "CPR-minőség", "CPR Assist",
                 '<p class="lead">A folyamatos és minőségi mellkaskompressziót ellenőrző eszköz.</p>'
                 f'<ul class="checklist"><li>{icon("check")} Éles helyzetben is alkalmazható</li><li>{icon("check")} Képzés során is használható</li></ul>',
                 gallery([("cpr-assist-mellkaskompresszio-ellenorzo", "Nihon Kohden CPR Assist mellkaskompresszió-ellenőrző eszköz"),
                          ("cpr-assist-hasznalat-kozben", "CPR Assist használat közben újraélesztéskor")], "CPR Assist képek"),
                 "https://eu.nihonkohden.com/products/resuscitation/cpr-assist", reverse=True)
    p3 = product("tec-5600", "Manuális defibrillátor", "Manuális defibrillátor és monitor – Nihon Kohden TEC-5600 sorozat",
                 '<p class="lead">Elérhető típusok:</p><ul class="model-list"><li>TEC-5621 K</li><li>TEC-5631 K</li></ul>'
                 f'<ul class="checklist"><li>{icon("check")} Opcionális külső pacemaker (PM) funkcióval</li></ul>',
                 gallery([("nihon-kohden-tec-5600-defibrillator-monitor", "Nihon Kohden Cardiolife TEC-5600 manuális defibrillátor és monitor"),
                          ("nihon-kohden-tec-5600-allvanyon", "TEC-5600 defibrillátor gurulós állványon"),
                          ("nihon-kohden-tec-5600-korhazi-hasznalat", "TEC-5600 defibrillátor kórházi használat közben")], "TEC-5600 képek"),
                 "https://eu.nihonkohden.com/products/resuscitation/cardiolife-tec-8300")
    items = [
        ("Lifeline ARM mellkaskompressziós készülék", "lifeline-arm-mellkaskompresszios-keszulek"),
        ("CPR Assist", "cpr-assist-mellkaskompresszio-ellenorzo"),
        ("Nihon Kohden TEC-5600 manuális defibrillátor és monitor", "nihon-kohden-tec-5600-defibrillator-monitor"),
    ]
    list_ld = {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1,
         "item": {"@type": "Product", "name": n, "image": SITE + src_of(im), "brand": {"@type": "Brand", "name": "Nihon Kohden"}}}
        for i, (n, im) in enumerate(items)]}
    jump = "".join(f'<a href="#{a}">{t}</a>' for a, t in
                   [("lifeline-arm", "Lifeline ARM"), ("cpr-assist", "CPR Assist"), ("tec-5600", "TEC-5600")])
    body = f'''{page_hero(crumbs, "Egészségügyi szakembereknek", "Szakmai felhasználóknak",
                     "Professzionális újraélesztési eszközök mentőszolgálatok, kórházak és egészségügyi intézmények számára – közvetlen kapcsolattal a gyártóhoz.",
                     img("szakmai-felhasznaloknak", "Mentőápolók ellátják a hordágyon fekvő sérültet", "(min-width: 960px) 460px, 100vw", eager=True),
                     f'<nav aria-label="Termékek az oldalon" class="jump-links">{jump}</nav>')}

<section class="section" aria-label="Termékek">
  <div class="container">
    {p1}
    {p2}
    {p3}
  </div>
</section>

{cta_band("Szakmai ajánlatot kér?", "Mentőszolgálatok, kórházak és intézmények számára egyedi ajánlatot készítünk.")}'''
    return page("/szakmai-felhasznaloknak/", "Lifeline ARM, CPR Assist, TEC-5600 defibrillátor | Emcrem",
                "Szakmai újraélesztési eszközök: Lifeline ARM mellkaskompressziós készülék, CPR Assist és Nihon Kohden TEC-5600 manuális defibrillátor és monitor.",
                body, schema=[bc, list_ld])


def build_quote():
    crumbs, bc = breadcrumbs([("Ajánlatkérés", "/ajanlatkeres/")])
    o = ORG
    body = f'''<section class="page-hero" style="padding-bottom:clamp(32px,4vw,48px)">
  <div class="container">
    {crumbs}
    <h1>Kérjen ajánlatot</h1>
    <p class="lead mb-0">Defibrillátor, munkahelyi oktatás vagy szakmai eszköz – töltse ki az űrlapot, és hamarosan jelentkezünk.</p>
  </div>
</section>

<section class="section" style="padding-top:clamp(32px,4vw,56px)">
  <div class="container form-layout">
    <div class="form-card" id="urlap">
      <div class="alert alert--error" id="urlap-hiba" role="alert" hidden>{icon("alert")}<span></span></div>
      <form id="ajanlatkero-urlap" action="/kuldes.php" method="post" accept-charset="UTF-8"{f' data-mailto="{o["email"]}"' if FORM_MAILTO else ""}>
        <h2 class="visually-hidden">Ajánlatkérő űrlap</h2>
        <div class="form-grid">
          <div class="field"><label for="nev">Név <span class="req" aria-hidden="true">*</span></label><input id="nev" name="nev" type="text" autocomplete="name" required maxlength="120"></div>
          <div class="field"><label for="email">E-mail-cím <span class="req" aria-hidden="true">*</span></label><input id="email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
          <div class="field"><label for="telefon">Telefonszám <span class="hint">(nem kötelező)</span></label><input id="telefon" name="telefon" type="tel" autocomplete="tel" maxlength="40"></div>
          <div class="field"><label for="ceg">Cég / intézmény <span class="hint">(nem kötelező)</span></label><input id="ceg" name="ceg" type="text" autocomplete="organization" maxlength="160"></div>
          <div class="field"><label for="targy">Miben segíthetünk?</label>
            <select id="targy" name="targy">
              <option value="aed">Automata defibrillátor (AED-3100)</option>
              <option value="oktatas">Munkahelyi elsősegély-oktatás</option>
              <option value="extrak">Oktatás extrák (szimuláció, iskola, angol nyelvű)</option>
              <option value="szakmai">Szakmai eszközök (Lifeline ARM, CPR Assist, TEC-5600)</option>
              <option value="egyeb">Egyéb kérdés</option>
            </select></div>
          <div class="field"><label for="letszam">Létszám <span class="hint">(oktatás esetén)</span></label><input id="letszam" name="letszam" type="number" min="1" max="999" inputmode="numeric"></div>
          <div class="field span-2"><label for="uzenet">Üzenet</label><textarea id="uzenet" name="uzenet" maxlength="5000" placeholder="Pl. a defibrillátor tervezett helye, darabszám, az oktatás kívánt időpontja…"></textarea></div>
          <div class="hp-field" aria-hidden="true"><label for="weboldal">Ezt a mezőt hagyja üresen</label><input id="weboldal" name="weboldal" type="text" tabindex="-1" autocomplete="off"></div>
          <div class="span-2"><label class="checkbox"><input type="checkbox" name="adatvedelem" value="1" required><span>Elolvastam és elfogadom az <a href="/adatkezelesi-tajekoztato/">adatkezelési tájékoztatót</a>. <span class="req" aria-hidden="true">*</span></span></label></div>
          <div class="span-2"><button class="btn btn--primary btn--block" type="submit">{icon("send")} Ajánlatkérés elküldése</button></div>
          <p class="form-note span-2">A <span aria-hidden="true">*</span>-gal jelölt mezők kitöltése kötelező.</p>
        </div>
      </form>
    </div>
    <aside class="contact-aside" aria-label="Közvetlen elérhetőség">
      <div class="contact-line"><span class="feature-icon feature-icon--red">{icon("phone")}</span><div><span>Hívjon minket</span><a href="tel:{o["phone_tel"]}">{o["phone_display"]}</a></div></div>
      <div class="contact-line"><span class="feature-icon">{icon("mail")}</span><div><span>Írjon nekünk</span><a href="mailto:{o["email"]}">{o["email"]}</a></div></div>
      <div class="aside-block">
        <h2>Mi történik ezután?</h2>
        <ol class="steps">
          <li><strong>Feldolgozzuk a kérését</strong><span>Átnézzük az igényeit.</span></li>
          <li><strong>Felvesszük Önnel a kapcsolatot</strong><span>E-mailben vagy telefonon egyeztetünk a részletekről.</span></li>
          <li><strong>Személyre szabott ajánlat</strong><span>Megkapja az ajánlatot, kötelezettség nélkül.</span></li>
        </ol>
      </div>
    </aside>
  </div>
</section>'''
    return page("/ajanlatkeres/", "Ajánlatkérés – AED és elsősegély-oktatás | Emcrem",
                "Kérjen ajánlatot AED-3100 automata defibrillátorra, munkahelyi elsősegély-oktatásra vagy szakmai újraélesztési eszközökre. Gyors válasz, kötelezettség nélkül.",
                body, schema=[bc], page_type="ContactPage")


def build_contact():
    crumbs, bc = breadcrumbs([("Kapcsolat", "/kapcsolat/")])
    o = ORG
    maps = "https://www.google.com/maps/search/?api=1&query=" + "Esztergom%2C+%C3%9Aj+utca+12."
    body = f'''{page_hero(crumbs, "Kapcsolat", "Kapcsolat",
                     "Kérdése van a defibrillátorokkal vagy az oktatással kapcsolatban? Hívjon, írjon, vagy kérjen ajánlatot az űrlapon.",
                     None,
                     f'<div class="btn-row"><a class="btn btn--primary" href="/ajanlatkeres/">Ajánlatkérés {icon("arrow", "icon--arrow")}</a></div>')}

<section class="section" aria-labelledby="elerhetoseg-cim">
  <div class="container">
    <div class="contact-layout">
      <div class="contact-intro">
        <h2 id="elerhetoseg-cim">{o["name"]}</h2>
        <p>Defibrillátorral, oktatással vagy szakmai eszközökkel kapcsolatos kérdésével keressen minket telefonon vagy e-mailben. Konkrét ajánlathoz használja az <a href="/ajanlatkeres/">ajánlatkérő űrlapot</a>.</p>
      </div>
      <dl class="contact-list">
        <div><dt>Telefon</dt><dd><a class="contact-phone" href="tel:{o["phone_tel"]}">{o["phone_display"]}</a></dd></div>
        <div><dt>E-mail</dt><dd><a href="mailto:{o["email"]}">{o["email"]}</a><br><a href="mailto:{o["email2"]}">{o["email2"]}</a></dd></div>
        <div><dt>Levelezési cím</dt><dd><address>{o["name"]}<br>{o["zip"]} {o["city"]}, {o["street"]}</address>
          <a class="contact-map" href="{maps}" target="_blank" rel="noopener">Megnyitás térképen {icon("external")}<span class="visually-hidden"> (új lapon nyílik)</span></a></dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section section--soft section--tight" aria-labelledby="gyarto-cim">
  <div class="container">
    <div class="section-head section-head--center">
      <h2 id="gyarto-cim">Közvetlen kapcsolat a gyártóval</h2>
    </div>
    <div class="partners partners--center">
      <a class="partner" href="https://eu.nihonkohden.com/en/contactus" target="_blank" rel="noopener"><img src="/assets/img/nihon-kohden-logo.png" width="357" height="48" alt="Nihon Kohden – kapcsolat" loading="lazy"></a>
      <a class="partner" href="https://nkuniversity.org/" target="_blank" rel="noopener"><img src="/assets/img/nihon-kohden-university-logo.png" width="362" height="61" alt="Nihon Kohden University" loading="lazy"></a>
    </div>
  </div>
</section>

{cta_band()}'''
    return page("/kapcsolat/", "Kapcsolat – Emcrem Kft., Esztergom | Emcrem",
                f"Emcrem Kft., {o['zip']} {o['city']}, {o['street']} Telefon: {o['phone_display']}, e-mail: {o['email']}. AED defibrillátorok és elsősegély-oktatás.",
                body, schema=[bc], page_type="ContactPage")


def build_press():
    crumbs, bc = breadcrumbs([("Érdekes linkek, sajtófigyelő", "/erdekes-linkek-sajtofigyelo/")])
    list_ld = {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "url": links[0][1]} for i, (d, t, s, links) in enumerate(PRESS)]}
    body = f'''<section class="page-hero" style="padding-bottom:clamp(32px,4vw,48px)">
  <div class="container">
    {crumbs}
    <h1>Érdekes linkek, sajtófigyelő</h1>
    <p class="lead mb-0">Válogatott cikkek és videók az újraélesztésről, a defibrillátorokról és az elsősegélynyújtásról.</p>
  </div>
</section>
<section class="section" style="padding-top:clamp(32px,4vw,56px)" aria-label="Linkek">
  <div class="container">
    {press_items(PRESS)}
  </div>
</section>
{cta_band()}'''
    return page("/erdekes-linkek-sajtofigyelo/", "Érdekes linkek, sajtófigyelő – AED, újraélesztés | Emcrem",
                "Válogatott cikkek és videók az újraélesztésről, az automata defibrillátorok (AED) használatáról és a hirtelen szívhalálról.",
                body, schema=[bc, list_ld], page_type="CollectionPage")


def build_privacy():
    crumbs, bc = breadcrumbs([("Adatkezelési tájékoztató", "/adatkezelesi-tajekoztato/")])
    o = ORG
    body = f'''<section class="page-hero" style="padding-bottom:clamp(32px,4vw,48px)">
  <div class="container">
    {crumbs}
    <h1>Adatkezelési tájékoztató</h1>
    <p class="lead mb-0">Hatályos: {hu_date(LASTMOD)}</p>
  </div>
</section>
<section class="section" style="padding-top:clamp(32px,4vw,56px)">
  <div class="container prose">
    <h2>1. Az adatkezelő</h2>
    <div class="table-wrap"><table>
      <tr><th scope="row">Név</th><td>{o["name"]}</td></tr>
      <tr><th scope="row">Székhely / levelezési cím</th><td>{o["zip"]} {o["city"]}, {o["street"]}</td></tr>
      <tr><th scope="row">E-mail</th><td><a href="mailto:{o["email"]}">{o["email"]}</a></td></tr>
      <tr><th scope="row">Telefon</th><td>{o["phone_display"]}</td></tr>
      <tr><th scope="row">Cégjegyzékszám</th><td><span class="todo">[kitöltendő]</span></td></tr>
      <tr><th scope="row">Adószám</th><td><span class="todo">[kitöltendő]</span></td></tr>
      <tr><th scope="row">Weboldal</th><td>{SITE}</td></tr>
    </table></div>

    <h2>2. Milyen személyes adatokat kezelünk, és milyen céllal?</h2>
    <h3>Ajánlatkérő űrlap és kapcsolatfelvétel</h3>
    <p>Ha az ajánlatkérő űrlapot kitölti, vagy e-mailben, telefonon megkeres minket, az alábbi adatokat kezeljük:</p>
    <ul>
      <li>név, e-mail-cím (kötelező),</li>
      <li>telefonszám, cég / intézmény neve, létszám (nem kötelező),</li>
      <li>az üzenet tartalma.</li>
    </ul>
    <p><strong>Cél:</strong> a megkeresés megválaszolása, ajánlat készítése, kapcsolattartás.<br>
    <strong>Jogalap:</strong> az érintett hozzájárulása (GDPR 6. cikk (1) a) pont), illetve a szerződés megkötését megelőzően az érintett kérésére történő lépések megtétele (GDPR 6. cikk (1) b) pont).<br>
    <strong>Időtartam:</strong> a megkeresés lezárásától számított <span class="todo">[1 év – kitöltendő]</span>, illetve a hozzájárulás visszavonásáig. Szerződéskötés esetén a számviteli és egyéb jogszabályi kötelezettségek szerinti ideig.</p>

    <h3>Sütik (cookie-k)</h3>
    <p>A weboldal nem használ követő, reklám- vagy analitikai sütiket. A betűtípusokat saját szerverünkről töltjük be, harmadik félhez a látogatás adatai nem kerülnek. Ha a jövőben analitikai eszközt vezetünk be, erről itt tájékoztatjuk, és a működéséhez előzetes hozzájárulást kérünk.</p>

    <h3>Külső hivatkozások</h3>
    <p>Az oldalon található külső hivatkozások (pl. sajtócikkek, YouTube-videók, a gyártó weboldala, Facebook, Instagram) más szolgáltatók oldalaira vezetnek. Ezek adatkezelésére az adott szolgáltató saját tájékoztatója vonatkozik.</p>

    <h3>Szerver naplófájlok</h3>
    <p>A tárhelyszolgáltató a weboldal biztonságos működése érdekében technikai naplót vezethet (pl. IP-cím, időpont, böngésző típusa). Tárhelyszolgáltató: <span class="todo">[név, cím – kitöltendő]</span>.</p>

    <h2>3. Kik férhetnek hozzá az adatokhoz?</h2>
    <p>Az adatokhoz kizárólag az {o["name"]} munkatársai férnek hozzá, a fenti célok teljesítéséhez szükséges mértékben. Az adatokat harmadik félnek nem adjuk át, kivéve, ha erre jogszabály kötelez. Adatfeldolgozóként a tárhely- és e-mail-szolgáltató működhet közre.</p>

    <h2>4. Hogyan védjük az adatokat?</h2>
    <p>Az oldal titkosított (HTTPS) kapcsolaton keresztül érhető el. Az adatokat a jogosulatlan hozzáférés, módosítás és törlés ellen megfelelő technikai és szervezési intézkedésekkel védjük.</p>

    <h2>5. Az Ön jogai</h2>
    <ul>
      <li>tájékoztatást kérhet a kezelt adatairól és hozzáférhet azokhoz,</li>
      <li>kérheti adatai helyesbítését, törlését vagy kezelésük korlátozását,</li>
      <li>tiltakozhat az adatkezelés ellen, és élhet az adathordozhatóság jogával,</li>
      <li>hozzájárulását bármikor visszavonhatja – ez nem érinti a visszavonás előtti adatkezelés jogszerűségét.</li>
    </ul>
    <p>Kérését a <a href="mailto:{o["email"]}">{o["email"]}</a> címre küldheti; legfeljebb egy hónapon belül válaszolunk.</p>

    <h2>6. Jogorvoslat</h2>
    <p>Ha úgy érzi, hogy adatai kezelése sérti a jogszabályokat, panaszt tehet a Nemzeti Adatvédelmi és Információszabadság Hatóságnál (NAIH, 1055 Budapest, Falk Miksa utca 9–11., <a href="https://www.naih.hu" target="_blank" rel="noopener">www.naih.hu</a>, ugyfelszolgalat@naih.hu), illetve bírósághoz fordulhat. Javasoljuk, hogy panaszával először minket keressen meg.</p>
  </div>
</section>'''
    return page("/adatkezelesi-tajekoztato/", "Adatkezelési tájékoztató | Emcrem",
                "Az Emcrem Kft. adatkezelési tájékoztatója: milyen adatokat kezelünk az ajánlatkérés során, milyen célból, és milyen jogok illetik meg Önt.",
                body, schema=[bc])


def build_thanks():
    body = f'''<section class="section page-hero" style="min-height:60vh;display:grid;align-items:center">
  <div class="container center" style="max-width:720px">
    <span class="feature-icon feature-icon--green" style="margin:0 auto 20px;width:72px;height:72px;border-radius:50%">{icon("check")}</span>
    <h1>Köszönjük megkeresését!</h1>
    <p class="lead">Üzenetét megkaptuk, hamarosan felvesszük Önnel a kapcsolatot. Sürgős esetben hívjon minket: <a href="tel:{ORG["phone_tel"]}">{ORG["phone_display"]}</a>.</p>
    <div class="btn-row" style="justify-content:center"><a class="btn btn--secondary" href="/">Vissza a kezdőlapra</a><a class="btn btn--secondary" href="/automata-defibrillator/">AED-3100</a></div>
  </div>
</section>'''
    return page("/koszonjuk/", "Köszönjük megkeresését | Emcrem", "Ajánlatkérését megkaptuk, hamarosan jelentkezünk.",
                body, noindex=True, current="/ajanlatkeres/")


def build_404():
    body = f'''<section class="section page-hero" style="min-height:60vh;display:grid;align-items:center">
  <div class="container center" style="max-width:720px">
    <h1>Az oldal nem található</h1>
    <p class="lead">Lehet, hogy a keresett oldal megszűnt vagy átköltözött. Az alábbi linkek segíthetnek:</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn btn--primary" href="/">Kezdőlap</a>
      <a class="btn btn--secondary" href="/automata-defibrillator/">Automata defibrillátor</a>
      <a class="btn btn--secondary" href="/munkahelyi-elsosegely-oktatas/">Elsősegély-oktatás</a>
    </div>
  </div>
</section>'''
    return page("/404.html", "Az oldal nem található | Emcrem", "A keresett oldal nem található.", body,
                noindex=True, current="")


def write_static(pages):
    urls = [p for p, noindex in pages if not noindex]
    prio = {"/": "1.0", "/automata-defibrillator/": "0.9", "/munkahelyi-elsosegely-oktatas/": "0.9",
            "/ajanlatkeres/": "0.8", "/adatkezelesi-tajekoztato/": "0.2"}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{SITE}{u}</loc><lastmod>{LASTMOD}</lastmod><priority>{prio.get(u, '0.7')}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /kuldes.php\nDisallow: /koszonjuk/\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": "Emcrem defibrillátor", "short_name": "Emcrem", "lang": "hu",
        "icons": [{"src": BASE + "icon-192.png", "sizes": "192x192", "type": "image/png"}],
        "theme_color": "#0b1d36", "background_color": "#ffffff", "display": "browser", "start_url": BASE},
        ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    built = [build_home(), build_aed(), build_training(), build_extras(), build_pro(), build_quote(),
             build_contact(), build_press(), build_privacy(), build_thanks(), build_404()]
    write_static(built)
    for p, ni in built:
        print(("  (noindex) " if ni else "  ") + p)
    print("Kész:", ROOT)
