# emcremdefibrillator.hu – új, statikus weboldal

## Szerkezet
- `build.py` – az összes oldal tartalma, közös fejléc/lábléc, SEO meta, strukturált adatok (JSON-LD), sitemap.
- `public/` – a kész weboldal.
  - `assets/css/style.css`, `assets/js/main.js`, `assets/img/` (WebP), `assets/fonts/` (saját szerverről, GDPR-barát)
  - `kuldes.php` – ajánlatkérő űrlap feldolgozása PHP-s tárhelyen (címzett: aed@emcrem.hu)
  - `.htaccess` – HTTPS, 301 átirányítások a régi WordPress-címekről, gyorsítótár, biztonsági fejlécek (Apache)
- `.github/workflows/pages.yml` – automatikus közzététel GitHub Pages-re.

## Sajtófigyelő admin (`/admin/`)
- Cím: https://emcremdefibrillator.hu/admin/
- Új cikk / videó felvétele, szerkesztése, törlése pár kattintással; előnézettel. A „Közzététel” a
  `content/sajtofigyelo.json` fájlt menti a repóba, amire a GitHub Pages pár percen belül frissül.
- Belépés: a szerkesztő (ügyfél) a fejlesztőtől kapott belépőkulcsot illeszti be; a belépő oldal ezt kéri.
  A kulcs egy GitHub *fine-grained* token, amit a repó tulajdonosa hoz létre
  (https://github.com/settings/personal-access-tokens/new): **Only select repositories → `emcrem`**,
  **Contents: Read and write** + **Actions: Read-only** (ettől látszik a közzététel állapota), a lejárat tetszőleges.
  A token csak a böngészőben tárolódik; a „Kijelentkezés” törli. Elvesztés esetén a GitHubon visszavonható, és új adható ki.
- A bejegyzések a `content/sajtofigyelo.json` fájlban vannak; kézzel is szerkeszthető (dátum `ÉÉÉÉ-HH-NN`,
  `group`: `mindenkinek` vagy `szakmai` – az oldalon e szerint két csoportban jelennek meg).

## Módosítás
1. Szöveg / ár / elérhetőség: `build.py` (a cég adatai az `ORG` blokkban).
2. `python build.py` – újragenerálja a `public/` mappát.
3. Helyi előnézet: `cd public && python -m http.server 8090` → http://localhost:8090
4. Commit + push a `main` ágra → a GitHub Pages pár percen belül frissül.

## GitHub Pages
- Cím: https://emcremdefibrillator.hu/ (a régi https://domcsika123.github.io/emcrem/ cím ide irányít át)
- Egyszeri beállítás: a repó **Settings → Pages → Build and deployment → Source: GitHub Actions**,
  ugyanitt **Custom domain: emcremdefibrillator.hu**; a domain DNS-ében a GitHub Pages rekordjai.
  `public/CNAME` fájl nem kell: Actions-ös közzétételnél a GitHub a domaint a Pages beállításból veszi.
- A munkafolyamat `SITE_BASE=/` értékkel generál (a domain gyökerébe), és `FORM_MODE=mailto` módban:
  mivel a Pages nem futtat PHP-t, az űrlap a látogató levelezőprogramjában nyit egy kitöltött levelet.
- Ha az oldal visszakerülne a domain nélküli, almappás címre, a munkafolyamatban `SITE_BASE: /emcrem/` kell.

## Élesítés előtt
- Az adatkezelési tájékoztató sárgával jelölt `[kitöltendő]` részeinek kitöltése (cégjegyzékszám, adószám, tárhelyszolgáltató, megőrzési idő), jogi átnézés.
- PHP-s tárhelyen: űrlap tesztelése élesben (a `noreply@emcremdefibrillator.hu` feladóhoz SPF rekord ajánlott).
- Google Search Console: sitemap beküldése (`/sitemap.xml`).
