/* FolderStream — motor do player (gerado automaticamente, não editar as duas constantes abaixo) */
const COURSE_ID = "__COURSE_ID__";
const COURSE_DATA = __COURSE_DATA__;

const THEMES = [
  { id: "light-a", label: "Light — Neutral" },
  { id: "light-b", label: "Light — Warm" },
  { id: "dark-a", label: "Dark — Slate" },
  { id: "dark-b", label: "Dark — Carbon" },
  { id: "blue-a", label: "Blue — Corporate" },
  { id: "blue-b", label: "Blue — Light" },
  { id: "orange-a", label: "Orange & Black — High Contrast" },
  { id: "orange-b", label: "Orange & Black — Soft" },
];
const DEFAULT_THEME = "dark-a";

const ICONS = {
  chevron: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg>',
  sidebar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></svg>',
  notes: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h5"/></svg>',
  timer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 2h6"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
  star: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.9 6.4 7 .6-5.3 4.6 1.6 6.9L12 17l-6.2 3.5 1.6-6.9L2 8.9l7-.6z"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
  pause: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>',
  reset: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 3-6.7M3 4v5h5"/></svg>',
  prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 6l-6 6 6 6"/></svg>',
  next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0l-4-4m4 4l4-4M4 21h16"/></svg>',
  upload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21V9m0 0l-4 4m4-4l4 4M4 3h16"/></svg>',
  settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.55V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 1 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1z"/></svg>',
  trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M9 7V4h6v3m-8 0 1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13"/></svg>',
};

/* ---------- storage seguro, isolado por curso ---------- */
function skey(name) { return `pm:${COURSE_ID}:${name}`; }

function storageGet(name, fallback) {
  try {
    const raw = localStorage.getItem(skey(name));
    return raw === null ? fallback : JSON.parse(raw);
  } catch (e) {
    return fallback;
  }
}

function storageSet(name, value) {
  try {
    localStorage.setItem(skey(name), JSON.stringify(value));
  } catch (e) {
    /* localStorage indisponível (modo privado etc.) — segue sem persistir */
  }
}

