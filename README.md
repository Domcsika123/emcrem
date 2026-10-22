# emcremdefibrillator.hu – új, statikus weboldal

## Szerkezet
- `build.py` – az összes oldal tartalma, közös fejléc/lábléc, SEO meta, strukturált adatok (JSON-LD), sitemap.
- `public/` – a kész weboldal.
  - `assets/css/style.css`, `assets/js/main.js`, `assets/img/` (WebP), `assets/fonts/` (saját szerverről, GDPR-barát)
  - `kuldes.php` – ajánlatkérő űrlap feldolgozása PHP-s tárhelyen (címzett: aed@emcrem.hu)
  - `.htaccess` – HTTPS, 301 átirányítások a régi WordPress-címekről, gyorsítótár, biztonsági fejlécek (Apache)
- `.github/workflows/pages.yml` – automatikus közzététel GitHub Pages-re.

## Módosítás
1. Szöveg / ár / elérhetőség: `build.py` (a cég adatai az `ORG` blokkban).
2. `python build.py` – újragenerálja a `public/` mappát.
3. Helyi előnézet: `cd public && python -m http.server 8090` → http://localhost:8090
4. Commit + push a `main` ágra → a GitHub Pages pár percen belül frissül.

## GitHub Pages
- Cím: https://domcsika123.github.io/emcrem/
- Egyszeri beállítás: a repó **Settings → Pages → Build and deployment → Source: GitHub Actions**.
- A munkafolyamat `SITE_BASE=/emcrem/` értékkel generál (almappás cím), és `FORM_MODE=mailto` módban:
  mivel a Pages nem futtat PHP-t, az űrlap a látogató levelezőprogramjában nyit egy kitöltött levelet.
- Saját domainre (emcremdefibrillator.hu) váltáskor: `public/CNAME` fájl a domainnel, a munkafolyamatban
  `SITE_BASE: /`, a domain DNS-ében pedig a GitHub Pages rekordjai.

## Élesítés előtt
- Az adatkezelési tájékoztató sárgával jelölt `[kitöltendő]` részeinek kitöltése (cégjegyzékszám, adószám, tárhelyszolgáltató, megőrzési idő), jogi átnézés.
- PHP-s tárhelyen: űrlap tesztelése élesben (a `noreply@emcremdefibrillator.hu` feladóhoz SPF rekord ajánlott).
- Google Search Console: sitemap beküldése (`/sitemap.xml`).
