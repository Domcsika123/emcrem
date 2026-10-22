/* Sajtófigyelő szerkesztő: reads/writes content/sajtofigyelo.json in the GitHub repo via the REST API.
   Saving commits to main, which triggers the GitHub Pages workflow that rebuilds the site. */
(function () {
  'use strict';

  var CFG = { owner: 'Domcsika123', repo: 'emcrem', branch: 'main', path: 'content/sajtofigyelo.json' };
  var API = 'https://api.github.com/repos/' + CFG.owner + '/' + CFG.repo;
  var TOKEN_KEY = 'emcrem-admin-token';

  var state = { token: null, items: [], sha: null, editing: -1, busy: false, watch: 0 };
  var $ = function (id) { return document.getElementById(id); };

  /* ---------- storage (may be unavailable, e.g. private mode) ---------- */
  function readToken() {
    try { return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
  }
  function storeToken(t, remember) {
    try { (remember ? localStorage : sessionStorage).setItem(TOKEN_KEY, t); } catch (e) { /* keep in memory only */ }
  }
  function forgetToken() {
    try { localStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(TOKEN_KEY); } catch (e) { /* ignore */ }
  }

  /* ---------- UTF-8 safe base64 (GitHub contents API) ---------- */
  function toBase64(str) {
    var bytes = new TextEncoder().encode(str), bin = '';
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  }
  function fromBase64(b64) {
    var bin = atob(String(b64).replace(/\s/g, '')), bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  /* ---------- GitHub API ---------- */
  function gh(path, opts) {
    opts = opts || {};
    var headers = { 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
    if (state.token) headers.Authorization = 'Bearer ' + state.token;
    if (opts.body) headers['Content-Type'] = 'application/json';
    return fetch(API + path, {
      method: opts.method || 'GET', headers: headers, cache: 'no-store',
      body: opts.body ? JSON.stringify(opts.body) : undefined
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (!r.ok) { var err = new Error(data.message || ('HTTP ' + r.status)); err.status = r.status; throw err; }
        return data;
      });
    });
  }

  function errorText(err) {
    if (!navigator.onLine) return 'Nincs internetkapcsolat. Ellenőrizd a hálózatot, és próbáld újra.';
    if (err.status === 401) return 'A belépőkulcs érvénytelen vagy lejárt. Hozz létre újat, és lépj be vele.';
    if (err.status === 403) return 'A kulcsnak nincs jogosultsága ehhez. Ellenőrizd, hogy a „Contents” jog „Read and write”.';
    if (err.status === 404) return 'A repó vagy az adatfájl nem található, vagy a kulcs nem fér hozzá a(z) „' + CFG.repo + '” repóhoz.';
    if (err.status === 409) return 'Közben valaki más is módosított. Frissítettem a listát – próbáld újra.';
    return 'Hiba történt: ' + escapeHtml(err.message);
  }

  function loadItems() {
    return gh('/contents/' + CFG.path + '?ref=' + CFG.branch).then(function (d) {
      state.sha = d.sha;
      state.items = sortItems(JSON.parse(fromBase64(d.content)));
    });
  }

  function saveItems(items, message) {
    var content = JSON.stringify(sortItems(items), null, 2) + '\n';
    return gh('/contents/' + CFG.path, {
      method: 'PUT',
      body: { message: message, content: toBase64(content), sha: state.sha, branch: CFG.branch }
    }).then(function (d) {
      state.sha = d.content.sha;
      state.items = sortItems(items);
      return d.commit.sha;
    });
  }

  /* After a commit, follow the Pages workflow so the user knows when it is live. */
  function watchDeploy(commitSha, startedAt) {
    var tries = 0, id = ++state.watch;
    var live = ' <a href="' + pressPageUrl() + '" target="_blank" rel="noopener">Megnézem ↗</a>';
    (function poll() {
      if (id !== state.watch) return; // a newer save/delete is being followed
      tries++;
      gh('/actions/runs?head_sha=' + commitSha + '&per_page=1').then(function (d) {
        if (id !== state.watch) return;
        var run = d.workflow_runs && d.workflow_runs[0];
        if (run && run.status === 'completed') {
          if (run.conclusion === 'success') status('ok', 'Kint van az oldalon!' + live);
          else status('error', 'A mentés sikerült, de a közzététel hibára futott. <a href="' + run.html_url + '" target="_blank" rel="noopener">Részletek ↗</a>');
          return;
        }
        status('busy', 'Mentve. Közzététel folyamatban… (általában 1–2 perc, ' + elapsed(startedAt) + ')');
        if (tries < 60) setTimeout(poll, 5000);
        else status('ok', 'Mentve. A közzététel szokatlanul sokáig tart – pár perc múlva nézd meg az oldalt.' + live);
      }).catch(function () {
        if (id !== state.watch) return;
        // Token without "Actions: Read" – cannot follow the run.
        status('ok', 'Mentve! Kb. 1–2 perc múlva jelenik meg az oldalon.' + live);
      });
    })();
  }

  /* ---------- helpers ---------- */
  function sortItems(items) {
    return items.slice().sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function huDate(iso) { return iso ? iso.replace(/-/g, '.') + '.' : ''; }
  function elapsed(t) { var s = Math.round((Date.now() - t) / 1000); return s < 60 ? s + ' mp' : Math.floor(s / 60) + ' perc ' + (s % 60) + ' mp'; }
  function pressPageUrl() { return new URL('../erdekes-linkek-sajtofigyelo/', location.href).href; }
  function validUrl(u) { return /^https?:\/\/[^\s/]+\.[^\s]+$/i.test(u); }

  function sourceName(url) {
    var host;
    try { host = new URL(url).hostname.replace(/^www\./, '').toLowerCase(); } catch (e) { return ''; }
    if (/(^|\.)youtube\.com$|^youtu\.be$/.test(host)) return 'YouTube-videó';
    if (/(^|\.)wikipedia\.org$/.test(host)) return 'Wikipedia';
    if (/(^|\.)facebook\.com$|^fb\.watch$/.test(host)) return 'Facebook';
    if (/(^|\.)instagram\.com$/.test(host)) return 'Instagram';
    if (/(^|\.)tiktok\.com$/.test(host)) return 'TikTok';
    if (/(^|\.)webbeteg\.hu$/.test(host)) return 'WEBBeteg';
    return host;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function status(kind, html) {
    var box = $('status');
    box.className = 'admin-status admin-status--' + kind;
    box.innerHTML = (kind === 'busy' ? '<span class="admin-spinner" aria-hidden="true"></span>' : '') + '<span>' + html + '</span>';
    box.hidden = false;
  }
  function clearStatus() { $('status').hidden = true; }

  function setBusy(on, label) {
    state.busy = on;
    var btn = $('save-btn');
    btn.disabled = on;
    btn.textContent = on ? (label || 'Mentés…') : (state.editing >= 0 ? 'Módosítás mentése' : 'Közzététel');
  }

  /* ---------- views ---------- */
  function showConnect(message) {
    $('app').hidden = true;
    $('logout').hidden = true;
    $('connect').hidden = false;
    if (message) status('error', message); else clearStatus();
    $('token').focus();
  }

  function showApp() {
    $('connect').hidden = true;
    $('app').hidden = false;
    $('logout').hidden = false;
    renderList();
  }

  function renderList(highlightIndex) {
    var list = $('list');
    list.textContent = '';
    $('count').textContent = '(' + state.items.length + ')';
    if (!state.items.length) {
      list.appendChild(el('li', 'admin-empty', 'Még nincs bejegyzés. Kattints az „+ Új bejegyzés” gombra.'));
      return;
    }
    state.items.forEach(function (it, i) {
      var li = el('li', 'admin-item' + (i === highlightIndex ? ' is-new' : ''));
      var time = el('time', '', huDate(it.date));
      time.dateTime = it.date;
      var body = el('div');
      body.appendChild(el('div', 'admin-item__title', it.title));
      var meta = (it.links || []).map(function (l) { return l.label || sourceName(l.url); }).join(' · ');
      if (it.summary) meta = it.summary + (meta ? ' — ' + meta : '');
      body.appendChild(el('div', 'admin-item__meta', meta));
      var actions = el('div', 'admin-item__actions');
      var edit = el('button', 'admin-link-btn', 'Szerkesztés');
      edit.type = 'button';
      edit.addEventListener('click', function () { openEditor(i); });
      var del = el('button', 'admin-link-btn admin-link-btn--danger', 'Törlés');
      del.type = 'button';
      del.addEventListener('click', function () { removeItem(i); });
      actions.appendChild(edit);
      actions.appendChild(del);
      li.appendChild(time);
      li.appendChild(body);
      li.appendChild(actions);
      list.appendChild(li);
    });
  }

  /* ---------- editor ---------- */
  var f = {};
  ['url', 'title', 'summary', 'date', 'label', 'url2', 'label2'].forEach(function (k) { f[k] = $('f-' + k); });

  function setSecondLink(show) {
    $('second-link').hidden = !show;
    $('add-second').hidden = show;
    if (!show) { f.url2.value = ''; f.label2.value = ''; }
  }

  function openEditor(index) {
    state.editing = index;
    var it = index >= 0 ? state.items[index] : null;
    var links = it ? it.links || [] : [];
    f.url.value = links[0] ? links[0].url : '';
    f.label.value = links[0] ? links[0].label || '' : '';
    f.url2.value = links[1] ? links[1].url : '';
    f.label2.value = links[1] ? links[1].label || '' : '';
    f.title.value = it ? it.title : '';
    f.summary.value = it ? it.summary || '' : '';
    f.date.value = it ? it.date : today();
    f.label.dataset.auto = f.label2.dataset.auto = '';
    setSecondLink(!!links[1]);
    $('editor-title').textContent = it ? 'Bejegyzés szerkesztése' : 'Új bejegyzés';
    $('editor-error').hidden = true;
    setBusy(false);
    $('editor').hidden = false;
    $('new-btn').hidden = true;
    renderPreview();
    $('editor').scrollIntoView({ behavior: 'smooth', block: 'start' });
    (it ? f.title : f.url).focus({ preventScroll: true });
  }

  function closeEditor() {
    $('editor').hidden = true;
    $('new-btn').hidden = false;
    state.editing = -1;
  }

  // Fill in the source name from the link, unless the user typed their own.
  function autoLabel(urlInput, labelInput) {
    if (labelInput.value && !labelInput.dataset.auto) return;
    var name = validUrl(urlInput.value.trim()) ? sourceName(urlInput.value.trim()) : '';
    labelInput.value = name;
    labelInput.dataset.auto = name ? '1' : '';
  }

  function collect() {
    var links = [];
    var u1 = f.url.value.trim(), u2 = f.url2.value.trim();
    if (u1) links.push({ label: f.label.value.trim() || sourceName(u1), url: u1 });
    if (u2) links.push({ label: f.label2.value.trim() || sourceName(u2), url: u2 });
    return { date: f.date.value, title: f.title.value.trim(), summary: f.summary.value.trim(), links: links };
  }

  function validate(item) {
    if (!item.links.length || !validUrl(item.links[0].url)) return { field: f.url, msg: 'Add meg a cikk vagy videó linkjét (https://-sel kezdődjön).' };
    if (item.links[1] && !validUrl(item.links[1].url)) return { field: f.url2, msg: 'A második link nem érvényes webcím.' };
    if (!item.title) return { field: f.title, msg: 'Adj meg egy címet.' };
    if (!/^\d{4}-\d{2}-\d{2}$/.test(item.date)) return { field: f.date, msg: 'Adj meg egy dátumot.' };
    return null;
  }

  function renderPreview() {
    var it = collect(), p = $('preview');
    p.textContent = '';
    var time = el('time', '', huDate(it.date));
    var body = el('div');
    body.appendChild(el('h3', it.title ? '' : 'is-empty', it.title || 'A bejegyzés címe'));
    if (it.summary) body.appendChild(el('p', '', it.summary));
    var links = el('div', 'press-links');
    (it.links.length ? it.links : [{ label: 'forrás' }]).forEach(function (l) {
      var a = el('span', 'press-link' + (l.url ? '' : ' is-empty'), (l.label || 'forrás') + ' ↗');
      links.appendChild(a);
    });
    p.appendChild(time);
    p.appendChild(body);
    p.appendChild(links);
  }

  function submitEditor(e) {
    e.preventDefault();
    if (state.busy) return;
    var item = collect(), problem = validate(item), errBox = $('editor-error');
    if (problem) { errBox.textContent = problem.msg; errBox.hidden = false; problem.field.focus(); return; }
    errBox.hidden = true;

    var editing = state.editing, items = state.items.slice();
    if (editing >= 0) items[editing] = item; else items.push(item);
    var msg = (editing >= 0 ? 'Sajtófigyelő: bejegyzés módosítása – ' : 'Sajtófigyelő: új bejegyzés – ') + item.title;
    var startedAt = Date.now();

    setBusy(true);
    status('busy', 'Mentés…');
    saveItems(items, msg).then(function (commitSha) {
      setBusy(false);
      closeEditor();
      renderList(state.items.indexOf(item));
      watchDeploy(commitSha, startedAt);
    }).catch(function (err) {
      setBusy(false);
      state.watch++;
      status('error', errorText(err));
      if (err.status === 409) loadItems().then(function () { renderList(); });
    });
  }

  function removeItem(index) {
    if (state.busy) return;
    var it = state.items[index];
    if (!window.confirm('Biztosan törlöd ezt a bejegyzést?\n\n„' + it.title + '”')) return;
    var items = state.items.slice();
    items.splice(index, 1);
    var startedAt = Date.now();
    state.busy = true;
    status('busy', 'Törlés…');
    saveItems(items, 'Sajtófigyelő: bejegyzés törlése – ' + it.title).then(function (commitSha) {
      state.busy = false;
      if (state.editing === index) closeEditor();
      renderList();
      watchDeploy(commitSha, startedAt);
    }).catch(function (err) {
      state.busy = false;
      state.watch++;
      status('error', errorText(err));
      if (err.status === 409) loadItems().then(function () { renderList(); });
    });
  }

  /* ---------- connect ---------- */
  function connect(token, remember) {
    state.token = token;
    status('busy', 'Belépés…');
    return gh('').then(function (repo) {
      if (!repo.permissions || !repo.permissions.push) {
        var e = new Error('no push'); e.status = 403; throw e;
      }
      return loadItems();
    }).then(function () {
      if (remember !== undefined) storeToken(token, remember);
      clearStatus();
      showApp();
    }).catch(function (err) {
      state.token = null;
      if (remember === undefined) forgetToken();
      showConnect(errorText(err));
    });
  }

  /* ---------- wire up ---------- */
  $('connect-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var t = $('token').value.trim();
    if (!t) { status('error', 'Illeszd be a belépőkulcsot.'); $('token').focus(); return; }
    connect(t, $('remember').checked);
  });
  $('logout').addEventListener('click', function () {
    forgetToken();
    state.token = null;
    $('token').value = '';
    closeEditor();
    showConnect();
  });
  $('new-btn').addEventListener('click', function () { clearStatus(); openEditor(-1); });
  $('cancel-btn').addEventListener('click', closeEditor);
  $('add-second').addEventListener('click', function () { setSecondLink(true); f.url2.focus(); });
  $('remove-second').addEventListener('click', function () { setSecondLink(false); renderPreview(); });
  $('editor').addEventListener('submit', submitEditor);
  $('editor').addEventListener('input', function (e) {
    if (e.target === f.url) autoLabel(f.url, f.label);
    if (e.target === f.url2) autoLabel(f.url2, f.label2);
    if (e.target === f.label) f.label.dataset.auto = '';
    if (e.target === f.label2) f.label2.dataset.auto = '';
    renderPreview();
  });
  document.querySelectorAll('[data-repo]').forEach(function (n) { n.textContent = CFG.repo; });

  var saved = readToken();
  if (saved) connect(saved); else showConnect();
})();