function iconSpan(svg) {
  return `<span class="icon">${svg}</span>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function highlightMatch(text, query) {
  if (!query) return escapeHtml(text);
  const idx = text.toLowerCase().indexOf(query);
  if (idx === -1) return escapeHtml(text);
  const before = text.slice(0, idx);
  const match = text.slice(idx, idx + query.length);
  const after = text.slice(idx + query.length);
  return `${escapeHtml(before)}<mark>${escapeHtml(match)}</mark>${escapeHtml(after)}`;
}

function formatTime(seconds) {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return "--:--";
  seconds = Math.floor(seconds);
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

let notifTimer = null;
function notify(msg) {
  const el = document.getElementById("notif");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(notifTimer);
  notifTimer = setTimeout(() => el.classList.remove("show"), 2200);
}

/* ---------- tema ---------- */
function applyTheme(id) {
  document.documentElement.setAttribute("data-theme", id);
  storageSet("theme", id);
  const sel = document.getElementById("theme-switcher");
  if (sel) sel.value = id;
}

function initTheme() {
  const sel = document.getElementById("theme-switcher");
  sel.innerHTML = THEMES.map((t) => `<option value="${t.id}">${escapeHtml(t.label)}</option>`).join("");
  const saved = storageGet("theme", null);
  applyTheme(saved || DEFAULT_THEME);
  sel.addEventListener("change", () => applyTheme(sel.value));
}

/* ---------- árvore de dados ---------- */
// Ordem para o que conta como "aula concluível" (progresso/estatísticas) —
// qualquer tipo de arquivo pode marcar a aula como feita.
const PRIMARY_KIND_ORDER = ["video", "html", "pdf", "image", "audio"];
// Só vídeo/HTML viram conteúdo principal exibido na área do player — PDF,
// imagem, áudio etc. sem vídeo/HTML na aula ficam só na lista de materiais
// (evita embutir um PDF/imagem solto como se fosse "a aula").
const VIEWER_KIND_ORDER = ["video", "html"];

function pickPrimaryFile(files) {
  if (!files || !files.length) return null;
  for (const kind of PRIMARY_KIND_ORDER) {
    const found = files.find((f) => f.kind === kind);
    if (found) return found;
  }
  return files[0];
}

function pickViewerFile(files) {
  if (!files || !files.length) return null;
  for (const kind of VIEWER_KIND_ORDER) {
    const found = files.find((f) => f.kind === kind);
    if (found) return found;
  }
  return null;
}

function encodePath(path) {
  return path
    .split("/")
    .map((seg) => (seg === "" || seg === "." || seg === ".." ? seg : encodeURIComponent(seg)))
    .join("/");
}

function walkLessons(lessons, cb, path = []) {
  lessons.forEach((lesson, idx) => {
    const lessonPath = [...path, idx];
    cb(lesson, lessonPath);
    if (lesson.lessons && lesson.lessons.length) {
      walkLessons(lesson.lessons, cb, lessonPath);
    }
  });
}

function buildFlatVideoList() {
  const flat = [];
  COURSE_DATA.modules.forEach((mod, mIdx) => {
    walkLessons(mod.lessons, (lesson) => {
      const primary = pickPrimaryFile(lesson.files);
      if (primary && primary.kind === "video") {
        flat.push({ moduleIndex: mIdx, lesson, file: primary });
      }
    });
  });
  return flat;
}

function findFileById(fileId) {
  let result = null;
  COURSE_DATA.modules.forEach((mod) => {
    walkLessons(mod.lessons, (lesson) => {
      (lesson.files || []).forEach((f) => {
        if (f.id === fileId) result = { module: mod, lesson, file: f };
      });
    });
  });
  return result;
}

function allFilesFlat() {
  const files = [];
  COURSE_DATA.modules.forEach((mod) => {
    walkLessons(mod.lessons, (lesson) => {
      (lesson.files || []).forEach((f) => files.push(f));
    });
  });
  return files;
}

/* ---------- progresso ---------- */
function getCompletedSet() {
  return new Set(storageGet("completed", []));
}

function saveCompletedSet(set) {
  storageSet("completed", Array.from(set));
}

function isLessonCompleted(lesson, completedSet) {
  const primary = pickPrimaryFile(lesson.files);
  return primary ? completedSet.has(primary.id) : false;
}

function toggleLessonCompleted(lesson) {
  const primary = pickPrimaryFile(lesson.files);
  if (!primary) return;
  const set = getCompletedSet();
  if (set.has(primary.id)) set.delete(primary.id);
  else set.add(primary.id);
  saveCompletedSet(set);
  renderSidebar();
  updateStatsBar();
}

function computeModuleStats(mod, completedSet) {
  let total = 0, done = 0;
  walkLessons(mod.lessons, (lesson) => {
    const primary = pickPrimaryFile(lesson.files);
    if (!primary) return;
    total += 1;
    if (completedSet.has(primary.id)) done += 1;
  });
  return { total, done };
}

function computeCourseStats(completedSet) {
  let total = 0, done = 0;
  COURSE_DATA.modules.forEach((mod) => {
    const s = computeModuleStats(mod, completedSet);
    total += s.total;
    done += s.done;
  });
  return { total, done };
}

function updateStatsBar() {
  const completed = getCompletedSet();
  const { total, done } = computeCourseStats(completed);
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById("stats-count").textContent = `${done}/${total} aulas`;
  document.getElementById("stats-fill").style.width = `${pct}%`;
  document.getElementById("stats-pct").textContent = `${pct}%`;
}

/* ---------- avanço automático ---------- */
function getAutoAdvance() { return storageGet("autoAdvance", true); }
function setAutoAdvance(value) { storageSet("autoAdvance", value); }

function initAutoAdvanceToggle() {
  const toggle = document.getElementById("auto-advance-toggle");
  toggle.checked = getAutoAdvance();
  toggle.addEventListener("change", () => setAutoAdvance(toggle.checked));
}

/* ---------- velocidade de reprodução ---------- */
function getPlaybackSpeed() { return storageGet("playbackSpeed", 1); }
function setPlaybackSpeed(value) { storageSet("playbackSpeed", value); }

/* ---------- UI state (sidebar, último arquivo, módulos abertos) ---------- */
function getUiState() { return storageGet("ui", { openModules: [0], lastFileId: null, sidebarClosed: false }); }
function setUiState(patch) { storageSet("ui", { ...getUiState(), ...patch }); }

/* ---------- sidebar ---------- */
let currentFileId = null;

function renderSidebar(filterText = "") {
  const root = document.getElementById("modules");
  const completed = getCompletedSet();
  const ui = getUiState();
  const query = filterText.trim().toLowerCase();

  root.innerHTML = "";
  COURSE_DATA.modules.forEach((mod, mIdx) => {
    const stats = computeModuleStats(mod, completed);
    const matches = !query || mod.name.toLowerCase().includes(query) ||
      lessonMatchesQuery(mod.lessons, query);

    if (!matches) return;

    const modEl = document.createElement("div");
    modEl.className = "module" + (ui.openModules.includes(mIdx) || query ? " open" : "");

    const header = document.createElement("div");
    header.className = "module-header";
    header.innerHTML = `<span class="icon chevron">${ICONS.chevron}</span>
      <span>${highlightMatch(mod.name, query)}</span>
      <span class="module-progress">${stats.done}/${stats.total}</span>`;
    header.addEventListener("click", () => {
      modEl.classList.toggle("open");
      const openNow = getUiState().openModules.filter((i) => i !== mIdx);
      if (modEl.classList.contains("open")) openNow.push(mIdx);
      setUiState({ openModules: openNow });
    });

    const list = document.createElement("div");
    list.className = "lesson-list";
    renderLessonList(list, mod.lessons, completed, query);

    modEl.appendChild(header);
    modEl.appendChild(list);
    root.appendChild(modEl);
  });
}

function lessonMatchesQuery(lessons, query) {
  return lessons.some((l) => l.name.toLowerCase().includes(query) ||
    (l.lessons && lessonMatchesQuery(l.lessons, query)));
}

function renderLessonList(container, lessons, completed, query) {
  lessons.forEach((lesson) => {
    const primary = pickPrimaryFile(lesson.files);
    const matches = !query || lesson.name.toLowerCase().includes(query);
    if (matches) {
      const item = document.createElement("div");
      const isCompleted = isLessonCompleted(lesson, completed);
      item.className = "lesson-item" + (isCompleted ? " completed" : "") +
        (primary && primary.id === currentFileId ? " active" : "");
      item.innerHTML = `<span class="check"></span>
        <span class="name">${highlightMatch(lesson.name, query)}</span>
        <span class="duration">${primary && primary.kind === "video" ? formatTime(primary.duration) : ""}</span>`;
      item.querySelector(".check").addEventListener("click", (e) => {
        e.stopPropagation();
        toggleLessonCompleted(lesson);
      });
      item.addEventListener("click", () => openLesson(lesson));
      container.appendChild(item);
    }
    if (lesson.lessons && lesson.lessons.length) {
      const subList = document.createElement("div");
      subList.className = "lesson-list";
      subList.style.display = "block";
      subList.style.paddingLeft = "14px";
      renderLessonList(subList, lesson.lessons, completed, query);
      container.appendChild(subList);
    }
  });
}

/* ---------- player / viewer ---------- */
function openLesson(lesson) {
  const completable = pickPrimaryFile(lesson.files);
  const viewerFile = pickViewerFile(lesson.files);
  if (!completable && !viewerFile) return;
  currentFileId = completable ? completable.id : null;
  setUiState({ lastFileId: currentFileId });
  if (completable && completable.kind !== "video") {
    // conteúdo que não é vídeo não tem "fim": abrir já conta como concluído.
    const set = getCompletedSet();
    if (!set.has(completable.id)) {
      set.add(completable.id);
      saveCompletedSet(set);
    }
  }
  document.getElementById("topbar-title").textContent = lesson.name;
  renderAttachments(lesson, viewerFile);
  renderViewer(viewerFile);
  renderSidebar(document.getElementById("search-box").value);
  updateStatsBar();
  renderNotesForCurrentFile();
}

function renderAttachments(lesson, viewerFile) {
  const box = document.getElementById("attachments");
  const others = (lesson.files || []).filter((f) => {
    if (viewerFile && f.id === viewerFile.id) return false;
    return f.kind !== "video";
  });
  if (!others.length) { box.innerHTML = ""; box.hidden = true; return; }
  box.hidden = false;
  box.innerHTML = "Materiais: " + others.map((f) =>
    `<a class="btn" href="${escapeHtml(encodePath(f.path))}" target="_blank" rel="noopener">${escapeHtml(f.name)}</a>`
  ).join(" ");
}

function renderViewer(file) {
  const wrap = document.getElementById("player-container");
  if (!file) {
    wrap.innerHTML = `<div class="empty-state"><p>Esta aula não tem vídeo — veja os materiais abaixo.</p></div>`;
    return;
  }
  if (file.kind === "video") {
    const { flat, idx } = getFlatIndexFor(file.id);
    const hasPrev = idx > 0;
    const hasNext = idx >= 0 && idx + 1 < flat.length;
    wrap.innerHTML = `
      <div id="video-wrapper"><video id="main-video" controls></video></div>
      <div class="video-nav-controls">
        <button id="btn-prev-video" class="btn" ${hasPrev ? "" : "disabled"}>${iconSpan(ICONS.prev)} Aula anterior</button>
        <select id="playback-speed" class="btn" aria-label="Velocidade de reprodução">
          <option value="0.75">0.75x</option>
          <option value="1">1x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2x</option>
        </select>
        <button id="btn-next-video" class="btn btn-primary" ${hasNext ? "" : "disabled"}>Próxima aula ${iconSpan(ICONS.next)}</button>
      </div>`;
    const video = document.getElementById("main-video");
    video.src = encodePath(file.path);
    const speedSelect = document.getElementById("playback-speed");
    const speed = getPlaybackSpeed();
    speedSelect.value = String(speed);
    video.playbackRate = speed;
    speedSelect.addEventListener("change", () => {
      const value = parseFloat(speedSelect.value);
      setPlaybackSpeed(value);
      video.playbackRate = value;
    });
    (file.subtitles || []).forEach((sub) => {
      const track = document.createElement("track");
      track.kind = "subtitles";
      track.src = encodePath(sub.path);
      track.srclang = sub.lang || "pt-br";
      track.label = sub.label || sub.lang || "Legenda";
      video.appendChild(track);
    });
    const savedTime = storageGet(`vtime:${file.id}`, 0);
    if (savedTime > 1) {
      // não retoma perto do fim: evita reabrir uma aula já concluída
      // e disparar "ended" de novo assim que o vídeo carrega.
      video.addEventListener("loadedmetadata", () => {
        if (!video.duration || video.duration - savedTime > 2) {
          video.currentTime = savedTime;
        }
      }, { once: true });
    }
    video.addEventListener("timeupdate", () => {
      storageSet(`vtime:${file.id}`, video.currentTime);
      updateNoteTimeButton(video.currentTime);
    });
    video.addEventListener("ended", () => {
      markFileCompleted(file.id);
      storageSet(`vtime:${file.id}`, 0);
      if (getAutoAdvance()) {
        goToRelativeVideo(1, { auto: true });
      } else {
        notify("Aula concluída.");
      }
    });
    video.play().catch(() => {});

    document.getElementById("btn-prev-video").addEventListener("click", () => goToRelativeVideo(-1));
    document.getElementById("btn-next-video").addEventListener("click", () => goToRelativeVideo(1));
  } else if (file.kind === "html") {
    wrap.innerHTML = `<div id="file-viewer"><iframe src="${escapeHtml(encodePath(file.path))}" style="width:100%;height:65vh;border:0;background:#fff;border-radius:8px"></iframe></div>`;
  } else {
    // pickViewerFile só retorna vídeo/html — este ramo é só uma rede de segurança.
    wrap.innerHTML = `<div id="file-viewer"><p>Este arquivo não pode ser exibido diretamente.</p>
      <a class="btn btn-primary" href="${escapeHtml(encodePath(file.path))}" target="_blank" rel="noopener">Abrir "${escapeHtml(file.name)}"</a></div>`;
  }
}

function markFileCompleted(fileId) {
  const set = getCompletedSet();
  set.add(fileId);
  saveCompletedSet(set);
  renderSidebar(document.getElementById("search-box").value);
  updateStatsBar();
}

function getFlatIndexFor(fileId) {
  const flat = buildFlatVideoList();
  const idx = flat.findIndex((item) => item.file.id === fileId);
  return { flat, idx };
}

function goToRelativeVideo(offset, { auto = false } = {}) {
  const { flat, idx } = getFlatIndexFor(currentFileId);
  if (idx < 0) return;
  const targetIdx = idx + offset;
  if (targetIdx < 0) {
    notify("Esta já é a primeira aula.");
    return;
  }
  if (targetIdx >= flat.length) {
    notify(auto ? "Você concluiu o último vídeo desta lista." : "Esta já é a última aula.");
    return;
  }
  openLesson(flat[targetIdx].lesson);
}

function loadInitialFile() {
  const ui = getUiState();
  let target = null;
  if (ui.lastFileId) target = findFileById(ui.lastFileId);
  if (!target) {
    const flat = buildFlatVideoList();
    if (flat.length) target = { lesson: flat[0].lesson, file: flat[0].file };
  }
  if (target) {
    openLesson(target.lesson);
  } else {
    document.getElementById("player-container").innerHTML =
      `<div class="empty-state"><p>Nenhum arquivo encontrado neste curso.</p></div>`;
  }
}

/* ---------- notas ---------- */
function notesKeyFor(fileId) { return `notes:${fileId}`; }

function loadNotes(fileId) { return storageGet(notesKeyFor(fileId), []); }
function saveNotes(fileId, notes) { storageSet(notesKeyFor(fileId), notes); }

function renderNotesForCurrentFile() {
  const list = document.getElementById("notes-list");
  if (!currentFileId) { list.innerHTML = ""; return; }
  const notes = loadNotes(currentFileId).slice().sort((a, b) => a.time - b.time);
  if (!notes.length) {
    list.innerHTML = `<p style="color:var(--text-secondary);font-size:12.5px">Nenhuma anotação ainda.</p>`;
    return;
  }
  list.innerHTML = notes.map((n) => `
    <div class="note-item${n.important ? " important" : ""}" data-id="${n.id}">
      <span class="note-time">${formatTime(n.time)}</span>
      ${n.important ? `<span class="icon" style="color:var(--accent)">${ICONS.star}</span>` : ""}
      <div>${escapeHtml(n.text)}</div>
      <div class="note-actions">
        <button data-act="important">${n.important ? "Desmarcar" : "Marcar"} importante</button>
        <button data-act="delete">Excluir</button>
      </div>
    </div>`).join("");

  list.querySelectorAll(".note-item").forEach((el) => {
    const id = el.dataset.id;
    el.querySelector(".note-time").addEventListener("click", () => {
      const video = document.getElementById("main-video");
      const note = notes.find((n) => n.id === id);
      if (video && note) { video.currentTime = note.time; video.play().catch(() => {}); }
    });
    el.querySelector('[data-act="important"]').addEventListener("click", () => {
      const all = loadNotes(currentFileId);
      const note = all.find((n) => n.id === id);
      if (note) { note.important = !note.important; saveNotes(currentFileId, all); renderNotesForCurrentFile(); }
    });
    el.querySelector('[data-act="delete"]').addEventListener("click", () => {
      openConfirmDelete(() => {
        const all = loadNotes(currentFileId).filter((n) => n.id !== id);
        saveNotes(currentFileId, all);
        renderNotesForCurrentFile();
      });
    });
  });
}

function updateNoteTimeButton(time) {
  const btn = document.getElementById("btn-add-note");
  if (btn) btn.dataset.time = time;
}

function addNoteAtCurrentTime() {
  if (!currentFileId) return;
  const video = document.getElementById("main-video");
  const time = video ? video.currentTime : 0;
  openNoteModal(time);
}

function openNoteModal(time) {
  const modal = document.getElementById("note-modal");
  modal.hidden = false;
  modal.dataset.time = time;
  const textarea = document.getElementById("note-text");
  textarea.value = "";
  textarea.focus();
}

function closeNoteModal() { document.getElementById("note-modal").hidden = true; }

function confirmNoteModal() {
  const modal = document.getElementById("note-modal");
  const text = document.getElementById("note-text").value.trim();
  if (!text) { closeNoteModal(); return; }
  const notes = loadNotes(currentFileId);
  notes.push({ id: `n${Date.now()}`, time: parseFloat(modal.dataset.time) || 0, text, important: false });
  saveNotes(currentFileId, notes);
  closeNoteModal();
  renderNotesForCurrentFile();
  notify("Anotação salva.");
}

function openConfirmDelete(onConfirm, opts = {}) {
  const modal = document.getElementById("confirm-delete-modal");
  document.getElementById("confirm-delete-title").textContent = opts.title || "Excluir anotação?";
  document.getElementById("confirm-delete-message").textContent = opts.message || "Essa ação não pode ser desfeita.";
  const okBtn = document.getElementById("confirm-ok");
  okBtn.textContent = opts.confirmLabel || "Excluir";
  okBtn.className = opts.dangerous ? "btn btn-danger" : "btn btn-primary";

  document.getElementById("confirm-delete-options").hidden = !opts.showClearOptions;
  document.getElementById("confirm-clear-notes").checked = false;
  document.getElementById("confirm-clear-settings").checked = false;

  modal.hidden = false;
  modal._onConfirm = onConfirm;
}

function closeConfirmDelete() { document.getElementById("confirm-delete-modal").hidden = true; }

/* ---------- pomodoro ---------- */
const POMO_DEFAULT = { work: 25, short: 5, long: 15, cyclesUntilLong: 4 };
let pomoState = { phase: "work", remaining: 0, running: false, cycle: 0, timerId: null };

function pomoCfg() { return storageGet("pomoCfg", POMO_DEFAULT); }
function savePomoCfg(cfg) { storageSet("pomoCfg", cfg); }

function pomoPhaseSeconds(phase) {
  const cfg = pomoCfg();
  if (phase === "work") return cfg.work * 60;
  if (phase === "short") return cfg.short * 60;
  return cfg.long * 60;
}

function initPomodoro() {
  pomoState.remaining = pomoPhaseSeconds("work");
  updatePomodoroUI();
  const cfg = pomoCfg();
  document.getElementById("pomo-work").value = cfg.work;
  document.getElementById("pomo-short").value = cfg.short;
  document.getElementById("pomo-long").value = cfg.long;
}

function drawPomodoroRing() {
  const canvas = document.getElementById("pomo-ring");
  const ctx = canvas.getContext("2d");
  const total = pomoPhaseSeconds(pomoState.phase);
  const pct = total ? 1 - pomoState.remaining / total : 0;
  const w = canvas.width, h = canvas.height, r = w / 2 - 8;
  ctx.clearRect(0, 0, w, h);
  ctx.lineWidth = 8;
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--border") || "#333";
  ctx.beginPath(); ctx.arc(w / 2, h / 2, r, 0, Math.PI * 2); ctx.stroke();
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent") || "#60A5FA";
  ctx.beginPath(); ctx.arc(w / 2, h / 2, r, -Math.PI / 2, -Math.PI / 2 + pct * Math.PI * 2); ctx.stroke();
}

function updatePomodoroUI() {
  document.getElementById("pomo-time").textContent = formatTime(pomoState.remaining);
  document.getElementById("pomo-phase").textContent =
    pomoState.phase === "work" ? "Foco" : pomoState.phase === "short" ? "Pausa curta" : "Pausa longa";
  const toggleBtn = document.getElementById("btn-pomo-toggle");
  toggleBtn.innerHTML = pomoState.running
    ? `${iconSpan(ICONS.pause)} Pausar`
    : `${iconSpan(ICONS.play)} Iniciar`;
  toggleBtn.title = pomoState.running ? "Pausar o cronômetro" : "Iniciar o cronômetro";
  drawPomodoroRing();
}

function tickPomodoro() {
  pomoState.remaining -= 1;
  if (pomoState.remaining <= 0) {
    switchPomodoroPhase();
  }
  updatePomodoroUI();
}

function switchPomodoroPhase() {
  playPomoBeep();
  if (pomoState.phase === "work") {
    pomoState.cycle += 1;
    const cfg = pomoCfg();
    pomoState.phase = pomoState.cycle % cfg.cyclesUntilLong === 0 ? "long" : "short";
    notify("Hora da pausa!");
  } else {
    pomoState.phase = "work";
    notify("De volta ao foco!");
  }
  pomoState.remaining = pomoPhaseSeconds(pomoState.phase);
}

function startPomodoro() {
  if (pomoState.running) return;
  pomoState.running = true;
  pomoState.timerId = setInterval(tickPomodoro, 1000);
  updatePomodoroUI();
}

function pausePomodoro() {
  pomoState.running = false;
  clearInterval(pomoState.timerId);
  updatePomodoroUI();
}

function resetPomodoro() {
  pausePomodoro();
  pomoState.phase = "work";
  pomoState.cycle = 0;
  pomoState.remaining = pomoPhaseSeconds("work");
  updatePomodoroUI();
}

function playPomoBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.value = 660;
    osc.connect(gain); gain.connect(ctx.destination);
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } catch (e) { /* áudio indisponível, segue sem som */ }
}

/* ---------- atalhos de teclado ---------- */
function initKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select" || e.target.isContentEditable) return;

    const video = document.getElementById("main-video");

    if (e.code === "Space") {
      if (!video) return;
      e.preventDefault();
      video.paused ? video.play().catch(() => {}) : video.pause();
    } else if (e.code === "ArrowLeft") {
      if (!video) return;
      e.preventDefault();
      video.currentTime = Math.max(0, video.currentTime - 5);
    } else if (e.code === "ArrowRight") {
      if (!video) return;
      e.preventDefault();
      video.currentTime = Math.min(video.duration || Infinity, video.currentTime + 5);
    } else if (e.key === "n" || e.key === "N") {
      goToRelativeVideo(1);
    } else if (e.key === "p" || e.key === "P") {
      goToRelativeVideo(-1);
    }
  });
}

/* ---------- backup (exportar/importar notas e progresso) ---------- */
function exportBackup() {
  const prefix = `pm:${COURSE_ID}:`;
  const data = {};
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(prefix)) {
      try { data[key.slice(prefix.length)] = JSON.parse(localStorage.getItem(key)); } catch (e) { /* ignora entrada corrompida */ }
    }
  }
  const payload = {
    courseId: COURSE_ID,
    courseName: COURSE_DATA.name || "",
    exportedAt: new Date().toISOString(),
    data,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const safeName = (COURSE_DATA.name || "curso").replace(/[^\w.-]+/g, "_");
  const a = document.createElement("a");
  a.href = url;
  a.download = `backup-${safeName}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  notify("Backup exportado.");
}

function importBackupFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    let payload;
    try {
      payload = JSON.parse(String(reader.result));
    } catch (e) {
      notify("Não foi possível importar: arquivo inválido.");
      return;
    }
    const data = payload && typeof payload === "object" && payload.data ? payload.data : payload;
    if (!data || typeof data !== "object") {
      notify("Não foi possível importar: formato inesperado.");
      return;
    }
    const ok = confirm("Importar este backup vai sobrescrever notas, progresso e preferências deste curso neste navegador. Continuar?");
    if (!ok) return;
    Object.keys(data).forEach((key) => {
      storageSet(key, data[key]);
    });
    notify("Backup importado. Recarregando...");
    setTimeout(() => location.reload(), 800);
  };
  reader.readAsText(file);
}

function initBackupControls() {
  document.getElementById("btn-export-backup").innerHTML = `${iconSpan(ICONS.download)} Exportar backup`;
  document.getElementById("btn-import-backup").innerHTML = `${iconSpan(ICONS.upload)} Importar backup`;
  document.getElementById("btn-export-backup").addEventListener("click", exportBackup);
  document.getElementById("btn-import-backup").addEventListener("click", () => {
    document.getElementById("import-backup-input").click();
  });
  document.getElementById("import-backup-input").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) importBackupFile(file);
    e.target.value = "";
  });

  document.getElementById("btn-settings").innerHTML = iconSpan(ICONS.settings);
  document.getElementById("btn-close-settings").innerHTML = iconSpan(ICONS.close);
}

/* ---------- apagar todos os dados do curso ---------- */
const PLAYER_SETTINGS_KEYS = new Set(["theme", "playbackSpeed", "autoAdvance", "pomoCfg"]);

function clearAllData({ includeProgress, includeNotes, includeSettings }) {
  const prefix = `pm:${COURSE_ID}:`;
  const keysToRemove = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (!key || !key.startsWith(prefix)) continue;
    const name = key.slice(prefix.length);
    const isProgress = name === "completed" || name.startsWith("vtime:");
    const isNotes = name.startsWith("notes:");
    const isSettings = PLAYER_SETTINGS_KEYS.has(name);
    if ((includeProgress && isProgress) || (includeNotes && isNotes) || (includeSettings && isSettings)) {
      keysToRemove.push(key);
    }
  }
  keysToRemove.forEach((key) => localStorage.removeItem(key));
}

function initClearDataControls() {
  document.getElementById("btn-clear-data").innerHTML = `${iconSpan(ICONS.trash)} Apagar todos os dados`;
  document.getElementById("btn-clear-data").addEventListener("click", () => {
    openConfirmDelete(
      () => {
        const includeProgress = document.getElementById("confirm-clear-progress").checked;
        const includeNotes = document.getElementById("confirm-clear-notes").checked;
        const includeSettings = document.getElementById("confirm-clear-settings").checked;
        clearAllData({ includeProgress, includeNotes, includeSettings });
        notify("Dados apagados. Recarregando...");
        setTimeout(() => location.reload(), 600);
      },
      {
        title: "Apagar dados do curso?",
        message: "Marque abaixo o que você quer apagar deste curso, só neste navegador. Essa ação não pode ser desfeita.",
        confirmLabel: "Apagar",
        dangerous: true,
        showClearOptions: true,
      }
    );
  });
}

/* ---------- painéis flutuantes (abertura mutuamente exclusiva) ---------- */
const FLOATING_PANEL_IDS = ["notes-panel", "pomodoro-panel", "settings-panel"];

function closePanel(panelId) {
  document.getElementById(panelId).hidden = true;
}

function togglePanel(panelId) {
  const target = document.getElementById(panelId);
  const wasOpen = !target.hidden;
  FLOATING_PANEL_IDS.forEach((id) => closePanel(id));
  target.hidden = wasOpen;
}

/* ---------- setup geral ---------- */
function setupGlobalUI() {
  document.getElementById("course-title").textContent = COURSE_DATA.name || "Curso";

  document.getElementById("btn-toggle-sidebar").innerHTML = iconSpan(ICONS.sidebar);
  document.getElementById("btn-notes").innerHTML = iconSpan(ICONS.notes);
  document.getElementById("btn-pomodoro").innerHTML = iconSpan(ICONS.timer);
  document.getElementById("btn-close-notes").innerHTML = iconSpan(ICONS.close);
  document.getElementById("btn-close-pomodoro").innerHTML = iconSpan(ICONS.close);
  document.getElementById("btn-add-note").innerHTML = `${iconSpan(ICONS.plus)} Adicionar anotação no tempo atual`;
  document.getElementById("btn-pomo-reset").innerHTML = `${iconSpan(ICONS.reset)} Reiniciar`;
  document.getElementById("btn-pomo-reset").title = "Reiniciar o ciclo do pomodoro";

  document.getElementById("btn-toggle-sidebar").addEventListener("click", () => {
    document.body.classList.toggle("sidebar-closed");
    document.body.classList.toggle("sidebar-open");
    setUiState({ sidebarClosed: document.body.classList.contains("sidebar-closed") });
  });
  if (getUiState().sidebarClosed) document.body.classList.add("sidebar-closed");

  document.getElementById("search-box").addEventListener("input", (e) => renderSidebar(e.target.value));

  document.getElementById("btn-notes").addEventListener("click", () => togglePanel("notes-panel"));
  document.getElementById("btn-close-notes").addEventListener("click", () => closePanel("notes-panel"));
  document.getElementById("btn-add-note").addEventListener("click", addNoteAtCurrentTime);

  document.getElementById("btn-pomodoro").addEventListener("click", () => togglePanel("pomodoro-panel"));
  document.getElementById("btn-close-pomodoro").addEventListener("click", () => closePanel("pomodoro-panel"));

  document.getElementById("btn-settings").addEventListener("click", () => togglePanel("settings-panel"));
  document.getElementById("btn-close-settings").addEventListener("click", () => closePanel("settings-panel"));

  document.getElementById("btn-pomo-toggle").addEventListener("click", () => {
    pomoState.running ? pausePomodoro() : startPomodoro();
  });
  document.getElementById("btn-pomo-reset").addEventListener("click", resetPomodoro);
  ["pomo-work", "pomo-short", "pomo-long"].forEach((id) => {
    document.getElementById(id).addEventListener("change", () => {
      const cfg = {
        work: Math.max(1, parseInt(document.getElementById("pomo-work").value) || 25),
        short: Math.max(1, parseInt(document.getElementById("pomo-short").value) || 5),
        long: Math.max(1, parseInt(document.getElementById("pomo-long").value) || 15),
        cyclesUntilLong: POMO_DEFAULT.cyclesUntilLong,
      };
      savePomoCfg(cfg);
      resetPomodoro();
    });
  });

  document.getElementById("note-cancel").addEventListener("click", closeNoteModal);
  document.getElementById("note-save").addEventListener("click", confirmNoteModal);
  document.getElementById("confirm-cancel").addEventListener("click", closeConfirmDelete);
  document.getElementById("confirm-ok").addEventListener("click", () => {
    const modal = document.getElementById("confirm-delete-modal");
    if (modal._onConfirm) modal._onConfirm();
    closeConfirmDelete();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initAutoAdvanceToggle();
  initBackupControls();
  initClearDataControls();
  initKeyboardShortcuts();
  setupGlobalUI();
  renderSidebar();
  updateStatsBar();
  initPomodoro();
  loadInitialFile();
});
